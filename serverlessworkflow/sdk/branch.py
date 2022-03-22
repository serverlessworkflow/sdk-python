import copy

from serverlessworkflow.sdk.action import Action
from serverlessworkflow.sdk.branch_timeout import BranchTimeOut
from serverlessworkflow.sdk.swf_base import ArrayTypeOf, ComplexTypeOf, HydratableParameter, SwfBase


class Branch(SwfBase):
    name: str = None
    timeouts: BranchTimeOut = None
    actions: [Action] = None

    def __init__(self,
                 name: str = None,
                 timeouts: BranchTimeOut = None,
                 actions: [Action] = None,
                 **kwargs):

        SwfBase.__init__(self, locals(), kwargs, Branch.f_hydration)

    @staticmethod
    def f_hydration(p_key, p_value):

        if p_key == 'timeouts':
            return HydratableParameter(value=p_value).hydrateAs(ComplexTypeOf(BranchTimeOut))

        if p_key == 'actions':
            return HydratableParameter(value=p_value).hydrateAs(ArrayTypeOf(Action))

        return copy.deepcopy(p_value)
