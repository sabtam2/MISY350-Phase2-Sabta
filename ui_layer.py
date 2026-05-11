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