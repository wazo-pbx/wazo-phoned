# Copyright 2019-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from wazo_amid_client import Client as AmidClient
from wazo_auth_client import Client as AuthClient
from wazo_confd_client import Client as ConfdClient
from wazo_dird_client import Client as DirdClient

from wazo_phoned.plugin_helpers.common import create_blueprint_api
from .bus_consume import BusEventHandler
from .http import (
    BusyUserForward,
    DNDUserServiceEnable,
    DNDUserServiceDisable,
    Lookup,
    NoAnswerUserForward,
    UnconditionalUserForward,
)
from .services import YealinkService

logger = logging.getLogger(__name__)


class Plugin:

    # NOTE(afournier): this vendor-ending URL will be deprecated
    lookup_url_fmt = '/directories/lookup/<profile>/{vendor}'

    directories_lookup_url_fmt = '/{vendor}/directories/lookup/<profile>'

    user_service_dnd_enable_url_fmt = '/{vendor}/users/<user_uuid>/services/dnd/enable'
    user_service_dnd_disable_url_fmt = (
        '/{vendor}/users/<user_uuid>/services/dnd/disable'
    )
    user_forward_busy_disable_url_fmt = (
        '/{vendor}/users/<user_uuid>/forwards/busy/disable'
    )
    user_forward_noanswer_disable_url_fmt = (
        '/{vendor}/users/<user_uuid>/forwards/noanswer/disable'
    )
    user_forward_unconditional_disable_url_fmt = (
        '/{vendor}/users/<user_uuid>/forwards/unconditional/disable'
    )

    vendor = 'yealink'
    import_name = __name__

    def load(self, dependencies):
        app = dependencies['app']
        amid_client = AmidClient(**dependencies['config']['amid'])
        auth_client = AuthClient(**dependencies['config']['auth'])
        confd_client = ConfdClient(**dependencies['config']['confd'])
        dird_client = DirdClient(**dependencies['config']['dird'])
        token_changed_subscribe = dependencies['token_changed_subscribe']
        token_changed_subscribe(amid_client.set_token)
        token_changed_subscribe(auth_client.set_token)
        token_changed_subscribe(confd_client.set_token)
        token_changed_subscribe(dird_client.set_token)

        service = YealinkService(amid_client, confd_client)

        bus_consumer = dependencies['bus_consumer']
        bus_event_handler = BusEventHandler(service)
        bus_event_handler.subscribe(bus_consumer)

        directories_class_kwargs = {
            'vendor': self.vendor,
            'dird_client': dird_client,
            'auth_client': auth_client,
        }
        user_service_class_kwargs = {
            'service': service,
        }

        api = create_blueprint_api(
            app, '{}_plugin'.format(self.vendor), self.import_name
        )

        self.lookup_url = self.lookup_url_fmt.format(vendor=self.vendor)

        self.directories_lookup_url = self.directories_lookup_url_fmt.format(
            vendor=self.vendor
        )

        self.user_service_dnd_enable_url = self.user_service_dnd_enable_url_fmt.format(
            vendor=self.vendor
        )
        self.user_service_dnd_disable_url = self.user_service_dnd_disable_url_fmt.format(
            vendor=self.vendor
        )
        self.user_forward_busy_disable_url = self.user_forward_busy_disable_url_fmt.format(
            vendor=self.vendor
        )
        self.user_forward_noanswer_disable_url = self.user_forward_noanswer_disable_url_fmt.format(
            vendor=self.vendor
        )
        self.user_forward_unconditional_disable_url = self.user_forward_unconditional_disable_url_fmt.format(
            vendor=self.vendor
        )
        self._add_resources(api, directories_class_kwargs)
        self._add_user_service_resources(api, user_service_class_kwargs)

    def _add_resources(self, api, class_kwargs):
        api.add_resource(
            Lookup,
            self.lookup_url,
            endpoint='yealink_lookup',
            resource_class_kwargs=class_kwargs,
        )
        api.add_resource(
            Lookup,
            self.directories_lookup_url,
            endpoint='yealink_directories_lookup',
            resource_class_kwargs=class_kwargs,
        )

    def _add_user_service_resources(self, api, class_kwargs):
        api.add_resource(
            DNDUserServiceEnable,
            self.user_service_dnd_enable_url,
            endpoint='yealink_user_service_dnd_enable',
            resource_class_kwargs=class_kwargs,
        )
        api.add_resource(
            DNDUserServiceDisable,
            self.user_service_dnd_disable_url,
            endpoint='yealink_user_service_dnd_disable',
            resource_class_kwargs=class_kwargs,
        )
        api.add_resource(
            BusyUserForward,
            self.user_forward_busy_disable_url,
            endpoint='yealink_user_forward_busy_disable',
            resource_class_kwargs=class_kwargs,
        )
        api.add_resource(
            NoAnswerUserForward,
            self.user_forward_noanswer_disable_url,
            endpoint='yealink_user_forward_noanswer_disable',
            resource_class_kwargs=class_kwargs,
        )
        api.add_resource(
            UnconditionalUserForward,
            self.user_forward_unconditional_disable_url,
            endpoint='yealink_user_forward_unconditional_disable',
            resource_class_kwargs=class_kwargs,
        )
