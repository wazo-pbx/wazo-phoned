# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import logging
import requests

from flask import request
from flask import Response
from flask_restful import reqparse
from time import time
from xivo_dird_phoned.rest_api import api
from xivo_dird_phoned.auth_remote_addr import AuthResource
from xivo_dird_phoned import auth


logger = logging.getLogger(__name__)


parser = reqparse.RequestParser()
parser.add_argument('xivo_user_uuid', type=unicode, required=True, location='args')

# TODO Use this when the flask_restful will be in version >= 3.2
# parser_lookup = parser.copy()
parser_lookup = reqparse.RequestParser()
parser_lookup.add_argument('xivo_user_uuid', type=unicode, required=True, location='args')

parser_lookup.add_argument('limit', type=int, required=False, help='limit cannot be converted', location='args')
parser_lookup.add_argument('offset', type=int, required=False, help='offset cannot be converted', location='args')
parser_lookup.add_argument('term', type=unicode, required=True, help='term is missing', location='args')

# TODO Use this when the flask_restful will be in version >= 3.2
# parser_lookup_autodetect = parser_lookup.copy()
# parser_lookup_autodetect.remove_argument('xivo_user_uuid')
parser_lookup_autodetect = reqparse.RequestParser()
parser_lookup_autodetect.add_argument('limit', type=int, required=False,
                                      help='limit cannot be converted', location='args')
parser_lookup_autodetect.add_argument('offset', type=int, required=False,
                                      help='offset cannot be converted', location='args')
parser_lookup_autodetect.add_argument('term', type=unicode, required=True,
                                      help='term is missing', location='args')

AUTH_BACKEND = 'xivo_service'
AUTH_EXPIRATION = 10
DIRD_API_VERSION = '0.1'
FAKE_XIVO_USER_UUID = '00000000-0000-0000-0000-000000000000'


def _error(code, msg):
    return {'reason': [msg],
            'timestamp': [time()],
            'status_code': code}, code


class DirectoriesConfiguration(object):

    menu_url = '/directories/menu/<profile>/<vendor>'
    input_url = '/directories/input/<profile>/<vendor>'
    lookup_url = '/directories/lookup/<profile>/<vendor>'
    menu_autodetect_url = '/directories/menu/autodetect'
    input_autodetect_url = '/directories/input/autodetect'
    lookup_autodetect_url = '/directories/lookup/autodetect'

    def __init__(self, dird_config):
        dird_host = dird_config['host']
        dird_port = dird_config['port']
        dird_default_profile = dird_config['default_profile']
        dird_verify_certificate = dird_config.get('verify_certificate', True)

        Menu.configure(dird_host, dird_port, dird_verify_certificate)
        Input.configure(dird_host, dird_port, dird_verify_certificate)
        Lookup.configure(dird_host, dird_port, dird_verify_certificate)
        api.add_resource(Menu, self.menu_url)
        api.add_resource(Input, self.input_url)
        api.add_resource(Lookup, self.lookup_url)

        MenuAutodetect.configure(dird_host, dird_port, dird_verify_certificate, dird_default_profile)
        InputAutodetect.configure(dird_host, dird_port, dird_verify_certificate, dird_default_profile)
        LookupAutodetect.configure(dird_host, dird_port, dird_verify_certificate, dird_default_profile)
        api.add_resource(MenuAutodetect, self.menu_autodetect_url)
        api.add_resource(InputAutodetect, self.input_autodetect_url)
        api.add_resource(LookupAutodetect, self.lookup_autodetect_url)


class Menu(AuthResource):

    dird_host = None
    dird_port = None
    dird_verify_certificate = None

    @classmethod
    def configure(cls, dird_host, dird_port, dird_verify_certificate):
        cls.dird_host = dird_host
        cls.dird_port = dird_port
        cls.dird_verify_certificate = dird_verify_certificate

    def get(self, profile, vendor):
        args = parser.parse_args()
        xivo_user_uuid = args['xivo_user_uuid']

        try:
            backend_args = {'xivo_user_uuid': xivo_user_uuid}
            token_infos = auth.client().token.new(AUTH_BACKEND, expiration=AUTH_EXPIRATION, backend_args=backend_args)
        except requests.RequestException as e:
            message = 'Could not connect to authentication server: {error}'.format(error=e)
            logger.exception(message)
            return _error(503, message)

        headers = {'X-Auth-Token': token_infos['token'],
                   'Proxy-URL': request.base_url.replace('menu', 'input', 1)}
        url = 'https://{host}:{port}/{version}/directories/menu/{profile}/{vendor}'
        r = requests.get(url.format(host=self.dird_host,
                                    port=self.dird_port,
                                    version=DIRD_API_VERSION,
                                    profile=profile,
                                    vendor=vendor),
                         headers=headers,
                         verify=self.dird_verify_certificate)

        return Response(response=r.content, content_type=r.headers['content-type'], status=r.status_code)


