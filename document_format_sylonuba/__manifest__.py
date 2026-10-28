{
    "name": "Document Format Sylonuba",
    "summary": """Formatos de documentos de Xtendoo para Sylonuba, sin fabricación ni comisiones""",
    "version": "19.0.1.0.0",
    "description": """
Variante de document_format para Sylonuba: mismos informes de factura, albarán,
pedido, compra y etiquetas, sin el informe de fabricación (mrp) ni la
dependencia de comisiones. Incompatible con document_format: ambos modifican
account.report_invoice y los informes de albarán y pedido; instalar solo uno.
""",
    "author": "Manuel Calero, Daniel Dominguez",
    "company": "Xtendoo",
    "website": "http://xtendoo.es",
    "category": "Extra Tools",
    "license": "AGPL-3",
    "depends": [
        "sale",
        "stock",
        "stock_picking_report_valued",
        "product",
        "account",
        "account_payment_mode",  # renombrado de account_payment_partner en 19.0
        "account_invoice_report_grouped_by_picking",
        "mail",
        "contacts",
        "purchase",  # views/purchase/purchase.xml hereda purchase.report_purchaseorder
        "xtendoo_account_invoice_report_due_list",  # get_multi_due_list de las facturas
        "account_payment_order",  # campo reference_type de las facturas
        "l10n_es_partner",  # campo comercial del cliente
        "product_expiry",  # fecha de caducidad del lote en los albaranes
        "xtendoo_product_classification",  # clasificación en el informe acumulado de pedidos
    ],
    "data": [
        "data/paper_format_label.xml",
        "views/stock_picking/stock_picking_view.xml",
        "views/delivery/delivery_document.xml",
        "views/delivery/delivery_commodity.xml",
        "views/delivery/delivery_document_without_price.xml",
        "views/invoice/account_tax_template.xml",
        "views/invoice/invoice_document.xml",
        "views/invoice/invoice_dossier.xml",
        "views/invoice/invoice_gruped_by_picking.xml",
        "views/layout/external_layout_clean.xml",
        "views/sale/sale_order_document.xml",
        "views/sale/sale_order_blank_document.xml",
        "views/label/product_label.xml",
        "report/report_label_barcode.xml",
        "report/report_label_barcode_template.xml",
        "views/email_default_template/account_invoice_send_views.xml",
        "views/purchase/purchase.xml",
        "report/report_saleorder_accumulate.xml",
    ],
    "installable": True,
    "auto_install": False,
}
