from . import models
# report/report_saleorder_accumulate.xml está desactivado en el manifest
# desde v15 de producción; el AbstractModel de Python que lo respalda
# nunca se llega a usar sin esa vista. Causaba un ImportError circular
# al cargar (ya detectado en el salto 16->17) - desactivado aquí también,
# consistente con el estado ya existente.
# from . import report
