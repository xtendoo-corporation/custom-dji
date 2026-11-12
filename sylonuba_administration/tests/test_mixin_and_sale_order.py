from odoo.tests import TransactionCase, tagged

MIXIN_BOOLEAN_FIELDS = (
    "is_admin",
    "can_edit_tax",
    "can_edit_discounts",
    "can_edit_price",
    "can_edit_account",
    "can_edit_quantity",
    "can_edit_product_desc",
    "can_edit_product_id",
    "can_create_invoice",
    "can_cancel_invoice",
    "can_create_refund_invoice",
    "show_ecommerce_page",
)


@tagged("post_install", "-at_install")
class TestAdministratorMixinRule(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group_user = cls.env.ref("base.group_user")
        cls.group_admin = cls.env.ref("sylonuba_administration.administration_group")
        cls.group_commercial = cls.env.ref("sylonuba_administration.commercial_group")
        cls.admin_user = cls.env["res.users"].create(
            {
                "name": "Administrador prueba",
                "login": "admin_mixin_prueba",
                "group_ids": [(6, 0, [cls.group_user.id, cls.group_admin.id])],
            }
        )
        cls.commercial_user = cls.env["res.users"].create(
            {
                "name": "Comercial mixin prueba",
                "login": "comercial_mixin_prueba",
                "group_ids": [(6, 0, [cls.group_user.id, cls.group_commercial.id])],
            }
        )

    def _read_flags(self, user):
        rule = self.env["administrator.mixin.rule"].with_user(user).create({})
        return rule.read(list(MIXIN_BOOLEAN_FIELDS))[0]

    def test_defaults_and_computes_for_admin(self):
        flags = self._read_flags(self.admin_user)
        self.assertTrue(flags["is_admin"])
        self.assertEqual(flags["can_edit_tax"], self.admin_user.has_group("sylonuba_administration.edit_tax"))

    def test_defaults_and_computes_for_commercial(self):
        flags = self._read_flags(self.commercial_user)
        self.assertFalse(flags["is_admin"])
        self.assertFalse(flags["can_edit_tax"])
        self.assertFalse(flags["can_create_invoice"])

    def test_admin_gets_every_flag_granted_by_its_group(self):
        rule = self.env["administrator.mixin.rule"].with_user(self.admin_user).new({})
        for field_name in MIXIN_BOOLEAN_FIELDS:
            self.assertIsInstance(rule[field_name], bool, field_name)

    def test_commercial_flags_match_group_membership(self):
        rule = self.env["administrator.mixin.rule"].with_user(self.commercial_user).new({})
        expected_groups = {
            "can_edit_tax": "sylonuba_administration.edit_tax",
            "can_edit_discounts": "sylonuba_administration.edit_discounts",
            "can_edit_price": "sylonuba_administration.edit_sale_price",
            "can_edit_account": "sylonuba_administration.edit_account",
            "can_edit_quantity": "sylonuba_administration.edit_quantity",
            "can_edit_product_desc": "sylonuba_administration.edit_product_desc",
            "can_edit_product_id": "sylonuba_administration.edit_product_id",
            "can_create_invoice": "sylonuba_administration.create_invoice",
            "can_cancel_invoice": "sylonuba_administration.cancel_invoice",
            "can_create_refund_invoice": "sylonuba_administration.create_refund_invoice",
            "show_ecommerce_page": "sylonuba_administration.show_ecommerce_page",
        }
        for field_name, group_xmlid in expected_groups.items():
            granted = self.commercial_user.has_group(group_xmlid)
            self.assertEqual(rule[field_name], granted, field_name)

    def test_admin_user_sees_admin_flag_through_computed_field(self):
        rule = self.env["administrator.mixin.rule"].with_user(self.admin_user).new({})
        self.assertTrue(rule.is_admin)


@tagged("post_install", "-at_install")
class TestSaleOrderPickingState(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Cliente picking"})
        cls.product = cls.env["product.product"].create(
            {"name": "Producto picking", "type": "consu", "is_storable": True}
        )

    def _confirm_order(self):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (0, 0, {"product_id": self.product.id, "product_uom_qty": 2, "price_unit": 10}),
                ],
            }
        )
        order.action_confirm()
        return order

    def test_picking_state_not_done_before_validation(self):
        order = self._confirm_order()
        self.assertTrue(order.picking_ids)
        self.assertFalse(order.is_picking_state_done)

    def test_picking_state_done_after_validation(self):
        order = self._confirm_order()
        for move in order.picking_ids.move_ids:
            move.quantity = move.product_uom_qty
        order.picking_ids.button_validate()
        self.assertEqual(set(order.picking_ids.mapped("state")), {"done"})
        self.assertTrue(order.is_picking_state_done)

    def test_compute_without_pickings_is_false(self):
        order = self.env["sale.order"].create({"partner_id": self.partner.id})
        self.assertFalse(order.is_picking_state_done)
