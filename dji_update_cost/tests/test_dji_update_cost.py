from unittest.mock import patch

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestDjiUpdateCost(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.template"].create({
            "name": "Producto coste",
            "type": "consu",
            "purchase_ok": True,
            "standard_price": 1.0,
        })
        cls.partner = cls.env["res.partner"].create({"name": "Proveedor coste"})
        cls.purchase_order = cls.env["purchase.order"].create({
            "partner_id": cls.partner.id,
            "order_line": [(0, 0, {
                "product_id": cls.product.product_variant_id.id,
                "product_qty": 2,
                "price_unit": 10.0,
            })],
        })
        cls.purchase_line = cls.purchase_order.order_line
        cls.wizard = cls.env["dji.update.cost"].create({})

    def _run_update(self, po_result=None, line_result=None, product_result=None):
        """Ejecuta el wizard simulando las búsquedas de producto, pedido y línea."""
        products = product_result if product_result is not None else self.product
        po_value = po_result if po_result is not None else self.purchase_order
        line_value = line_result if line_result is not None else self.purchase_line
        models = {
            "product.template": products,
            "purchase.order": po_value,
            "purchase.order.line": line_value,
        }
        patches = [
            patch.object(
                type(self.env[name]),
                "search",
                return_value=result,
            )
            for name, result in models.items()
        ]
        for active_patch in patches:
            active_patch.start()
            self.addCleanup(active_patch.stop)
        self.wizard.product_update_cost()

    def test_cost_unchanged_when_no_purchase_order_found(self):
        self.product.standard_price = 5.0
        self._run_update(
            po_result=self.env["purchase.order"],
            line_result=self.env["purchase.order.line"],
        )
        self.assertEqual(self.product.standard_price, 5.0)

    def test_cost_unchanged_when_no_purchase_line_found(self):
        self.product.standard_price = 5.0
        self._run_update(line_result=self.env["purchase.order.line"])
        self.assertEqual(self.product.standard_price, 5.0)

    def test_cost_equals_price_unit_without_discount(self):
        self.purchase_line.discount = 0.0
        self._run_update()
        self.assertEqual(self.product.standard_price, 10.0)

    def test_cost_applies_line_discount(self):
        self.purchase_line.discount = 10.0
        self._run_update()
        self.assertAlmostEqual(self.product.standard_price, 9.0, places=2)

    def test_no_products_does_nothing(self):
        self.product.standard_price = 5.0
        self._run_update(product_result=self.env["product.template"])
        self.assertEqual(self.product.standard_price, 5.0)
