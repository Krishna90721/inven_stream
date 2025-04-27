import streamlit as st
import pandas as pd
import os
import plotly.express as px
from streamlit_option_menu import option_menu

# -------------------- USER LOGIN SYSTEM -------------------- #
USERNAME = "admin"
PASSWORD = "1234"

# -------------------- INVENTORY FUNCTIONS -------------------- #
def load_inventory():
    if os.path.exists("inventory.csv"):
        return pd.read_csv("inventory.csv")
    else:
        return pd.DataFrame(columns=["Product", "Quantity", "Price", "Supplier"])

def save_inventory(inventory):
    inventory.to_csv("inventory.csv", index=False)

def load_suppliers():
    if os.path.exists("suppliers.csv"):
        return pd.read_csv("suppliers.csv")
    else:
        return pd.DataFrame(columns=["Supplier"])

def save_suppliers(suppliers):
    suppliers.to_csv("suppliers.csv", index=False)

# -------------------- STREAMLIT APP -------------------- #
st.set_page_config(page_title="Inventory Manager", page_icon="🛒", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

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

if st.session_state.logged_in:
    with st.sidebar:
        choice = option_menu(
            "Menu", 
            ["Dashboard", "View Inventory", "Add Product", "Update Stock", "Manage Suppliers", "Download CSV", "Logout"],
            icons=["bar-chart", "table", "plus", "pencil", "building", "cloud-download", "box-arrow-right"],
            menu_icon="cast", 
            default_index=0,
        )

    inventory = load_inventory()
    suppliers = load_suppliers()

    if choice == "Dashboard":
        st.title("📊 Dashboard Overview")

        total_products = inventory['Product'].nunique()
        total_stock = inventory['Quantity'].sum()
        total_value = (inventory['Quantity'] * inventory['Price']).sum()

        st.metric("Total Products", total_products)
        st.metric("Total Stock Items", total_stock)
        st.metric("Total Stock Value (₹)", f"{total_value:,.2f}")

        st.subheader("Stock Value Distribution by Supplier")
        if not inventory.empty:
            inventory["Stock Value"] = inventory["Quantity"] * inventory["Price"]
            if "Supplier" in inventory.columns:
                fig = px.pie(inventory, names="Supplier", values="Stock Value", title="Stock Value by Supplier")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No suppliers found. Please add supplier data.")
        else:
            st.info("No data to display.")

    elif choice == "View Inventory":
        st.title("📋 View Inventory")
        
        if not inventory.empty:
            search = st.text_input("🔎 Search for a product")
            supplier_filter = st.selectbox("🏢 Filter by Supplier", ["All"] + inventory['Supplier'].dropna().unique().tolist())

            filtered_inventory = inventory.copy()

            if search:
                filtered_inventory = filtered_inventory[filtered_inventory['Product'].str.contains(search, case=False)]

            if supplier_filter != "All":
                filtered_inventory = filtered_inventory[filtered_inventory['Supplier'] == supplier_filter]

            st.dataframe(filtered_inventory)

            st.subheader("✏️ Edit or 🗑️ Delete a Product")
            selected_product = st.selectbox("Select a product", inventory['Product'].tolist())

            if selected_product:
                prod_data = inventory[inventory['Product'] == selected_product].iloc[0]

                new_name = st.text_input("Product Name", prod_data['Product'])
                new_quantity = st.number_input("Quantity", value=int(prod_data['Quantity']), min_value=0)
                new_price = st.number_input("Price", value=float(prod_data['Price']), min_value=0.0, format="%.2f")
                new_supplier = st.selectbox(
                    "Supplier", 
                    suppliers['Supplier'].tolist(), 
                    index=int(suppliers[suppliers['Supplier'] == prod_data['Supplier']].index[0])
                )

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Update Product"):
                        inventory.loc[inventory['Product'] == selected_product, ['Product', 'Quantity', 'Price', 'Supplier']] = [new_name, new_quantity, new_price, new_supplier]
                        save_inventory(inventory)
                        st.success(f"✅ '{selected_product}' updated successfully!")
                with col2:
                    if st.button("Delete Product"):
                        inventory = inventory[inventory['Product'] != selected_product]
                        save_inventory(inventory)
                        st.success(f"🗑️ '{selected_product}' deleted successfully!")
        else:
            st.info("Inventory is empty. Add products first.")

    elif choice == "Add Product":
        st.title("➕ Add New Product")
        if not suppliers.empty:
            with st.form(key="add_product_form"):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    name = st.text_input("Product Name")
                with col2:
                    quantity = st.number_input("Quantity", min_value=0)
                with col3:
                    price = st.number_input("Price", min_value=0.0, format="%.2f")
                with col4:
                    supplier = st.selectbox("Supplier", suppliers['Supplier'].tolist())

                submit = st.form_submit_button("Add Product")

                if submit:
                    new_product = pd.DataFrame([[name, quantity, price, supplier]], columns=["Product", "Quantity", "Price", "Supplier"])
                    inventory = pd.concat([inventory, new_product], ignore_index=True)
                    save_inventory(inventory)
                    st.success(f"✅ Product '{name}' added successfully!")
        else:
            st.warning("⚠️ Add suppliers first before adding products!")

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

    elif choice == "Manage Suppliers":
        st.title("🏢 Manage Suppliers")

        st.subheader("Existing Suppliers")
        st.dataframe(suppliers)

        st.subheader("➕ Add a New Supplier")
        with st.form(key="add_supplier_form"):
            new_supplier = st.text_input("Supplier Name")
            submit_supplier = st.form_submit_button("Add Supplier")

            if submit_supplier:
                if new_supplier and new_supplier not in suppliers['Supplier'].values:
                    new_row = pd.DataFrame([[new_supplier]], columns=["Supplier"])
                    suppliers = pd.concat([suppliers, new_row], ignore_index=True)
                    save_suppliers(suppliers)
                    st.success(f"✅ Supplier '{new_supplier}' added successfully!")
                else:
                    st.warning("Supplier already exists or input is empty.")

        st.subheader("✏️ Edit or 🗑️ Delete Supplier")
        if not suppliers.empty:
            selected_supplier = st.selectbox("Select a supplier", suppliers['Supplier'].tolist())

            new_supplier_name = st.text_input("New Supplier Name", selected_supplier)
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Update Supplier"):
                    suppliers.loc[suppliers['Supplier'] == selected_supplier, 'Supplier'] = new_supplier_name
                    inventory.loc[inventory['Supplier'] == selected_supplier, 'Supplier'] = new_supplier_name
                    save_suppliers(suppliers)
                    save_inventory(inventory)
                    st.success(f"✅ Supplier '{selected_supplier}' updated to '{new_supplier_name}' successfully!")

            with col2:
                if st.button("Delete Supplier"):
                    inventory = inventory[inventory['Supplier'] != selected_supplier]
                    suppliers = suppliers[suppliers['Supplier'] != selected_supplier]
                    save_inventory(inventory)
                    save_suppliers(suppliers)
                    st.success(f"🗑️ Supplier '{selected_supplier}' and related products deleted successfully!")

    elif choice == "Download CSV":
        st.title("💾 Download Inventory CSV")
        csv = inventory.to_csv(index=False).encode('utf-8')
        st.download_button("Download Inventory File", data=csv, file_name='inventory.csv', mime='text/csv')

    elif choice == "Logout":
        st.session_state.logged_in = False
        st.success("Logged out successfully!")
