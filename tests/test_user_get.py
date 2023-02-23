import requests
from Lesson_4.lib.base_case import BaseCase
from Lesson_4.lib.assertions import Assertions
from Lesson_4.lib.my_requests import MyRequests

class TestUserGet(BaseCase):
    # Проверка, что для неавторизованного пользователя возвращается только одно поле username
    def test_get_user_details_not_auth(self):
        response = MyRequests.get("/user/2")
        Assertions.assert_json_has_key(response, "username")
        Assertions.assert_json_has_not_key(response, "email")
        Assertions.assert_json_has_not_key(response, "firstName")
        Assertions.assert_json_has_not_key(response, "lastName")

    # Проверка, что для авторизованного пользователя возвращаются все поля
    def test_get_user_details_as_same_user(self):
        data = {
            'email': 'vinkotov@example.com',
            'password': '1234'
        }

        response1 = MyRequests.post("/user/login", data=data)

        auth_sid = self.get_cookie(response1, "auth_sid")
        token = self.get_header(response1, "x-csrf-token")
        user_id_from_auth_method = self.get_json_value(response1, "user_id")

        response2 = MyRequests.get(
            f"/user/{user_id_from_auth_method}",
            headers={"x-csrf-token": token},
            cookies={"auth_sid": auth_sid}
        )

        expected_fields = ["username", "email", "firstName", "lastName"]
        Assertions.assert_json_has_keys(response2, expected_fields)


    # Проверка, что нет доступа к чуим данным
    def test_get_user_details_foreign_user(self):
        # LOGIN WITH USER1
        data = {
            'email': 'vinkotov@example.com',
            'password': '1234'
        }

        response1 = MyRequests.post("/user/login", data=data)

        auth_sid = self.get_cookie(response1, "auth_sid")
        token = self.get_header(response1, "x-csrf-token")
        user_id_from_auth_method = self.get_json_value(response1, "user_id")

        # CREATE USER2
        register_data = self.prepare_registration_data()
        response2 = MyRequests.post("/user", data=register_data)

        Assertions.assert_code_status(response2, 200)
        Assertions.assert_json_has_key(response2, "id")
        user_id = self.get_json_value(response2, "id")

        # GET INFO USER2 WITH TOKENS USER1
        response3 = MyRequests.get(
            f"/user/{user_id}",
            headers={"x-csrf-token": token},
            cookies={"auth_sid": auth_sid}
        )

        Assertions.assert_json_has_key(response3, "username")
        Assertions.assert_json_has_not_key(response3, "email")
        Assertions.assert_json_has_not_key(response3, "firstName")
        Assertions.assert_json_has_not_key(response3, "lastName")
