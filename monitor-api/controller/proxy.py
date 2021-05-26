import logging

from . import cache
from . import comment
from . import monitor
try:
    import common.database.factory as db_fac
except ModuleNotFoundError:
    print('common package not in python path or dependencies not installed')

class ControllerProxy:
    def __init__(self):
        self.logger: logging.Logger = logging.getLogger(__name__)
        # make connection
        conn_fac = db_fac.DatabaseConnectionFactory()
        conn = conn_fac.make_connection()
        self.cache = cache.CacheController(conn=conn)
        self.monitor = monitor.ControllerMonitor(cache_controller=self.cache)
        self.comment = comment.ControllerComment(
            cache_controller=self.cache,
            connection=conn,
        )

    def get_monitor_data(self):
        return self.monitor.get_data()

    def post_monitor_data(self):
        self.cache.update_monitor_data()

    def post_comment(self, req):
        return self.comment.write_comment(req=req)
