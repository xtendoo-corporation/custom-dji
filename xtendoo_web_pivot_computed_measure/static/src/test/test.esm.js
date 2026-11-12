/* Copyright 2022 Tecnativa - Carlos Roca
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html) */

import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("web_pivot_computed_measure_tour", {
    url: "/odoo/action-xtendoo_web_pivot_computed_measure.demo_action_res_partner_report_pivot",
    steps: () => [
        {
            trigger: '.o_pivot_buttons div[aria-label="Main actions"] button',
            run: "click",
        },
        {
            trigger: 'div[data-id="__computed__"] a',
            run: "click",
        },
        {
            trigger: "select#computed_measure_field_1",
            run: "select partner_latitude",
        },
        {
            trigger: "select#computed_measure_field_2",
            run: "select partner_longitude",
        },
        {
            trigger: "select#computed_measure_operation",
            run: "select m1+m2",
        },
        {
            trigger: "select#computed_measure_format",
            run: "select float",
        },
        {
            trigger: "button.o_add_computed_measure",
            run: "click",
        },
        {
            trigger: '.o_pivot_buttons div[aria-label="Main actions"] button',
            run: "click",
        },
        {
            trigger: 'th.o_pivot_measure_row:contains("Geo Latitude")',
        },
        {
            trigger: 'th.o_pivot_measure_row:contains("Geo Longitude")',
        },
        {
            trigger: 'th.o_pivot_measure_row:contains("Geo Latitude+Geo Longitude")',
        },
        {
            trigger: 'div.o_value:contains("40.7127760")',
        },
        {
            trigger: 'div.o_value:contains("-74.0059740")',
        },
        {
            trigger: 'div.o_value:contains("-33.29")',
        },
    ],
});
