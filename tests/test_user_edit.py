import requests
from Lesson_4.lib.base_case import BaseCase
from Lesson_4.lib.assertions import Assertions
from Lesson_4.lib.my_requests import MyRequests

class TestUserEdit(BaseCase):
    def test_edit_just_created_user(self):
        # REGISTER
        register_data = self.prepare_registration_data()
        response1 = MyRequests.post("/user", data=register_data)

        Assertions.assert_code_status(response1, 200)
        Assertions.assert_json_has_key(response1, "id")

        email = register_data['email']
        first_name = register_data['firstName']
        password = register_data['password']
        user_id = self.get_json_value(response1, "id")

        # LOGIN
        login_data = {
            'email': email,
            'password': password
        }
        response2 = MyRequests.post("/user/login", data=login_data)

        auth_sid = self.get_cookie(response2, "auth_sid")
        token = self.get_header(response2, "x-csrf-token")

        # EDIT
        new_name = "Changed Name"

        response3 = MyRequests.put(
            f"/user/{user_id}",
            headers={"x-csrf-token": token},
            cookies={"auth_sid": auth_sid},
            data={"firstName": new_name}
        )
        Assertions.assert_code_status(response3, 200)

        # GET
        response4 = MyRequests.get(
            f"/user/{user_id}",
            headers={"x-csrf-token": token},
            cookies={"auth_sid": auth_sid},
        )

        Assertions.assert_json_value_by_name(
            response4,
            "firstName",
            new_name,
            "Wrong name of the user after edit"
        )

    def test_edit_negative_without_auth(self):
        # REGISTER
        register_data = self.prepare_registration_data()
        response1 = MyRequests.post("/user", data=register_data)

        Assertions.assert_code_status(response1, 200)
        Assertions.assert_json_has_key(response1, "id")

        user_id = self.get_json_value(response1, "id")

        # EDIT
        new_name = "Changed Name"

        response2 = MyRequests.put(
            f"/user/{user_id}",
            data={"firstName": new_name}
        )

        Assertions.assert_code_status(response2, 400)
        assert response2.content.decode("utf-8") == f"Auth token not supplied", f"Unexpected response content {response2.content}"

    def test_edit_negative_foreign_user(self):
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
        register_data['firstName'] = register_data['firstName'] + '_02'

        response = MyRequests.post("/user", data=register_data)

        Assertions.assert_code_status(response, 200)
        Assertions.assert_json_has_key(response, "id")

        email2 = register_data['email']
        password2 = register_data['password']
        first_name2 = register_data['firstName']
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

        # EDIT USER2 UNDER USER1
        new_name = "Changed Name"

        response = MyRequests.put(
            f"/user/{user_id2}",
            headers={"x-csrf-token": token1},
            cookies={"auth_sid": auth_sid1},
            data={"firstName": new_name}
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
            "firstName",
            first_name2,
            "Wrong name of the user after edit"
        )

    def test_edit_negative_incorrect_email(self):
        # REGISTER
        register_data = self.prepare_registration_data()
        response = MyRequests.post("/user", data=register_data)

        Assertions.assert_code_status(response, 200)
        Assertions.assert_json_has_key(response, "id")

        email = register_data['email']
        first_name = register_data['firstName']
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

        # EDIT
        new_email = "vinkotovexample.com"

        response = MyRequests.put(
            f"/user/{user_id}",
            headers={"x-csrf-token": token},
            cookies={"auth_sid": auth_sid},
            data={"email": new_email}
        )

        Assertions.assert_code_status(response, 400)
        assert response.content.decode("utf-8") == f"Invalid email format", f"Unexpected response content {response.content}"

    def test_edit_just_created_user_with_too_short_name(self):
        # REGISTER
        register_data = self.prepare_registration_data()
        response = MyRequests.post("/user", data=register_data)

        Assertions.assert_code_status(response, 200)
        Assertions.assert_json_has_key(response, "id")

        email = register_data['email']
        first_name = register_data['firstName']
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

        # EDIT
        new_name = "T"

        response = MyRequests.put(
            f"/user/{user_id}",
            headers={"x-csrf-token": token},
            cookies={"auth_sid": auth_sid},
            data={"firstName": new_name}
        )

        Assertions.assert_code_status(response, 400)
        assert response.content.decode("utf-8") == '{"error":"Too short value for field firstName"}', f"Unexpected response content {response.content}"
