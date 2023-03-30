# Copyright 2023 Xtendoo (https://xtendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).from odoo import api, models, fields
from odoo import api, models, fields, _


class AdministratorMixinRule(models.Model):
    _name = 'administrator.mixin.rule'
    _description = 'Administrator mixin rule'


    def _get_default_admin(self):
        return self.env["res.users"].has_group(
            "dji_administration.administration_group"
        )

    def _is_admin(self):
        self.is_admin = self.env["res.users"].has_group(
            "dji_administration.administration_group"
        )

    is_admin = fields.Boolean(
        compute='_is_admin',
        string="isAdmin",
        default=lambda self: self._get_default_admin()
    )

    is_commercial = fields.Boolean(
        string="Check user ia a commercial",
        default=False,
    )

    def _get_can_edit_tax(self):
        return self.env["res.users"].has_group(
            "dji_administration.edit_tax"
        )

    can_edit_tax = fields.Boolean(
        compute='_can_edit_tax',
        string="Can edit Tax",
        default=lambda self: self._get_can_edit_tax()
    )

    def _can_edit_tax(self):
        self.can_edit_tax = self.env["res.users"].has_group(
            "dji_administration.edit_tax"
        )

    def _can_edit_discounts(self):
        self.can_edit_discounts = self.env["res.users"].has_group(
            "dji_administration.edit_discounts"
        )

    def _get_can_edit_discounts(self):
        return self.env["res.users"].has_group(
            "dji_administration.edit_discounts"
        )

    can_edit_discounts = fields.Boolean(
        compute='_can_edit_discounts',
        string="Can edit discounts",
        default=lambda self: self._get_can_edit_discounts()
    )

    def _can_edit_price(self):
        self.can_edit_price = self.env["res.users"].has_group(
            "dji_administration.edit_sale_price"
        )

    can_edit_price = fields.Boolean(
        compute='_can_edit_price',
        string="Can edit price",
        default=lambda self: self._get_can_edit_price()
    )

    def _get_can_edit_price(self):
        return self.env["res.users"].has_group(
            "dji_administration.edit_sale_price"
        )

    def _can_edit_account(self):
        self.can_edit_account = self.env["res.users"].has_group(
            "dji_administration.edit_account"
        )

    def _get_can_edit_account(self):
        return self.env["res.users"].has_group(
            "dji_administration.edit_account"
        )

    can_edit_account = fields.Boolean(
        compute='_can_edit_account',
        string="Can edit account",
        default=lambda self: self._get_can_edit_account()
    )

    def _can_edit_quantity(self):
        self.can_edit_quantity = self.env["res.users"].has_group(
            "dji_administration.edit_quantity"
        )

    def _get_can_edit_quantity(self):
        return self.env["res.users"].has_group(
            "dji_administration.edit_quantity"
        )

    can_edit_quantity = fields.Boolean(
        compute='_can_edit_quantity',
        string="Can edit quantity",
        default=lambda self: self._get_can_edit_quantity()
    )

    def _can_edit_product_desc(self):
        self.can_edit_product_desc = self.env["res.users"].has_group(
            "dji_administration.edit_product_desc"
        )

    def _get_can_edit_product_desc(self):
        return self.env["res.users"].has_group(
            "dji_administration.edit_product_desc"
        )

    can_edit_product_desc = fields.Boolean(
        compute='_can_edit_product_desc',
        string="Can edit product_desc",
        default=lambda self: self._get_can_edit_product_desc()
    )

    def _can_edit_product_id(self):
        self.can_edit_product_id = self.env["res.users"].has_group(
            "dji_administration.edit_product_id"
        )

    def _get_can_edit_product_desc(self):
        return self.env["res.users"].has_group(
            "dji_administration.edit_product_id"
        )

    can_edit_product_id = fields.Boolean(
        compute='_can_edit_product_id',
        string="Can edit product_id",
        default=lambda self: self._get_can_edit_product_desc()
    )

    def _can_create_invoice(self):
        self.can_create_invoice = self.env["res.users"].has_group(
            "dji_administration.create_invoice"
        )

    def _get_can_create_invoice(self):
        return self.env["res.users"].has_group(
            "dji_administration.create_invoice"
        )

    can_create_invoice = fields.Boolean(
        compute='_can_create_invoice',
        string="Can create Invoice",
        default=lambda self: self._get_can_create_invoice()
    )

    def _can_cancel_invoice(self):
        self.can_cancel_invoice = self.env["res.users"].has_group(
            "dji_administration.cancel_invoice"
        )

    def _get_can_cancel_invoice(self):
        return self.env["res.users"].has_group(
            "dji_administration.cancel_invoice"
        )

    can_cancel_invoice = fields.Boolean(
        compute='_can_cancel_invoice',
        string="Can cancel Invoice",
        default=lambda self: self._get_can_cancel_invoice()
    )

    def _can_create_refund_invoice(self):
        self.can_create_refund_invoice = self.env["res.users"].has_group(
            "dji_administration.create_refund_invoice"
        )

    def _get_can_create_refund_invoice(self):
        return self.env["res.users"].has_group(
            "dji_administration.create_refund_invoice"
        )

    can_create_refund_invoice = fields.Boolean(
        compute='_can_create_refund_invoice',
        string="Can create refund Invoice",
        default=lambda self: self._get_can_create_refund_invoice()
    )

    def _show_ecommerce_page(self):
        self.show_ecommerce_page = self.env["res.users"].has_group(
            "dji_administration.show_ecommerce_page"
        )

    def _get_show_ecommerce_page(self):
        return self.env["res.users"].has_group(
            "dji_administration.show_ecommerce_page"
        )

    show_ecommerce_page = fields.Boolean(
        compute='_show_ecommerce_page',
        string="Show Ecommerce Page",
        default=lambda self: self._get_show_ecommerce_page()
    )

