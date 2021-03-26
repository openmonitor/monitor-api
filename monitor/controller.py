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
    components: typing.List[model.Component],
    systems: typing.List[model.System],
    component_frames: typing.List[model.ComponentFrame],
) -> model.DtoMonitorData:
    dto_systems: typing.List[model.DtoSystem] = []
    for s in systems:
        dto_systems.append(
            model.DtoSystem(
                name=s.name,
                ref=s.ref,
            )
        )

    dto_component_frames: typing.List[model.DtoComponentFrame] = []
    for cf in component_frames:
        dto_component_frames.append(
            model.DtoComponentFrame(
                id=cf.frame,
                timestamp=cf.timestamp,
                reachable=cf.reachable,
                responseTime=cf.responseTime,
            )
        )

    dto_components: typing.List[model.DtoComponent] = []
    for c in components:
        dto_components.append(
            model.DtoComponent(
                name=c.name,
                frequency=c.frequency,
                system=c.system,
                ref=c.ref,
                expectedTime=c.expectedTime,
                timeout=c.timeout,
                frames=[],
            )
        )
    return model.DtoMonitorData(
        components=dto_components,
        systems=dto_systems,
    )


def get_monitor_data():
    conn = database.get_connection()
    c = database.select_components(
        conn=conn,
    )
    s = database.select_systems(
        conn=conn,
    )
    cf = database.select_component_frames(
        conn=conn,
    )
    database.kill_connection(
        conn=conn,
    )
    data = _parse_monitor_data(
        components=c,
        systems=s,
        component_frames=cf,
    )
    return json.dumps(data)
