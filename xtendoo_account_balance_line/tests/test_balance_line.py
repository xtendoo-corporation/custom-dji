from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestBalanceLine(TransactionCase):
    def test_balance_column_visible_by_default_with_total(self):
        view = self.env.ref("account.view_move_line_tree")
        arch = self.env["account.move.line"].get_view(view.id, "list")["arch"]
        self.assertRegex(arch, r'name="balance"[^>]*optional="show"|optional="show"[^>]*name="balance"')
        self.assertIn("Total Balance", arch)
