from app.models.user_model import (
    list_users,
    update_user_profile,
    update_user_role,
    update_user_status
)

# 1. List users
result = list_users(page=1, page_size=5)
print("USER LIST:", result)

# Replace with an actual user ObjectId from your database
user_id = "YOUR_USER_OBJECT_ID"

# 2. Update profile
profile = update_user_profile(
    user_id,
    {"full_name": "Updated Test User"}
)
print("PROFILE:", profile)

# 3. Update role
role = update_user_role(user_id, "reviewer")
print("ROLE:", role)

# 4. Deactivate user
status = update_user_status(user_id, False)
print("STATUS:", status)