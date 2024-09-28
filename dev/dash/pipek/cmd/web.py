import optparse
from pipek import web, dashapp
import os


def main():
    options = web.get_program_options()
    app = web.create_app()

    if options.profile:
        from werkzeug.middleware.profiler import ProfilerMiddleware

        app.config["PROFILE"] = True
        app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])
        options.debug = True

    app.config["DEBUG"] = options.debug
    app.run(
        debug=options.debug,
        host=options.host,
        port=int(options.port),
    )
