from unittest.mock import patch

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestOnlyCommercialClients(TransactionCase):
    def _domain(self, is_commercial):
        users = type(self.env["res.users"])
        with patch.object(users, "has_group", return_value=is_commercial):
            return self.env["sale.order"].new({})._get_domain()["domain"]

    def test_non_commercial_sees_all_companies(self):
        self.assertEqual(
            self._domain(False), {"partner_id": [("parent_id", "=", False)]}
        )

    def test_commercial_sees_only_own_clients(self):
        self.assertEqual(
            self._domain(True),
            {
                "partner_id": [
                    ("user_id", "=", self.env.user.id),
                    ("parent_id", "=", False),
                ]
            },
        )
