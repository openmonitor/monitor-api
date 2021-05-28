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
class MonitorData:
    components: typing.List[model.Component]
    systems: typing.List[model.System]
    results: typing.List[model.Result]
    comments: typing.List[model.Comment]

class CacheController:
    def __init__(
        self,
        conn: common.database.connection.DatabaseConnection,
    ):
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.db_ops = common.database.operations.DatabaseOperator(connection=conn)
        self.update_monitor_data()

    def update_monitor_data(self):
        self.logger.info('updating cache')
        self.monitor_data = self._get_monitor_data()

    def get_monitor_data(
        self,
        timeunit_as_string: bool,
    ) -> MonitorData:
        data = self.monitor_data
        if timeunit_as_string:

            components: typing.List[model.Component] = []
            for component in data.components:
                metrics = []
                for metric in component.metrics:
                    metric_copy: model.Metric = model.Metric(
                        id=metric.id,
                        endpoint=metric.endpoint,
                        frequency=metric.frequency.as_string(),
                        expectedTime=metric.expectedTime.as_string(),
                        timeout=metric.timeout.as_string(),
                        deleteAfter=metric.deleteAfter.as_string(),
                        authToken=metric.authToken,
                        baseUrl=metric.baseUrl,
                    )
                    metrics.append(metric_copy)
                component: model.Component = model.Component(
                    id=component.id,
                    name=component.name,
                    systemId=component.systemId,
                    baseUrl=component.baseUrl,
                    ref=component.ref,
                    authToken=component.authToken,
                    metrics=metrics,
                )
                components.append(component)

            data = MonitorData(
                components=components,
                systems=self.monitor_data.systems,
                results=self.monitor_data.results,
                comments=self.monitor_data.comments,
            )
        return data

    def _get_monitor_data(self):
        components = self.db_ops.select_all_components()
        systems = self.db_ops.select_all_systems()
        results = self.db_ops.select_all_results()
        comments = self.db_ops.select_all_comments()

        data = MonitorData(
            components=components,
            systems=systems,
            results=results,
            comments=comments,
        )
        return data
