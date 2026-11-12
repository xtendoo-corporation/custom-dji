from datetime import datetime, timedelta

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAlertDateCalculate(TransactionCase):
    def _lot(self, alert_time):
        product = self.env["product.product"].create(
            {
                "name": "Expiry product",
                "type": "consu",
                "is_storable": True,
                "tracking": "lot",
                "use_expiration_date": True,
                "alert_time": alert_time,
            }
        )
        return self.env["stock.lot"].create(
            {
                "name": "LOT-%s" % alert_time,
                "product_id": product.id,
                "expiration_date": datetime(2030, 6, 30, 12, 0),
            }
        )

    def test_alert_date_is_expiration_minus_alert_time(self):
        lot = self._lot(10)
        lot.alert_date = False
        lot._onchange_life_date()
        self.assertEqual(lot.alert_date, datetime(2030, 6, 30, 12, 0) - timedelta(days=10))

    def test_without_alert_time_alert_date_is_untouched(self):
        lot = self._lot(0)
        lot.alert_date = False
        lot._onchange_life_date()
        self.assertFalse(lot.alert_date)
