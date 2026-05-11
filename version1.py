import streamlit as st
import json
import time
import uuid
from pathlib import Path

st.set_page_config(
    page_title="Shop Inventory Portal",
    page_icon=" ",
    layout="centered",
    initial_sidebar_state="expanded",
)

inventory_file = Path("inventory.json")
sales_file = Path("sales.json")
users_file = Path("users.json")

def save_inventory():
    with open(inventory_file, "w", encoding="utf-8") as f:
        json.dump(st.session_state["inventory"], f, indent=2)

def save_sales():
    with open(sales_file, "w", encoding="utf-8") as f:
        json.dump(st.session_state["sales"], f, indent=2)

def save_users():
    with open(users_file, "w", encoding="utf-8") as f:
        json.dump(st.session_state["users"], f, indent=2)

#Inventory

def load_inventory():
    default = [
        {"item_id": 1, "name": "Sourdough Loaf",   "price": 8.50, "stock": 12, "category": "Bread",   "flagged": False},
        {"item_id": 2, "name": "Croissant",         "price": 3.25, "stock": 20, "category": "Pastry",  "flagged": False},
        {"item_id": 3, "name": "Blueberry Muffin",  "price": 2.95, "stock": 4,  "category": "Pastry",  "flagged": False},
        {"item_id": 4, "name": "Cinnamon Roll",     "price": 4.00, "stock": 8,  "category": "Pastry",  "flagged": False},
        {"item_id": 5, "name": "Whole Wheat Loaf",  "price": 7.75, "stock": 6,  "category": "Bread",   "flagged": False},
        {"item_id": 6, "name": "Chocolate Eclair",  "price": 4.50, "stock": 3,  "category": "Pastry",  "flagged": False},
        {"item_id": 7, "name": "Bagel",             "price": 2.00, "stock": 15, "category": "Bread",   "flagged": False},
        {"item_id": 8, "name": "Lemon Tart",        "price": 5.25, "stock": 2,  "category": "Dessert", "flagged": False},
    ]
    if inventory_file.exists():
        with open(inventory_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            return default

        next_id = max(
            (item.get("item_id") or item.get("id") or 0)
            for item in data if isinstance(item, dict)
        ) + 1
        changed = False

        for item in data:
            if not isinstance(item, dict):
                continue

            if "item_id" not in item:
                if "id" in item:
                    item["item_id"] = item.pop("id")
                else:
                    item["item_id"] = next_id
                    next_id += 1
                changed = True

            if "category" not in item:
                item["category"] = "Other"
                changed = True

            if "flagged" not in item:
                item["flagged"] = False
                changed = True

        if changed:
            with open(inventory_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

        return data

    with open(inventory_file, "w", encoding="utf-8") as f:
        json.dump(default, f, indent=2)
    return default

def load_sales():
    if sales_file.exists():
        with open(sales_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def load_users():
    default = [
        {"username": "owner",    "password": "owner123",    "role": "Owner"},
        {"username": "employee", "password": "employee123", "role": "Employee"},
    ]
    if users_file.exists():
        with open(users_file, "r", encoding="utf-8") as f:
            return json.load(f)
    with open(users_file, "w", encoding="utf-8") as f:
        json.dump(default, f, indent=2)
    return default

#Initalizing Session State 

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "user" not in st.session_state:
    st.session_state["user"] = None

if "role" not in st.session_state:
    st.session_state["role"] = None

if "page" not in st.session_state:          
    st.session_state["page"] = "login"

if "inventory" not in st.session_state:
    st.session_state["inventory"] = load_inventory()

if "sales" not in st.session_state:
    st.session_state["sales"] = load_sales()

if "users" not in st.session_state:
    st.session_state["users"] = load_users()

if "messages" not in st.session_state:     
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hi! How can I help you today?"}
    ]

#Chatbox Responses

def simulated_chatbot(message):
    message = message.lower().strip()
    inventory = st.session_state["inventory"]

    # Response 1 
    if any(w in message for w in ["low", "running out", "low stock", "almost out"]):
        low = [i for i in inventory if i["stock"] < 5]
        if not low:
            return "No items are critically low right now."
        lines = "\n".join(f"- **{i['name']}**: {i['stock']} left" for i in low)
        return f" **Items running low (stock < 5):**\n\n{lines}"

    # Response 2 
    elif any(w in message for w in ["flag", "flagged", "marked", "alert"]):
        flagged = [i for i in inventory if i.get("flagged")]
        if not flagged:
            return "No items are currently flagged."
        lines = "\n".join(f"- **{i['name']}** ({i['stock']} in stock)" for i in flagged)
        return f" **Flagged items:**\n\n{lines}"

    # Response 3 
    elif any(w in message for w in ["value", "worth", "total value", "inventory value"]):
        total = sum(i["price"] * i["stock"] for i in inventory)
        return f"Total estimated inventory value: **${total:,.2f}**"

    # Response 4 
    elif any(w in message for w in ["most stock", "highest stock", "most items", "best stocked"]):
        top = max(inventory, key=lambda i: i["stock"])
        return f"Best-stocked item: **{top['name']}** with **{top['stock']}** units."

    # Response 5
    elif any(w in message for w in ["help", "what can you", "commands", "hi", "hello", "hey"]):
        return (
            " Here's what you can ask me:\n\n"
            "- *What items are low on stock?*\n"
            "- *Are there any flagged items?*\n"
            "- *What is the total inventory value?*\n"
            "- *What item has the most stock?*"
        )

    # Fallback
    return (
        " I'm not sure about that yet. Try:\n"
        "- *What items are low on stock?*\n"
        "- *What is the total inventory value?*\n"
        "- *Are there any flagged items?*"
    )
#Sidebar

with st.sidebar:
    st.title("Shop Portal")
    st.divider()

    if "logged_in" in st.session_state and st.session_state["logged_in"]:
        user = st.session_state["user"]
        st.markdown(f"**User:** {user['username']}")
        st.markdown(f"**Role:** {user['role']}")
        st.divider()

        inv = st.session_state["inventory"]
        st.metric("Total Products", len(inv))
        st.metric("Total Units",    sum(i["stock"] for i in inv))
        low = sum(1 for i in inv if i["stock"] < 5)
        if low:
            st.warning(f"{low} item(s) critically low")
        else:
            st.success(" Stock levels OK")

        st.divider()

        if st.button("Log Out", use_container_width=True, key="logout_btn"):
            st.session_state["logged_in"] = False
            st.session_state["user"]      = None
            st.session_state["role"]      = None
            st.session_state["page"]      = "login"
            st.session_state["messages"]  = [
                {"role": "assistant", "content": "Hi! How can I help you today?"}
            ]
            st.rerun()
    else:
        st.caption("Please log in to continue.")

    st.divider()
    st.caption("Shop Inventory Portal")


if st.session_state["role"] is None:

    st.title("Shop Inventory Portal")
    st.markdown("Internal operations portal — log in or register to continue.")
    st.divider()

    tab1, tab2 = st.tabs([" Login", " Register"])

    with tab1:
        st.subheader("Login")
        with st.container(border=True):
            login_username = st.text_input(
                "Username", placeholder="e.g. owner",
                key="login_username"
            )
            login_password = st.text_input(
                "Password", type="password",
                key="login_password"
            )
            login_btn = st.button(
                "Log In", type="primary",
                use_container_width=True, key="login_btn"
            )

        if login_btn:
            if not login_username.strip() or not login_password.strip():
                st.warning("Please enter both username and password.")
            else:
                found = next(
                    (u for u in st.session_state["users"]
                     if u["username"] == login_username.strip()
                     and u["password"] == login_password.strip()),
                    None
                )
                if found:
                    with st.spinner("Logging in..."):
                        # Writing to the notebook  (Slide: "Writing to the Notebook")
                        st.session_state["logged_in"] = True
                        st.session_state["user"]      = found
                        st.session_state["role"]      = found["role"]
                        st.session_state["page"]      = "home"
                        time.sleep(1)
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

        st.caption("Demo — **owner** / owner123 · **employee** / employee123")

    with tab2:
        st.subheader("Register a New Employee Account")
        with st.container(border=True):
            reg_username = st.text_input(
                "Choose a Username", placeholder="e.g. jane",
                key="reg_username"
            )
            reg_password = st.text_input(
                "Choose a Password", type="password",
                key="reg_password"
            )
            reg_confirm = st.text_input(
                "Confirm Password", type="password",
                key="reg_confirm"
            )
            st.markdown("**Role:** Employee *(all new accounts are employees)*")
            register_btn = st.button(
                "Create Account", type="primary",
                use_container_width=True, key="register_btn"
            )

        if register_btn:
            uname = reg_username.strip()
            pwd   = reg_password.strip()
            if not uname or not pwd or not reg_confirm.strip():
                st.warning("Please fill in all fields.")
            elif pwd != reg_confirm.strip():
                st.error("Passwords do not match.")
            elif len(pwd) < 4:
                st.warning("Password must be at least 4 characters.")
            elif any(u["username"] == uname for u in st.session_state["users"]):
                st.error("That username is already taken.")
            else:
                with st.spinner("Creating account..."):
                    st.session_state["users"].append(
                        {"username": uname, "password": pwd, "role": "Employee"}
                    )
                    save_users()
                    time.sleep(1)
                st.success(f"Account created! You can now log in as **{uname}**.")

# OWNER DASHBOARD 
elif st.session_state["role"] == "Owner":

    # ── Owner: Home ──
    if st.session_state["page"] == "home":
        st.title("Owner Dashboard")
        st.markdown("What would you like to manage today?")
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
                st.caption("Update prices, categories, and stock levels.")
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
                st.caption("Delete discontinued items.")
                if st.button("Remove Product", use_container_width=True, key="go_delete"):
                    st.session_state["page"] = "delete"
                    st.rerun()

        st.divider()
        with st.container(border=True):
            st.markdown("### Sales Log")
            st.caption("Review all employee-logged transactions.")
            if st.button("View Sales Log", use_container_width=True, key="go_sales"):
                st.session_state["page"] = "sales"
                st.rerun()

    # Owner: Catalog
    elif st.session_state["page"] == "catalog":
        if st.button("← Back", key="catalog_back"):
            st.session_state["page"] = "home"
            st.rerun()

        st.header("Product Catalog")
        search = st.text_input(
            "Search by name", placeholder="e.g. Croissant",
            key="owner_search"                          # static key
        )
        inventory = st.session_state["inventory"]
        filtered  = (
            [i for i in inventory if search.lower() in i["name"].lower()]
            if search else inventory
        )
        st.divider()

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Products",    len(inventory))
        col2.metric("Total Units",       sum(i["stock"] for i in inventory))
        col3.metric("Critically Low", sum(1 for i in inventory if i["stock"] < 5))
        st.divider()

        if not filtered:
            st.info("No items match your search.")
        else:
            for item in filtered:
                with st.container(border=True):
                    c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 2, 2])
                    c1.markdown(f"**{item['name']}**")
                    c2.markdown(f"_{item.get('category', 'Other')}_")
                    c3.markdown(f"${item['price']:.2f}")
                    c4.markdown(f"Stock: **{item['stock']}**")
                    if item["stock"] == 0:
                        c5.error("Out of Stock")
                    elif item["stock"] < 5:
                        c5.warning("Low")
                    else:
                        c5.success("OK")

    # Owner: Add Product
    elif st.session_state["page"] == "add":
        if st.button("← Back", key="add_back"):
            st.session_state["page"] = "home"
            st.rerun()

        st.header("Add a New Product")

        with st.container(border=True):
            st.subheader("New Product Details")
            col1, col2 = st.columns(2)

            with col1:
                new_name = st.text_input(
                    "Product Name", placeholder="e.g. Almond Croissant",
                    key="new_product_name"
                )
                new_price = st.number_input(
                    "Price ($)", min_value=0.01, value=1.00,
                    step=0.25, key="new_product_price"
                )

            with col2:
                new_stock = st.number_input(
                    "Initial Stock", min_value=0, value=10,
                    step=1, key="new_product_stock"
                )
                new_category = st.selectbox(
                    "Category",
                    ["Bread", "Pastry", "Dessert", "Beverage", "Other"],
                    key="new_product_category"
                )

            add_btn = st.button(
                "Add Product", type="primary",
                use_container_width=True, key="add_product_btn"
            )

        if add_btn:
            if not new_name.strip():
                st.warning("Please enter a product name.")
            elif any(i["name"].lower() == new_name.strip().lower()
                     for i in st.session_state["inventory"]):
                st.error("A product with that name already exists.")
            else:
                with st.spinner("Adding product..."):
                    new_id = max(
                        (i["item_id"] for i in st.session_state["inventory"]), default=0
                    ) + 1
                    st.session_state["inventory"].append({
                        "item_id":  new_id,
                        "name":     new_name.strip(),
                        "price":    round(new_price, 2),
                        "stock":    new_stock,
                        "category": new_category,
                        "flagged":  False,
                    })
                    save_inventory()
                    time.sleep(1)
                st.success(f"**{new_name.strip()}** added!")
                st.session_state["page"] = "home"
                st.rerun()

    # Owner: Edit / Restock
    elif st.session_state["page"] == "edit":
        if st.button("Back", key="edit_back"):
            st.session_state["page"] = "home"
            st.rerun()

        st.header("Edit or Restock a Product")
        inventory  = st.session_state["inventory"]

        with st.container(border=True):
            st.subheader("Select a Product")

            edit_item = st.selectbox(
                "Choose product to edit",
                options=inventory,
                format_func=lambda x: f"{x['name']} (Stock: {x['stock']})",
                key="edit_item_select"
            )

            st.divider()
            st.subheader("Update Details")
            col1, col2 = st.columns(2)

            with col1:
                updated_price = st.number_input(
                    "New Price ($)", min_value=0.01,
                    value=float(edit_item["price"]),
                    step=0.25, key=f"edit_price_{edit_item['item_id']}"
                )
                add_stock = st.number_input(
                    "Units to Add to Stock", min_value=0, value=0,
                    step=1, key=f"edit_stock_{edit_item['item_id']}"
                )

            with col2:
                updated_category = st.selectbox(
                    "Category",
                    ["Bread", "Pastry", "Dessert", "Beverage", "Other"],
                    index=["Bread", "Pastry", "Dessert", "Beverage", "Other"].index(
                        edit_item.get("category", "Other")
                    ),
                    key=f"edit_cat_{edit_item['item_id']}"
                )
                st.markdown(f"**Current stock:** {edit_item['stock']} units")
                if add_stock > 0:
                    st.markdown(f"**New stock:** {edit_item['stock'] + add_stock} units")

            update_btn = st.button(
                "Save Changes", type="primary",
                use_container_width=True, key="update_btn"
            )

        if update_btn:
            with st.spinner("Saving changes..."):
                for item in st.session_state["inventory"]:
                    if item["item_id"] == edit_item["item_id"]:
                        item["price"]    = round(updated_price, 2)
                        item["stock"]   += add_stock
                        item["category"] = updated_category
                        break
                save_inventory()
                time.sleep(1)
            st.success(f"**{edit_item['name']}** updated.")
            st.session_state["page"] = "home"
            st.rerun()

    # Owner: Delete Product
    elif st.session_state["page"] == "delete":
        if st.button("← Back", key="delete_back"):
            st.session_state["page"] = "home"
            st.rerun()

        st.header("Remove a Discontinued Product")
        inventory = st.session_state["inventory"]

        with st.container(border=True):
            st.subheader("Select Product to Remove")
            delete_item = st.selectbox(
                "Choose product",
                options=inventory,
                format_func=lambda x: f"{x['name']} (Stock: {x['stock']})",
                key="delete_item_select"
            )

            col1, col2 = st.columns(2)
            col1.markdown(f"**Price:** ${delete_item['price']:.2f}")
            col2.markdown(f"**Stock remaining:** {delete_item['stock']}")

            st.warning(
                f"This will permanently remove **{delete_item['name']}** from the catalog."
            )
            confirm = st.checkbox(
                "I confirm I want to delete this product.",
                key="confirm_delete"
            )
            delete_btn = st.button(
                "Delete Product", type="primary",
                use_container_width=True, key="delete_btn"
            )

        if delete_btn:
            if not confirm:
                st.error("Please check the confirmation box first.")
            else:
                with st.spinner("Removing product..."):
                    st.session_state["inventory"] = [
                        i for i in st.session_state["inventory"]
                        if i["item_id"] != delete_item["item_id"]
                    ]
                    save_inventory()
                    time.sleep(1)
                st.success(f"**{delete_item['name']}** removed.")
                st.session_state["page"] = "home"
                st.rerun()

    #Owner: Sales Log 
    elif st.session_state["page"] == "sales":
        if st.button("← Back", key="sales_back"):
            st.session_state["page"] = "home"
            st.rerun()

        st.header("Sales Log")
        sales = st.session_state["sales"]

        if not sales:
            st.info("No sales have been logged yet.")
        else:
            col1, col2 = st.columns(2)
            col1.metric("Total Transactions", len(sales))
            col2.metric("Total Revenue",      f"${sum(s['total'] for s in sales):.2f}")
            st.divider()

            for sale in reversed(sales):
                with st.container(border=True):
                    c1, c2, c3, c4 = st.columns([3, 2, 2, 3])
                    c1.markdown(f"**{sale['item']}**")
                    c2.markdown(f"Qty: {sale['quantity']}")
                    c3.markdown(f"${sale['total']:.2f}")
                    c4.markdown(f"_{sale['logged_by']} · {sale['date']}_")


