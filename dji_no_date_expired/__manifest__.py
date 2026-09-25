# Copyright 2022 Xtendoo
# Portado de la rama 15.0 a 19.0 el 2026-09-08: en 19.0 "stock.production.lot"
# se renombro a "stock.lot", "_get_dates" ya no existe (ahora son
# "_compute_expiration_date" + "_compute_dates" separados), y se anadio
# "removal_date" tambien en stock.move.line (antes solo vivia en el lote).
# Mismo objetivo que en 15.0: DJI usa lote para trazabilidad pero NUNCA
# quiere que Odoo trate nada como "caducado" (eso rompe el calculo de
# stock disponible/previsto en presupuestos).

{
    "name": "DJI No Expired Date",
    "summary": "DJI No Expired Date",
    "version": "19.0.1.0.0",
    "depends": ["product_expiry"],
    "maintainers": ["Daniel Dominguez"],
    "author": "Xtendoo",
    "license": "AGPL-3",
    "data": [],
    "installable": True,
    "auto_install": True,
    "post_init_hook": "post_init_hook",
}
