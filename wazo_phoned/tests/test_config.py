# Copyright 2015-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from unittest import TestCase
from unittest.mock import Mock, patch, sentinel as s

from hamcrest import assert_that, has_entries, equal_to

from .. import config


@patch('builtins.print', Mock())
@patch('wazo_phoned.config.open', create=True)
@patch('wazo_phoned.config._load_key_file', lambda x: {})
class TestConfig(TestCase):
    def test_load_when_no_args_and_no_default_config_file_then_return_default_values(
        self, mock_open
    ):
        mock_open.side_effect = IOError('no such file')
        config._DEFAULT_CONFIG = {
            'config': 'default',
            'config_file': '/etc/wazo-phoned/config.yml',
            'extra_config_files': '/etc/wazo-phoned/conf.d/',
            'auth': {},
        }

        result = config.load(s.logger, [])

        assert_that(result, has_entries(config._DEFAULT_CONFIG))

    def test_load_when_config_file_in_argv_then_read_config_from_file(self, _):
        result = config.load(s.logger, ['-c', 'my_file'])

        assert_that(result['config_file'], equal_to('my_file'))

    def test_load_when_user_in_argv_then_ignore_default_value(self, mock_open):
        mock_open.side_effect = IOError('no such file')

        result = config.load(s.logger, ['-u', 'my_user'])

        assert_that(result['user'], equal_to('my_user'))

    def test_load_when_debug_in_argv_then_ignore_default_value(self, mock_open):
        mock_open.side_effect = IOError('no such file')

        result = config.load(s.logger, ['-d'])

        assert_that(result['debug'], equal_to(True))

    def test_load_when_log_level_in_argv_then_ignore_default_value(self, mock_open):
        mock_open.side_effect = IOError('no such file')

        result = config.load(s.logger, ['-l', 'ERROR'])

        assert_that(result['log_level'], equal_to(logging.ERROR))