# EMPLOYEE DASHBOARD 
elif st.session_state["role"] == "Employee":

    user = st.session_state["user"]

    if st.session_state["page"] == "home":
        st.title(f"🏪 Welcome, {user['username']}!")
        st.markdown("What would you like to do today?")
        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            with st.container(border=True):
                st.markdown("### Log a Sale")
                st.caption("Record items sold and update stock.")
                if st.button("Log a Sale", use_container_width=True, key="go_log_sale"):
                    st.session_state["page"] = "log_sale"
                    st.rerun()

        with col2:
            with st.container(border=True):
                st.markdown("### View Catalog")
                st.caption("Browse products and flag low items.")
                if st.button("View Catalog", use_container_width=True, key="go_emp_catalog"):
                    st.session_state["page"] = "emp_catalog"
                    st.rerun()


    elif st.session_state["page"] == "log_sale":
        if st.button("← Back", key="log_sale_back"):
            st.session_state["page"] = "home"
            st.rerun()

        st.header("🛒 Log a Sale")
        inventory = st.session_state["inventory"]
        available = [i for i in inventory if i["stock"] > 0]

        left_col, right_col = st.columns([1.4, 1])

        with left_col:
            if not available:
                st.error("No items currently in stock.")
            else:
                with st.container(border=True):
                    st.subheader("Sale Details")

                    selected_item = st.selectbox(
                        "Select an Item",
                        options=available,
                        format_func=lambda x: f"{x['name']} (Stock: {x['stock']})",
                        key="sale_item_select"
                    )
                    quantity = st.number_input(
                        "Quantity",
                        min_value=1,
                        step=1,
                        key="sale_quantity"
                    )

                    st.markdown(f"**Unit price:** ${selected_item['price']:.2f}")
                    st.markdown(f"**Sale total:** ${round(selected_item['price'] * quantity, 2):.2f}")

    
                    if st.button("Create Order", type="primary",
                                 use_container_width=True, key="create_order_btn"):
                        if selected_item["stock"] < quantity:
                            st.error(
                                f"❌ Not enough stock — only **{selected_item['stock']}** available."
                            )
                        else:
                            with st.spinner("Creating order..."):
                                total = round(quantity * selected_item["price"], 2)

                                # Update stock
                                for item in st.session_state["inventory"]:
                                    if item["item_id"] == selected_item["item_id"]:
                                        item["stock"] -= quantity
                                        if item["stock"] < 5:
                                            item["flagged"] = True
                                        break

                                # Append sale record
                                new_sale = {
                                    "sale_id":    str(uuid.uuid4())[:8].upper(),
                                    "item":       selected_item["name"],
                                    "item_id":    selected_item["item_id"],
                                    "quantity":   quantity,
                                    "unit_price": selected_item["price"],
                                    "total":      total,
                                    "logged_by":  user["username"],
                                    "date":       time.strftime("%Y-%m-%d %H:%M"),
                                }
                                st.session_state["sales"].append(new_sale)

                                # Save both JSON files  
                                save_inventory()
                                save_sales()

                                st.balloons()              
                                time.sleep(2)

                            st.session_state["page"] = "home"
                            st.rerun()

        with right_col:
            st.subheader("Shop Assistant")

            with st.container(height=250, border=True):
                for message in st.session_state["messages"]:
                    with st.chat_message(message["role"]):
                        st.write(message["content"])

            user_input = st.chat_input("Ask a question...")

            if user_input:
                with st.spinner("Thinking..."):
                    st.session_state["messages"].append(
                        {"role": "user", "content": user_input}
                    )
                    ai_response = simulated_chatbot(user_input)
                    st.session_state["messages"].append(
                        {"role": "assistant", "content": ai_response}
                    )
                    time.sleep(1)
                st.rerun()

            if st.button("Clear Chat", key="clear_chat_btn"):
                st.session_state["messages"] = [
                    {"role": "assistant", "content": "Hi! How can I help you today?"}
                ]
                st.rerun()

    elif st.session_state["page"] == "emp_catalog":
        if st.button(" Back", key="emp_catalog_back"):
            st.session_state["page"] = "home"
            st.rerun()

        st.header("Current Catalog")

        search = st.text_input(
            " Search by name", placeholder="e.g. Bagel",
            key="emp_search"                       
        )
        inventory = st.session_state["inventory"]
        filtered = (
            [i for i in inventory if search.lower() in i["name"].lower()]
            if search else inventory
        )
        st.divider()

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Products",   len(inventory))
        col2.metric("Total Units",      sum(i["stock"] for i in inventory))
        col3.metric("Low / Flagged", sum(1 for i in inventory if i["stock"] < 5))
        st.divider()

        if not filtered:
            st.info("No items match your search.")
        else:
            for item in filtered:
                with st.container(border=True):
                    c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 2, 2])
                    c1.markdown(f"**{item['name']}**")
                    c2.markdown(f"_{item.get('category', 'Other')}_")
                    c3.markdown(f"${item['price']:.2f}")
                    c4.markdown(f"Stock: **{item['stock']}**")

                    if item["stock"] == 0:
                        c5.error(" Out of Stock")
                    elif item["stock"] < 5:
                        c5.warning(" Low")
                    else:
                        c5.success("OK")

                    flag_label = " Unflag" if item.get("flagged") else "Flag"
                    flag_key = item.get("item_id", item.get("id", item.get("name")))
                    if st.button(
                        flag_label,
                        key=f"flag_{flag_key}",   # dynamic key per item
                        use_container_width=False
                    ):
                        for i in st.session_state["inventory"]:
                            if i["item_id"] == item["item_id"]:
                                i["flagged"] = not i.get("flagged", False)
                                break
                        save_inventory()
                        st.rerun()