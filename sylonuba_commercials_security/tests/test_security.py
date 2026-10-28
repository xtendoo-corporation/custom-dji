from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSecurity(TransactionCase):
    def test_grupos_y_privilegio(self):
        privilegio = self.env.ref("sylonuba_commercials_security.privilege_commercials_security")
        for xmlid in ("jose_gonzalez_payments", "domingo_payments"):
            grupo = self.env.ref(f"sylonuba_commercials_security.{xmlid}")
            self.assertEqual(grupo.privilege_id, privilegio)

    def test_regla_de_diarios_por_comercial(self):
        diario_ok = self.env["account.journal"].create(
            {"name": "Efectivo Domingo", "type": "cash", "code": "EFD"}
        )
        diario_otro = self.env["account.journal"].create(
            {"name": "Efectivo de otro", "type": "cash", "code": "EFO"}
        )
        grupo = self.env.ref("sylonuba_commercials_security.domingo_payments")
        user = self.env["res.users"].create(
            {
                "name": "Comercial Domingo",
                "login": "domingo_test",
                "group_ids": [(6, 0, [self.env.ref("base.group_user").id, self.env.ref("account.group_account_invoice").id, grupo.id])],
            }
        )
        visibles = self.env["account.journal"].with_user(user).search([("id", "in", (diario_ok | diario_otro).ids)])
        self.assertIn(diario_ok, visibles)
        # la regla deja ver los diarios de venta/compra/general y los de efectivo propios: el de efectivo ajeno queda fuera
        self.assertNotIn(diario_otro, visibles)
