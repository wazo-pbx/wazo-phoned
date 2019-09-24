# Copyright 2015-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo.mallow import fields
from xivo.mallow_helpers import Schema


class UserUUIDSchema(Schema):
    xivo_user_uuid = fields.String(required=True)


class LookupSchema(UserUUIDSchema):
    term = fields.String(required=True)
    limit = fields.Integer(missing=None)
    offset = fields.Integer(missing=None)


class LookupGigasetSchema(Schema):
    set_first = fields.String(attribute='term', missing='')
    count = fields.Integer(attribute='limit', missing=None)
    first = fields.Integer(attribute='first', missing=1)
