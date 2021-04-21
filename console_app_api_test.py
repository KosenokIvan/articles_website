from requests import get, post, put, delete, Session
from tools.image_to_byte_array import image_to_byte_array

WEB_ADDRESS = "http://localhost:5000/api"

SUCCESS = 0
PASSWORD_MISMATCH = 1
USER_ALREADY_EXIST = 2
EMAIL_ALREADY_USE = 3
INCORRECT_NICKNAME_LENGTH = 4
NICKNAME_CONTAINS_INVALID_CHARACTERS = 5
INCORRECT_PASSWORD_LENGTH = 6
NOT_SECURE_PASSWORD = 7
INCORRECT_EMAIL_OR_PASSWORD = 8
UNAUTHORIZED = 9
USER_NOT_FOUND = 10
PARAMETER_NOT_SPECIFIED = 11
FORBIDDEN = 12


class HttpWorker:
    def __init__(self):
        self.session = Session()

    def register_(self, name, surname, nickname, email,
                  password, password_again, description, avatar_filename=None):
        user_data = {
            "name": name,
            "surname": surname,
            "nickname": nickname,
            "email": email,
            "password": password,
            "password_again": password_again,
            "description": description
        }
        if avatar_filename is not None:
            user_data["avatar"] = image_to_byte_array(avatar_filename).hex()
        response = self.session.post(f"{WEB_ADDRESS}/users", json=user_data)
        if response:
            return SUCCESS
        message = response.json()["message"]
        if message == "Password mismatch":
            return PASSWORD_MISMATCH
        if message.startswith("User @"):
            return USER_ALREADY_EXIST
        if message.startswith("Email"):
            return EMAIL_ALREADY_USE
        if message.startswith("Length of the nickname"):
            return INCORRECT_NICKNAME_LENGTH
        if message.startswith("Nickname"):
            return NICKNAME_CONTAINS_INVALID_CHARACTERS
        if message.startswith("Length of password"):
            return INCORRECT_PASSWORD_LENGTH
        if message.startswith("Password"):
            return NOT_SECURE_PASSWORD
        raise ValueError(f"Unknown message: {message}")

    def login_(self, email, password, remember_me=False):
        user_data = {
            "email": email,
            "password": password,
            "remember_me": remember_me
        }
        response = self.session.post(f"{WEB_ADDRESS}/login", json=user_data)
        if response:
            return SUCCESS
        return INCORRECT_EMAIL_OR_PASSWORD

    def logout_(self):
        response = self.session.post(f"{WEB_ADDRESS}/logout")
        if response:
            return SUCCESS
        return UNAUTHORIZED

    def get_user_(self, user_id, fields):
        response = self.session.get(f"{WEB_ADDRESS}/user/{user_id}", params={"get_field": fields})
        if response:
            return response.json(), SUCCESS
        if response.status_code == 404:
            return response.json(), USER_NOT_FOUND
        return response.json(), PARAMETER_NOT_SPECIFIED

    def delete_user_(self, user_id, password):
        response = self.session.delete(f"{WEB_ADDRESS}/user/{user_id}", json={"password": password})
        if response:
            del self.session.cookies["session"]
            return SUCCESS
        if response.status_code == 404:
            return USER_NOT_FOUND
        if response.status_code == 403:
            return FORBIDDEN
        return INCORRECT_EMAIL_OR_PASSWORD


class TestApiApp(HttpWorker):
    def __init__(self):
        super().__init__()
        self.run = True

    @staticmethod
    def print_sep():
        print("-" * 30, end="\n\n")

    @staticmethod
    def check_arguments_count(count, min_req_count=None, max_req_count=None):
        if min_req_count is not None and count < min_req_count:
            print(f"Few parameters: {count} < {min_req_count}")
            TestApiApp.print_sep()
            return False
        if max_req_count is not None and count > max_req_count:
            print(f"Many parameters: {count} > {max_req_count}")
            TestApiApp.print_sep()
            return False
        return True

    def main(self):
        while self.run:
            print("Commands:")
            print("\tRegistration: register <name> <surname> <nickname> <email> "
                  "<password> <password_again> <description> [avatar_filename]")
            print("\tLogin: login <email> <password>")
            if self.session.cookies.get("session"):
                print("\tLogout: logout")
                print("\tDelete account: delete <user_id> <password>")
            print("\tGet user: get_user <user_id> [*get_fields choices=['id', 'name', 'surname',"
                  " 'nickname', 'email', 'description', 'avatar', 'modified_date']"
                  " default=['id', 'nickname']]")
            print("\tClose program: exit")
            command, *args = input("~ ").split()
            if command == "register":
                if TestApiApp.check_arguments_count(len(args), 7, 8):
                    self.register(*args)
            elif command == "login":
                if TestApiApp.check_arguments_count(len(args), 2, 2):
                    self.login(*args)
            elif command == "logout":
                if TestApiApp.check_arguments_count(len(args), 0, 0):
                    self.logout()
            elif command == "delete":
                if TestApiApp.check_arguments_count(len(args), 2, 2):
                    self.delete_user(*args)
            elif command == "get_user":
                if TestApiApp.check_arguments_count(len(args), 1, 9):
                    if len(args) <= 1:
                        args = (args[0], "id", "nickname")
                    self.get_user(*args)
            elif command == "exit":
                if TestApiApp.check_arguments_count(len(args), 0, 0):
                    self.run = False
            else:
                print("Unknown command")

    def register(self, *args):
        result = self.register_(*args)
        if result == SUCCESS:
            print("Success")
        elif result == PASSWORD_MISMATCH:
            print("Password mismatch")
        elif result == USER_ALREADY_EXIST:
            print("User already exist")
        elif result == EMAIL_ALREADY_USE:
            print("Email already use")
        elif result == INCORRECT_NICKNAME_LENGTH:
            print("Incorrect nickname length")
        elif result == NICKNAME_CONTAINS_INVALID_CHARACTERS:
            print("Nickname contains invalid characters")
        elif result == INCORRECT_PASSWORD_LENGTH:
            print("Incorrect password length")
        elif result == NOT_SECURE_PASSWORD:
            print("Passwords contains white-spaces characters only")
        TestApiApp.print_sep()

    def login(self, *args):
        result = self.login_(*args)
        if result == SUCCESS:
            print("Success")
        elif result == INCORRECT_EMAIL_OR_PASSWORD:
            print("Incorrect email or password")
        TestApiApp.print_sep()

    def logout(self):
        result = self.logout_()
        if result == SUCCESS:
            print("Success")
        elif result == UNAUTHORIZED:
            print("Unauthorized")
        TestApiApp.print_sep()

    def get_user(self, *args):
        result, code = self.get_user_(args[0], args[1:])
        if code == SUCCESS:
            for key in result["user"]:
                print(f"{key}: {result['user'][key]}")
        elif code == USER_NOT_FOUND:
            print("User not found")
        elif code == PARAMETER_NOT_SPECIFIED:
            for key in result["message"]:
                print(f"{key}: {result['message'][key]}")
        TestApiApp.print_sep()

    def delete_user(self, *args):
        result = self.delete_user_(*args)
        if result == SUCCESS:
            print("Success")
        elif result == USER_NOT_FOUND:
            print("User not found")
        elif result == INCORRECT_EMAIL_OR_PASSWORD:
            print("Incorrect password")
        elif result == FORBIDDEN:
            print("Forbidden")
        TestApiApp.print_sep()


if __name__ == '__main__':
    TestApiApp().main()
