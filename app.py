import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
import base64

st.set_page_config(page_title="Tiny Retail Toolkit", layout="wide")
st.title("🧸 Tiny Retail Toolkit")

# --- Session state init ---
if "items" not in st.session_state or not isinstance(st.session_state.items, list):
    st.session_state.items = []

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
    href = f'<a href="data:file/csv;base64,{b64}" download="inventory.csv">📥 Download Inventory CSV</a>'
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
        st.success("Item added!")

# --- Main Inventory View ---
st.subheader("🗃️ Inventory")
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
        with cols[5]:
            if st.button("Remove", key=f"remove_{i}"):
                st.session_state.items.remove(item)
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

# --- Google Sheets Connection Placeholder ---
st.markdown("---")
st.info("🔗 Google Sheets integration coming soon for persistent backup!")
