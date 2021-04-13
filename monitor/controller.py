import dataclasses
import json
import logging
import typing

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
                )
            )

        dto_components.append(
            model.DtoComponent(
                name=c_cfs.component.name,
                frequency=c_cfs.component.frequency,
                system=c_cfs.component.system,
                ref=c_cfs.component.ref,
                expectedTime=c_cfs.component.expectedTime,
                timeout=c_cfs.component.timeout,
                frames=dto_component_frames,
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


def post_comment():
    conn = database.get_connection()
    c = database.select_component(
        conn=conn,
        component='openmonitor-static-file-server',
    )
    fc = model.FrameComment(
        component=c,
        comment=0,
        startFrame=4,
        endFrame=12,
        commentText='Nuclear incident, please dont tell anyone!',
    )
    database.insert_framecomment(
        conn=conn,
        fc=fc,
    )
    database.kill_connection(conn=conn)
