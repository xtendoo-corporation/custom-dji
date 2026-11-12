from odoo.tests import TransactionCase

MIXIN_FIELD_GROUPS = {
    'can_edit_tax': 'dji_administration.edit_tax',
    'can_edit_discounts': 'dji_administration.edit_discounts',
    'can_edit_price': 'dji_administration.edit_sale_price',
    'can_edit_account': 'dji_administration.edit_account',
    'can_edit_quantity': 'dji_administration.edit_quantity',
    'can_edit_product_desc': 'dji_administration.edit_product_desc',
    'can_edit_product_id': 'dji_administration.edit_product_id',
    'can_create_invoice': 'dji_administration.create_invoice',
    'can_cancel_invoice': 'dji_administration.cancel_invoice',
    'can_create_refund_invoice': 'dji_administration.create_refund_invoice',
    'show_ecommerce_page': 'dji_administration.show_ecommerce_page',
}

ADMIN_GROUP = 'dji_administration.administration_group'

MODELS_WITH_MIXIN = [
    'sale.order',
    'sale.order.line',
    'account.move',
    'account.move.line',
    'product.template',
]

BASE_GROUPS = [
    'base.group_user',
    'sales_team.group_sale_salesman',
    'account.group_account_invoice',
]


class TestAdministratorMixin(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        all_group_xmlids = BASE_GROUPS + [ADMIN_GROUP] + list(MIXIN_FIELD_GROUPS.values())
        cls.admin_user = cls._create_user('dji_admin_user', all_group_xmlids)
        cls.restricted_user = cls._create_user('dji_restricted_user', BASE_GROUPS)

    @classmethod
    def _create_user(cls, login, group_xmlids):
        group_ids = [cls.env.ref(xmlid).id for xmlid in group_xmlids]
        return cls.env['res.users'].create({
            'name': login,
            'login': login,
            'group_ids': [(6, 0, group_ids)],
        })

    def _expected_mixin_values(self, user):
        return {
            field: user.has_group(group_xmlid)
            for field, group_xmlid in MIXIN_FIELD_GROUPS.items()
        }

    def test_is_admin_compute_follows_administration_group(self):
        for model_name in MODELS_WITH_MIXIN:
            with self.subTest(model=model_name):
                record = self.env[model_name].with_user(self.admin_user).new({})
                self.assertTrue(record.with_user(self.admin_user).is_admin)
                record = self.env[model_name].with_user(self.restricted_user).new({})
                self.assertFalse(record.with_user(self.restricted_user).is_admin)

    def test_is_admin_default_follows_administration_group(self):
        admin_default = self.env['sale.order'].with_user(self.admin_user).new({}).is_admin
        restricted_default = self.env['sale.order'].with_user(self.restricted_user).new({}).is_admin
        self.assertTrue(admin_default)
        self.assertFalse(restricted_default)

    def test_permission_defaults_follow_user_groups(self):
        for model_name in MODELS_WITH_MIXIN:
            for user in (self.admin_user, self.restricted_user):
                with self.subTest(model=model_name, user=user.login):
                    record = self.env[model_name].with_user(user).new({})
                    for field, group_xmlid in MIXIN_FIELD_GROUPS.items():
                        self.assertEqual(
                            record[field],
                            user.has_group(group_xmlid),
                            f"default of {field} on {model_name} for {user.login}",
                        )

    def test_permission_computes_follow_user_groups(self):
        for model_name in MODELS_WITH_MIXIN:
            for user in (self.admin_user, self.restricted_user):
                with self.subTest(model=model_name, user=user.login):
                    record = self.env[model_name].with_user(user).new({})
                    expected = self._expected_mixin_values(user)
                    for field, value in expected.items():
                        self.assertEqual(
                            record.with_user(user)[field],
                            value,
                            f"compute of {field} on {model_name} for {user.login}",
                        )

    def test_is_commercial_defaults_to_false(self):
        record = self.env['sale.order'].with_user(self.admin_user).new({})
        self.assertFalse(record.is_commercial)

    def test_picking_state_done_is_false_without_pickings(self):
        order = self.env['sale.order'].create({
            'partner_id': self.env['res.partner'].create({'name': 'Cliente sin albaran'}).id,
        })
        self.assertFalse(order.is_picking_state_done)

    def test_picking_state_done_is_true_when_picking_is_validated(self):
        product = self.env['product.product'].create({
            'name': 'Producto con albaran',
            'is_storable': True,
            'list_price': 10.0,
        })
        order = self.env['sale.order'].create({
            'partner_id': self.env['res.partner'].create({'name': 'Cliente con albaran'}).id,
            'order_line': [(0, 0, {'product_id': product.id, 'product_uom_qty': 2})],
        })
        order.action_confirm()
        picking = order.picking_ids
        self.assertTrue(picking)
        self.assertFalse(order.is_picking_state_done)

        for move in picking.move_ids:
            move.quantity = move.product_uom_qty
        picking.with_context(skip_backorder=True).button_validate()

        self.assertEqual(picking.state, 'done')
        self.assertTrue(order.is_picking_state_done)
