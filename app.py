import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
import base64
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Tiny Retail Toolkit", layout="wide")
st.title("🥸 Tiny Retail Toolkit")

# --- Session state init ---
if "items" not in st.session_state or not isinstance(st.session_state.items, list):
    st.session_state.items = []

if "use_gsheets" not in st.session_state:
    st.session_state.use_gsheets = False

# --- Google Sheets Setup ---
def upload_to_google_sheets(items):
    if not st.session_state.use_gsheets:
        return
    try:
        creds = Credentials.from_service_account_info(st.secrets["gcp"])
        client = gspread.authorize(creds)
        spreadsheet = client.open("Tiny Retail Toolkit")
        try:
            worksheet = spreadsheet.worksheet("Inventory")
        except gspread.exceptions.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(title="Inventory", rows="100", cols="10")

        df = pd.DataFrame(items)
        worksheet.clear()
        if not df.empty:
            worksheet.update([df.columns.values.tolist()] + df.values.tolist())
    except Exception as e:
        st.warning(f"Google Sheets sync failed: {e}")

# --- Helper Functions ---
def filter_items(items, status, query):
    filtered = []
    for item in items:
        status_match = (
            status == "All" or
            (status == "Available" and not item["sold"]) or
            (status == "Sold" and item["sold"])
        )
        query_match = query.lower() in item["name"].lower()
        if status_match and query_match:
            filtered.append(item)
    return filtered

def download_csv(data):
    df = pd.DataFrame(data)
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="inventory.csv">📅 Download Inventory CSV</a>'
    return href

# --- Sidebar Form to Add Item ---
st.sidebar.header("Add New Item")
with st.sidebar.form(key="item_form"):
    name = st.text_input("Item Name")
    brand = st.text_input("Brand")
    size = st.text_input("Size")
    price = st.number_input("Price", min_value=0.0, step=0.5)
    photo = st.file_uploader("Photo", type=["jpg", "jpeg", "png"])
    submit = st.form_submit_button("Add Item")

    if submit and name:
        st.session_state.items.append({
            "name": name,
            "brand": brand,
            "size": size,
            "price": price,
            "sold": False,
            "photo": photo.getvalue() if photo else None,
            "added": datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        upload_to_google_sheets(st.session_state.items)
        st.success("Item added!")

# --- Settings: Enable Google Sheets ---
st.sidebar.header("Settings")
st.session_state.use_gsheets = st.sidebar.checkbox("Enable Google Sheets Sync", value=st.session_state.use_gsheets)
if st.session_state.use_gsheets:
    st.sidebar.success("Google Sheets sync is ON.")
else:
    st.sidebar.info("Google Sheets sync is OFF.")

# --- Main Inventory View ---
st.subheader("📃️ Inventory")
status_filter = st.selectbox("Filter by Status", ["All", "Available", "Sold"])
search_query = st.text_input("Search by Name")

items = st.session_state.items if isinstance(st.session_state.items, list) else []
filtered_items = filter_items(items, status_filter, search_query)

if filtered_items:
    for i, item in enumerate(filtered_items):
        cols = st.columns([1, 2, 1, 1, 1, 1])
        with cols[0]:
            if item["photo"]:
                st.image(item["photo"], width=80)
            else:
                st.write("📦")
        with cols[1]:
            st.markdown(f"**{item['name']}**\n{item['brand']} - {item['size']}")
        with cols[2]:
            st.write(f"${item['price']:.2f}")
        with cols[3]:
            st.write("✅" if item["sold"] else "❌")
        with cols[4]:
            if st.button("Toggle Sold", key=f"sold_{i}"):
                item["sold"] = not item["sold"]
                upload_to_google_sheets(st.session_state.items)
        with cols[5]:
            if st.button("Remove", key=f"remove_{i}"):
                st.session_state.items.remove(item)
                upload_to_google_sheets(st.session_state.items)
                st.experimental_rerun()
else:
    st.info("No items found.")

# --- Download Link ---
st.markdown(download_csv(st.session_state.items), unsafe_allow_html=True)

# --- Promo Generator ---
st.subheader("🎉 Promo Generator")
promo_text = st.text_input("Enter promo description (e.g. Buy 2 Get 1 Free!)")
promo_code = st.text_input("Promo Code (optional)")
if st.button("Generate Promo"):
    st.success(f"Use promo: **{promo_text}** {'with code **' + promo_code + '**' if promo_code else ''}!")

# --- Loyalty Card Generator ---
st.subheader("💳 Loyalty Card")
shop_name = st.text_input("Shop Name")
reward = st.text_input("Reward After N Visits")
visit_count = st.number_input("How many visits to reward?", min_value=1, step=1)
if st.button("Generate Loyalty Card"):
    st.markdown(f"**{shop_name} Loyalty Card**\n\n⭐ Collect a star on each visit!\n⭐ After **{visit_count}** visits, earn: **{reward}**")

# --- Google Sheets Connection Status ---
st.markdown("---")
if st.session_state.use_gsheets:
    st.success("🔗 Google Sheets is connected for persistent backup!")
else:
    st.info("📁 Using local memory only. Data will reset on refresh.")
