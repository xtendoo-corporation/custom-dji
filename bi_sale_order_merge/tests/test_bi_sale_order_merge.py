from unittest.mock import PropertyMock, patch

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestBiSaleOrderMerge(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.SaleOrder = cls.env["sale.order"]
        cls.partner = cls.env["res.partner"].create({"name": "Merge customer"})
        cls.other_partner = cls.env["res.partner"].create({"name": "Other customer"})
        cls.product_a = cls.env["product.product"].create({"name": "Product A", "list_price": 10})
        cls.product_b = cls.env["product.product"].create({"name": "Product B", "list_price": 20})

    def _set_auto_merge(self, enabled):
        settings = self.env["res.config.settings"].create({"auto_merge_sale_orderlines": enabled})
        settings.set_values()

    def _order(self, lines=None, partner=None, **vals):
        order_vals = {"partner_id": (partner or self.partner).id}
        order_vals.update(vals)
        order_vals["order_line"] = [
            (0, 0, {"product_id": product.id, "product_uom_qty": qty, "price_unit": price})
            for product, qty, price in (lines or [])
        ]
        return self.SaleOrder.create(order_vals)

    def _quoted_order(self, partner=None, **vals):
        return self._order(
            lines=[(self.product_a, 1, 10), (self.product_b, 2, 20)],
            partner=partner,
            **vals,
        )

    def _same_product_order(self, enabled_before=False):
        self._set_auto_merge(enabled_before)
        return self._order(lines=[(self.product_a, 1, 10), (self.product_a, 2, 10)])

    # _merge_notes

    def test_merge_notes_joins_unique_notes_as_paragraphs(self):
        first = self.SaleOrder.new({"note": "First note"})
        second = self.SaleOrder.new({"note": "<p>Second note</p>"})
        duplicate = self.SaleOrder.new({"note": "First note"})
        empty = self.SaleOrder.new({"note": False})
        result = self.SaleOrder._merge_notes(first | second | duplicate | empty)
        self.assertEqual(str(result), "<p>First note</p><p>Second note</p>")

    def test_merge_notes_empty_when_no_notes(self):
        empty = self.SaleOrder.new({"note": False})
        self.assertFalse(str(self.SaleOrder._merge_notes(empty)))

    # _merge_orders

    def test_merge_orders_new_creates_order_and_cancels_sources(self):
        first = self._quoted_order(client_order_ref="REF-1", note="Note one")
        second = self._quoted_order(client_order_ref="REF-2", note="Note two")
        merged = self.SaleOrder._merge_orders(
            first | second, "new", customer_ref="REF-1,REF-2", origin="S1, S2")
        self.assertNotIn(merged, first | second)
        self.assertEqual(merged.state, "draft")
        self.assertEqual(merged.client_order_ref, "REF-1,REF-2")
        self.assertEqual(merged.origin, "S1, S2")
        self.assertEqual(len(merged.order_line), 4)
        self.assertEqual(first.state, "cancel")
        self.assertEqual(second.state, "cancel")
        self.assertIn("Note one", str(merged.note))
        self.assertIn("Note two", str(merged.note))

    def test_merge_orders_new_with_different_partner(self):
        first = self._quoted_order()
        second = self._quoted_order()
        merged = self.SaleOrder._merge_orders(
            first | second, "new", partner=self.other_partner, origin="S")
        self.assertEqual(merged.partner_id, self.other_partner)
        self.assertEqual(len(merged.order_line), 4)

    def test_merge_orders_exist_creates_order_and_deletes_sources(self):
        first = self._quoted_order()
        second = self._quoted_order()
        source_ids = (first | second).ids
        merged = self.SaleOrder._merge_orders(first | second, "exist", origin="S")
        self.assertEqual(len(merged.order_line), 4)
        self.assertFalse(self.SaleOrder.search([("id", "in", source_ids)]))

    def test_merge_orders_exist_1_merges_into_target_and_cancels_others(self):
        target = self._quoted_order()
        other = self._quoted_order()
        result = self.SaleOrder._merge_orders(
            target | other, "exist_1", target=target, origin="S")
        self.assertEqual(result, target)
        self.assertEqual(len(target.order_line), 4)
        self.assertEqual(other.state, "cancel")
        self.assertTrue(other.exists())

    def test_merge_orders_exist_2_moves_lines_and_deletes_others(self):
        target = self._quoted_order(client_order_ref="TARGET")
        other = self._quoted_order()
        other_id = other.id
        result = self.SaleOrder._merge_orders(
            target | other, "exist_2", target=target, customer_ref="REF", origin="S")
        self.assertEqual(result, target)
        self.assertEqual(target.client_order_ref, "REF")
        self.assertEqual(len(target.order_line), 4)
        self.assertFalse(self.SaleOrder.search([("id", "=", other_id)]))

    def test_merge_orders_exist_1_keeps_target_ref_without_customer_ref(self):
        target = self._quoted_order(client_order_ref="TARGET")
        other = self._quoted_order()
        self.SaleOrder._merge_orders(target | other, "exist_1", target=target, origin="S")
        self.assertEqual(target.client_order_ref, "TARGET")

    # auto_merge and overrides

    def test_auto_merge_returns_none_when_no_draft_orders(self):
        order = self._quoted_order()
        order.action_cancel()
        self.assertIsNone(order.auto_merge())

    def test_auto_merge_sums_same_product_and_price(self):
        order = self._order(lines=[(self.product_a, 1, 10), (self.product_a, 3, 10)])
        merged_lines = order.auto_merge()
        self.assertEqual(len(merged_lines), 1)
        self.assertEqual(next(iter(merged_lines)).product_uom_qty, 4)

    def test_auto_merge_keeps_same_product_with_different_price(self):
        order = self._order(lines=[(self.product_a, 1, 10), (self.product_a, 1, 15)])
        self.assertEqual(len(order.auto_merge()), 2)

    def test_create_merges_lines_when_auto_merge_enabled(self):
        order = self._same_product_order(enabled_before=True)
        self.assertEqual(len(order.order_line), 1)
        self.assertEqual(order.order_line.product_uom_qty, 3)

    def test_create_keeps_lines_when_auto_merge_disabled(self):
        order = self._same_product_order(enabled_before=False)
        self.assertEqual(len(order.order_line), 2)

    def test_create_keeps_distinct_products_when_auto_merge_enabled(self):
        self._set_auto_merge(True)
        order = self._order(lines=[(self.product_a, 1, 10), (self.product_b, 1, 20)])
        self.assertEqual(len(order.order_line), 2)

    def test_create_keeps_same_product_with_different_price_when_enabled(self):
        self._set_auto_merge(True)
        order = self._order(lines=[(self.product_a, 1, 10), (self.product_a, 1, 15)])
        self.assertEqual(len(order.order_line), 2)

    def test_write_merges_lines_when_auto_merge_enabled(self):
        order = self._same_product_order()
        self._set_auto_merge(True)
        order.write({"note": "Updated"})
        self.assertEqual(len(order.order_line), 1)
        self.assertEqual(order.order_line.product_uom_qty, 3)

    def test_write_keeps_lines_when_auto_merge_disabled(self):
        order = self._same_product_order()
        order.write({"note": "Updated"})
        self.assertEqual(len(order.order_line), 2)

    def test_write_skips_merge_for_non_draft_order_when_enabled(self):
        order = self._same_product_order()
        order.action_cancel()
        self._set_auto_merge(True)
        order.write({"note": "Cancelled"})
        self.assertEqual(len(order.order_line), 2)

    def test_action_confirm_merges_lines_when_auto_merge_enabled(self):
        order = self._same_product_order()
        self._set_auto_merge(True)
        order.action_confirm()
        self.assertEqual(order.state, "sale")
        self.assertEqual(len(order.order_line), 1)
        self.assertEqual(order.order_line.product_uom_qty, 3)

    def test_action_confirm_keeps_lines_when_auto_merge_disabled(self):
        order = self._same_product_order()
        order.action_confirm()
        self.assertEqual(order.state, "sale")
        self.assertEqual(len(order.order_line), 2)

    def test_action_quotation_send_merges_lines_when_auto_merge_enabled(self):
        order = self._same_product_order()
        self._set_auto_merge(True)
        order.action_quotation_send()
        self.assertEqual(len(order.order_line), 1)

    def test_action_quotation_send_keeps_lines_when_auto_merge_disabled(self):
        order = self._same_product_order()
        order.action_quotation_send()
        self.assertEqual(len(order.order_line), 2)

    # sale.orderline.merge.wizard

    def test_merge_orderlines_sums_duplicate_lines(self):
        order = self._same_product_order()
        self.env["sale.orderline.merge.wizard"].with_context(
            active_id=order.id).merge_orderlines()
        self.assertEqual(len(order.order_line), 1)
        self.assertEqual(order.order_line.product_uom_qty, 3)

    def test_merge_orderlines_keeps_different_prices(self):
        order = self._order(lines=[(self.product_a, 1, 10), (self.product_a, 1, 15)])
        self.env["sale.orderline.merge.wizard"].with_context(
            active_id=order.id).merge_orderlines()
        self.assertEqual(len(order.order_line), 2)

    def test_merge_orderlines_rejects_non_draft_order(self):
        order = self._quoted_order()
        order.action_confirm()
        with self.assertRaises(ValidationError):
            self.env["sale.orderline.merge.wizard"].with_context(
                active_id=order.id).merge_orderlines()

    # res.config.settings

    def test_config_settings_roundtrip_enabled(self):
        self._set_auto_merge(True)
        values = self.env["res.config.settings"].create({}).get_values()
        self.assertTrue(values["auto_merge_sale_orderlines"])

    def test_config_settings_roundtrip_disabled(self):
        self._set_auto_merge(False)
        values = self.env["res.config.settings"].create({}).get_values()
        self.assertFalse(values["auto_merge_sale_orderlines"])

    # sale.order.merge wizard

    def _merge_wizard(self, orders, **vals):
        return self.env["sale.order.merge"].with_context(
            active_model="sale.order", active_ids=orders.ids).create(vals)

    def test_default_get_fills_selected_orders(self):
        first = self._quoted_order()
        second = self._quoted_order()
        wizard = self.env["sale.order.merge"].with_context(
            active_model="sale.order", active_ids=(first | second).ids).new({})
        self.assertEqual(set(wizard.sale_order_to_merge.ids), set((first | second).ids))

    def test_default_get_rejects_done_orders(self):
        first = self._quoted_order()
        second = self._quoted_order()
        with patch.object(type(self.SaleOrder), "state", new_callable=PropertyMock,
                          return_value="done"):
            with self.assertRaises(UserError):
                self.env["sale.order.merge"].with_context(
                    active_model="sale.order", active_ids=(first | second).ids).default_get(
                    ["sale_order_to_merge"])

    def test_merge_orders_exist_1_concatenates_notes_when_present(self):
        target = self._quoted_order(note="<p>Target note</p>")
        other = self._quoted_order(note="<p>Other note</p>")
        self.SaleOrder._merge_orders(target | other, "exist_1", target=target, origin="S")
        self.assertIn("Target note", target.note)
        self.assertIn("Other note", target.note)

    def test_set_data_resets_fields_when_different_customer(self):
        wizard = self.env["sale.order.merge"].new({
            "merge_with_diff_partner": True,
            "type": "exist_1",
            "sale_order": self._quoted_order().id,
        })
        wizard.set_data()
        self.assertFalse(wizard.sale_order)
        self.assertEqual(wizard.type, "new")

    def test_set_data_clears_partner_when_same_customer(self):
        wizard = self.env["sale.order.merge"].new({
            "merge_with_diff_partner": False,
            "partner_id": self.partner.id,
        })
        wizard.set_data()
        self.assertFalse(wizard.partner_id)

    def test_merge_sale_requires_two_orders(self):
        order = self._quoted_order()
        with self.assertRaises(UserError):
            self._merge_wizard(order).merge_sale()

    def test_merge_sale_rejects_confirmed_orders(self):
        first = self._quoted_order()
        second = self._quoted_order()
        second.action_confirm()
        with self.assertRaises(UserError):
            self._merge_wizard(first | second).merge_sale()

    def test_merge_sale_rejects_different_partners(self):
        first = self._quoted_order()
        second = self._quoted_order(partner=self.other_partner)
        with self.assertRaises(UserError):
            self._merge_wizard(first | second).merge_sale()

    def test_merge_sale_rejects_done_target(self):
        first = self._quoted_order()
        second = self._quoted_order()
        target = self._quoted_order()
        target.state = "cancel"
        wizard = self._merge_wizard(first | second, type="exist_1", sale_order=target.id)
        with self.assertRaises(UserError):
            wizard.merge_sale()

    def test_merge_sale_new_order_action(self):
        first = self._quoted_order(client_order_ref="A")
        second = self._quoted_order(client_order_ref="B")
        action = self._merge_wizard(first | second, type="new").merge_sale()
        merged = self.SaleOrder.browse(action["res_id"])
        self.assertEqual(action["res_model"], "sale.order")
        self.assertEqual(merged.client_order_ref, "A,B")
        self.assertEqual(first.state, "cancel")

    def test_merge_sale_exist_1_into_selected_target(self):
        first = self._quoted_order()
        second = self._quoted_order()
        action = self._merge_wizard(
            first | second, type="exist_1", sale_order=first.id).merge_sale()
        self.assertEqual(action["res_id"], first.id)
        self.assertEqual(len(first.order_line), 4)

    def test_merge_sale_with_different_partner(self):
        first = self._quoted_order()
        second = self._quoted_order()
        wizard = self._merge_wizard(
            first | second, merge_with_diff_partner=True, partner_id=self.other_partner.id)
        action = wizard.merge_sale()
        self.assertEqual(self.SaleOrder.browse(action["res_id"]).partner_id, self.other_partner)

    def test_merge_sale_with_different_partner_without_customer(self):
        first = self._quoted_order()
        second = self._quoted_order()
        wizard = self._merge_wizard(first | second, merge_with_diff_partner=True)
        action = wizard.merge_sale()
        self.assertEqual(self.SaleOrder.browse(action["res_id"]).partner_id, self.partner)

    # merge.same.customer.sale.order.wizard

    def test_same_customer_onchange_partner_loads_draft_orders(self):
        draft = self._quoted_order()
        self._quoted_order(partner=self.other_partner)
        wizard = self.env["merge.same.customer.sale.order.wizard"].new(
            {"partner_id": self.partner.id})
        wizard.update_so_list()
        self.assertIn(draft.id, wizard.sale_order_to_merge.ids)

    def test_same_customer_onchange_orders_clears_target_for_partner(self):
        order = self._quoted_order()
        wizard = self.env["merge.same.customer.sale.order.wizard"].new({
            "partner_id": self.partner.id,
            "sale_order": order.id,
        })
        wizard.update_so_value()
        self.assertFalse(wizard.sale_order)

    def test_same_customer_onchange_orders_keeps_target_without_partner(self):
        order = self._quoted_order()
        wizard = self.env["merge.same.customer.sale.order.wizard"].new(
            {"sale_order": order.id})
        wizard.update_so_value()
        self.assertEqual(wizard.sale_order, order)

    def test_same_customer_requires_two_orders(self):
        order = self._quoted_order()
        wizard = self.env["merge.same.customer.sale.order.wizard"].create({
            "sale_order_to_merge": [(6, 0, order.ids)],
        })
        with self.assertRaises(UserError):
            wizard.merge_same_customer_sale_orders()

    def test_same_customer_rejects_confirmed_orders(self):
        first = self._quoted_order()
        second = self._quoted_order()
        second.action_confirm()
        wizard = self.env["merge.same.customer.sale.order.wizard"].create({
            "sale_order_to_merge": [(6, 0, (first | second).ids)],
        })
        with self.assertRaises(UserError):
            wizard.merge_same_customer_sale_orders()

    def test_same_customer_rejects_different_partners(self):
        first = self._quoted_order()
        second = self._quoted_order(partner=self.other_partner)
        wizard = self.env["merge.same.customer.sale.order.wizard"].create({
            "sale_order_to_merge": [(6, 0, (first | second).ids)],
        })
        with self.assertRaises(UserError):
            wizard.merge_same_customer_sale_orders()

    def test_same_customer_rejects_done_target(self):
        first = self._quoted_order()
        second = self._quoted_order()
        target = self._quoted_order()
        target.state = "cancel"
        wizard = self.env["merge.same.customer.sale.order.wizard"].create({
            "sale_order_to_merge": [(6, 0, (first | second).ids)],
            "sale_order": target.id,
            "type": "exist_1",
        })
        with self.assertRaises(UserError):
            wizard.merge_same_customer_sale_orders()

    def test_same_customer_new_order_action(self):
        first = self._quoted_order(client_order_ref="X")
        second = self._quoted_order(client_order_ref="Y")
        wizard = self.env["merge.same.customer.sale.order.wizard"].create({
            "partner_id": self.partner.id,
            "sale_order_to_merge": [(6, 0, (first | second).ids)],
        })
        action = wizard.merge_same_customer_sale_orders()
        merged = self.SaleOrder.browse(action["res_id"])
        self.assertEqual(merged.client_order_ref, "X,Y")
        self.assertEqual(len(merged.order_line), 4)

    def test_same_customer_exist_2_deletes_others(self):
        target = self._quoted_order()
        other = self._quoted_order()
        other_id = other.id
        wizard = self.env["merge.same.customer.sale.order.wizard"].create({
            "partner_id": self.partner.id,
            "sale_order_to_merge": [(6, 0, (target | other).ids)],
            "sale_order": target.id,
            "type": "exist_2",
        })
        action = wizard.merge_same_customer_sale_orders()
        self.assertEqual(action["res_id"], target.id)
        self.assertFalse(self.SaleOrder.search([("id", "=", other_id)]))
        self.assertEqual(len(target.order_line), 4)
