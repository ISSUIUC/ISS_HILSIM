"""This file exposes classes, enums, and interfaces for storing data in relation to jobs."""
import enum

from apiflask import Schema
from apiflask.fields import Integer, String, DateTime
from apiflask.validators import Length, OneOf, Regexp

import internal.sanitizers as sanitizers


class JobStatus(enum.Enum):
    """An enum describing the current status of a job"""
    QUEUED = 0
    """Job is queued and will be run on the next available TARS"""
    RUNNING = 1
    """Job is currently running on TARS"""
    CANCELED = 2
    """Job was canceled by someone `#cancelculture`"""
    SUCCESS = 3
    """Job was successfully run"""
    FAILED_CRASHED = 4
    """Job crashed on TARS"""
    FAILED_COMPILE_ERROR = 5
    """Job failed to compile"""
    FAILED_TIMEOUT = 6
    """Job timed out, cancelled `#cancelculturestrikesagain`"""
    FAILED_OTHER = 7
    """Job failed for some other reason"""
    SETUP = 8
    """Job is currently in the process of being set up."""


class JobRequestSchema(Schema):
    """The database schema for a generic job request"""
    commit = String(
        required=True, validate=Regexp(
            sanitizers.git_hash_regexp()))
    username = String(
        required=True, validate=Regexp(
            sanitizers.github_username_regexp()))
    branch = String(
        required=True, validate=Regexp(
            sanitizers.branch_name_regexp()))
    description = String(required=False, load_default="", dump_default="")
    data_uri = String(
        required=False,
        load_default="/api/temp/data",
        dump_default="/api/temp/data")

# do keep this updated with the db please


class JobOutSchema(Schema):
    """Schema for job outputs"""
    run_id = Integer()
    user_id = String(validate=Length(max=40))
    branch = String(validate=Length(max=128))
    git_hash = String(validate=Length(max=40))
    submitted_time = DateTime()
    run_start = DateTime()
    run_end = DateTime()
    run_status = String(validate=OneOf([e.name for e in JobStatus]))
    description = String(validate=Length(max=512))
    data_uri = String(validate=Length(max=128))
