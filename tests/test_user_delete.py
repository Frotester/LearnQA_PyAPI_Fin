import requests
import pytest
from Lesson_4.lib.base_case import BaseCase
from Lesson_4.lib.assertions import Assertions
from Lesson_4.lib.my_requests import MyRequests
import allure

class TestUserDelete(BaseCase):

    def test_delete_negative_user_2(self):
        data = {
            'email': 'vinkotov@example.com',
            'password': '1234'
        }

        response = MyRequests.post("/user/login", data=data)

        auth_sid = self.get_cookie(response, "auth_sid")
        token = self.get_header(response, "x-csrf-token")
        user_id_2 = self.get_json_value(response, "user_id")

        response = MyRequests.delete(
            f"/user/{user_id_2}",
            headers={"x-csrf-token": token},
            cookies={"auth_sid": auth_sid},
        )

        Assertions.assert_code_status(response, 400)
        assert response.content.decode("utf-8") == f"Please, do not delete test users with ID 1, 2, 3, 4 or 5.", f"Unexpected response content {response.content}"

    def test_delete_just_created_user(self):
        # REGISTER
        register_data = self.prepare_registration_data()
        response = MyRequests.post("/user", data=register_data)

        Assertions.assert_code_status(response, 200)
        Assertions.assert_json_has_key(response, "id")

        email = register_data['email']
        password = register_data['password']
        user_id = self.get_json_value(response, "id")

        # LOGIN
        login_data = {
            'email': email,
            'password': password
        }
        response = MyRequests.post("/user/login", data=login_data)

        auth_sid = self.get_cookie(response, "auth_sid")
        token = self.get_header(response, "x-csrf-token")

        # DELETE
        response = MyRequests.delete(
            f"/user/{user_id}",
            headers={"x-csrf-token": token},
            cookies={"auth_sid": auth_sid},
        )
        Assertions.assert_code_status(response, 200)

        # GET
        response = MyRequests.get(
            f"/user/{user_id}",
            headers={"x-csrf-token": token},
            cookies={"auth_sid": auth_sid},
        )

        Assertions.assert_code_status(response, 404)
        Assertions.assert_content(response, "User not found")

    def test_delete_negative_foreign_user(self):
        # REGISTER USER1
        register_data = self.prepare_registration_data()
        response = MyRequests.post("/user", data=register_data)

        Assertions.assert_code_status(response, 200)
        Assertions.assert_json_has_key(response, "id")

        email1 = register_data['email']
        password1 = register_data['password']
        user_id1 = self.get_json_value(response, "id")

        # REGISTER USER2
        register_data = self.prepare_registration_data()
        register_data['email'] = register_data['email'].replace("@", "_02@")

        response = MyRequests.post("/user", data=register_data)

        Assertions.assert_code_status(response, 200)
        Assertions.assert_json_has_key(response, "id")

        email2 = register_data['email']
        password2 = register_data['password']
        user_id2 = self.get_json_value(response, "id")

        # LOGIN WITH USER1
        login_data = {
            'email': email1,
            'password': password1
        }
        response = MyRequests.post("/user/login", data=login_data)

        auth_sid1 = self.get_cookie(response, "auth_sid")
        token1 = self.get_header(response, "x-csrf-token")

        # LOGIN WITH USER2
        login_data = {
            'email': email2,
            'password': password2
        }
        response = MyRequests.post("/user/login", data=login_data)

        auth_sid2 = self.get_cookie(response, "auth_sid")
        token2 = self.get_header(response, "x-csrf-token")

        # DELETE USER2 UNDER USER1

        response = MyRequests.delete(
            f"/user/{user_id2}",
            headers={"x-csrf-token": token1},
            cookies={"auth_sid": auth_sid1},
        )

        Assertions.assert_code_status(response, 200)

        # GET
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
