import bcrypt
from modules.database import Database


class UserManagement:
    def __init__(self):
        self.db = Database()

    def register_user(self, username, password, role='user'):
        if self.db.get_user(username):
            return False, "Username already exists"

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Store the hashed password as bytes
        self.db.add_user(username, hashed_password, role)
        return True, "User registered successfully"

    def authenticate_user(self, username, password):
        user = self.db.get_user(username)
        if user:
            stored_password = user[2]  # Assuming the password is at index 2

            # Ensure the input password is in bytes
            input_password = password.encode('utf-8') if isinstance(password, str) else password

            try:
                if bcrypt.checkpw(input_password, stored_password):
                    return True, user
            except Exception as e:
                print(f"Error during password check: {str(e)}")

        return False, None

    def get_user_role(self, user_id):
        user = self.db.get_user_by_id(user_id)
        return user[3] if user else None

    def change_password(self, user_id, new_password):
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        self.db.update_user_password(user_id, hashed_password)
        return True, "Password changed successfully"

    def delete_user(self, user_id):
        self.db.delete_user(user_id)
        return True, "User deleted successfully"