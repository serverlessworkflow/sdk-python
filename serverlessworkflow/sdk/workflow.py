from __future__ import annotations

import copy
import json

import yaml

from serverlessworkflow.sdk.auth_def import AuthDef
from serverlessworkflow.sdk.callback_state import CallbackState
from serverlessworkflow.sdk.databased_switch_state import DataBasedSwitchState
from serverlessworkflow.sdk.error_def import ErrorDef
from serverlessworkflow.sdk.event_based_switch_state import EventBasedSwitchState
from serverlessworkflow.sdk.event_def import EventDef
from serverlessworkflow.sdk.event_state import EventState
from serverlessworkflow.sdk.foreach_state import ForEachState
from serverlessworkflow.sdk.function import Function
from serverlessworkflow.sdk.inject_state import InjectState
from serverlessworkflow.sdk.metadata import Metadata
from serverlessworkflow.sdk.operation_state import OperationState
from serverlessworkflow.sdk.parallel_state import ParallelState
from serverlessworkflow.sdk.retry_def import RetryDef
from serverlessworkflow.sdk.sleep_state import SleepState
from serverlessworkflow.sdk.start_def import StartDef
from serverlessworkflow.sdk.state import State
from serverlessworkflow.sdk.swf_base import HydratableParameter, UnionTypeOf, SimpleTypeOf, ComplexTypeOf, \
    ArrayTypeOf, SwfBase
from serverlessworkflow.sdk.workflow_time_out import WorkflowTimeOut


class DataInputSchema:
    schema: str
    failOnValidationErrors: bool


class Workflow(SwfBase):
    id: str = None
    key: str = None
    name: str = None
    description: str = None
    version: str = None
    annotations: [str] = None
    dataInputSchema: (str | DataInputSchema) = None
    secrets: str = None  # Secrets
    constants: (str | dict[str, dict]) = None
    start: (str | StartDef) = None
    specVersion: str = None
    expressionLang: str = None
    timeouts: (str | WorkflowTimeOut) = None
    errors: (str | [ErrorDef]) = None
    keepActive: bool = None
    metadata: Metadata = None
    events: (str | [EventDef]) = None
    functions: (str | [Function]) = None
    autoRetries: bool = None
    retries: (str | [RetryDef]) = None
    auth: (str, [AuthDef]) = None
    states: [State] = None

    def __init__(self,
                 id: str = None,
                 key: str = None,
                 name: str = None,
                 version: str = None,
                 description: str = None,
                 specVersion: str = None,
                 annotations: [str] = None,
                 dataInputSchema: (str | DataInputSchema) = None,
                 secrets: str = None,  # Secrets
                 constants: (str | dict[str, dict]) = None,
                 start: (str | StartDef) = None,
                 expressionLang: str = None,
                 timeouts: (str | WorkflowTimeOut) = None,
                 errors: (str | [ErrorDef]) = None,
                 keepActive: bool = None,
                 metadata: Metadata = None,
                 events: (str | [EventDef]) = None,
                 autoRetries: bool = None,
                 retries: (str | [RetryDef]) = None,
                 auth: (str | [AuthDef]) = None,
                 states: [State] = None,
                 functions: (str | [Function]) = None
                 , **kwargs):

        _default_values = {'expressionLang': 'jq', 'keepActive': True}
        SwfBase.__init__(self, locals(), kwargs, Workflow.f_hydration,
                         _default_values)

    def to_json(self) -> str:

        self_copy = self.serialize()
        return json.dumps(self_copy,
                          default=lambda o: o.__dict__,
                          indent=4)

    def to_yaml(self):

        self_copy = self.serialize()
        yaml.emitter.Emitter.process_tag = lambda x: None
        return yaml.dump(self_copy,
                         sort_keys=False,
                         allow_unicode=True,
                         )

    @classmethod
    def from_source(cls, source: str):
        try:
            loaded_data = yaml.safe_load(source)
            return cls(**loaded_data)
        except Exception:
            raise Exception("Format not supported")

    def __repr__(self):
        return "{!r}".format(self.__dict__)

    @staticmethod
    def f_hydration(p_key, p_value):

        if p_key == 'dataInputSchema':
            return HydratableParameter(value=p_value).hydrateAs(UnionTypeOf([SimpleTypeOf(str),
                                                                             ComplexTypeOf(DataInputSchema)]))

        if p_key == 'constants':
            return HydratableParameter(value=p_value).hydrateAs(UnionTypeOf([SimpleTypeOf(str),
                                                                             ComplexTypeOf(dict)]))
        if p_key == 'start':
            return HydratableParameter(value=p_value).hydrateAs(UnionTypeOf([SimpleTypeOf(str),
                                                                             ComplexTypeOf(StartDef)]))

        if p_key == 'timeouts':
            return HydratableParameter(value=p_value).hydrateAs(UnionTypeOf([SimpleTypeOf(str),
                                                                             ComplexTypeOf(WorkflowTimeOut)]))

        if p_key == 'errors':
            return HydratableParameter(value=p_value).hydrateAs(UnionTypeOf([SimpleTypeOf(str),
                                                                             ArrayTypeOf(ErrorDef)]))

        if p_key == 'events':
            return HydratableParameter(value=p_value).hydrateAs(UnionTypeOf([SimpleTypeOf(str),
                                                                             ArrayTypeOf(EventDef)]))

        if p_key == 'retries':
            return HydratableParameter(value=p_value).hydrateAs(UnionTypeOf([SimpleTypeOf(str),
                                                                             ArrayTypeOf(RetryDef)]))

        if p_key == 'auth':
            return HydratableParameter(value=p_value).hydrateAs(UnionTypeOf([SimpleTypeOf(str),
                                                                             ArrayTypeOf(AuthDef)]))

        if p_key == 'states':
            return [Workflow.hydrate_state(v) if not isinstance(v, State) else v for v in p_value]

        if p_key == 'functions':
            return HydratableParameter(value=p_value).hydrateAs(UnionTypeOf([SimpleTypeOf(str),
                                                                             ArrayTypeOf(Function)]))

        return copy.deepcopy(p_value)

    @staticmethod
    def hydrate_state(raw_state: State):

        state = State(**raw_state)
        if state.is_inject_state():
            return InjectState(**raw_state)
        elif state.is_operation_state():
            return OperationState(**raw_state)
        elif state.is_foreach_state():
            return ForEachState(**raw_state)
        elif state.is_sleep_state():
            return SleepState(**raw_state)
        elif state.is_switch_state():
            if hasattr(state, "dataConditions"):
                return DataBasedSwitchState(**raw_state)
            if hasattr(state, "eventConditions"):
                return EventBasedSwitchState(**raw_state)
            raise Exception(f"Unexpected switch type in {raw_state}")
        elif state.is_callback_state():
            return CallbackState(**raw_state)
        elif state.is_parallel_state():
            return ParallelState(**raw_state)
        elif state.is_event_state():
            return EventState(**raw_state)
        else:
            raise Exception(f"Unexpected type in {raw_state}")
