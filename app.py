import streamlit as st
import pandas as pd
import os
import plotly.express as px
from streamlit_option_menu import option_menu

# -------------------- USER LOGIN SYSTEM -------------------- #
# Dummy login credentials (in real apps use a database)
USERNAME = "admin"
PASSWORD = "1234"

# -------------------- INVENTORY FUNCTIONS -------------------- #
def load_inventory():
    if os.path.exists("inventory.csv"):
        return pd.read_csv("inventory.csv")
    else:
        return pd.DataFrame(columns=["Product", "Quantity", "Price"])

def save_inventory(inventory):
    inventory.to_csv("inventory.csv", index=False)

# -------------------- STREAMLIT APP -------------------- #
st.set_page_config(page_title="Inventory Manager", page_icon="🛒", layout="wide")

# Login state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Login Form
if not st.session_state.logged_in:
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == USERNAME and password == PASSWORD:
            st.session_state.logged_in = True
            st.success("Login successful! 🎉")
        else:
            st.error("Invalid username or password")

# Main App
if st.session_state.logged_in:
    # Sidebar Menu
    with st.sidebar:
        choice = option_menu(
            "Menu", 
            ["Dashboard", "View Inventory", "Add Product", "Update Stock", "Download CSV", "Logout"],
            icons=["bar-chart", "table", "plus", "pencil", "cloud-download", "box-arrow-right"],
            menu_icon="cast", 
            default_index=0,
        )

    inventory = load_inventory()

    if choice == "Dashboard":
        st.title("📊 Dashboard Overview")

        # Show basic stats
        total_products = inventory['Product'].nunique()
        total_stock = inventory['Quantity'].sum()
        total_value = (inventory['Quantity'] * inventory['Price']).sum()

        st.metric("Total Products", total_products)
        st.metric("Total Stock Items", total_stock)
        st.metric("Total Stock Value (₹)", f"{total_value:,.2f}")

        st.subheader("Stock Value Distribution")
        if not inventory.empty:
            inventory["Stock Value"] = inventory["Quantity"] * inventory["Price"]
            fig = px.pie(inventory, names="Product", values="Stock Value", title="Stock Value by Product")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data to display.")

    elif choice == "View Inventory":
        st.title("📋 View Inventory")
        st.dataframe(inventory)

        search = st.text_input("🔎 Search for a product")
        if search:
            result = inventory[inventory['Product'].str.contains(search, case=False)]
            st.write(result)

    elif choice == "Add Product":
        st.title("➕ Add New Product")
        with st.form(key="add_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                name = st.text_input("Product Name")
            with col2:
                quantity = st.number_input("Quantity", min_value=0)
            with col3:
                price = st.number_input("Price", min_value=0.0, format="%.2f")
            
            submit = st.form_submit_button("Add Product")

            if submit:
                new_product = pd.DataFrame([[name, quantity, price]], columns=["Product", "Quantity", "Price"])
                inventory = pd.concat([inventory, new_product], ignore_index=True)
                save_inventory(inventory)
                st.success(f"✅ Product '{name}' added successfully!")

    elif choice == "Update Stock":
        st.title("✏️ Update Stock")
        if not inventory.empty:
            product_list = inventory['Product'].tolist()
            selected_product = st.selectbox("Select a product to update", product_list)
            new_quantity = st.number_input("New Quantity", min_value=0)
            if st.button("Update Stock"):
                inventory.loc[inventory['Product'] == selected_product, 'Quantity'] = new_quantity
                save_inventory(inventory)
                st.success(f"✅ Stock for '{selected_product}' updated!")
        else:
            st.info("Inventory is empty. Add products first.")

    elif choice == "Download CSV":
        st.title("💾 Download Inventory CSV")
        csv = inventory.to_csv(index=False).encode('utf-8')
        st.download_button("Download Inventory File", data=csv, file_name='inventory.csv', mime='text/csv')

    elif choice == "Logout":
        st.session_state.logged_in = False
        st.success("Logged out successfully!")
