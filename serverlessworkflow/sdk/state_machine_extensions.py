from transitions.extensions.states import add_state_features, Tags, State
from transitions.extensions import (
    HierarchicalMachine,
    GraphMachine,
    HierarchicalGraphMachine,
)


class Metadata(State):
    """Allows states to have metadata.
    Attributes:
        metadata (dict): A dictionary with the state metadata.
    """

    def __init__(self, *args, **kwargs):
        """
        Args:
            **kwargs: If kwargs contains `metadata`, assign them to the attribute.
        """
        self.metadata = kwargs.pop("metadata", [])
        super(Metadata, self).__init__(*args, **kwargs)

    def __getattr__(self, key):
        if value := self.metadata.get(key) is not None:
            return value
        return super(Metadata, self).__getattribute__(key)


@add_state_features(Tags, Metadata)
class CustomHierarchicalMachine(HierarchicalMachine):
    pass


@add_state_features(Tags, Metadata)
class CustomHierarchicalGraphMachine(HierarchicalGraphMachine):
    pass


@add_state_features(Tags, Metadata)
class CustomGraphMachine(GraphMachine):
    pass
