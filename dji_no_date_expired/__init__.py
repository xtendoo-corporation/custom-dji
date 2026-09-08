from . import models


def post_init_hook(env):
    """Recalcula fechas de lotes/lineas ya existentes tras instalar el modulo.

    Instalar el modulo solo cambia el comportamiento para lotes/lineas
    NUEVAS. Los que ya existian (creados mientras el modulo no estaba, p.ej.
    tras la migracion 15->19) se quedarian con expiration_date/removal_date
    reales -- este hook fuerza el mismo recalculo que haria un alta nueva.
    """
    lots = env["stock.lot"].search([("product_id.use_expiration_date", "=", True)])
    lots.invalidate_recordset(["expiration_date", "use_date", "removal_date", "alert_date"])
    lots._compute_expiration_date()
    lots._compute_dates()

    move_lines = env["stock.move.line"].search([("product_id.use_expiration_date", "=", True)])
    move_lines.invalidate_recordset(["expiration_date", "removal_date"])
    move_lines._compute_expiration_date()
    move_lines._compute_removal_date()
