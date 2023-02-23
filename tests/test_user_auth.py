import requests
import pytest
from lib.base_case import BaseCase
from lib.assertions import Assertions
from lib.my_requests import MyRequests
import allure


# Для запуска теста из командной строки:
# python -m pytest -s tests/test_user_auth.py


#  Для генерации allure-отчета
#  python -m pytest --alluredir=test_results Lesson_4/tests/test_user_auth.py
#  allure serve Lesson_4/test_results/


@allure.epic("Authorization cases")
class TestUserAuth(BaseCase):
    exclude_params = [
        ("no_cookie"),
        ("no_token")
    ]
    # Вызывается перед каждым тестом
    def setup_method(self):
        data = {
            "email": "vinkotov@example.com",
            "password": "1234"
        }

        response = MyRequests.post("/user/login", data=data)

        self.auth_sid = self.get_cookie(response, "auth_sid")
        self.token = self.get_header(response, "x-csrf-token")
        self.user_id_from_auth_method = self.get_json_value(response, "user_id")

    @allure.description("This test successfully authorize user by email and password and get his info")
    def test_auth_user(self):
        response = MyRequests.get(
            "/user/auth",
            headers={"x-csrf-token": self.token},
            cookies={"auth_sid": self.auth_sid}
        )

        Assertions.assert_json_value_by_name(
            response,
            "user_id",
            self.user_id_from_auth_method,
            "User id from auth method is not equal to user id from from check method"
        )

    @allure.description("This test checks authorization status w/o sending auth cookie or token")
    @pytest.mark.parametrize('condition', exclude_params)
    def test_negative_auth_check(self, condition):
        if condition == "no_cookie":
            response = MyRequests.get(
                "/user/auth",
                 headers={"x-csrf-token": self.token}
            )
        else:
            response = MyRequests.get(
                "/user/auth",
                cookies={"auth_sid": self.auth_sid}
            )

        Assertions.assert_json_value_by_name(
            response,
            "user_id",
            0,
            f"User is authorized with condition {condition}"
        )
