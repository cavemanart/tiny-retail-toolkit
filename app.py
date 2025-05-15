import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Tiny Retail Toolkit", layout="wide")

st.title("👕 Tiny Retail Toolkit")
st.caption("A simple inventory manager for small children's resale shops.")

# Initialize session state
if "items" not in st.session_state:
    st.session_state.items = []

# Add item form
with st.form("add_item_form", clear_on_submit=True):
    st.subheader("➕ Add New Item")
    name = st.text_input("Item name", max_chars=50)
    price = st.number_input("Price ($)", min_value=0.0, format="%.2f")
    photo = st.file_uploader("Optional photo", type=["jpg", "jpeg", "png"])
    submitted = st.form_submit_button("Add Item")
    if submitted and name:
        st.session_state.items.append({
            "name": name,
            "price": price,
            "sold": False,
            "added": datetime.now().strftime("%Y-%m-%d"),
            "photo": photo.name if photo else "",
        })
        st.success(f"Added: {name}")

# Sidebar filters
st.sidebar.header("🔍 Filters & Tools")
status_filter = st.sidebar.selectbox("Filter by status", ["All", "Available", "Sold"])
search_query = st.sidebar.text_input("Search by name")

# Filter logic
filtered_items = [
    item for item in st.session_state.items
    if (status_filter == "All"
        or (status_filter == "Available" and not item["sold"])
        or (status_filter == "Sold" and item["sold"]))
    and (search_query.lower() in item["name"].lower())
]

# Inventory overview
st.subheader("📦 Inventory")
if filtered_items:
    for i, item in enumerate(filtered_items):
        cols = st.columns([4, 1, 1, 1])
        status = "✅ Sold" if item["sold"] else "🟢 Available"
        cols[0].markdown(f"**{item['name']}**  \n${item['price']}  \n*Added:* {item['added']}  \n*Status:* {status}")
        if cols[1].button("Toggle", key=f"toggle_{i}"):
            original_index = st.session_state.items.index(item)
            st.session_state.items[original_index]["sold"] = not item["sold"]
            st.experimental_rerun()
        if cols[2].button("🗑️", key=f"delete_{i}"):
            original_index = st.session_state.items.index(item)
            st.session_state.items.pop(original_index)
            st.experimental_rerun()
else:
    st.info("No items match your filters.")

# Export to CSV
if st.session_state.items:
    df = pd.DataFrame(st.session_state.items)
    st.download_button("⬇️ Export Inventory to CSV", data=df.to_csv(index=False), file_name="inventory.csv", mime="text/csv")

# Summary stats
st.sidebar.markdown("---")
st.sidebar.subheader("📊 Summary")
total = len(st.session_state.items)
sold = sum(item["sold"] for item in st.session_state.items)
available = total - sold
value = sum(item["price"] for item in st.session_state.items if not item["sold"])

st.sidebar.metric("Total Items", total)
st.sidebar.metric("Available", available)
st.sidebar.metric("Sold", sold)
st.sidebar.metric("Unsold Value ($)", f"${value:.2f}")
