from . import models
# report/report_saleorder_accumulate.xml está desactivado en el manifest
# desde v15 de producción; el AbstractModel de Python que lo respalda
# nunca se llega a usar sin esa vista. Causaba un ImportError circular
# al cargar en v17 (nunca se había probado instalar hasta ahora) -
# desactivado aquí también, consistente con el estado ya existente.
# from . import report
