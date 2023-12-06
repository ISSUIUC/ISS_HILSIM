
from marshmallow import fields, Schema, validates, ValidationError
from marshmallow.validate import Regexp
from marshmallow.fields import *

class JobRequestSchema(Schema):
    commit = String(required=True, validate=Regexp(r"^[0-9a-fA-F]+"))
    username = String(required=True, validate=Regexp(r"^[a-zA-Z0-9\-\_]+$"))
    branch = String(required=True, validate=Regexp(r"^[a-zA-Z0-9\-\_\/\.]+$"))
    description = String(required=False, load_default="", dump_default="")
    data_uri = String(required=False, load_default="/api/temp/data", dump_default="/api/temp/data")

JobRequestSchema().load({"commit": "test"})