# XXX Migration code
class MenuAutodetect(AuthResource):

    dird_default_profile = None
    dird_host = None
    dird_port = None
    dird_verify_certificate = None

    @classmethod
    def configure(cls, dird_host, dird_port, dird_verify_certificate, dird_default_profile):
        cls.dird_default_profile = dird_default_profile
        cls.dird_host = dird_host
        cls.dird_port = dird_port
        cls.dird_verify_certificate = dird_verify_certificate

    def get(self):
        xivo_user_uuid = FAKE_XIVO_USER_UUID
        profile = self.dird_default_profile

        user_agent = request.headers.get('User-agent', '').lower()
        vendor = _find_vendor_by_user_agent(user_agent)
        if not vendor:
            return _error(404, 'No vendor found')

        try:
            backend_args = {'xivo_user_uuid': xivo_user_uuid}
            token_infos = auth.client().token.new(AUTH_BACKEND, expiration=AUTH_EXPIRATION, backend_args=backend_args)
        except requests.RequestException as e:
            message = 'Could not connect to authentication server: {error}'.format(error=e)
            logger.exception(message)
            return _error(503, message)

        headers = {'X-Auth-Token': token_infos['token'],
                   'Proxy-URL': request.base_url.replace('menu', 'input', 1)}
        url = 'https://{host}:{port}/{version}/directories/menu/{profile}/{vendor}'
        r = requests.get(url.format(host=self.dird_host,
                                    port=self.dird_port,
                                    version=DIRD_API_VERSION,
                                    profile=profile,
                                    vendor=vendor),
                         headers=headers,
                         verify=self.dird_verify_certificate)

        return Response(response=r.content, content_type=r.headers['content-type'], status=r.status_code)


class Input(AuthResource):

    dird_host = None
    dird_port = None
    dird_verify_certificate = None

    @classmethod
    def configure(cls, dird_host, dird_port, dird_verify_certificate):
        cls.dird_host = dird_host
        cls.dird_port = dird_port
        cls.dird_verify_certificate = dird_verify_certificate

    def get(self, profile, vendor):
        args = parser.parse_args()
        xivo_user_uuid = args['xivo_user_uuid']

        try:
            backend_args = {'xivo_user_uuid': xivo_user_uuid}
            token_infos = auth.client().token.new(AUTH_BACKEND, expiration=AUTH_EXPIRATION, backend_args=backend_args)
        except requests.RequestException as e:
            message = 'Could not connect to authentication server: {error}'.format(error=e)
            logger.exception(message)
            return _error(503, message)

        headers = {'X-Auth-Token': token_infos['token'],
                   'Proxy-URL': request.base_url.replace('input', 'lookup', 1)}
        url = 'https://{host}:{port}/{version}/directories/input/{profile}/{vendor}'
        r = requests.get(url.format(host=self.dird_host,
                                    port=self.dird_port,
                                    version=DIRD_API_VERSION,
                                    profile=profile,
                                    vendor=vendor),
                         headers=headers,
                         verify=self.dird_verify_certificate)

        return Response(response=r.content, content_type=r.headers['content-type'], status=r.status_code)


class InputAutodetect(AuthResource):

    dird_default_profile = None
    dird_host = None
    dird_port = None
    dird_verify_certificate = None

    @classmethod
    def configure(cls, dird_host, dird_port, dird_verify_certificate, dird_default_profile):
        cls.dird_default_profile = dird_default_profile
        cls.dird_host = dird_host
        cls.dird_port = dird_port
        cls.dird_verify_certificate = dird_verify_certificate

    def get(self):
        xivo_user_uuid = FAKE_XIVO_USER_UUID
        profile = self.dird_default_profile

        user_agent = request.headers.get('User-agent', '').lower()
        vendor = _find_vendor_by_user_agent(user_agent)
        if not vendor:
            return _error(404, 'No vendor found')

        try:
            backend_args = {'xivo_user_uuid': xivo_user_uuid}
            token_infos = auth.client().token.new(AUTH_BACKEND, expiration=AUTH_EXPIRATION, backend_args=backend_args)
        except requests.RequestException as e:
            message = 'Could not connect to authentication server: {error}'.format(error=e)
            logger.exception(message)
            return _error(503, message)

        headers = {'X-Auth-Token': token_infos['token'],
                   'Proxy-URL': request.base_url.replace('input', 'lookup', 1)}
        url = 'https://{host}:{port}/{version}/directories/input/{profile}/{vendor}'
        r = requests.get(url.format(host=self.dird_host,
                                    port=self.dird_port,
                                    version=DIRD_API_VERSION,
                                    profile=profile,
                                    vendor=vendor),
                         headers=headers,
                         verify=self.dird_verify_certificate)

        return Response(response=r.content, content_type=r.headers['content-type'], status=r.status_code)


