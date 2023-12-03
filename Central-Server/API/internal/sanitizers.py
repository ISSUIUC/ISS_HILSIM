import re
# Just a bunch of helper functions to help with sanitizing and verification

def is_git_hash(s):
    return re.fullmatch(r"^[0-9a-fA-F]+", s or "") is not None

def is_github_username(s):
    return re.fullmatch(r"^[a-zA-Z0-9\-\_]+$", s or "") is not None

def is_branch_name(s):
    return re.fullmatch(r"^[a-zA-Z0-9\-\_\/\.]+$", s or "") is not None
