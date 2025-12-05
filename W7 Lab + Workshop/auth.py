import bcrypt
import os

USER_DATA_FILE = "user.txt"

def hash_password(plain_text_password):
    # Encode to bytes
    password_bytes = plain_text_password.encode('utf-8')
    # Generate salt
    salt = bcrypt.gensalt()
    # Hash password
    hashed = bcrypt.hashpw(password_bytes, salt)
    # Decode back to string for storage
    return hashed.decode('utf-8')

def verify_password(plain_text_password, hashed_password):
    # Encode both
    password_bytes = plain_text_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    # bcrypt handles salt internally
    return bcrypt.checkpw(password_bytes, hashed_bytes)

def user_exists(username):
    if not os.path.exists(USER_DATA_FILE):
        return False
    with open(USER_DATA_FILE, 'r') as f:
        for line in f:
            stored_username, _ = line.strip().split(',')
            if stored_username == username:
                return True
    return False

def register_user(username, password, role='user'):
    if user_exists(username):
        print(f"Error: Username '{username}' already exists.")
        return False
    hashed = hash_password(password)
    with open(USER_DATA_FILE, 'a') as f:
        f.write(f"{username},{hashed},{role}\n")
    print(f"Success: User '{username}' registered with role '{role}'!")
    return True

def login_user(username, password):
    if not os.path.exists(USER_DATA_FILE):
        print("Error: No users registered yet.")
        return False
    with open(USER_DATA_FILE, 'r') as f:
        for line in f:
            parts = line.strip().split(',')
            stored_username = parts[0]
            stored_hash = parts[1]
            role = parts[2] if len(parts) > 2 else "user"
            if stored_username == username:
                if verify_password(password, stored_hash):
                    print(f"Success: Welcome, {username}! Your role is '{role}'.")
                    return True
                else:
                    print("Error: Invalid password.")
                    return False
    print("Error: Username not found.")
    return False

import re

def check_password_strength(password):
    length = len(password)
    has_upper = bool(re.search(r'[A-Z]', password))
    has_lower = bool(re.search(r'[a-z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
    common_patterns = ['123456', 'password', 'qwerty', 'letmein']

    if any(p in password.lower() for p in common_patterns):
        return "Weak"
    if length >= 12 and has_upper and has_lower and has_digit and has_special:
        return "Strong"
    if length >= 8 and (has_upper or has_lower) and has_digit:
        return "Medium"
    return "Weak"

def validate_username(username):
    if not (3 <= len(username) <= 20) or not username.isalnum():
        return False, "Username must be 3-20 alphanumeric characters."
    return True, ""

def validate_password(password):
    if not (6 <= len(password) <= 50):
        return False, "Password must be 6-50 characters."
    return True, ""



def display_menu():
    print("\n" + "="*50)
    print(" MULTI-DOMAIN INTELLIGENCE PLATFORM")
    print(" Secure Authentication System")
    print("="*50)
    print("\n [1] Register a new user")
    print("[2] Login")
    print("[3] Exit")
    print("-"*50)

def main():
    print("\nWelcome to the Week 7 Authentication System!")
    while True:
        display_menu()
        choice = input("\nPlease select an option (1-3): ").strip()
        if choice == '1':
            # Registration flow

            username = input("Enter a username: ").strip()
            is_valid, error_msg = validate_username(username)
            if not is_valid:
                print(f"Error: {error_msg}")
                continue
            password = input("Enter a password: ").strip()
            is_valid, error_msg = validate_password(password)
            if not is_valid:
                print(f"Error: {error_msg}")
                continue
            password_confirm = input("Confirm password: ").strip()
            if password != password_confirm:
                print("Error: Passwords do not match.")
                continue
            strength = check_password_strength(password)
            print(f"Password strength: {strength}")
            
            # blocking weak passwords completely

            if strength == "Weak":
                print("Error: Password too weak. Please choose a stronger password.")
                continue

            # User Role selection
            
            role = input("Enter role (user/admin/analyst): ").strip().lower()
   
            register_user(username, password, role)
        elif choice == '2':
            # Login flow
            username = input("Enter your username: ").strip()
            password = input("Enter your password: ").strip()
            login_user(username, password)
        elif choice == '3':
            print("\nThank you for using the authentication system.")
            break
        else:
            print("\nError: Invalid option. Please select 1, 2, or 3.")

if __name__ == "__main__":
    main()