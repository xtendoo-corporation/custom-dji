import base64

from odoo import _, fields, models


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def _track_signature(self, values, field):
        """Deja en el chatter un mensaje al crear o borrar la firma.

        :param values: diccionario con los valores que se escriben
        :param field: nombre del campo de firma que se rastrea
        """
        if field not in values:
            return
        attachments = []
        messages = []
        if values.get(field):
            content = base64.b64decode(values.get(field))
            attachments = [("signature", content)]
            messages.append(_("Signature has been created."))
            messages.append(_("Signature date: %s", fields.Datetime.now()))
        else:
            messages.append(_("Signature has been deleted."))
            messages.append(_("Deletion date: %s", fields.Datetime.now()))
        msg_body = "<ul>%s</ul>" % "".join("<li>%s</li>" % m for m in messages)
        self.message_post(body=msg_body, attachments=attachments)
