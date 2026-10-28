# Origen: OCA/account-financial-tools 15.0 (account_balance_line), último con rama.
# Copyright 2010-2014 Camptocamp - Vincent Renaville
# Copyright 2016 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Xtendoo Balance on journal items",
    "summary": "Muestra la columna de saldo con total en las listas de apuntes contables",
    "version": "19.0.1.0.0",
    "category": "Accounting",
    "website": "https://github.com/xtendoo-corporation/custom-dji",
    "author": "Camptocamp, Tecnativa, Xtendoo, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["account"],
    "data": ["views/account_move_line_view.xml"],
}
