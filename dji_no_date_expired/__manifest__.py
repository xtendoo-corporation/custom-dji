# Copyright 2022 Xtendoo
# Portado de la rama 15.0 a 19.0 el 2026-09-08: en 19.0 "stock.production.lot"
# se renombro a "stock.lot", "_get_dates" ya no existe (ahora son
# "_compute_expiration_date" + "_compute_dates" separados), y se anadio
# "removal_date" tambien en stock.move.line (antes solo vivia en el lote).
# Objetivo: DJI usa lote para trazabilidad y quiere ver la fecha de caducidad
# que escribe el usuario, pero Odoo NUNCA debe tratar nada como "caducado" a
# efectos de stock (eso rompe el stock disponible/previsto en presupuestos).
# Desde 19.0.1.1.0 se conserva expiration_date (solo la pone el usuario, sin
# valor por defecto) y se siguen anulando removal_date, alert_date y use_date.

{
    "name": "DJI No Expired Date",
    "summary": "DJI No Expired Date",
    "version": "19.0.1.1.0",
    "depends": ["product_expiry"],
    "maintainers": ["Daniel Dominguez"],
    "author": "Xtendoo",
    "license": "AGPL-3",
    "data": ["views/stock_move_line_views.xml"],
    "installable": True,
    "auto_install": True,
    "post_init_hook": "post_init_hook",
}
