# Copyright 2019 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestAccountMoveLineStockInfo(TransactionCase):
    def test_account_move_line_stock_move_fields(self):
        """Test that the stock_move_id field exists on account.move.line."""
        # Verify the field exists and is properly defined
        aml_model = self.env["account.move.line"]
        self.assertTrue(hasattr(aml_model, "stock_move_id"))

    def test_stock_move_account_move_line_ids(self):
        """Test that the account_move_line_ids field exists on stock.move."""
        # Verify the field exists and is properly defined
        move_model = self.env["stock.move"]
        self.assertTrue(hasattr(move_model, "account_move_line_ids"))

    def test_account_move_lines_are_linked_to_stock_move(self):
        stock = self.env.ref("stock.stock_location_stock")
        account = self.env["account.account"].search(
            [("company_ids", "in", self.env.company.id), ("account_type", "=", "expense")],
            limit=1,
        )
        scrap = self.env["stock.location"].create(
            {"name": "Merma valorada", "usage": "inventory", "valuation_account_id": account.id}
        )
        product = self.env["product.product"].create({"name": "Valorado", "is_storable": True})
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.env.ref("stock.picking_type_internal").id,
                "location_id": stock.id,
                "location_dest_id": scrap.id,
            }
        )
        move = self.env["stock.move"].create(
            {
                "product_id": product.id,
                "product_uom_qty": 1,
                "picking_id": picking.id,
                "location_id": stock.id,
                "location_dest_id": scrap.id,
            }
        )
        vals_list = move._get_account_move_line_vals()
        self.assertEqual(len(vals_list), 2)
        self.assertEqual({vals["stock_move_id"] for vals in vals_list}, {move.id})
