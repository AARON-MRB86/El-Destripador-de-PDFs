"""Script para verificar que la aplicación se importa correctamente sin errores.
Ejecutar este script ayuda a identificar problemas de importación o errores de sintaxis en los archivos de la aplicación antes de iniciar el servidor.
"""

import traceback

try:
    from App.main import app

    routes = list(app.router.routes)
    print('OK', 'routes_count=', len(routes))
    for r in routes:
        print(getattr(r, 'path', r))
except Exception as e:
    traceback.print_exc()
    print('ERROR', e)
