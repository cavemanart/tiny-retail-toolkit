
import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="Tiny Retail Toolkit", layout="centered")

if "inventory" not in st.session_state:
    st.session_state.inventory = pd.DataFrame(columns=[
        "Item Name", "Category", "Size", "Brand", "Price", "Condition", "Date Received", "Sold"
    ])

if "loyalty" not in st.session_state:
    st.session_state.loyalty = pd.DataFrame(columns=["Customer", "Visits"])

page = st.sidebar.radio("Choose a tool:", [
    "Inventory Intake",
    "Promo Generator",
    "Loyalty Tracker"
])

if page == "Inventory Intake":
    st.title("📦 Inventory Intake")
    with st.form("inventory_form"):
        col1, col2 = st.columns(2)
        with col1:
            item_name = st.text_input("Item Name")
            category = st.selectbox("Category", ["Clothing", "Toys", "Books", "Other"])
            size = st.text_input("Size")
            brand = st.text_input("Brand")
        with col2:
            price = st.number_input("Price ($)", min_value=0.0, step=0.5)
            condition = st.selectbox("Condition", ["New", "Like New", "Good", "Worn"])
            received_date = st.date_input("Date Received", value=date.today())
        submitted = st.form_submit_button("Add Item")
        if submitted:
            new_row = pd.DataFrame.from_dict({
                "Item Name": [item_name],
                "Category": [category],
                "Size": [size],
                "Brand": [brand],
                "Price": [price],
                "Condition": [condition],
                "Date Received": [received_date],
                "Sold": [False]
            })
            st.session_state.inventory = pd.concat([st.session_state.inventory, new_row], ignore_index=True)
            st.success("Item added!")

    st.subheader("Current Inventory")
    df = st.session_state.inventory.copy()
    sold_toggle = st.checkbox("Show only unsold items", value=True)
    if sold_toggle:
        df = df[df["Sold"] == False]
    st.dataframe(df, use_container_width=True)
    st.download_button("Download CSV", data=df.to_csv(index=False), file_name="inventory.csv")

elif page == "Promo Generator":
    st.title("📣 Promo Generator")
    with st.form("promo_form"):
        title = st.text_input("Event Name", "Spring Sale")
        details = st.text_area("Details", "30% off all toys and jackets!")
        start_date = st.date_input("Start Date", date.today())
        end_date = st.date_input("End Date")
        platform = st.selectbox("Platform", ["Instagram", "Facebook", "Text Message"])
        submitted = st.form_submit_button("Generate Promo")

    if submitted:
        promo_text = f"{title} is here! 🎉\n{details}\nCome see us between {start_date.strftime('%b %d')} and {end_date.strftime('%b %d')}!"
        if platform == "Instagram":
            promo_text += "\n#resalekids #momlife #dealsforkids"
        elif platform == "Facebook":
            promo_text += "\n🧸👕👶 Come shop local with us!"
        elif platform == "Text Message":
            promo_text = f"{title}: {details} ({start_date.strftime('%m/%d')}–{end_date.strftime('%m/%d')})"

        st.subheader("Promo Caption")
        st.code(promo_text)
        st.download_button("Download Promo Text", promo_text, file_name="promo.txt")

elif page == "Loyalty Tracker":
    st.title("💳 Loyalty Tracker")
    with st.form("loyalty_form"):
        name = st.text_input("Customer Name or Initials")
        submitted = st.form_submit_button("Add Visit")
        if submitted and name:
            if name in st.session_state.loyalty.Customer.values:
                st.session_state.loyalty.loc[st.session_state.loyalty.Customer == name, "Visits"] += 1
            else:
                st.session_state.loyalty = pd.concat([
                    st.session_state.loyalty,
                    pd.DataFrame({"Customer": [name], "Visits": [1]})
                ], ignore_index=True)
            st.success("Visit recorded!")

    st.subheader("Customer Loyalty List")
    df_loyalty = st.session_state.loyalty.copy()
    st.dataframe(df_loyalty)
    st.download_button("Download Loyalty List", data=df_loyalty.to_csv(index=False), file_name="loyalty.csv")
