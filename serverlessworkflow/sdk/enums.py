from enum import Enum


class Invoke(Enum):
    SYNC = "sync"
    ASYNC = "async"


class ActionMode(Enum):
    PARALLEL = "parallel"
    SEQUENTIAL = "sequential"
