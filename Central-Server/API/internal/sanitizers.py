import re
# Just a bunch of helper functions to help with sanitizing and verification

def git_hash_regexp():
    return r"^[0-9a-fA-F]+$"

def github_username_regexp():
    return r"^[a-zA-Z0-9\-\_]+$"

def branch_name_regexp():
    return r"^[a-zA-Z0-9\-\_\/\.]+$"

def is_git_hash(s: str) -> bool:
    return re.fullmatch(git_hash_regexp(), s or "") is not None

def is_github_username(s: str) -> bool:
    return re.fullmatch(github_username_regexp(), s or "") is not None

def is_branch_name(s: str) -> bool:
    return re.fullmatch(branch_name_regexp(), s or "") is not None

