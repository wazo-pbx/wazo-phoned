# Copyright 2019-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request

from wazo_phoned.auth import AuthResource
from wazo_phoned.plugin_helpers.client.http import ClientLookup


class Lookup(ClientLookup):
    content_type = 'text/xml; charset=utf-8'
    template = 'yealink_results.jinja'


class DNDUserServiceEnable(AuthResource):
    def __init__(self, service, *args, **kwargs):
        super().__init__()
        self._service = service

    def get(self, user_uuid):
        self._service.update_dnd(user_uuid, True)

        return '', 200


class DNDUserServiceDisable(AuthResource):
    def __init__(self, service, *args, **kwargs):
        super().__init__()
        self._service = service

    def get(self, user_uuid):
        self._service.update_dnd(user_uuid, False)

        return '', 200


class AuthenticationUserService(AuthResource):
    def __init__(self, service, *args, **kwargs):
        super().__init__()
        self._service = service

    def get(self):
        return self._service.view_authentication()


class AuthenticateUserService(AuthResource):
    def __init__(self, service, *args, **kwargs):
        super().__init__()
        self._service = service

    def get(self):
        provcode = request.args.get('pin')
        return self._service.authenticate(provcode)
