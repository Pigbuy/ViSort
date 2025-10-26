from enum import Enum
from typing import Self, Union, Callable

class ErrMsg:
    def __init__(self, txt:str) -> None:
        self.txt = txt

    def message(self, **params:dict[str,str]) -> str:
        return self.txt.format(params)

class PathEnum(Enum):
    def __new__(cls, value):
        # value is either:
        # - a (actual_value, full_path) tuple for leaves
        # - any other object (usually a nested Enum class) for branch nodes
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    @property
    def value(self):
        v = self._value_
        return v[0] if isinstance(v, tuple) else v

    @property
    def full_name(self):
        v = self._value_
        if isinstance(v, tuple):
            return v[1]
        raise AttributeError("no full_name for non-leaf node")

    def __getattr__(self, name):
        # delegate attribute lookup to the underlying value (nested Enum class)
        return getattr(self._value_, name)

def nest_enum(name, mapping, parent_path=""):
    attrs = {}
    for k, v in mapping.items():
        if isinstance(v, dict):
            # nested Enum class becomes the member value for branch nodes
            attrs[k] = nest_enum(k, v, parent_path + name + ".")
        else:
            # leaf: store (value, full_path) tuple
            attrs[k] = (v, parent_path + name + "." + k)
    return PathEnum(name, attrs)


ERR_BUF: list = []
class Error(Exception):
    def __init__(self, err:PathEnum, **err_details:dict[str,str]) -> None:
        self.name:str = err.full_name
        self.msg:ErrMsg = err.value # technically unhandled error but wont happen if used correctly
        if r:
            super().__init__(self.msg.message(err_details))

    
    def raise_now(self):
        raise 

    def add_to_buf(self):
        ERR_BUF.append(self)

    def raise_buf():
        pass

class ErrorType(Enum):
    def __new__(cls, value) -> Self:
        obj = object.__new__(cls)
        obj._value_ = (value[0], value[1], obj)
        return obj 
    
    @property
    def value(self):
        v = self._value_
        return v[0] if isinstance(v, tuple) else v


ERROR_TYPES = ErrorType("ERROR_TYPES",{

}
)


ERROR_TYPES = nest_enum("ERRORS",{
#    "SETUP_ERROR":{
#
#    },
    "CONFIGURATION_ERROR":{
        "TEST": ErrMsg("another test error {lol}")
    },
    "PROGRAM_LOOP_ERROR":{
        "TEST": ErrMsg("this is a test error {lol}")
    }
}
)



ERROR_TYPES.ERRORS.CONFIGURATION_ERROR.TEST