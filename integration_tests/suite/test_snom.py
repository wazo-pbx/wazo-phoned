# Copyright 2015-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from textwrap import dedent

from hamcrest import assert_that, equal_to

from .helpers.base import (
    DEFAULT_PROFILE,
    USER_1_UUID,
    VALID_TERM,
    BasePhonedIntegrationTest,
)
from .helpers.wait_strategy import PhonedEverythingUpWaitStrategy

VENDOR = 'snom'


class TestSnom(BasePhonedIntegrationTest):
    asset = 'default_config'
    wait_strategy = PhonedEverythingUpWaitStrategy()

    # Menu - There is no menu for snom

    def test_that_menu_return_error_when_query_ssl(self):
        response = self.get_ssl_menu_result(
            vendor=VENDOR,
            xivo_user_uuid=USER_1_UUID,
            profile=DEFAULT_PROFILE,
        )
        assert_that(response.status_code, equal_to(404))

    def test_that_menu_return_error_when_query(self):
        response = self.get_menu_result(
            vendor=VENDOR,
            xivo_user_uuid=USER_1_UUID,
            profile=DEFAULT_PROFILE,
        )
        assert_that(response.status_code, equal_to(404))

    # Input

    def test_that_input_return_no_error_when_query_ssl(self):
        response = self.get_ssl_input_result(
            vendor=VENDOR,
            xivo_user_uuid=USER_1_UUID,
            profile=DEFAULT_PROFILE,
        )
        assert_that(response.status_code, equal_to(200))
        assert_that(
            response.text,
            equal_to(
                dedent(
                    f"""\
        <?xml version="1.0" encoding="UTF-8" ?>
        <SnomIPPhoneInput>
         <Url>https://127.0.0.1:{self.service_port(9499, 'phoned')}/0.1/directories/lookup/{DEFAULT_PROFILE}/snom?xivo_user_uuid={USER_1_UUID}&term=__X__</Url>
         <InputItem>
          <DisplayName>Name or number</DisplayName>
          <InputToken>__X__</InputToken>
          <DefaultValue />
          <InputFlags>a</InputFlags>
         </InputItem>
        </SnomIPPhoneInput>"""
                )
            ),
        )

    def test_that_input_return_no_error_when_query(self):
        response = self.get_input_result(
            vendor=VENDOR,
            xivo_user_uuid=USER_1_UUID,
            profile=DEFAULT_PROFILE,
        )
        assert_that(response.status_code, equal_to(200))

    def test_that_input_return_error_when_no_xivo_user_uuid(self):
        response = self.get_input_result(vendor=VENDOR, profile=DEFAULT_PROFILE)
        assert_that(response.status_code, equal_to(400))

    # Lookup

    def test_that_lookup_return_no_error_when_query_ssl(self):
        response = self.get_ssl_lookup_result(
            vendor=VENDOR,
            xivo_user_uuid=USER_1_UUID,
            profile=DEFAULT_PROFILE,
            term=VALID_TERM,
        )
        assert_that(response.status_code, equal_to(200))
        assert_that(
            response.text,
            equal_to(
                dedent(
                    """\
        <?xml version="1.0" encoding="UTF-8" ?>
        <SnomIPPhoneMenu>
         <Title>Wazo Directory</Title>
        <MenuItem name="Test User1">
          <Url>snom://mb_nop#numberdial=0033123456789</Url>
          <ExtraText>0033123456789</ExtraText>
         </MenuItem>
        <MenuItem name="Test User1 (mobile)">
          <Url>snom://mb_nop#numberdial=5555555555</Url>
          <ExtraText>5555555555</ExtraText>
         </MenuItem>
        <MenuItem name="Test User2">
          <Url>snom://mb_nop#numberdial=1000</Url>
          <ExtraText>1000</ExtraText>
         </MenuItem>
        </SnomIPPhoneMenu>"""
                )
            ),
        )

    def test_that_lookup_return_no_entries_when_no_results(self):
        response = self.get_ssl_lookup_result(
            vendor=VENDOR,
            xivo_user_uuid=USER_1_UUID,
            profile=DEFAULT_PROFILE,
            term='no-result',
        )
        assert_that(response.status_code, equal_to(200))
        assert_that(
            response.text,
            equal_to(
                dedent(
                    """\
        <?xml version="1.0" encoding="UTF-8" ?>
        <SnomIPPhoneMenu>
         <Title>Wazo Directory</Title>
        <MenuItem name="No entries">
         </MenuItem>
        </SnomIPPhoneMenu>"""
                )
            ),
        )

    def test_that_lookup_with_limit_one_shows_next_page_link(self):
        response = self.get_ssl_lookup_result(
            vendor=VENDOR,
            xivo_user_uuid=USER_1_UUID,
            profile=DEFAULT_PROFILE,
            term=VALID_TERM,
            limit=1,
        )
        assert_that(response.status_code, equal_to(200))
        assert_that(
            response.text,
            equal_to(
                dedent(
                    f"""\
        <?xml version="1.0" encoding="UTF-8" ?>
        <SnomIPPhoneMenu>
         <Title>Wazo Directory</Title>
        <MenuItem name="Test User1">
          <Url>snom://mb_nop#numberdial=0033123456789</Url>
          <ExtraText>0033123456789</ExtraText>
         </MenuItem>
        <SoftKeyItem>
        <Label>NextPage</Label>
        <URL>https://127.0.0.1:{self.service_port(9499, 'phoned')}/0.1/directories/lookup/{DEFAULT_PROFILE}/snom?xivo_user_uuid={USER_1_UUID}&amp;term={VALID_TERM}&amp;limit=1&amp;offset=1</URL>
        <Name>F4</Name>
        </SoftKeyItem>
        </SnomIPPhoneMenu>"""
                )
            ),
        )

    def test_that_lookup_with_limit_one_offset_one_shows_previous_and_next_page_links(
        self,
    ):
        response = self.get_ssl_lookup_result(
            vendor=VENDOR,
            xivo_user_uuid=USER_1_UUID,
            profile=DEFAULT_PROFILE,
            term=VALID_TERM,
            limit=1,
            offset=1,
        )
        assert_that(response.status_code, equal_to(200))
        assert_that(
            response.text,
            equal_to(
                dedent(
                    f"""\
        <?xml version="1.0" encoding="UTF-8" ?>
        <SnomIPPhoneMenu>
         <Title>Wazo Directory</Title>
        <MenuItem name="Test User1 (mobile)">
          <Url>snom://mb_nop#numberdial=5555555555</Url>
          <ExtraText>5555555555</ExtraText>
         </MenuItem>
        <SoftKeyItem>
        <Label>PrevPage</Label>
        <URL>https://127.0.0.1:{self.service_port(9499, 'phoned')}/0.1/directories/lookup/{DEFAULT_PROFILE}/snom?xivo_user_uuid={USER_1_UUID}&amp;term={VALID_TERM}&amp;limit=1&amp;offset=0</URL>
        <Name>F2</Name>
        </SoftKeyItem>
        <SoftKeyItem>
        <Label>NextPage</Label>
        <URL>https://127.0.0.1:{self.service_port(9499, 'phoned')}/0.1/directories/lookup/{DEFAULT_PROFILE}/snom?xivo_user_uuid={USER_1_UUID}&amp;term={VALID_TERM}&amp;limit=1&amp;offset=2</URL>
        <Name>F4</Name>
        </SoftKeyItem>
        </SnomIPPhoneMenu>"""
                )
            ),
        )

    def test_that_lookup_with_limit_one_offset_two_shows_previous_page_link(self):
        response = self.get_ssl_lookup_result(
            vendor=VENDOR,
            xivo_user_uuid=USER_1_UUID,
            profile=DEFAULT_PROFILE,
            term=VALID_TERM,
            limit=1,
            offset=2,
        )
        assert_that(response.status_code, equal_to(200))
        assert_that(
            response.text,
            equal_to(
                dedent(
                    f"""\
        <?xml version="1.0" encoding="UTF-8" ?>
        <SnomIPPhoneMenu>
         <Title>Wazo Directory</Title>
        <MenuItem name="Test User2">
          <Url>snom://mb_nop#numberdial=1000</Url>
          <ExtraText>1000</ExtraText>
         </MenuItem>
        <SoftKeyItem>
        <Label>PrevPage</Label>
        <URL>https://127.0.0.1:{self.service_port(9499, 'phoned')}/0.1/directories/lookup/{DEFAULT_PROFILE}/snom?xivo_user_uuid={USER_1_UUID}&amp;term={VALID_TERM}&amp;limit=1&amp;offset=1</URL>
        <Name>F2</Name>
        </SoftKeyItem>
        </SnomIPPhoneMenu>"""
                )
            ),
        )

    def test_lookup_translation_fr(self):
        response = self.get_ssl_lookup_result(
            vendor=VENDOR,
            xivo_user_uuid=USER_1_UUID,
            profile=DEFAULT_PROFILE,
            term='no-result',
            headers={'Accept-Language': 'gibberish,fr-CA,*q=nothing'},
        )
        assert_that(response.status_code, equal_to(200))
        assert_that(
            response.text,
            equal_to(
                dedent(
                    """\
        <?xml version="1.0" encoding="UTF-8" ?>
        <SnomIPPhoneMenu>
         <Title>Répertoire Wazo</Title>
        <MenuItem name="Aucune entrée">
         </MenuItem>
        </SnomIPPhoneMenu>"""
                )
            ),
        )

    def test_that_lookup_return_no_error_when_query(self):
        response = self.get_lookup_result(
            vendor=VENDOR,
            xivo_user_uuid=USER_1_UUID,
            profile=DEFAULT_PROFILE,
            term=VALID_TERM,
        )
        assert_that(response.status_code, equal_to(200))

    def test_that_lookup_return_error_when_no_xivo_user_uuid(self):
        response = self.get_lookup_result(
            vendor=VENDOR, profile=DEFAULT_PROFILE, term=VALID_TERM
        )
        assert_that(response.status_code, equal_to(400))

    def test_that_lookup_return_error_when_invalid_user_uuid(self):
        response = self.get_lookup_result(
            vendor=VENDOR, profile='a', xivo_user_uuid='invalid', term=VALID_TERM
        )
        assert_that(response.status_code, equal_to(404))

    def test_that_lookup_return_error_when_no_term(self):
        response = self.get_lookup_result(
            vendor=VENDOR,
            xivo_user_uuid=USER_1_UUID,
            profile=DEFAULT_PROFILE,
        )
        assert_that(response.status_code, equal_to(400))


class TestAuthError(BasePhonedIntegrationTest):
    asset = 'no_auth_server'

    def test_no_auth_server_gives_503(self):
        response = self.get_lookup_result(
            vendor=VENDOR,
            xivo_user_uuid=USER_1_UUID,
            profile=DEFAULT_PROFILE,
            term='a',
        )
        assert_that(response.status_code, equal_to(503))


class TestDirdError(BasePhonedIntegrationTest):
    asset = 'no_dird_server'

    def test_no_dird_server_gives_503(self):
        response = self.get_lookup_result(
            vendor=VENDOR,
            xivo_user_uuid=USER_1_UUID,
            profile=DEFAULT_PROFILE,
            term='a',
        )
        assert_that(response.status_code, equal_to(503))
