from app.database import SessionLocal, User, init_db

def create_authorized_user(username, password, full_name, role="employee"):
    """
    Passes the plain password to the User model, which automatically hashes 
    it before saving to the MySQL database.
    """
    db = SessionLocal()
    try:
        # 1. Check if user already exists
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            print(f"⚠️ User '{username}' already exists.")
            return

        # 2. Create the database record
        # Note: We pass the plain-text password here. The User model's 
        # @password.setter will automatically hash it securely!
        new_user = User(
            username=username,
            password=password, 
            full_name=full_name,
            role=role
        )

        db.add(new_user)
        db.commit()
        print(f"✅ User '{username}' ({full_name}) successfully authorized as {role}.")

    except Exception as e:
        print(f"❌ Error creating user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Initialize tables if they don't exist
    init_db()
    
    # --- ADD YOUR USERS HERE ---
    create_authorized_user(
        username="MAGESH_ADMIN", 
        password="securepassword123", 
        full_name="Magesh Mahalingam", 
        role="manager"
    )

    create_authorized_user(
        username="KAYU_DEV", 
        password="user123", 
        full_name="Kayathri", 
        role="employee"
    )