from odoo.exceptions import AccessError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAdministration(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group_comercial = cls.env.ref("sylonuba_administration.commercial_group")
        cls.group_user = cls.env.ref("base.group_user")
        cls.group_invoice = cls.env.ref("account.group_account_invoice")
        cls.comercial = cls.env["res.users"].create(
            {
                "name": "Comercial prueba",
                "login": "comercial_prueba",
                "group_ids": [(6, 0, [cls.group_user.id, cls.group_invoice.id, cls.group_comercial.id])],
            }
        )
        cls.otro = cls.env["res.users"].create(
            {"name": "Otro comercial", "login": "otro_comercial", "group_ids": [(6, 0, [cls.group_user.id, cls.group_invoice.id])]}
        )
        cls.partner = cls.env["res.partner"].create({"name": "Cliente"})

    def _factura(self, user):
        return self.env["account.move"].with_user(self.env.ref("base.user_admin")).create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "invoice_user_id": user.id,
                "invoice_line_ids": [(0, 0, {"name": "linea", "quantity": 1, "price_unit": 10})],
            }
        )

    def test_grupo_registrar_pagos_y_menus(self):
        grupo = self.env.ref("sylonuba_administration.register_payments")
        self.assertEqual(grupo.name, "Register Payments")
        menu = self.env.ref("account.menu_action_account_payments_receivable")
        self.assertIn(grupo, menu.group_ids)

    def test_reglas_existen(self):
        for xmlid in ("own_invoices", "own_payment", "commercials_no_create_invoices"):
            regla = self.env.ref(f"sylonuba_administration.{xmlid}")
            self.assertIn(self.group_comercial, regla.groups)
        regla = self.env.ref("sylonuba_administration.commercials_no_create_invoices")
        self.assertIn("move_type", regla.domain_force)

    def test_reglas_iguales_a_la_13(self):
        """Las tres reglas tienen la misma definición que en la 13 de producción (dominio con move_type en vez de type).
        En la 13 convivían con account.account_move_see_all (grupo de facturación, todo visible): por eso no restringen
        a quien ya está en un grupo contable; hay que conservarlas igual, no endurecerlas."""
        propias = self.env.ref("sylonuba_administration.own_invoices")
        self.assertEqual(propias.model_id.model, "account.move")
        self.assertIn("invoice_user_id", propias.domain_force)
        self.assertEqual((propias.perm_read, propias.perm_write, propias.perm_create, propias.perm_unlink), (True, False, False, False))
        pagos = self.env.ref("sylonuba_administration.own_payment")
        self.assertEqual(pagos.model_id.model, "account.payment")
        self.assertIn("create_uid", pagos.domain_force)
        self.assertEqual((pagos.perm_read, pagos.perm_write, pagos.perm_create, pagos.perm_unlink), (True, False, False, False))
        no_crear = self.env.ref("sylonuba_administration.commercials_no_create_invoices")
        self.assertEqual(no_crear.model_id.model, "account.move")
        self.assertEqual((no_crear.perm_read, no_crear.perm_write, no_crear.perm_create, no_crear.perm_unlink), (False, True, True, True))

    def test_comercial_en_grupo_de_facturacion_ve_todo(self):
        # igual que en la 13: account_move_see_all (grupo de facturación) prevalece sobre Facturas Propias
        propia = self._factura(self.comercial)
        ajena = self._factura(self.otro)
        visibles = self.env["account.move"].with_user(self.comercial).search([("id", "in", (propia | ajena).ids)])
        self.assertEqual(visibles, propia | ajena)

    def test_vistas_cargan(self):
        for modelo, xmlid in (
            ("account.move", "account.view_move_form"),
            ("sale.order", "sale.view_order_form"),
            ("product.product", "product.product_product_tree_view"),
        ):
            vista = self.env.ref(xmlid)
            self.env[modelo].get_view(vista.id, vista.type)
