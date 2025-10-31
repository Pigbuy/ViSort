from enum import Enum

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
    class Other(TreeBase):
        QueuedErrors = ErrMsg("") #required

##################

QUEUED_ERROR_MSGS:list[str] = []

class ViSortError(Exception):
    """class that makes usage of custom ViSort Errors defined in Error Tree possible"""
    def __init__(self, type:TreeBase, **params:str) -> None:
        if type != Errors.Other.QueuedErrors:
            super().__init__(f"- {type.get_path()}: {type.msg.message(**params)}")
        else:
            if len(QUEUED_ERROR_MSGS) != 0:
                msg = "\n\nTHE FOLLOWING ERROR(S) OCCURED:\n\n"
                for m in QUEUED_ERROR_MSGS:
                    msg = msg + m + "\n"
                super().__init__(msg)
            else:
                super().__init__("\nTHERE ARE NO REAL ERRORS, THIS SHOULD NOT HAVE HAPPENED")

    @staticmethod
    def queue_error(type:TreeBase, **params:str) -> TreeBase:
        """Instead of creating an exception that can be raised, just make the error message
        and queue the error in the error queue. Then just raise the Errors.Other.QueuedErrors Error
        like this:
        `raise ViSortError(Errors.Other.QueuedErrors)`
        This function also returns its error type so it can be passed on to preceding functions."""
        QUEUED_ERROR_MSGS.append(f"{type.get_path()}: {type.msg.message(**params)}")
        return type

    @staticmethod
    def if_errors_raise():
        """If there are any queued errors, raise them as a single ViSortError"""
        if len(QUEUED_ERROR_MSGS) != 0:
            raise ViSortError(Errors.Other.QueuedErrors)


#############
##  Usage  ##
#############
#raise ViSortError(Errors.SetupError.MoreTests, lol= "nononono")