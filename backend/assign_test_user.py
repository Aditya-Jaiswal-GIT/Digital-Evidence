from app.models.user_model import assign_user_to_organization

ORGANIZATION_ID = '6aeb252e9870ceefdcb482c6'

USER_IDS = [
    
    "6ae9ab14c3735847b99be227"
    
]

for user_id in USER_IDS:
    result = assign_user_to_organization(
        user_id=user_id,
        organization_id=ORGANIZATION_ID
    )

    if result:
        print("Assigned:", result["email"])
    else:
        print("Could not assign user:", user_id)