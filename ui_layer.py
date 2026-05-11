import streamlit as st
import time
from pathlib import Path
from data_layer import save_data
import service_layer as service

Inventory_Path = Path("Iventory.json")
Sales_path = Path("sales.json")
Users_path = Path("users.json")

def render_sidebar():
    with st.sidebar:
        st.title("Shop Portal")
        st.divider()

        if st.session_state["logged_in"] == True:
            user = st.session_state["user"]
            st.markdown("**User:** " + user.username)
            st.markdown("**Role:** " + user.role)
            st.divider()

inventory = st.session_state["inventory"]
total_units = 0

for item in inventory:
    total_units = total_units + item["stock"]

st.metric("Total Products", len(inventory))
st.metric("Total Units", total_units)

low_items = service.get_low_stock_items(inventory)
if len(low_items) > 0:
    st.warning(str(len(low_items)) + " item(s) low on stock")
else:
    st.success("Stock levels OK")

st.divider()

if st.button("Log Out", use_container_width=True, key="logout_btn"):
    st.session_state["logged_in"] = False
    st.session_state["user"] = None
    st.session_state["role"] = None
    st.session_state["page"] = "login"
    st.session_state["messages"] = [{"role": "assistant", "content": "Hi! How can I help you today?"}]
    st.rerun()
else:
    st.caption("Please log in to continue.")

st.divider()
st.caption("Shop Inventory Portal v2")


def render_login_page():
    users = st.session_state["users"]

    st.title("Shop Inventory Portal")
    st.markdown("Log in or register to continue.")
    st.divider()

    with st.container(border=True):
        st.markdown("**Test Accounts**")
        st.caption("Owner: owner / owner123")
        st.caption("Employee: employee / employee123")

    st.divider()

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.subheader("Login")
        with st.container(border=True):
            login_username = st.text_input("Username", key="login_username")
            login_password = st.text_input("Password", type="password", key="login_password")
            login_btn = st.button("Log In", type="primary", use_container_width=True, key="login_btn")

        if login_btn:
            if login_username == "" or login_password == "":
                st.warning("Please enter both username and password.")
            else:
                user_obj = service.find_user(users, login_username, login_password)
                if user_obj:
                    with st.spinner("Logging in..."):
                        st.session_state["logged_in"] = True
                        st.session_state["user"] = user_obj
                        st.session_state["role"] = user_obj.role
                        st.session_state["page"] = "home"
                        time.sleep(1)
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

    with tab2:
        st.subheader("Register")
        with st.container(border=True):
            reg_username = st.text_input("Choose a Username", key="reg_username")
            reg_password = st.text_input("Choose a Password", type="password", key="reg_password")
            reg_confirm = st.text_input("Confirm Password", type="password", key="reg_confirm")
            st.markdown("**Role:** Employee (all new accounts are employees)")
            register_btn = st.button("Create Account", type="primary", use_container_width=True, key="register_btn")

        if register_btn:
            new_user, message = service.register_user(users, reg_username, reg_password, reg_confirm)
            if new_user:
                save_data(Users_path, users)
                st.success(message)
            else:
                st.error(message)

