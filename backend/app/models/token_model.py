from datetime import datetime, timezone

from app.core.database import database


tokens_collection = database["refresh_tokens"]


def store_refresh_token(
    user_id: str,
    token_hash: str,
    expires_at: datetime
):

    tokens_collection.insert_one({

        "user_id": user_id,

        "token_hash": token_hash,

        "created_at": datetime.now(timezone.utc),

        "expires_at": expires_at,

        "revoked_at": None

    })


def consume_refresh_token(token_hash: str):

    now = datetime.now(timezone.utc)

    return tokens_collection.find_one_and_update(

        {
            "token_hash": token_hash,
            "revoked_at": None,
            "expires_at": {"$gt": now}
        },

        {
            "$set": {
                "revoked_at": now
            }
        }

    )