# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
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

    def _users_services_dnd_updated(self, event):
        user_uuid = event.get('user_uuid') or event.get('user_id')
        enabled = event['enabled']
        self._service.notify_dnd(user_uuid, enabled)
