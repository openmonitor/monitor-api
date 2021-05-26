import dataclasses
import json
import logging

import falcon

from . import cache
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
        self.db_ops = common.database.operations.DatabaseOperations(connection=connection)

    def get_comment(self):
        self.logger.info('getting comments')
        data = self.cache_controller.get_comment_data()
        return json.dumps(dataclasses.asdict(data))

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
        if not token:
            return falcon.HTTP_BAD_REQUEST
        if not len(token) == 32:
            return falcon.HTTP_FORBIDDEN

        component = self.db_ops.select_component(component_id=body.get('component'))

        if not component:
            return falcon.HTTP_NOT_FOUND

        if token != component.authToken:
            return falcon.HTTP_FORBIDDEN

        comment = model.Comment(
            metricId=body.get('metric'),
            componentId=body.get('component'),
            comment=body.get('comment'),
            timestamp='now()',
            startTimestamp=body.get('start'),
            endTimestamp=body.get('end'),
        )

        self.db_ops.insert_comment(comment=comment)
        return falcon.HTTP_CREATED

    def delete_comment(self):
        self.logger.info('deleting comment')
        data = self.cache_controller.get_comment_data()
        return json.dumps(dataclasses.asdict(data))

    def update_comment(self):
        self.logger.info('updating comment')
        data = self.cache_controller.get_comment_data()
        return json.dumps(dataclasses.asdict(data))
