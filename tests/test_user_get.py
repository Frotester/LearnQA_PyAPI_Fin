import requests
from lib.base_case import BaseCase
from lib.assertions import Assertions
from lib.my_requests import MyRequests
import allure

#  Для генерации allure-отчета
#  python -m pytest --alluredir=test_results tests/test_user_get.py
#  allure serve test_results/


# Для запуска теста из командной строки:
# python -m pytest -s tests/test_user_get.py


@allure.epic("User get cases")
@allure.severity(allure.severity_level.CRITICAL)
class TestUserGet(BaseCase):
    # Проверка, что для неавторизованного пользователя возвращается только одно поле username
    @allure.description("This test tries to get info without auth tokens")
    def test_get_user_details_not_auth(self):
        response = MyRequests.get("/user/2")
        Assertions.assert_json_has_key(response, "username")
        Assertions.assert_json_has_not_key(response, "email")
        Assertions.assert_json_has_not_key(response, "firstName")
        Assertions.assert_json_has_not_key(response, "lastName")

    # Проверка, что для авторизованного пользователя возвращаются все поля
    @allure.description("TThis test tries to get info with auth tokens")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_user_details_as_same_user(self):
        with allure.step("It logs in under the user"):
            data = {
                'email': 'vinkotov@example.com',
                'password': '1234'
            }

            response = MyRequests.post("/user/login", data=data)

            auth_sid = self.get_cookie(response, "auth_sid")
            token = self.get_header(response, "x-csrf-token")
            user_id_from_auth_method = self.get_json_value(response, "user_id")

        with allure.step("It gets information about the logged in user"):
            response = MyRequests.get(
                f"/user/{user_id_from_auth_method}",
                headers={"x-csrf-token": token},
                cookies={"auth_sid": auth_sid}
            )

            expected_fields = ["username", "email", "firstName", "lastName"]
            Assertions.assert_json_has_keys(response, expected_fields)


    # Проверка, что нет доступа к чужим данным
    @allure.description("This test tries to get user1 with user2 tokens")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_user_details_foreign_user(self):
        # LOGIN WITH USER1
        with allure.step("It registers the user1"):
            data = {
                'email': 'vinkotov@example.com',
                'password': '1234'
            }

            response = MyRequests.post("/user/login", data=data)

            auth_sid = self.get_cookie(response, "auth_sid")
            token = self.get_header(response, "x-csrf-token")
            user_id_from_auth_method = self.get_json_value(response, "user_id")

        # REGISTER USER2
        with allure.step("It registers the user2"):
            register_data = self.prepare_registration_data()

            response = MyRequests.post("/user", data=register_data)

            Assertions.assert_code_status(response, 200)
            Assertions.assert_json_has_key(response, "id")
            user_id = self.get_json_value(response, "id")

        # GET INFO USER2 WITH TOKENS USER1
        with allure.step("It tries to get user2 under the user1 and checks that only one field is returned"):
            response = MyRequests.get(
                f"/user/{user_id}",
                headers={"x-csrf-token": token},
                cookies={"auth_sid": auth_sid}
            )

            Assertions.assert_json_has_key(response, "username")
            Assertions.assert_json_has_not_key(response, "email")
            Assertions.assert_json_has_not_key(response, "firstName")
            Assertions.assert_json_has_not_key(response, "lastName")
