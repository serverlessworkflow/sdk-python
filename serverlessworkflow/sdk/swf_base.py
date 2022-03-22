from __future__ import annotations

import copy
import dataclasses
import traceback
from abc import ABC, abstractmethod
from typing import Any


class HydratableType(ABC):
    @abstractmethod
    def hydrate(self, value):
        pass


class ArrayTypeOf(HydratableType):
    def __init__(self, Type):
        self.Type = Type

    def hydrate(self, value):
        return [self.Type(**v) if type(v) is not self.Type else v for v in value]


class ComplexTypeOf(HydratableType):
    def __init__(self, Type):
        self.Type = Type

    def hydrate(self, value):
        return self.Type(**value) if type(value) is not self.Type else value


class SimpleTypeOf(HydratableType):
    def __init__(self, Type):
        self.Type = Type

    def hydrate(self, value):
        if type(value) is self.Type:
            return value


class UnionTypeOf(HydratableType):
    types: [HydratableType]

    def __init__(self, types: [HydratableType]):
        self.types = types

    def hydrate(self, value):

        for t in self.types:
            if t.hydrate(value) is not None:
                return t.hydrate(value)

        return None


class HydratableParameter:
    def __init__(self, value: Any):
        self.complex_type = None
        self.simple_type = None
        self.value = value

    def hydrateAs(self, hydratable: HydratableType):
        return hydratable.hydrate(self.value)


@dataclasses.dataclass
class Field:
    def __init__(self, key: str, value: Any):
        self.key = key
        self.value = value


class SwfBase:
    def __init__(self, fields, kwargs, f_hydration, _default_values={}):
        self._default_values = {}
        self._initial_values = {}

        _attributes: [Field] = []
        _initial_values = {}
        k: str
        for k in list(fields):
            if k in ["self", "kwargs"]:
                continue
            if k.startswith("_"):
                continue

            final_value = fields.get(k)

            if final_value == "true":
                final_value = True

            if final_value == "false":
                final_value = False

            _initial_values[k] = final_value

            if final_value is None and _default_values.get(k) is not None:
                final_value = _default_values.get(k)

            if final_value is None:
                continue

            final_value = f_hydration(k, final_value)

            if final_value is not None:
                key_ = k.replace("_", "")
                _attributes.append(Field(key_, final_value))

            _attributes.append(Field("_initial_values", _initial_values))
            _attributes.append(Field("_default_values", _default_values))

        for k in kwargs.keys():
            final_value = kwargs[k]

            if final_value == "true":
                final_value = True

            if final_value == "false":
                final_value = False

            _initial_values[k] = final_value

            if final_value is None and _default_values.get(k) is not None:
                final_value = _default_values.get(k)

            if final_value is None:
                continue

            final_value = f_hydration(k, final_value)

            if final_value is not None:
                key_ = k.replace("_", "")
                _attributes.append(Field(key_, final_value))

            _attributes.append(Field("_initial_values", _initial_values))
            _attributes.append(Field("_default_values", _default_values))

        for f in _attributes:
            self.__setattr__(f.key, f.value)

    def serialize(self):

        try:
            self_copy: SwfBase = copy.deepcopy(self)

            for k in self_copy.__dict__:
                attribute_value = self_copy.__getattribute__(k)
                if isinstance(attribute_value, list):
                    elements: list = attribute_value
                    for element in elements.copy():
                        if isinstance(element, SwfBase):
                            elements.remove(element)
                            serialize = element.serialize()
                            elements.append(serialize)

                if isinstance(attribute_value, SwfBase):
                    self_copy.__setattr__(k, attribute_value.serialize())

            for k in self_copy._default_values.keys():
                if self_copy._initial_values.get(k) is None:
                    delattr(self_copy, k)

            for k in self_copy.__dict__.copy():
                if k.startswith("_"):
                    delattr(self_copy, k)

            return self_copy

        except Exception as e:
            traceback.print_exc()
            raise e

    @staticmethod
    def default_hydration(property_key, property_value):
        return property_value
