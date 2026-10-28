from odoo import _, fields, models


class WizardReportStockMinimum(models.TransientModel):
    _name = "wizard.report.stock.minimum"
    _description = "Products Report Under Minimum"

    warehouse_option = fields.Selection(
        [("1", "All warehouses"), ("2", "Specific warehouse")],
        string="Show",
        default="1",
        required=True,
    )
    warehouse_selected = fields.Many2one("stock.warehouse", string="Warehouse")

    def _get_domain(self):
        domain = []
        if self.warehouse_option == "2" and self.warehouse_selected:
            domain.append(("warehouse_id", "=", self.warehouse_selected.id))
        # se calcula en el momento: así no depende de un campo guardado
        orderpoints = self.env["stock.warehouse.orderpoint"].search(domain)
        # el stock disponible no es un campo guardado: se recalcula al generar
        orderpoints.product_id.invalidate_recordset(["qty_available"])
        orderpoints.invalidate_recordset(["qty_available", "under_minimum"])
        return [("id", "in", orderpoints.filtered("under_minimum").ids)]

    def run_wizard(self):
        self.ensure_one()
        view = self.env.ref("stock_minimum_report.view_minimum_warehouse_orderpoint_tree")
        return {
            "type": "ir.actions.act_window",
            "name": _("Products Report Under Minimum"),
            "res_model": "stock.warehouse.orderpoint",
            "view_mode": "list",
            "views": [(view.id, "list")],
            "domain": self._get_domain(),
        }
