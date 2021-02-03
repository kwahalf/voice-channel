import flask
import gunicorn.app.base
import importlib
import multiprocessing
import os
import plac
import sys
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class StandardConfig(object):
    """Flask configuration defaults across all blueprints."""

    def __init__(self):
        """Initialize config from environment."""

        try:
            self.SERVER_NAME = os.environ["SERVER_NAME"]
        except KeyError:
            pass

        self.DEBUG = bool(os.environ.get("FLASK_DEBUG"))
        self.SECRET_KEY = os.environ["FLASK_SECRET_KEY"]


def parse_registration(raw):
    """Parse a Flash blueprint registration request."""

    (blueprint_name, url_prefix) = raw.split(":")

    return (blueprint_name, url_prefix)


@plac.annotations(
    interface=("hostname", "option", "i", str),
    port=("port number", "option", "p", int),
    workers=("workers count", "option", "w", int),
    timeout=("worker timeout", "option", "t", int),
    max_requests=("requests before worker restart", "option", None, int),
    registrations=(
        "blueprint registrations",
        "positional",
        None,
        parse_registration,
    ),
)
def main(
    interface="0.0.0.0",
    port=os.getenv("PORT", 8000),
    workers=None,
    timeout=30,
    max_requests=0,
    *registrations
):

    def on_starting(server):
        logger.info("server is starting")

    class GunicornServer(gunicorn.app.base.Application):
        """Gunicorn server with custom configuration.
        Instantiated in the parent; `load()` is then called, post-fork, in each
        child.
        """

        def init(self, parser, opts, args):

            return {
                "bind": "{0}:{1}".format(interface, port),
                "forwarded_allow_ips": "*",
                "workers": workers or 2 * multiprocessing.cpu_count() + 1,
                "timeout": timeout,
                "on_starting": on_starting,
                "max_requests": max_requests,
            }


        def load(self):
            # create app and initialize config

            app = flask.Flask("voice")

            app.config.from_object(StandardConfig())

            @app.before_request
            def app_before_request():
                request_headers = flask.request.headers
                self.current_request = dict(
                    method=flask.request.method,
                    path=u"{}?{}".format(
                        flask.request.path, flask.request.query_string
                    ),
                    client_ip=request_headers.get("X-Forwarded-For", ""),
                    user_agent=request_headers.get("User-Agent", ""),
                )

                logger.info(self.current_request)

            @app.teardown_request
            def app_teardown_request(exception):
                self.current_request = dict()


            # register specified blueprints
            for (blueprint_name, url_prefix) in registrations:
                blueprint_name = ".".join(["api.blueprints", blueprint_name])
                module = importlib.import_module(blueprint_name)
                blueprint = module.create_blueprint(
                    url_prefix
                )

                app.register_blueprint(blueprint, url_prefix=url_prefix)
            return app

    old_argv = sys.argv

    try:
        sys.argv = sys.argv[:1]

        server = GunicornServer()

        server.run()
    except BaseException:
        sys.argv = old_argv
