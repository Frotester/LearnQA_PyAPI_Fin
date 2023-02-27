import requests
import pytest
from lib.base_case import BaseCase
from lib.assertions import Assertions
from lib.my_requests import MyRequests
import allure


# Для запуска теста из командной строки:
# python -m pytest -s tests/test_user_auth.py

#  Для генерации allure-отчета
#  python -m pytest --alluredir=test_results tests/test_user_delete.py
#  allure serve test_results/


@allure.epic("User delete cases")
class TestUserDelete(BaseCase):

    @allure.description("This test tries to delete user with id 2")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_delete_negative_user_2(self):
        # LOGIN
        with allure.step("It logins under the user with id 2"):
            data = {
                'email': 'vinkotov@example.com',
                'password': '1234'
            }

            response = MyRequests.post("/user/login", data=data)

            auth_sid = self.get_cookie(response, "auth_sid")
            token = self.get_header(response, "x-csrf-token")
            user_id_2 = self.get_json_value(response, "user_id")

        with allure.step("It tries to delete the user with id 2 and checks for an error when trying to delete"):
            response = MyRequests.delete(
                f"/user/{user_id_2}",
                headers={"x-csrf-token": token},
                cookies={"auth_sid": auth_sid},
            )

            Assertions.assert_code_status(response, 400)
            Assertions.assert_content(response, "Please, do not delete test users with ID 1, 2, 3, 4 or 5.")

    @allure.description("The test removes the newly created user")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_delete_just_created_user(self):
        # REGISTER
        with allure.step("It registers the user"):
            register_data = self.prepare_registration_data()
            response = MyRequests.post("/user", data=register_data)

            Assertions.assert_code_status(response, 200)
            Assertions.assert_json_has_key(response, "id")

            email = register_data['email']
            password = register_data['password']
            user_id = self.get_json_value(response, "id")

        # LOGIN
        with allure.step("It logs in under the newly created user"):
            login_data = {
                'email': email,
                'password': password
            }
            response = MyRequests.post("/user/login", data=login_data)

            auth_sid = self.get_cookie(response, "auth_sid")
            token = self.get_header(response, "x-csrf-token")

        # DELETE
        with allure.step("It deletes the newly created user"):
            response = MyRequests.delete(
                f"/user/{user_id}",
                headers={"x-csrf-token": token},
                cookies={"auth_sid": auth_sid},
            )
            Assertions.assert_code_status(response, 200)

        # GET
        with allure.step("It checks that the user has been deleted"):
            response = MyRequests.get(
                f"/user/{user_id}",
                headers={"x-csrf-token": token},
                cookies={"auth_sid": auth_sid},
            )

            Assertions.assert_code_status(response, 404)
            Assertions.assert_content(response, "User not found")

    @allure.description("Test tries to delete user1 with user2 tokens")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_delete_negative_foreign_user(self):
        # REGISTER USER1
        with allure.step("It registers the user1"):
            register_data = self.prepare_registration_data()
            response = MyRequests.post("/user", data=register_data)

            Assertions.assert_code_status(response, 200)
            Assertions.assert_json_has_key(response, "id")

            email1 = register_data['email']
            password1 = register_data['password']
            user_id1 = self.get_json_value(response, "id")

        # REGISTER USER2
        with allure.step("It registers the user2"):
            register_data = self.prepare_registration_data()
            register_data['email'] = register_data['email'].replace("@", "_02@")

            response = MyRequests.post("/user", data=register_data)

            Assertions.assert_code_status(response, 200)
            Assertions.assert_json_has_key(response, "id")

            email2 = register_data['email']
            password2 = register_data['password']
            user_id2 = self.get_json_value(response, "id")

        # LOGIN WITH USER1
        with allure.step("It logs in under the user1"):
            login_data = {
                'email': email1,
                'password': password1
            }
            response = MyRequests.post("/user/login", data=login_data)

            auth_sid1 = self.get_cookie(response, "auth_sid")
            token1 = self.get_header(response, "x-csrf-token")

        # LOGIN WITH USER2
        with allure.step("It logs in under the user2"):
            login_data = {
                'email': email2,
                'password': password2
            }

            response = MyRequests.post("/user/login", data=login_data)

            auth_sid2 = self.get_cookie(response, "auth_sid")
            token2 = self.get_header(response, "x-csrf-token")

        # DELETE USER2 UNDER USER1
        with allure.step("It tries to delete user2 under the user1"):
            response = MyRequests.delete(
                f"/user/{user_id2}",
                headers={"x-csrf-token": token1},
                cookies={"auth_sid": auth_sid1},
            )

            Assertions.assert_code_status(response, 200)

        # GET
        with allure.step("It checks that the user has not been deleted"):
            response = MyRequests.get(
                f"/user/{user_id2}",
                headers={"x-csrf-token": token2},
                cookies={"auth_sid": auth_sid2},
            )

            Assertions.assert_json_value_by_name(
                response,
                "email",
                email2,
                "Wrong email of the user after delete"
            )
