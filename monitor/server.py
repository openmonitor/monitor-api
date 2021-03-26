import logging

import falcon

import controller
try:
    import util
except ModuleNotFoundError:
    print('common package not in python path or dependencies not installed')


logger = logging.getLogger(__name__)
util.configure_default_logging(stdout_level=logging.DEBUG)


class Monitor:

    def on_get(self, req, resp):
        logger.info('GET /')
        resp.body = controller.get_monitor_data()


class Comment:

    def on_post(self, req, resp):
        resp.status_code = falcon.HTTP_NOT_IMPLEMENTED

    def on_update(self, req, resp):
        resp.status_code = falcon.HTTP_NOT_IMPLEMENTED


def create():
    api = falcon.API()
    api.add_route('/', Monitor())
    api.add_route('/comment', Comment())
    logger.info('falcon initialized')
    return api


application = create()
