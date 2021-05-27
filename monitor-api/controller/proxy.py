import logging

from . import cache
from . import comment
from . import monitor
try:
    import common.database.factory as db_fac
    import common.observer as observer
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
        obs = observer.Observer(
            name='comment-controller-observer',
            callback='http://127.0.0.1:1337',
        )
        self.comment.register_observer(observer=obs)

    def get_monitor_data(
        self,
        timeunit_as_string: bool =False,
    ):
        return self.monitor.get_data(timeunit_as_string=timeunit_as_string)

    def post_monitor_data(self):
        return self.cache.update_monitor_data()

    def post_comment(self, req):
        return self.comment.write_comment(req=req)
