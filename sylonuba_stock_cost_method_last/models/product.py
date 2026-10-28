# Copyright 2016-2019 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo import fields, models
from odoo.tools import SQL


class ProductCategory(models.Model):
    _inherit = "product.category"

    property_cost_method = fields.Selection(
        selection_add=[("last", "Last Price")],
        ondelete={"last": "set default"},
    )


class ProductTemplate(models.Model):
    _inherit = "product.template"

    # product.template.cost_method (stock_account) es un campo computado
    # cuyo valor viene de categ_id.property_cost_method, pero su propia
    # lista de selection es estática y NO hereda las opciones añadidas
    # arriba - hay que extenderla también aquí o la asignación del valor
    # 'last' calculado falla con ValueError "Wrong value for
    # product.template.cost_method" en cuanto se crea/actualiza cualquier
    # producto de una categoría con coste 'last' (detectado en el salto
    # 18->19 al cargar l10n_es/data/product_data.xml).
    cost_method = fields.Selection(
        selection_add=[("last", "Last Price")],
    )



class ProductProduct(models.Model):
    _inherit = "product.product"

    def _run_fifo_batch(self, at_date=None, lot=None, location=None):
        # El core valora con _run_fifo_batch todo método que no sea estándar
        # ni promedio. Con 'last' las salidas se valoran al último precio de
        # compra, así que valorar el stock por capas FIFO no cuadra con los
        # asientos contables. Se valora con el valor de los movimientos.
        last_products = self.filtered(
            lambda product: product.cost_method == "last"
        ) if not lot else self.browse()
        std_prices, values = super(
            ProductProduct, self - last_products
        )._run_fifo_batch(at_date=at_date, lot=lot, location=location)
        if last_products:
            last_std_prices, last_values = last_products._run_last_batch(
                at_date=at_date
            )
            std_prices.update(last_std_prices)
            values.update(last_values)
        return std_prices, values

    def _run_fifo(self, quantity, lot=None, at_date=None, location=None):
        # Salidas sin movimiento asociado (p. ej. una factura de cliente
        # suelta) se valoran en el core con la pila FIFO. Con 'last' deben
        # valorarse al último precio, igual que las salidas de stock.
        self.ensure_one()
        if self.cost_method == "last" and not lot:
            price = self.standard_price
            if at_date:
                last_in = self._get_last_in(at_date)
                price = last_in._get_price_unit() if last_in else price
            return quantity * price
        return super()._run_fifo(
            quantity, lot=lot, at_date=at_date, location=location
        )

    def _run_last_batch(self, at_date=None):
        """Valor y precio unitario de los productos con coste 'last':
        entradas menos salidas, a su valor registrado en cada movimiento.
        Si hay una actualización manual de precio, se parte de ella: valor
        manual por la cantidad anterior más los movimientos desde entonces."""
        manual_by_product = self._get_last_product_value(at_date)
        params = SQL(", ").join(
            SQL(
                "(%s, %s::timestamp, %s::numeric)",
                product.id,
                manual_by_product[product].date if product in manual_by_product
                else datetime.min,
                manual_by_product[product].value if product in manual_by_product
                else 0.0,
            )
            for product in self
        )
        query = SQL(
            """
            SELECT mv.product_id,
                   mv.value * COALESCE(SUM(
                       CASE WHEN m.date < mv.date THEN
                            CASE WHEN m.is_in THEN m.product_qty
                                 ELSE -m.product_qty END
                       END), 0)
                   + COALESCE(SUM(
                       CASE WHEN m.date >= mv.date THEN
                            CASE WHEN m.is_in THEN m.value ELSE -m.value END
                       END), 0)
              FROM (VALUES %s) AS mv(product_id, date, value)
              LEFT JOIN stock_move m
                     ON m.product_id = mv.product_id
                    AND m.company_id = %s
                    AND m.state = 'done'
                    AND (m.is_in OR m.is_out)
                    AND (%s IS NULL OR m.date <= %s)
             GROUP BY mv.product_id, mv.value
            """,
            params,
            self.env.company.id,
            at_date or None,
            at_date or None,
        )
        # consulta SQL directa: volcar antes lo pendiente en ORM
        self.env["stock.move"].flush_model()
        value_by_product_id = dict(self.env.execute_query(query))
        std_price_by_product_id = {}
        for product in self:
            value = float(value_by_product_id.setdefault(product.id, 0.0))
            value_by_product_id[product.id] = value
            quantity = (
                product.with_context(to_date=at_date).qty_available
                if at_date
                else product.qty_available
            )
            std_price_by_product_id[product.id] = (
                value / quantity if quantity else product.standard_price
            )
        return std_price_by_product_id, value_by_product_id
