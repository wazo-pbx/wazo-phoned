# Copyright 2020-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

logger = logging.getLogger(__name__)


class BusEventHandler:
    def __init__(self, service):
        self._service = service

    def subscribe(self, bus_consumer):
        bus_consumer.on_event(
            'users_services_dnd_updated', self._users_services_dnd_updated
        )
        bus_consumer.on_event(
            'users_services_incallfilter_updated',
            self._users_services_incallfilter_updated,
        )
        bus_consumer.on_event(
            'users_forwards_unconditional_updated',
            self._users_forwards_unconditional_updated,
        )
        bus_consumer.on_event(
            'users_forwards_noanswer_updated', self._users_forwards_noanswer_updated
        )
        bus_consumer.on_event(
            'users_forwards_busy_updated', self._users_forwards_busy_updated
        )
        bus_consumer.on_event(
            'extension_feature_edited', self._extension_feature_edited
        )

    def _users_services_dnd_updated(self, event):
        user_id = event['user_id']
        user_uuid = event['user_uuid']
        enabled = event['enabled']
        self._service.notify_dnd(user_id, user_uuid, enabled)

    def _users_services_incallfilter_updated(self, event):
        user_id = event['user_id']
        enabled = event['enabled']
        self._service.notify_incallfilter(user_id, enabled)

    def _users_forwards_unconditional_updated(self, event):
        user_id = event['user_id']
        enabled = event['enabled']
        destination = event['destination']
        self._service.notify_forward_unconditional(user_id, destination, enabled)

    def _users_forwards_noanswer_updated(self, event):
        user_id = event['user_id']
        enabled = event['enabled']
        destination = event['destination']
        self._service.notify_forward_noanswer(user_id, destination, enabled)

    def _users_forwards_busy_updated(self, event):
        user_id = event['user_id']
        enabled = event['enabled']
        destination = event['destination']
        self._service.notify_forward_busy(user_id, destination, enabled)

    def _extension_feature_edited(self, event):
        self._service.invalidate_cache()
