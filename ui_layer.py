import streamlit as st
import time
from pathlib import Path
from data_layer import save_data
import service_layer as service

Inventory_Path = Path("Iventory.json")
Sales_path = Path("sales.json")
Users_path = Path("users.json")


