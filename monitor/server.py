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
        resp.text = controller.get_monitor_data()


class Comment:

    def on_post(self, req, resp):
        logger.info('POST /comment')
        resp.status = controller.post_comment(
            req=req,
        )

    def on_update(self, req, resp):
        resp.status = falcon.HTTP_NOT_IMPLEMENTED


def create():
    api = falcon.App(cors_enable=True)
    api.add_route('/', Monitor())
    api.add_route('/comment', Comment())
    logger.info('falcon initialized')
    return api


application = create()
