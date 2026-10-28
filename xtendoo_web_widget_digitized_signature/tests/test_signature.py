from odoo.tests import tagged
from odoo.tests.common import TransactionCase, new_test_user

PNG = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
)


@tagged("post_install", "-at_install")
class TestDigitizedSignature(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1
        )

    def _picking(self):
        picking_type = self.warehouse.out_type_id
        return self.env["stock.picking"].create(
            {
                "picking_type_id": picking_type.id,
                "location_id": picking_type.default_location_src_id.id,
                "location_dest_id": picking_type.default_location_dest_id.id,
            }
        )

    def test_fields_keep_the_names_used_in_13(self):
        fields_ = self.env["stock.picking"]._fields
        self.assertEqual(fields_["digital_signature"].type, "binary")
        self.assertTrue(fields_["digital_signature"].attachment)
        self.assertEqual(fields_["name_receiver"].type, "char")
        self.assertEqual(fields_["vat_receiver"].type, "char")
        self.assertTrue(self.env["res.users"]._fields["digital_signature"].attachment)

    def test_signature_receiver_name_and_vat_on_picking(self):
        picking = self._picking()
        picking.write(
            {"digital_signature": PNG, "name_receiver": "Juan Receptor", "vat_receiver": "12345678Z"}
        )
        picking.invalidate_recordset()
        self.assertTrue(picking.digital_signature)
        self.assertEqual(picking.name_receiver, "Juan Receptor")
        self.assertEqual(picking.vat_receiver, "12345678Z")
        attachment = self.env["ir.attachment"].search(
            [
                ("res_model", "=", "stock.picking"),
                ("res_id", "=", picking.id),
                ("res_field", "=", "digital_signature"),
            ]
        )
        self.assertEqual(len(attachment), 1)

    def test_existing_attachment_is_read_back(self):
        """Una firma guardada como adjunto (como las 7.513 de 13) se lee sin migrarla."""
        picking = self._picking()
        self.env["ir.attachment"].create(
            {
                "name": "digital_signature",
                "res_model": "stock.picking",
                "res_id": picking.id,
                "res_field": "digital_signature",
                "datas": PNG,
            }
        )
        picking.invalidate_recordset()
        self.assertTrue(picking.digital_signature)

    def test_picking_form_has_the_signature_widget(self):
        user = new_test_user(
            self.env, login="almacen_firma", groups="stock.group_stock_user,base.group_user"
        )
        arch = self.env["stock.picking"].with_user(user).get_view(view_type="form")["arch"]
        self.assertIn('name="digital_signature"', arch)
        self.assertIn('widget="signature"', arch)
        self.assertIn('name="name_receiver"', arch)
        self.assertIn('name="vat_receiver"', arch)

    def test_user_signature_is_tracked_in_the_chatter(self):
        user = self.env["res.users"].create(
            {"name": "Usuario firma", "login": "usuario_firma", "email": "firma@example.com"}
        )
        messages_before = self.env["mail.message"].search([])
        attachments_before = self.env["ir.attachment"].search_count([])
        user.digital_signature = PNG
        new = self.env["mail.message"].search([]) - messages_before
        self.assertIn("Signature has been created.", "".join(new.mapped("body")))
        self.assertGreaterEqual(self.env["ir.attachment"].search_count([]) - attachments_before, 1)
        messages_before = self.env["mail.message"].search([])
        user.digital_signature = False
        new = self.env["mail.message"].search([]) - messages_before
        self.assertIn("Signature has been deleted.", "".join(new.mapped("body")))
