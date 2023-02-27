import requests
from lib.base_case import BaseCase
from lib.assertions import Assertions
from lib.my_requests import MyRequests
import allure

#  Для генерации allure-отчета
#  python -m pytest --alluredir=test_results tests/test_user_edit.py
#  allure serve test_results/


# Для запуска теста из командной строки:
# python -m pytest -s tests/test_user_edit.py

@allure.epic("User edit cases")
class TestUserEdit(BaseCase):
    @allure.description("This test edits a newly created user")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_edit_just_created_user(self):
        # REGISTER
        with allure.step("It registers the user"):
            register_data = self.prepare_registration_data()
            response = MyRequests.post("/user", data=register_data)

            Assertions.assert_code_status(response, 200)
            Assertions.assert_json_has_key(response, "id")

            email = register_data['email']
            first_name = register_data['firstName']
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

        # EDIT
        with allure.step("It edits the newly created user"):
            new_name = "Changed Name"

            response = MyRequests.put(
                f"/user/{user_id}",
                headers={"x-csrf-token": token},
                cookies={"auth_sid": auth_sid},
                data={"firstName": new_name}
            )
            Assertions.assert_code_status(response, 200)

        # GET
        with allure.step("It checks that user data has been edited"):
            response = MyRequests.get(
                f"/user/{user_id}",
                headers={"x-csrf-token": token},
                cookies={"auth_sid": auth_sid},
            )

            Assertions.assert_json_value_by_name(
                response,
                "firstName",
                new_name,
                "Wrong name of the user after edit"
            )

    @allure.description("This test tries to edit a user without authorization")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_edit_negative_without_auth(self):
        # REGISTER
        with allure.step("It registers the user"):
            register_data = self.prepare_registration_data()
            response = MyRequests.post("/user", data=register_data)

            Assertions.assert_code_status(response, 200)
            Assertions.assert_json_has_key(response, "id")

            user_id = self.get_json_value(response, "id")

        # EDIT
        with allure.step("It tries to edit the user without registration and checks for errors"):
            new_name = "Changed Name"

            response = MyRequests.put(
                f"/user/{user_id}",
                data={"firstName": new_name}
            )

            Assertions.assert_code_status(response, 400)
            Assertions.assert_content(response, "Auth token not supplied")

    @allure.description("This test tries to edit user1 with user2 tokens")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_edit_negative_foreign_user(self):
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
        with allure.step("It registers the user1"):
            register_data = self.prepare_registration_data()
            register_data['email'] = register_data['email'].replace("@", "_02@")
            register_data['firstName'] = register_data['firstName'] + '_02'

            response = MyRequests.post("/user", data=register_data)

            Assertions.assert_code_status(response, 200)
            Assertions.assert_json_has_key(response, "id")

            email2 = register_data['email']
            password2 = register_data['password']
            first_name2 = register_data['firstName']
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
        with allure.step("It logs in under the user1"):
            login_data = {
                'email': email2,
                'password': password2
            }
            response = MyRequests.post("/user/login", data=login_data)

            auth_sid2 = self.get_cookie(response, "auth_sid")
            token2 = self.get_header(response, "x-csrf-token")

        # EDIT USER2 UNDER USER1
        with allure.step("It tries to edit user2 under the user1"):
            new_name = "Changed Name"

            response = MyRequests.put(
                f"/user/{user_id2}",
                headers={"x-csrf-token": token1},
                cookies={"auth_sid": auth_sid1},
                data={"firstName": new_name}
            )
            Assertions.assert_code_status(response, 200)

        # GET
        with allure.step("It checks that the user has not been edited"):
            response = MyRequests.get(
                f"/user/{user_id2}",
                headers={"x-csrf-token": token2},
                cookies={"auth_sid": auth_sid2},
            )

            Assertions.assert_json_value_by_name(
                response,
                "firstName",
                first_name2,
                "Wrong name of the user after edit"
            )

    @allure.description("This test tries to edit a user with an invalid email")
    @allure.severity(allure.severity_level.MINOR)
    def test_edit_negative_invalid_email(self):
        # REGISTER
        with allure.step("It registers the user"):
            register_data = self.prepare_registration_data()
            response = MyRequests.post("/user", data=register_data)

            Assertions.assert_code_status(response, 200)
            Assertions.assert_json_has_key(response, "id")

            email = register_data['email']
            first_name = register_data['firstName']
            password = register_data['password']
            user_id = self.get_json_value(response, "id")

        # LOGIN
        with allure.step("It logs in under the user"):
            login_data = {
                'email': email,
                'password': password
            }
            response = MyRequests.post("/user/login", data=login_data)

            auth_sid = self.get_cookie(response, "auth_sid")
            token = self.get_header(response, "x-csrf-token")

        # EDIT
        with allure.step("It tries to edit with invalid email and checks for an error when trying to edit"):
            new_email = "vinkotovexample.com"

            response = MyRequests.put(
                f"/user/{user_id}",
                headers={"x-csrf-token": token},
                cookies={"auth_sid": auth_sid},
                data={"email": new_email}
            )

            Assertions.assert_code_status(response, 400)
            Assertions.assert_content(response, "Invalid email format")

    @allure.description("This test tries to edit a user with too short name")
    @allure.severity(allure.severity_level.MINOR)
    def test_edit_just_created_user_with_too_short_name(self):
        # REGISTER
        with allure.step("It registers the user"):
            register_data = self.prepare_registration_data()
            response = MyRequests.post("/user", data=register_data)

            Assertions.assert_code_status(response, 200)
            Assertions.assert_json_has_key(response, "id")

            email = register_data['email']
            first_name = register_data['firstName']
            password = register_data['password']
            user_id = self.get_json_value(response, "id")

        # LOGIN
        with allure.step("It logs in under the user"):
            login_data = {
                'email': email,
                'password': password
            }
            response = MyRequests.post("/user/login", data=login_data)

            auth_sid = self.get_cookie(response, "auth_sid")
            token = self.get_header(response, "x-csrf-token")

        # EDIT
        with allure.step("It tries to edit with too short name and checks for an error when trying to edit"):
            new_name = "T"

            response = MyRequests.put(
                f"/user/{user_id}",
                headers={"x-csrf-token": token},
                cookies={"auth_sid": auth_sid},
                data={"firstName": new_name}
            )

            Assertions.assert_code_status(response, 400)
            Assertions.assert_content(response, '{"error":"Too short value for field firstName"}')

