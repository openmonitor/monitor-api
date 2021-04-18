import dataclasses
import json
import logging
import typing

import falcon

try:
    import database
    import model
except ModuleNotFoundError:
    print('common package not in python path or dependencies not installed')


logger = logging.getLogger(__name__)


def _parse_monitor_data(
    component_component_frames_l: typing.List[model.ComponentComponentFrames],
    systems: typing.List[model.System],
) -> model.DtoMonitorData:
    dto_systems: typing.List[model.DtoSystem] = []
    for s in systems:
        dto_systems.append(
            model.DtoSystem(
                system=s.system,
                name=s.name,
                ref=s.ref,
            )
        )

    dto_components: typing.List[model.DtoComponent] = []
    for c_cfs in component_component_frames_l:
        dto_component_frames: typing.List[model.DtoComponentFrame] = []
        for cf in c_cfs.componentFrames:
            dto_component_frames.append(
                model.DtoComponentFrame(
                    id=cf.frame,
                    timestamp=cf.timestamp,
                    reachable=cf.reachable,
                    responseTime=cf.responseTime,
                    cpu=cf.cpu,
                )
            )

        dto_frame_comment: typing.List[model.DtoFrameComment] = []
        conn = database.get_connection()
        fc_l = database.select_framecomments_for_component(
            conn=conn,
            comp=c_cfs.component,
        )
        database.kill_connection(conn=conn)
        for fc in fc_l:
            if fc:
                dto_frame_comment.append(model.DtoFrameComment(
                    comment=fc.comment,
                    startFrame=fc.startFrame,
                    endFrame=fc.endFrame,
                    commentText=fc.commentText,
                ))

        dto_components.append(
            model.DtoComponent(
                name=c_cfs.component.name,
                frequency=c_cfs.component.frequency,
                system=c_cfs.component.system,
                ref=c_cfs.component.ref,
                expectedTime=c_cfs.component.expectedTime,
                timeout=c_cfs.component.timeout,
                frames=dto_component_frames,
                comments=dto_frame_comment,
            )
        )
    return model.DtoMonitorData(
        components=dto_components,
        systems=dto_systems,
    )


def get_monitor_data():
    conn = database.get_connection()
    comps = database.select_components(
        conn=conn,
    )
    sys = database.select_systems(
        conn=conn,
    )

    c_cfs_l: typing.List[model.ComponentComponentFrames] = []
    for c in comps:
        cfs = database.select_component_frames_with_component(
            conn=conn,
            comp=c,
        )
        c_cfs_l.append(model.ComponentComponentFrames(
            component=c,
            componentFrames=cfs,
        ))
    database.kill_connection(
        conn=conn,
    )

    data = _parse_monitor_data(
        component_component_frames_l=c_cfs_l,
        systems=sys,
    )

    return json.dumps(dataclasses.asdict(data))


def post_comment(
    req,
):

    try:
        body = json.loads(req.stream.read())
    except json.decoder.JSONDecodeError:
        return falcon.HTTP_BAD_REQUEST

    if not body.get('component') or\
            not body.get('startFrame') or \
            not body.get('endFrame') or \
            not body.get('comment'):
        return falcon.HTTP_BAD_REQUEST

    token: str = req.headers.get('AUTHTOKEN')
    if not token:
        return falcon.HTTP_BAD_REQUEST
    if not len(token) == 32:
        return falcon.HTTP_FORBIDDEN

    conn = database.get_connection()

    c = database.select_component(
        conn=conn,
        component=body['component'],
    )

    if not c:
        return falcon.HTTP_BAD_REQUEST

    if token != c.authToken:
        return falcon.HTTP_FORBIDDEN

    fc = model.FrameComment(
        component=c,
        comment=0,
        startFrame=body['startFrame'],
        endFrame=body['endFrame'],
        commentText=body['comment'],
    )
    database.insert_framecomment(
        conn=conn,
        fc=fc,
    )
    database.kill_connection(conn=conn)

    return falcon.HTTP_CREATED


def update_comment(
    req,
):
    try:
        body = json.loads(req.stream.read())
    except json.decoder.JSONDecodeError:
        return falcon.HTTP_BAD_REQUEST

    if not body.get('component') or\
            not body.get('comment') or \
            not body.get('commenttext'):
        return falcon.HTTP_BAD_REQUEST

    token: str = req.headers.get('AUTHTOKEN')
    if not token:
        return falcon.HTTP_BAD_REQUEST
    if not len(token) == 32:
        return falcon.HTTP_FORBIDDEN

    conn = database.get_connection()

    c = database.select_component(
        conn=conn,
        component=body['component'],
    )

    if not c:
        return falcon.HTTP_BAD_REQUEST

    if token != c.authToken:
        return falcon.HTTP_FORBIDDEN

    fc = database.select_framecomments_for_component(
        conn=conn,
        comp=c,
    )

    if fc:
        database.update_framecomment(
            conn=conn,
            comment=body.get('commenttext'),
            text=body.get('comment'),
            comp=c,
        )
    return falcon.HTTP_NO_CONTENT


def delete_comment(
    req,
):
    try:
        body = json.loads(req.stream.read())
    except json.decoder.JSONDecodeError:
        return falcon.HTTP_BAD_REQUEST

    if not body.get('component') or\
            not body.get('comment'):
        return falcon.HTTP_BAD_REQUEST

    token: str = req.headers.get('AUTHTOKEN')
    if not token:
        return falcon.HTTP_BAD_REQUEST
    if not len(token) == 32:
        return falcon.HTTP_FORBIDDEN

    conn = database.get_connection()

    c = database.select_component(
        conn=conn,
        component=body['component'],
    )

    if not c:
        return falcon.HTTP_BAD_REQUEST

    if token != c.authToken:
        return falcon.HTTP_FORBIDDEN

    database.delete_framecomment(
        conn=conn,
        comment=body.get('commenttext'),
        comp=c,
    )
    return falcon.HTTP_NO_CONTENT
