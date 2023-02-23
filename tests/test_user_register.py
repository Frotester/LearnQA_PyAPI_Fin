import requests
from Lesson_4.lib.base_case import BaseCase
from Lesson_4.lib.assertions import Assertions
from datetime import datetime
from Lesson_4.lib.my_requests import MyRequests
import pytest

class TestUserRegister(BaseCase):

    def test_user_create_successfully(self):
        data = self.prepare_registration_data()

        response = MyRequests.post("/user", data=data)

        Assertions.assert_code_status(response, 200)
        Assertions.assert_json_has_key(response, "id")

    def test_create_user_with_existing_email(self):
        email = 'vinkotov@example.com'
        data = self.prepare_registration_data(email)

        response = MyRequests.post("/user", data=data)

        Assertions.assert_code_status(response, 400)
        assert response.content.decode("utf-8") == f"Users with email '{email}' already exists", f"Unexpected response content {response.content}"

    def test_create_user_with_incorrect_email(self):
        email = 'vinkotovexample.com'
        data = self.prepare_registration_data(email)

        response = MyRequests.post("/user", data=data)

        Assertions.assert_code_status(response, 400)
        assert response.content.decode("utf-8") == f"Invalid email format", f"Unexpected response content {response.content}"

    datas = [
        ({
            # 'password': '123',
            'username': 'learnqa',
            'firstName': 'learnqa',
            'lastName': 'learnqa',
            'email': 'vinkotov@example.com'
        }, 'password'),
        ({
            'password': '123',
            # 'username': 'learnqa',
            'firstName': 'learnqa',
            'lastName': 'learnqa',
            'email': 'vinkotov@example.com'
        }, 'username'),
        ({
            'password': '123',
            'username': 'learnqa',
            # 'firstName': 'learnqa',
            'lastName': 'learnqa',
            'email': 'vinkotov@example.com'
        }, 'firstName'),
        ({
            'password': '123',
            'username': 'learnqa',
            'firstName': 'learnqa',
            # 'lastName': 'learnqa',
            'email': 'vinkotov@example.com'
        }, 'lastName'),
        ({
            'password': '123',
            'username': 'learnqa',
            'firstName': 'learnqa',
            'lastName': 'learnqa',
            # 'email': 'vinkotov@example.com'
        }, 'email')
    ]
    @pytest.mark.parametrize('data', datas)
    def test_create_user_without_some_field(self, data):
        response = MyRequests.post("/user", data=data[0])

        Assertions.assert_code_status(response, 400)
        assert response.content.decode("utf-8") == f"The following required params are missed: {data[1]}", f"Unexpected response content {response.content}"


    def test_create_user_with_too_short_name(self):
        data = self.prepare_registration_data()
        data['username'] = "T"

        response = MyRequests.post("/user", data=data)

        Assertions.assert_code_status(response, 400)
        assert response.content.decode("utf-8") == f"The value of 'username' field is too short", f"Unexpected response content {response.content}"

    def test_create_user_with_too_long_name(self):
        data = self.prepare_registration_data()
        data['username'] = "T"*251

        response = MyRequests.post("/user", data=data)

        Assertions.assert_code_status(response, 400)
        assert response.content.decode("utf-8") == f"The value of 'username' field is too long", f"Unexpected response content {response.content}"
