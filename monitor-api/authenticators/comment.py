import logging
import typing

import falcon

try:
    import common.database.connection
    import common.database.operations
    import common.model as model
except ModuleNotFoundError:
    print('common package not in python path or dependencies not installed')


class CommentAuthenticator:
    def __init__(
        self,
        connection: common.database.connection.DatabaseConnection,
    ):
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.db_ops = common.database.operations.DatabaseOperator(connection=connection)
        super(CommentAuthenticator, self).__init__()

    def authenticate(
        self,
        token: str,
        body,
    ) -> typing.Union[None, falcon.HTTPStatus] :
        if (error := self._token_error(token=token)):
            return error

        component_id = body.get('component')

        if (error := self._token_component_error(
                token=token,
                component_id=component_id,
        )):
            return error

        return None

    def _token_error(
        self,
        token: typing.Union[None, str],
    ) -> typing.Union[None, falcon.HTTPStatus] :
        if not token:
            return falcon.HTTP_BAD_REQUEST
        if not len(token) == 32:
            return falcon.HTTP_FORBIDDEN

        return None

    def _token_component_error(
        self,
        token: str,
        component_id: str,
    ) -> typing.Union[None, falcon.HTTPStatus] :
        component = self.db_ops.select_component(component_id=component_id)

        if not component:
            return falcon.HTTP_NOT_FOUND

        if token != component.authToken:
            self.logger.debug(f'{token=} denied for {component.name=}')
            return falcon.HTTP_FORBIDDEN

        return None
