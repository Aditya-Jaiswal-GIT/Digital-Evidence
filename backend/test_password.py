from app.core.security import (
    hash_password,
    verify_password
)


password = "MySecurePassword123"

# Generate password hash
hashed_password = hash_password(password)

print("Original password:", password)
print("Hashed password:", hashed_password)

# Verify correct password
result1 = verify_password(
    password,
    hashed_password
)

print("Correct password:", result1)

# Verify incorrect password
result2 = verify_password(
    "WrongPassword123",
    hashed_password
)

print("Incorrect password:", result2)