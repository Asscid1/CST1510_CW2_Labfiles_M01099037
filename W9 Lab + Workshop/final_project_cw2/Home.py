import streamlit as st
from W7_lab import (
    register_user,
    login_user,
    verify_password,
    check_password_strength,
    validate_username,
    validate_password
)
import os

# Page configuration 
st.set_page_config(
    page_title="Multi-Domain Intelligence Platform",
    page_icon="🔒",
    layout="centered"
)

# Initialize session state variables
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "role" not in st.session_state:
    st.session_state.role = ""

# If already logged in, redirect to dashboard
if st.session_state.logged_in:
    st.success(f"✅ Already logged in as **{st.session_state.username}** ({st.session_state.role})")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🛡️ Cyber Incidents", use_container_width=True):
            st.switch_page("pages/1_Cyber_Incidents.py")
    with col2:
        if st.button("📊 Data Science", use_container_width=True):
            st.switch_page("pages/2_Data_Science.py")
    with col3:
        if st.button("⚙️ IT Operations", use_container_width=True):
            st.switch_page("pages/3_IT_Operations.py")
    
    st.divider()
    if st.button("🚪 Logout", type="secondary"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.rerun()
    
    st.stop()

# Header
st.title("🔒 Multi-Domain Intelligence Platform")
st.markdown("### Secure Authentication System")
st.divider()

# Create tabs for Login and Register
tab_login, tab_register = st.tabs(["🔑 Login", "📝 Register"])

# ==================== LOGIN TAB ====================
with tab_login:
    st.subheader("Login to Your Account")
    
    with st.form("login_form"):
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")
        submit_login = st.form_submit_button("🔓 Log In", type="primary", use_container_width=True)
        
        if submit_login:
            if not login_username or not login_password:
                st.error("⚠️ Please fill in all fields")
            else:
                # Read user.txt file to get user data
                if not os.path.exists("user.txt"):
                    st.error("❌ No users registered yet")
                else:
                    user_found = False
                    with open("user.txt", 'r') as f:
                        for line in f:
                            parts = line.strip().split(',')
                            stored_username = parts[0]
                            stored_hash = parts[1]
                            role = parts[2] if len(parts) > 2 else "user"
                            
                            if stored_username == login_username:
                                user_found = True
                                if verify_password(login_password, stored_hash):
                                    # Successful login
                                    st.session_state.logged_in = True
                                    st.session_state.username = login_username
                                    st.session_state.role = role
                                    st.success(f"✅ Welcome back, {login_username}!")
                                    st.rerun()
                                else:
                                    st.error("❌ Invalid password")
                                break
                    
                    if not user_found:
                        st.error("❌ Username not found")

# ==================== REGISTER TAB ====================
with tab_register:
    st.subheader("Create New Account")
    
    with st.form("register_form"):
        new_username = st.text_input("Choose Username", key="register_username")
        new_password = st.text_input("Choose Password", type="password", key="register_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="register_confirm")
        
        # Role selection
        role = st.selectbox(
            "Select Role",
            ["user", "admin", "analyst"],
            help="Choose your role in the system"
        )
        
        submit_register = st.form_submit_button("📝 Create Account", type="primary", use_container_width=True)
        
        if submit_register:
            # Validation checks
            if not new_username or not new_password or not confirm_password:
                st.error("⚠️ Please fill in all fields")
            
            elif new_password != confirm_password:
                st.error("❌ Passwords do not match")
            
            else:
                # Validate username
                is_valid, error_msg = validate_username(new_username)
                if not is_valid:
                    st.error(f"❌ {error_msg}")
                
                else:
                    # Validate password
                    is_valid, error_msg = validate_password(new_password)
                    if not is_valid:
                        st.error(f"❌ {error_msg}")
                    
                    else:
                        # Check password strength
                        strength = check_password_strength(new_password)
                        
                        if strength == "Weak":
                            st.error("❌ Password too weak. Please choose a stronger password.")
                            st.info("💡 Use at least 8 characters with uppercase, lowercase, and numbers")
                        
                        elif user_exists(new_username):
                            st.error(f"❌ Username '{new_username}' already exists")
                        
                        else:
                            # Register the user
                            if register_user(new_username, new_password, role):
                                st.success(f"✅ Account created successfully! Role: {role}")
                                st.info("👉 Switch to the Login tab to sign in")

# Footer
st.divider()
st.caption("🔐 Secure authentication powered by bcrypt | CST1510 Coursework 2")