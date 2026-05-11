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

def render_owner_home():
    inventory = st.session_state["inventory"]
    sales = st.session_state["sales"]
    user = st.session_state["user"]

    st.title("Owner Dashboard")
    st.markdown("Welcome back, " + user.username + ".")
    st.divider()

    total_units = 0
    for item in inventory:
        total_units = total_units + item["stock"]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Products", len(inventory))
    col2.metric("Total Units", total_units)
    col3.metric("Inventory Value", "$" + str(service.get_total_inventory_value(inventory)))
    col4.metric("Total Sales", len(sales))

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("### Catalog")
            st.caption("View and search all products.")
            if st.button("Open Catalog", use_container_width=True, key="go_catalog"):
                st.session_state["page"] = "catalog"
                st.rerun()

        with st.container(border=True):
            st.markdown("### Edit / Restock")
            st.caption("Update prices and stock levels.")
            if st.button("Open Editor", use_container_width=True, key="go_edit"):
                st.session_state["page"] = "edit"
                st.rerun()

    with col2:
        with st.container(border=True):
            st.markdown("### Add Product")
            st.caption("Add a new item to the catalog.")
            if st.button("Add Product", use_container_width=True, key="go_add"):
                st.session_state["page"] = "add"
                st.rerun()

        with st.container(border=True):
            st.markdown("### Remove Product")
            st.caption("Delete a product from the catalog.")
            if st.button("Remove Product", use_container_width=True, key="go_delete"):
                st.session_state["page"] = "delete"
                st.rerun()

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("### Sales Log")
            st.caption("Review all transactions.")
            if st.button("View Sales Log", use_container_width=True, key="go_sales"):
                st.session_state["page"] = "sales"
                st.rerun()

    with col2:
        with st.container(border=True):
            st.markdown("### Shop Assistant")
            st.caption("Ask the AI assistant questions.")
            if st.button("Open Assistant", use_container_width=True, key="go_ai_owner"):
                st.session_state["page"] = "assistant"
                st.rerun()


    st.divider()
    low_items = service.get_low_stock_items(inventory)
    if len(low_items) > 0:
        st.markdown("**Low Stock Alerts**")
        for item in low_items:
            st.warning(item["name"] + " - " + str(item["stock"]) + " units remaining")


def render_owner_catalog():
    inventory = st.session_state["inventory"]

    if st.button("Back", key="catalog_back"):
        st.session_state["page"] = "home"
        st.rerun()

    st.header("Product Catalog")

    search = st.text_input("Search by name", key="owner_search")

    st.divider()

    total_units = 0
    for item in inventory:
        total_units = total_units + item["stock"]

    low_items = service.get_low_stock_items(inventory)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Products", len(inventory))
    col2.metric("Total Units", total_units)
    col3.metric("Critically Low", len(low_items))
    st.divider()

    for item in inventory:
        # filter by search if something was typed
        if search != "":
            if search.lower() not in item["name"].lower():
                continue

        with st.container(border=True):
            c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 2, 2])
            c1.markdown("**" + item["name"] + "**")
            c2.markdown(item.get("category", "Other"))
            c3.markdown("$" + str(item["price"]))
            c4.markdown("Stock: " + str(item["stock"]))

            if item["stock"] == 0:
                c5.error("Out of Stock")
            elif item["stock"] < 5:
                c5.warning("Low")
            else:
                c5.success("OK")


def render_owner_add():
    inventory = st.session_state["inventory"]

    if st.button("Back", key="add_back"):
        st.session_state["page"] = "home"
        st.rerun()

    st.header("Add a New Product")

    with st.container(border=True):
        st.subheader("Product Details")

        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("Product Name", key="new_product_name")
            new_price = st.number_input("Price ($)", min_value=0.01, value=1.00, step=0.25, key="new_product_price")
        with col2:
            new_stock = st.number_input("Initial Stock", min_value=0, value=10, step=1, key="new_product_stock")
            new_category = st.selectbox("Category", ["Bread", "Pastry", "Dessert", "Beverage", "Other"], key="new_product_category")

        add_btn = st.button("Add Product", type="primary", use_container_width=True, key="add_product_btn")

    if add_btn:
        new_item, message = service.add_item(inventory, new_name, new_price, new_stock, new_category)
        if new_item:
            with st.spinner("Adding product..."):
                save_data(Inventory_Path, inventory)
                time.sleep(1)
            st.success(message)
            st.session_state["page"] = "home"
            st.rerun()
        else:
            st.error(message)


def render_owner_edit():
    inventory = st.session_state["inventory"]

    if st.button("Back", key="edit_back"):
        st.session_state["page"] = "home"
        st.rerun()

    st.header("Edit or Restock a Product")

    with st.container(border=True):
        st.subheader("Select a Product")

        edit_item = st.selectbox(
            "Choose product to edit",
            options=inventory,
            format_func=lambda x: x["name"] + " (Stock: " + str(x["stock"]) + ")",
            key="edit_item_select"
        )

        st.divider()
        st.subheader("Update Details")

        col1, col2 = st.columns(2)
        with col1:
            updated_price = st.number_input(
                "New Price ($)",
                min_value=0.01,
                value=float(edit_item["price"]),
                step=0.25,
                key="edit_price_" + str(edit_item["item_id"])
            )
            add_stock = st.number_input(
                "Units to Add to Stock",
                min_value=0,
                value=0,
                step=1,
                key="edit_stock_" + str(edit_item["item_id"])
            )
        with col2:
            categories = ["Bread", "Pastry", "Dessert", "Beverage", "Other"]
            current_cat = edit_item.get("category", "Other")
            if current_cat in categories:
                cat_index = categories.index(current_cat)
            else:
                cat_index = 0

            updated_category = st.selectbox(
                "Category",
                categories,
                index=cat_index,key="edit_cat_" + str(edit_item["item_id"])
            )
            st.markdown("**Current stock:** " + str(edit_item["stock"]) + " units")

        update_btn = st.button("Save Changes", type="primary", use_container_width=True, key="update_btn")

    if update_btn:
        success, message = service.update_item(inventory, edit_item["item_id"], updated_price, add_stock, updated_category)
        if success:
            with st.spinner("Saving..."):
                save_data(Inventory_Path, inventory)
                time.sleep(1)
            st.success(message)
            st.session_state["page"] = "home"
            st.rerun()
        else:
            st.error(message)
