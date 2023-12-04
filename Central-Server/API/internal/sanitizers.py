"""File exporting helper functions to assist in input sanitization and validation"""
import re

def git_hash_regexp() -> str:
    """Returns a RegEx that matches git hashes"""
    return r"^[0-9a-fA-F]+$"

def github_username_regexp() -> str:
    """Returns a RegEx that matches possible GitHub usernames"""
    return r"^[a-zA-Z0-9\-\_]+$"

def branch_name_regexp() -> str:
    """Returns a RegEx that matches possible GitHub branch names"""
    return r"^[a-zA-Z0-9\-\_\/\.]+$"

def is_git_hash(s: str) -> bool:
    """Returns TRUE if the given string is a possible git hash, FALSE otherwise."""
    return re.fullmatch(git_hash_regexp(), s or "") is not None

def is_github_username(s: str) -> bool:
    """Returns TRUE if the given string is a possible GitHub username, FALSE otherwise."""
    return re.fullmatch(github_username_regexp(), s or "") is not None

def is_branch_name(s: str) -> bool:
    """Returns TRUE if the given string is a possible GitHub branch, FALSE otherwise."""
    return re.fullmatch(branch_name_regexp(), s or "") is not None

