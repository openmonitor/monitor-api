import dataclasses
import json
import logging

from . import cache

class ControllerMonitor:
    def __init__(
        self,
        cache_controller: cache.CacheController,
    ):
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.cache_controller = cache_controller

    def get_data(self):
        self.logger.info('getting monitor data')
        data = self.cache_controller.get_monitor_data()
        return json.dumps(dataclasses.asdict(data))
