#!/usr/bin/env python3
import json
import os
import hashlib

def change_admin_password():
    """Change the admin password"""
    USERS_DB = "data/users.json"
    
    if not os.path.exists(USERS_DB):
        print("❌ Users database not found. Run the app first to initialize it.")
        return
    
    with open(USERS_DB, 'r') as f:
        users = json.load(f)
    
    admin_user = None
    for user in users:
        if user.get('is_admin'):
            admin_user = user
            break
    
    if not admin_user:
        print("❌ Admin user not found in database.")
        return
    
    print("🔐 Change Admin Password")
    print("=" * 30)
    print(f"Current admin email: {admin_user['email']}")
    
    new_email = input("Enter new admin email (press Enter to keep current): ").strip()
    new_password = input("Enter new admin password: ").strip()
    
    if not new_password:
        print("❌ Password cannot be empty!")
        return
    
    # Update the credentials
    if new_email:
        admin_user['email'] = new_email
    
    admin_user['password'] = new_password
    
    with open(USERS_DB, 'w') as f:
        json.dump(users, f, indent=2)
    
    # Also update the app.py file with new credentials
    with open('app.py', 'r') as f:
        app_content = f.read()
    
    # Update the hardcoded credentials in admin_login function
    if new_email:
        app_content = app_content.replace("email == 'admin@techshop.com'", f"email == '{new_email}'")
    app_content = app_content.replace("password == 'admin123'", f"password == '{new_password}'")
    
    with open('app.py', 'w') as f:
        f.write(app_content)
    
    print("✅ Admin credentials updated successfully!")
    print(f"📧 New email: {new_email if new_email else admin_user['email']}")
    print(f"🔑 New password: {new_password}")
    print("")
    print("💡 You need to restart the Flask app for changes to take effect.")

if __name__ == "__main__":
    change_admin_password()
