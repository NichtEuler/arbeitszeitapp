from typing import Dict, List

from injector import Module, provider

from arbeitszeit_flask.language_repository import LanguageRepositoryImpl

from .dependency_injection import FlaskConfiguration
from .flask import FlaskTestCase


class LanguageRepositoryTestCase(FlaskTestCase):
    @property
    def expected_languages(self) -> Dict[str, str]:
        raise NotImplementedError()

    def get_injection_modules(self) -> List[Module]:
        expected_languages = self.expected_languages

        class _Module(Module):
            @provider
            def provide_flask_configuration(self) -> FlaskConfiguration:
                configuration = FlaskConfiguration.default()
                configuration["LANGUAGES"] = expected_languages
                return configuration

        modules = super().get_injection_modules()
        modules.append(_Module())
        return modules


class TwoLanguagesAvailableTests(LanguageRepositoryTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.repository = self.injector.get(LanguageRepositoryImpl)

    @property
    def expected_languages(self) -> Dict[str, str]:
        return {"en": "English", "de": "Deutsch"}

    def test_that_repository_returns_at_least_one_code(self) -> None:
        self.assertTrue(self.repository.get_available_language_codes())

    def test_that_repository_returns_exactly_two_codes(self) -> None:
        self.assertEqual(len(self.repository.get_available_language_codes()), 2)

    def test_that_proper_language_name_is_returned_for_english(self) -> None:
        self.assertEqual(
            self.repository.get_language_name("en"),
            "English",
        )

    def test_that_proper_language_name_is_returned_for_german(self) -> None:
        self.assertEqual(
            self.repository.get_language_name("de"),
            "Deutsch",
        )


class NoLanguagesAvailableTests(LanguageRepositoryTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.repository = self.injector.get(LanguageRepositoryImpl)

    def test_that_no_language_codes_are_returned(self) -> None:
        self.assertFalse(self.repository.get_available_language_codes())

    def test_that_no_language_name_is_returned_if_language_is_not_stored_in_config(
        self,
    ) -> None:
        self.assertIsNone(self.repository.get_language_name("en"))

    @property
    def expected_languages(self) -> Dict[str, str]:
        return {}
