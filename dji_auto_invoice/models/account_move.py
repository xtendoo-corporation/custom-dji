from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    def post(self):
        res = super().post()
        for invoice in self:
            if invoice.partner_id.email and invoice.move_type == 'receivable' and invoice.partner_id.auto_invoice:
                invoice.send_email()
        return res

    def send_email(self):
        self.ensure_one()
        template = self.env.ref('account.email_template_edi_invoice')
        email_message = template.send_mail(self.id, force_send=True)
        subject = email_message.subject or 'Factura enviada por correo electrónico'
        message_body = f"Para: {self.partner_id.name}\n\n{email_message.body}"
        self.message_post(
            body=message_body,
            message_type='comment',
            subtype_id=self.env.ref('mail.mt_comment').id,
            partner_ids=[(4, self.partner_id.id)]
        )
