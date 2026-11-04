from app.services.organization_service import register_organization

organization = register_organization(
    name="Digital Forensic Laboratory",
    description="Organization for digital evidence investigation"
)

print("Organization created:")
print(organization)