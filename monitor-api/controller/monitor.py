import dataclasses
import json
import logging
import typing

from . import cache
try:
    import common.model as model
except ModuleNotFoundError:
    print('common package not in python path or dependencies not installed', flush=True)


class ControllerMonitor:
    def __init__(
        self,
        cache_controller: cache.CacheController,
    ):
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.cache_controller = cache_controller

    def get_data(
        self,
        timeunit_as_string: bool,
    ):
        self.logger.info('getting monitor data')
        data = self.cache_controller.get_monitor_data(timeunit_as_string=timeunit_as_string)
        return json.dumps(dataclasses.asdict(data))
