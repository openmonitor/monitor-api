import logging

import falcon

import controller.proxy as proxy
try:
    import common.model as model
    import common.util as commonutil
except ModuleNotFoundError:
    print('common package not in python path or dependencies not installed', flush=True)


logger: logging.Logger = logging.getLogger(__name__)
commonutil.configure_default_logging(stdout_level=logging.DEBUG)
proxy = proxy.ControllerProxy()


class Monitor:
    def __init__(self):
        self.logger: logging.Logger = logging.getLogger(__name__)

    def on_get(self, req, resp):
        self.logger.info('GET /')
        resp.text = proxy.get_monitor_data()

    def on_post(self, req, resp):
        self.logger.info('POST /')
        resp.text = proxy.post_monitor_data()


class Comment:
    def __init__(self):
        self.logger: logging.Logger = logging.getLogger(__name__)

    def on_post(self, req, resp):
        self.logger.info('POST /comment')
        resp.status = controller.post_comment(
            req=req,
        )

    def on_put(self, req, resp):
        self.logger.info('PUT /comment')
        resp.status = controller.update_comment(
            req=req,
        )

    def on_delete(self, req, resp):
        self.logger.info('DELETE /comment')
        resp.status = controller.delete_comment(
            req=req,
        )


def create():
    api = falcon.App(cors_enable=True)
    api.add_route('/', Monitor())
    #api.add_route('/comment', Comment())
    logger.info('falcon initialized')
    return api


application = create()
