import logging
import typing

import falcon

from . import cache
from monitor_api import util
import authenticators.comment as auth
try:
    import common.database.connection
    import common.database.operations
    import common.model as model
    import common.observer as observer
except ModuleNotFoundError:
    print('common package not in python path or dependencies not installed')


class ControllerComment:
    def __init__(
        self,
        cache_controller: cache.CacheController,
        connection: common.database.connection.DatabaseConnection,
    ):
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.cache_controller = cache_controller
        self.db_ops = common.database.operations.DatabaseOperator(connection=connection)
        self.auth = auth.CommentAuthenticator(connection=connection)
        self.observer: typing.List[observer.Observer] = []

    def register_observer(
        self,
        observer,
    ):
        self.observer.append(observer)
        self.logger.info(f'registered observer {observer.name}')

    def write_comment(
        self,
        req,
    ):
        self.logger.info('writing comment')
        if not (body := util.load_body(req=req)):
            return falcon.HTTP_BAD_REQUEST

        if not util.body_contains_requirements(
            body,
            'component',
            'metric',
            'comment',
            'start',
            'end',
        ):
            return falcon.HTTP_BAD_REQUEST

        if (error := self.auth.authenticate(
                token=req.headers.get('AUTHTOKEN'),
                body=body,
        )):
            return error

        component_id = body.get('component')
        if not self.db_ops.select_metric(
                component_id=component_id,
                metric_id=body.get('metric'),
        ):
            return falcon.HTTP_NOT_FOUND

        comment = model.Comment(
            metricId=body.get('metric'),
            componentId=body.get('component'),
            comment=body.get('comment'),
            timestamp='now()',
            startTimestamp=body.get('start'),
            endTimestamp=body.get('end'),
        )

        self.db_ops.insert_comment(comment=comment)

        for obs in self.observer:
            self.logger.info(f'calling observer {obs.name}')
            obs.call_by_callable(callable=self.cache_controller.update_monitor_data)

        return falcon.HTTP_CREATED

    def delete_comment(
        self,
        req,
    ):
        self.logger.info('deleting comment')
        if not (body := util.load_body(req=req)):
            return falcon.HTTP_BAD_REQUEST

        if not util.body_contains_requirements(
            body,
            'component',
            'metric',
            'timestamp',
        ):
            return falcon.HTTP_BAD_REQUEST

        if (error := self.auth.authenticate(
                token=req.headers.get('AUTHTOKEN'),
                body=body,
        )):
            return error

        self.db_ops.delete_comment(
            component_id=body.get('component'),
            metric_id=body.get('metric'),
            timestamp=body.get('timestamp'),
        )

        for obs in self.observer:
            self.logger.info(f'calling observer {obs.name}')
            obs.call_by_callable(callable=self.cache_controller.update_monitor_data)

        return falcon.HTTP_ACCEPTED

    def update_comment(
        self,
        req,
    ):
        self.logger.info('updating comment')
        if not (body := util.load_body(req=req)):
            return falcon.HTTP_BAD_REQUEST

        if not util.body_contains_requirements(
            body,
            'component',
            'metric',
            'timestamp',
        ):
            return falcon.HTTP_BAD_REQUEST

        if (error := self.auth.authenticate(
                token=req.headers.get('AUTHTOKEN'),
                body=body,
        )):
            return error

        old = self.db_ops.select_comment(
            component_id=body.get('component'),
            metric_id=body.get('metric'),
            timestamp=body.get('timestamp'),
        )

        if not old:
            return falcon.HTTP_NOT_FOUND

        new: model.Comment = model.Comment(
            metricId=body.get('metric'),
            componentId=body.get('component'),
            comment=body.get('comment') if body.get('comment') else old.comment,
            timestamp=body.get('timestamp'),
            startTimestamp=body.get('start') if body.get('start') else old.startTimestamp,
            endTimestamp=body.get('end') if body.get('end') else old.endTimestamp,
        )

        self.db_ops.update_comment(
            old=old,
            new=new,
        )

        for obs in self.observer:
            self.logger.info(f'calling observer {obs.name}')
            obs.call_by_callable(callable=self.cache_controller.update_monitor_data)

        return falcon.HTTP_NO_CONTENT
