import dataclasses
import json
import logging

import falcon

from . import cache
import authenticators.comment as auth
try:
    import common.database.connection
    import common.database.operations
    import common.model as model
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

    def write_comment(
        self,
        req,
    ):
        self.logger.info('writing comment')
        try:
            body = json.loads(req.stream.read())
        except json.decoder.JSONDecodeError:
            return falcon.HTTP_BAD_REQUEST

        if not body.get('component') or \
                not body.get('metric') or \
                not body.get('comment') or \
                not body.get('start') or \
                not body.get('end'):
            return falcon.HTTP_BAD_REQUEST

        token: str = req.headers.get('AUTHTOKEN')
        if (error := self.auth.token_error(token=token)):
            return error

        component_id = body.get('component')
        if (error := self.auth.token_component_error(
                token=token,
                component_id=component_id,
        )):
            return error

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
        self.cache_controller.update_monitor_data()
        return falcon.HTTP_CREATED

    def delete_comment(self):
        self.logger.info('deleting comment')
        data = self.cache_controller.delete_comment_data()
        return falcon.HTTP_NO_CONTENT

    def update_comment(self):
        self.logger.info('updating comment')
        data = self.cache_controller.update_comment_data()
        return falcon.HTTP_NO_CONTENT
