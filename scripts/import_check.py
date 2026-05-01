import traceback

try:
    from App.main import create_app
    app = create_app()
    routes = list(app.router.routes)
    print('OK', 'routes_count=', len(routes))
    for r in routes:
        print(r.path)
except Exception as e:
    traceback.print_exc()
    print('ERROR', e)
