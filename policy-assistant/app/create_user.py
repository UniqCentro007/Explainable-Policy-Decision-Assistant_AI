from app.database import SessionLocal, User, init_db


def create_authorized_user(
    username: str, password: str, full_name: str, role: str = "employee"
) -> None:
    """Create an authorized user with a hashed password."""
    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            print(f"⚠️ User '{username}' already exists.")
            return

        new_user = User(
            username=username,
            password=password,
            full_name=full_name,
            role=role,
        )

        db.add(new_user)
        db.commit()
        print(f"✅ User '{username}' ({full_name}) successfully authorized as {role}.")

    except Exception as exc:  # noqa: BLE001
        db.rollback()
        print(f"❌ Error creating user: {exc}")
    finally:
        db.close()


if __name__ == "__main__":
    init_db()

    create_authorized_user(
        username="MAGESH_ADMIN",
        password="securepassword123",
        full_name="Magesh Mahalingam",
        role="manager",
    )

    create_authorized_user(
        username="KAYU_DEV",
        password="user123",
        full_name="Kayathri",
        role="employee",
    )