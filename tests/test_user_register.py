import requests
from lib.base_case import BaseCase
from lib.assertions import Assertions
from datetime import datetime
from lib.my_requests import MyRequests
import pytest
import allure


#  Для генерации allure-отчета
#  python -m pytest --alluredir=test_results tests/test_user_register.py
#  allure serve test_results/


# Для запуска теста из командной строки:
# python -m pytest -s tests/test_user_registe.py


@allure.epic("User register cases")
class TestUserRegister(BaseCase):
    fields = [
        ('password'),
        ('username'),
        ('firstName'),
        ('lastName'),
        ('email')]

    @allure.description("This test creates a user")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_user_create_successfully(self):
        data = self.prepare_registration_data()

        response = MyRequests.post("/user", data=data)

        Assertions.assert_code_status(response, 200)
        Assertions.assert_json_has_key(response, "id")

    @allure.description("This test tries to create a user with an existing email")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_user_with_existing_email(self):
        email = 'vinkotov@example.com'
        data = self.prepare_registration_data(email)

        response = MyRequests.post("/user", data=data)

        Assertions.assert_code_status(response, 400)
        assert response.content.decode("utf-8") == f"Users with email '{email}' already exists", f"Unexpected response content {response.content}"

    @allure.description("This test tries to create a user with an invalid email")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_user_with_invalid_email(self):
        email = 'vinkotovexample.com'
        data = self.prepare_registration_data(email)

        response = MyRequests.post("/user", data=data)

        Assertions.assert_code_status(response, 400)
        Assertions.assert_content(response, "Invalid email format")

    @allure.description("This test tries to create a user without a required field")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize('field', fields)
    def test_create_user_without_some_field(self, field):
        data = self.prepare_registration_data()
        del data[field]
        response = MyRequests.post("/user", data)

        Assertions.assert_code_status(response, 400)
        Assertions.assert_content(response, f"The following required params are missed: {field}")

    @allure.description("This test tries to create a user with short name")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_user_with_too_short_name(self):
        data = self.prepare_registration_data()
        data['username'] = "T"

        response = MyRequests.post("/user", data=data)

        Assertions.assert_code_status(response, 400)
        Assertions.assert_content(response, "The value of 'username' field is too short")

    @allure.description("This test tries to create a user too long name")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_user_with_too_long_name(self):
        data = self.prepare_registration_data()
        data['username'] = "T"*251

        response = MyRequests.post("/user", data=data)

        Assertions.assert_code_status(response, 400)
        Assertions.assert_content(response, "The value of 'username' field is too long")
