#!/usr/bin/env python3
import json
import os
import sys

def print_menu():
    print("🔐 Admin Credentials Manager")
    print("=" * 40)
    print("1. Change Admin Email")
    print("2. Change Admin Password") 
    print("3. Change Both Email and Password")
    print("4. Show Current Credentials")
    print("5. Reset to Default")
    print("6. Exit")
    print("=" * 40)

def load_config():
    """Load admin configuration"""
    config_file = 'admin_config.json' if os.path.exists('admin_config.json') else None
    app_file = 'app.py'
    
    config = {}
    
    # Try to load from config file first
    if config_file:
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
        except:
            pass
    
    # Fallback to reading from app.py
    if not config and os.path.exists(app_file):
        with open(app_file, 'r') as f:
            content = f.read()
            # Extract email and password from app.py
            import re
            email_match = re.search(r"email == '([^']+)'", content)
            password_match = re.search(r"password == '([^']+)'", content)
            
            if email_match and password_match:
                config = {
                    'admin_email': email_match.group(1),
                    'admin_password': password_match.group(1)
                }
    
    return config or {'admin_email': 'admin@techshop.com', 'admin_password': 'admin123'}

def save_config(config):
    """Save configuration to file"""
    with open('admin_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    # Also update app.py if it exists
    if os.path.exists('app.py'):
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Update the credentials in app.py
        content = content.replace(
            f"email == '{load_config()['admin_email']}'", 
            f"email == '{config['admin_email']}'"
        )
        content = content.replace(
            f"password == '{load_config()['admin_password']}'", 
            f"password == '{config['admin_password']}'"
        )
        
        with open('app.py', 'w') as f:
            f.write(content)

def change_email():
    config = load_config()
    print(f"Current email: {config['admin_email']}")
    new_email = input("Enter new admin email: ").strip()
    
    if not new_email:
        print("❌ Email cannot be empty!")
        return
    
    config['admin_email'] = new_email
    save_config(config)
    print("✅ Admin email updated!")

def change_password():
    config = load_config()
    new_password = input("Enter new admin password: ").strip()
    
    if not new_password:
        print("❌ Password cannot be empty!")
        return
    
    config['admin_password'] = new_password
    save_config(config)
    print("✅ Admin password updated!")

def change_both():
    config = load_config()
    print(f"Current email: {config['admin_email']}")
    
    new_email = input("Enter new admin email: ").strip()
    new_password = input("Enter new admin password: ").strip()
    
    if not new_email or not new_password:
        print("❌ Both email and password are required!")
        return
    
    config['admin_email'] = new_email
    config['admin_password'] = new_password
    save_config(config)
    print("✅ Admin credentials updated!")

def show_credentials():
    config = load_config()
    print("📋 Current Admin Credentials:")
    print(f"📧 Email: {config['admin_email']}")
    print(f"🔑 Password: {config['admin_password']}")

def reset_default():
    config = {'admin_email': 'admin@techshop.com', 'admin_password': 'admin123'}
    save_config(config)
    print("✅ Reset to default credentials!")

def main():
    while True:
        print_menu()
        choice = input("Select option (1-6): ").strip()
        
        if choice == '1':
            change_email()
        elif choice == '2':
            change_password()
        elif choice == '3':
            change_both()
        elif choice == '4':
            show_credentials()
        elif choice == '5':
            reset_default()
        elif choice == '6':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice!")
        
        input("\nPress Enter to continue...")
        os.system('clear' if os.name == 'posix' else 'cls')

if __name__ == "__main__":
    main()
