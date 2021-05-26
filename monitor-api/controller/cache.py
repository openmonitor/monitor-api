from dataclasses import dataclass
import logging
import typing

try:
    import common.database.connection
    import common.database.operations
    import common.model as model
except ModuleNotFoundError:
    print('common package not in python path or dependencies not installed')


@dataclass(frozen=True)
class GetData:
    components: typing.List[model.Component]
    systems: typing.List[model.System]
    results: typing.List[model.Result]


class CacheController:
    def __init__(
        self,
        conn: common.database.connection.DatabaseConnection,
    ):
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.db_ops = common.database.operations.DatabaseOperations(connection=conn)
        self.update_monitor_data()

    def update_monitor_data(self):
        self.logger.info('updating cache')
        self.monitor_data = self._get_monitor_data()

    def get_monitor_data(self) -> GetData:
        return self.monitor_data

    def _get_monitor_data(self):
        components = self.db_ops.select_all_components()
        systems = self.db_ops.select_all_systems()
        results = self.db_ops.select_all_results()

        data = GetData(
            components=components,
            systems=systems,
            results=results,
        )
        return data
