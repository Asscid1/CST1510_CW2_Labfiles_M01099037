import streamlit as st
from app.services.user_service import register_user, login_user

st.set_page_config(
    page_title="Multi-Domain Intelligence Platform", page_icon="🔒", layout="centered"
)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "role" not in st.session_state:
    st.session_state.role = ""

if st.session_state.logged_in:
    st.success(
        f"✅ Already logged in as **{st.session_state.username}** ({st.session_state.role})"
    )

    st.markdown("### 📊 Select Your Dashboard")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🛡️ Cyber Incidents", use_container_width=True, type="primary"):
            st.switch_page("pages/1_Cyber_Dash.py")
    with col2:
        if st.button("📊 Data Science", use_container_width=True, type="primary"):
            st.switch_page("pages/2_Data_Science.py")
    with col3:
        if st.button("⚙️ IT Operations", use_container_width=True, type="primary"):
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
st.caption("Database-backed authentication with bcrypt encryption")
st.divider()

# Tabs for Login and Register
tab_login, tab_register = st.tabs(["🔑 Login", "📝 Register"])

# ==================== LOGIN TAB ====================
with tab_login:
    st.subheader("Login to Your Account")

    with st.form("login_form"):
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input(
            "Password", type="password", key="login_password"
        )
        submit_login = st.form_submit_button(
            "🔓 Log In", type="primary", use_container_width=True
        )

        if submit_login:
            if not login_username or not login_password:
                st.error("⚠️ Please fill in all fields")
            else:
                success, message, role = login_user(login_username, login_password)

                if success:
                    st.session_state.logged_in = True
                    st.session_state.username = login_username
                    st.session_state.role = role
                    st.success(f"✅ {message}")
                    st.rerun()
                else:
                    st.error(f"❌ {message}")

# ==================== REGISTER TAB ====================
with tab_register:
    st.subheader("Create New Account")

    with st.form("register_form"):
        new_username = st.text_input("Choose Username", key="register_username")
        new_password = st.text_input(
            "Choose Password", type="password", key="register_password"
        )
        confirm_password = st.text_input(
            "Confirm Password", type="password", key="register_confirm"
        )

        # Role selection
        role = st.selectbox(
            "Select Role",
            ["user", "admin", "analyst"],
            help="Choose your role in the system",
        )

        submit_register = st.form_submit_button(
            "📝 Create Account", type="primary", use_container_width=True
        )

        if submit_register:
            # Validation checks
            if not new_username or not new_password or not confirm_password:
                st.error("⚠️ Please fill in all fields")

            elif new_password != confirm_password:
                st.error("❌ Passwords do not match")

            elif len(new_password) < 6:
                st.error("❌ Password must be at least 6 characters long")

            elif len(new_username) < 3:
                st.error("❌ Username must be at least 3 characters long")

            else:
                # Register user in database
                success, message = register_user(new_username, new_password, role)

                if success:
                    st.success(f"✅ {message}")
                    st.info(
                        "👉 Switch to the Login tab to sign in with your new account"
                    )
                else:
                    st.error(f"❌ {message}")

# Footer
st.divider()
st.caption(
    "🔐 Secure authentication powered by bcrypt | 🗄️ Database: SQLite | CST1510 Coursework 2"
)
