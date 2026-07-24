import sys
sys.path.append("database")
from database.db_utils import init_db, create_user, verify_user

init_db()
print("Database initialized ✅")

success = create_user("testuser", "test@example.com", "mypassword123")
print("User created:", success)

result = verify_user("testuser", "mypassword123")
print("Login with correct password:", result is not None)

result_wrong = verify_user("testuser", "wrongpassword")
print("Login with wrong password:", result_wrong is not None)