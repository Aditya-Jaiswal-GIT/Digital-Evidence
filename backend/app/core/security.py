from pwdlib import PasswordHash  # type: ignore[import-not-found]


# Create password hashing configuration
password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """
    Convert plain-text password into Argon2id hash.
    """

    return password_hasher.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    """
    Verify plain-text password against stored hash.
    """

    return password_hasher.verify(
        plain_password,
        hashed_password
    )