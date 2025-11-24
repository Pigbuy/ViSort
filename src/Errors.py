from contextlib import contextmanager
from dataclasses import dataclass
import textwrap

# ANSI color codes
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
WHITE = "\033[97m"
RESET = "\033[0m"

@dataclass
class ErrorRecord:
    branch_path: list[str]
    reason: str

class ErrorMan:
    """ErrorMan is a class that can automatically make tree like Errors and make clearly tracable error messages"""
    def __init__(self) -> None:
        """make a new ErrorMan instance"""
        self._err_tree: dict = {}
        self._current_node: list = []


    def _get_current_tree(self):
        tree = self._err_tree
        for p in self._current_node:
            tree = tree[p]
        return tree

    @contextmanager
    def branch(self, name: str):
        """the code in the `with` block execute in a new error subnode. That means all ErrorMan.queue_error() calls will make errors in the new subnode"""
        tree = self._get_current_tree()
        if name not in tree:
            tree[name] = {}
        self._current_node.append(name)
        try:
            yield
        finally:
            self._current_node.pop()

    def queue_error(self, name: str, reason: str):
        """Make an error at the current tree node position. This will raise an error after ErrorMan.throw_if_errors() is called"""
        self._get_current_tree()[name] = reason
    
    def add_error_reason(self, name: str, reason: str):
        """adds a reason to an already existing error so there can be multiple reasons for an error to occur. This will break if there is not an error with that name already present."""
        tree = self._get_current_tree()
        if tree[name] == "":
            tree[name] = reason
        else:
            tree[name] = tree[name] + " and " + reason


    def throw_if_errors(self):
        """If there are queued errors, this raises an error and makes a nice tracable error message out of all of the errors that were queued"""
        errs_to_throw: list[ErrorRecord] = []

        def recurse(tree: dict, branch_path: list[str]):
            for key, value in tree.items():
                new_branch_path = branch_path + [key]
                if isinstance(value, dict):
                    recurse(value, new_branch_path)
                else:
                    errs_to_throw.append(ErrorRecord(new_branch_path, value))

        recurse(self._err_tree, [])

        if not errs_to_throw:
            return

        msg = f"{YELLOW}\n\nTHE FOLLOWING {len(errs_to_throw)} ERROR(S) OCCURRED:{RESET}"

        for i, error in enumerate(errs_to_throw, 1):
            err_msg = f"{WHITE}-----{i}-----{RESET}\n{RED}{error.branch_path[-1]}{RESET}\n"
            err_path = error.branch_path[:-1]
            for bn in reversed(err_path):
                err_msg += textwrap.indent(f"{WHITE}while{RESET} {CYAN}{bn}{RESET}\n", "    ")
            err_msg += f"{WHITE}because {RED}{error.reason}{RESET}\n"
            msg += "\n" + err_msg

        raise Exception(msg)
    
MEM = ErrorMan() #make main error manager