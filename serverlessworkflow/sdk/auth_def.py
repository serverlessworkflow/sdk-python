from __future__ import annotations

import copy

from serverlessworkflow.sdk.basic_props_def import BasicPropsDef
from serverlessworkflow.sdk.bearer_props_def import BearerPropsDef
from serverlessworkflow.sdk.oauth2props_def import Oauth2PropsDef
from serverlessworkflow.sdk.swf_base import SwfBase


class AuthDef(SwfBase):
    name: str = None
    scheme: str = None
    properties: (str | (BasicPropsDef | BearerPropsDef | Oauth2PropsDef)) = None

    def __init__(self,
                 name: str = None,
                 scheme: str = None,
                 properties: (str | (BasicPropsDef | BearerPropsDef | Oauth2PropsDef)) = None,
                 **kwargs):

        _default_values = {'scheme': 'basic'}
        SwfBase.__init__(self, locals(), kwargs, SwfBase.default_hydration, _default_values)

    @staticmethod
    def f_hydration(p_key, p_value):
        result = copy.deepcopy(p_value)

        if p_key == 'properties':
            if p_value["username"] and p_value["password"]:
                return BasicPropsDef(p_value)
            if p_value["token"]:
                return BearerPropsDef(p_value)
            if p_value["grantType"]:
                return Oauth2PropsDef(p_value)

        return result