class Lookup(AuthResource):

    dird_host = None
    dird_port = None
    dird_verify_certificate = None

    @classmethod
    def configure(cls, dird_host, dird_port, dird_verify_certificate):
        cls.dird_host = dird_host
        cls.dird_port = dird_port
        cls.dird_verify_certificate = dird_verify_certificate

    def get(self, profile, vendor):
        args = parser_lookup.parse_args()
        limit = args['limit']
        offset = args['offset']
        term = args['term']
        xivo_user_uuid = args['xivo_user_uuid']

        try:
            backend_args = {'xivo_user_uuid': xivo_user_uuid}
            token_infos = auth.client().token.new(AUTH_BACKEND, expiration=AUTH_EXPIRATION, backend_args=backend_args)
        except requests.RequestException as e:
            message = 'Could not connect to authentication server: {error}'.format(error=e)
            logger.exception(message)
            return _error(503, message)

        headers = {'X-Auth-Token': token_infos['token'],
                   'Proxy-URL': request.base_url}
        query = ['term={term}'.format(term=term)]
        query.append('limit={limit}'.format(limit=limit)) if limit else None
        query.append('offset={offset}'.format(offset=offset)) if offset else None
        url = 'https://{host}:{port}/{version}/directories/lookup/{profile}/{vendor}?{query}'
        r = requests.get(url.format(host=self.dird_host,
                                    port=self.dird_port,
                                    version=DIRD_API_VERSION,
                                    profile=profile,
                                    vendor=vendor,
                                    query='&'.join(query)),
                         headers=headers,
                         verify=self.dird_verify_certificate)

        return Response(response=r.content, content_type=r.headers['content-type'], status=r.status_code)


class LookupAutodetect(AuthResource):

    dird_default_profile = None
    dird_host = None
    dird_port = None
    dird_verify_certificate = None

    @classmethod
    def configure(cls, dird_host, dird_port, dird_verify_certificate, dird_default_profile):
        cls.dird_default_profile = dird_default_profile
        cls.dird_host = dird_host
        cls.dird_port = dird_port
        cls.dird_verify_certificate = dird_verify_certificate

    def get(self):
        args = parser_lookup_autodetect.parse_args()
        limit = args['limit']
        offset = args['offset']
        term = args['term']
        xivo_user_uuid = FAKE_XIVO_USER_UUID
        profile = self.dird_default_profile

        user_agent = request.headers.get('User-agent', '').lower()
        vendor = _find_vendor_by_user_agent(user_agent)
        if not vendor:
            return _error(404, 'No vendor found')

        try:
            backend_args = {'xivo_user_uuid': xivo_user_uuid}
            token_infos = auth.client().token.new(AUTH_BACKEND, expiration=AUTH_EXPIRATION, backend_args=backend_args)
        except requests.RequestException as e:
            message = 'Could not connect to authentication server: {error}'.format(error=e)
            logger.exception(message)
            return _error(503, message)

        headers = {'X-Auth-Token': token_infos['token'],
                   'Proxy-URL': request.base_url}
        query = ['term={term}'.format(term=term)]
        query.append('limit={limit}'.format(limit=limit)) if limit else None
        query.append('offset={offset}'.format(offset=offset)) if offset else None
        url = 'https://{host}:{port}/{version}/directories/lookup/{profile}/{vendor}?{query}'
        r = requests.get(url.format(host=self.dird_host,
                                    port=self.dird_port,
                                    version=DIRD_API_VERSION,
                                    profile=profile,
                                    vendor=vendor,
                                    query='&'.join(query)),
                         headers=headers,
                         verify=self.dird_verify_certificate)

        return Response(response=r.content, content_type=r.headers['content-type'], status=r.status_code)


def _find_vendor_by_user_agent(user_agent):

    if 'aastra' in user_agent:
        # '/^Aastra((?:(?:67)?5[1357]|673[01])i(?: CT)?) /'
        return 'aastra'
    elif 'cisco' in user_agent or 'allegro' in user_agent:
        # '/Allegro-/i'
        return 'cisco'
    elif 'snom' in user_agent:
        # '/(snom3[026]0)-/'
        return 'snom'
    elif 'thomson' in user_agent:
        # '/^THOMSON (ST2022|ST2030|TB30) /'
        return 'thomson'
    elif 'yealink' in user_agent:
        return 'yealink'
    return None
