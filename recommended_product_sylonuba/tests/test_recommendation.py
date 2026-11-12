from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestRecommendation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Cliente recomendaciones"})
        cls.product = cls.env["product.product"].create(
            {"name": "Producto recomendado", "type": "consu", "list_price": 12.5}
        )
        cls.other = cls.env["product.product"].create(
            {"name": "Otro producto", "type": "consu", "list_price": 3.0}
        )
        # Pedido pasado, confirmado y con unidades entregadas
        past = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (0, 0, {"product_id": cls.product.id, "product_uom_qty": 5}),
                    (0, 0, {"product_id": cls.other.id, "product_uom_qty": 2}),
                ],
            }
        )
        past.action_confirm()
        for line in past.order_line:
            line.qty_delivered = line.product_uom_qty
        cls.order = cls.env["sale.order"].create({"partner_id": cls.partner.id})

    def _wizard(self):
        wiz = (
            self.env["sale.order.recommendation"]
            .with_context(active_id=self.order.id)
            .create({"order_id": self.order.id})
        )
        wiz._generate_recommendations()
        return wiz

    def test_recomienda_lo_entregado(self):
        wiz = self._wizard()
        productos = wiz.line_ids.mapped("product_id")
        self.assertIn(self.product, productos)
        self.assertIn(self.other, productos)
        linea = wiz.line_ids.filtered(lambda x: x.product_id == self.product)
        self.assertEqual(linea.units_delivered, 5)
        self.assertEqual(linea.times_delivered, 1)

    def test_aceptar_crea_linea_en_el_pedido(self):
        wiz = self._wizard()
        linea = wiz.line_ids.filtered(lambda x: x.product_id == self.product)
        linea.units_included = 3
        wiz.action_accept()
        creadas = self.order.order_line.filtered(lambda x: x.product_id == self.product)
        self.assertEqual(len(creadas), 1)
        self.assertEqual(creadas.product_uom_qty, 3)

    def test_precio_origen_tarifa_y_ultima_venta(self):
        wiz = self._wizard()
        linea = wiz.line_ids.filtered(lambda x: x.product_id == self.product)
        self.assertEqual(linea.price_unit, 12.5)
        wiz.sale_recommendation_price_origin = "last_sale_price"
        linea._compute_price_unit()
        self.assertEqual(linea.price_unit, 12.5)

    def test_vistas_cargan(self):
        # el formulario del pedido (boton de recomendados) y el del asistente se combinan sin errores
        self.env["sale.order"].get_view(
            self.env.ref("sale.view_order_form").id, "form"
        )
        self.env["sale.order.recommendation"].get_view(
            self.env.ref("recommended_product_sylonuba.sale_order_recommendation_view_form").id, "form"
        )
        self.env["res.config.settings"].get_view(
            self.env.ref("sale.res_config_settings_view_form").id, "form"
        )

    def test_default_order_y_cache_de_calculo(self):
        wiz = (
            self.env["sale.order.recommendation"]
            .with_context(active_id=self.order.id)
            .create({})
        )
        self.assertEqual(wiz.order_id, self.order)
        wiz._generate_recommendations()
        wiz.line_ids = [(5, 0, 0)]
        # mismo calculo: no se regeneran las lineas
        wiz._generate_recommendations()
        self.assertFalse(wiz.line_ids)

    def test_limite_de_lineas(self):
        wiz = self._wizard()
        wiz.line_amount = 1
        wiz._generate_recommendations()
        self.assertEqual(len(wiz.line_ids), 1)

    def test_lineas_existentes_se_actualizan_y_eliminan(self):
        self.order.write(
            {
                "order_line": [
                    (0, 0, {"product_id": self.product.id, "product_uom_qty": 1}),
                    (0, 0, {"product_id": self.other.id, "product_uom_qty": 1}),
                ]
            }
        )
        wiz = self._wizard()
        self.assertEqual(len(wiz.line_ids), 2)
        linea = wiz.line_ids.filtered(lambda x: x.product_id == self.product)
        otra = wiz.line_ids.filtered(lambda x: x.product_id == self.other)
        self.assertTrue(linea.sale_line_id)
        self.assertEqual(linea.units_included, 1)
        linea.units_included = 4
        otra.units_included = 0
        wiz.action_accept()
        self.assertEqual(self.order.order_line.product_id, self.product)
        self.assertEqual(self.order.order_line.product_uom_qty, 4)

    def test_precio_tarifa_y_ultima_venta_en_linea_nueva(self):
        pricelist = self.env["product.pricelist"].create(
            {
                "name": "Tarifa recomendados",
                "item_ids": [
                    (
                        0,
                        0,
                        {
                            "applied_on": "1_product",
                            "product_tmpl_id": self.product.product_tmpl_id.id,
                            "compute_price": "fixed",
                            "fixed_price": 9.0,
                        },
                    )
                ],
            }
        )
        self.order.pricelist_id = pricelist
        wiz = self._wizard()
        linea = wiz.line_ids.filtered(lambda x: x.product_id == self.product)
        self.assertEqual(linea.price_unit, 9.0)
        wiz.sale_recommendation_price_origin = "last_sale_price"
        linea.units_included = 2
        wiz.action_accept()
        nueva = self.order.order_line.filtered(lambda x: x.product_id == self.product)
        self.assertEqual(nueva.price_unit, 12.5)
