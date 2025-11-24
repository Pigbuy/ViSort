from contextlib import contextmanager
from dataclasses import dataclass
import textwrap

# ANSI color codes
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
WHITE = "\033[97m"
RESET = "\033[0m"

ERROR_TREE: dict = {}
CURRENT_ERR_TREE_POS: list = []

def get_current_tree():
    tree = ERROR_TREE
    for p in CURRENT_ERR_TREE_POS:
        tree = tree[p]
    return tree

@dataclass
class ErrorRecord:
    branch_path: list[str]
    reason: str

class Errors:
    @staticmethod
    @contextmanager
    def branch(name: str):
        tree = get_current_tree()
        if name not in tree:
            tree[name] = {}
        CURRENT_ERR_TREE_POS.append(name)
        try:
            yield
        finally:
            CURRENT_ERR_TREE_POS.pop()

    @staticmethod
    def queue_error(name: str, reason: str):
        get_current_tree()[name] = reason
    
    @staticmethod
    def add_error_reason(name: str, reason: str):
        tree = get_current_tree()
        if tree[name] == "":
            tree[name] = reason
        else:
            tree[name] = tree[name] + " and " + reason


    @staticmethod
    def throw_if_errors():
        errs_to_throw: list[ErrorRecord] = []

        def recurse(tree: dict, branch_path: list[str]):
            for key, value in tree.items():
                new_branch_path = branch_path + [key]
                if isinstance(value, dict):
                    recurse(value, new_branch_path)
                else:
                    errs_to_throw.append(ErrorRecord(new_branch_path, value))

        recurse(ERROR_TREE, [])

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