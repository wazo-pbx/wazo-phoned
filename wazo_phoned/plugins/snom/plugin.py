# Copyright 2019-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_phoned.plugin_helpers.client.plugin import ClientPlugin

from .http import Input, Lookup, LookupV2


class Plugin(ClientPlugin):
    vendor = 'snom'
    import_name = __name__

    def _add_resources(self, api, class_kwargs):
        api.add_resource(
            Input,
            self.input_url,
            endpoint='snom_input',
            resource_class_kwargs=class_kwargs,
        )
        api.add_resource(
            Lookup,
            self.lookup_url,
            endpoint='snom_lookup',
            resource_class_kwargs=class_kwargs,
        )
        api.add_resource(
            LookupV2,
            self.lookup_url,
            endpoint='snom_lookup_v2',
            resource_class_kwargs=class_kwargs,
        )
