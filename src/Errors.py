from enum import Enum
from typing import Self, Union, Callable, Any, TypeVar, Generic

class ErrMsg:
    def __init__(self, txt:str) -> None:
        self.txt = txt

    def message(self, **params:str) -> str:
        return self.txt.format(**params)
    
class TreeBase(Enum):
    _path_: str
    msg: ErrMsg

    def __new__(cls, msg: ErrMsg):
        obj = object.__new__(cls)
        obj.msg = msg
        return obj

    def __init__(self, node: ErrMsg):
        parts = self.__class__.__qualname__.split(".")
        if parts:
            parts = parts[1:]
        parts = [p for p in parts] + [self.name]
        self._path_ = ".".join(parts)

    def get_path(self) -> str:
        return self._path_


##################
##  Error Tree  ##
##################

class Errors:
    class SetupError(TreeBase):
        MoreTests = ErrMsg("another test error {lol}")
    class ConfigurationError(TreeBase):
        TestAgain = ErrMsg("another test error {lol}")
    class ProgramLoopError(TreeBase):
        TestError = ErrMsg("testdasdf{lol}")

##################
    
class ViSortError(Exception):
    def __init__(self, type:TreeBase, **params:str) -> None:
        super().__init__(f"{type.get_path()}: {type.msg.message(**params)}")


#############
##  Usage  ##
#############
#raise ViSortError(Errors.SetupError.MoreTests, lol= "nononono")