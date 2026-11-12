# Copyright 2022 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from odoo.tests import common, tagged


@tagged("post_install", "-at_install")
class TestUIPivot(common.HttpCase):
    def test_ui(self):
        # El tour usa el menú y la vista pivot de los datos demo del módulo.
        if not self.env.ref(
            "xtendoo_web_pivot_computed_measure.demo_menu_res_partner_report_pivot",
            raise_if_not_found=False,
        ):
            self.skipTest("Requiere los datos demo del módulo")
        self.start_tour(
            "/odoo/action-xtendoo_web_pivot_computed_measure.demo_action_res_partner_report_pivot",
            "web_pivot_computed_measure_tour",
            login="admin",
        )
