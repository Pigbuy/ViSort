from enum import Enum
import textwrap

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
        FilterParseFailure = ErrMsg("failed to parse filter '{filter_name}'")
    class ProgramLoopError(TreeBase):
        TestError = ErrMsg("testdasdf{lol}")
    class Other(TreeBase):
        QueuedErrors = ErrMsg("") #required

##################

QUEUED_ERROR_MSGS:list[str] = []

class ViSortError(Exception):
    """class that makes usage of custom ViSort Errors defined in Error Tree possible"""
    def __init__(self, type:TreeBase, **params:str) -> None:
        if type == Errors.Other.QueuedErrors:
            if len(QUEUED_ERROR_MSGS) > 0:
                msg = "\n\nTHE FOLLOWING ERROR(S) OCCURED:\n\n"
                for m in QUEUED_ERROR_MSGS:
                    msg = msg + "- " + m + "\n"
                super().__init__(msg)
            else:
                super().__init__("\nTHERE ARE NO REAL ERRORS, THIS SHOULD NOT HAVE HAPPENED, THE PROGRAMMER IS STUPID")
        else:
            super().__init__(f"{type.get_path()}: {type.msg.message(**params)}")
           

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
    def if_errors_in_queue_raise():
        """only raise queued errors if there are any queued errors."""
        if len(QUEUED_ERROR_MSGS) > 0:
            raise ViSortError(Errors.Other.QueuedErrors)
    
    @staticmethod
    def make_blame_err(type:TreeBase, **params:str):
        """ A blame error is an error that blames other errors for its occurance.
        This function just makes one error message from all errors in the queue,
        formats it in a way that makes it clear that those errors caused the error
        given to this function. Then it clears the error queue and puts the generated
        blame error message in the queue alone """

        if len(QUEUED_ERROR_MSGS) > 0:
            msg = ""
            for m in QUEUED_ERROR_MSGS:
                msg = msg + "- " + m + "\n"
            msg = f"{type.get_path()}: {type.msg.message(**params)} due to the following error(s):\n" + textwrap.indent(msg, "    ")
            QUEUED_ERROR_MSGS.clear()
            QUEUED_ERROR_MSGS.append(msg)




#############
##  Usage  ##
#############
#raise ViSortError(Errors.SetupError.MoreTests, lol= "nononono")