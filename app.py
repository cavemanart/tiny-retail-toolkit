import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Tiny Retail Toolkit", layout="wide")

st.title("👕 Tiny Retail Toolkit")
st.caption("A simple inventory manager for small children's resale shops.")

# Initialize session state list once
if "items" not in st.session_state:
    st.session_state.items = []

# Add item form
with st.form("add_item_form", clear_on_submit=True):
    st.subheader("➕ Add New Item")
    name = st.text_input("Item name", max_chars=50)
    price = st.number_input("Price ($)", min_value=0.0, format="%.2f")
    photo = st.file_uploader("Take or upload photo", type=["jpg", "jpeg", "png"])
    submitted = st.form_submit_button("Add Item")

    if submitted:
        if not name.strip():
            st.error("Please enter a valid item name.")
        else:
            photo_bytes = photo.getvalue() if photo else None
            photo_name = photo.name if photo else ""
            st.session_state.items.append({
                "name": name.strip(),
                "price": price,
                "sold": False,
                "added": datetime.now().strftime("%Y-%m-%d"),
                "photo_bytes": photo_bytes,
                "photo_name": photo_name,
            })
            st.success(f"Added: {name.strip()}")
            st.experimental_rerun()  # Refresh to update item list immediately

# Sidebar filters
st.sidebar.header("🔍 Filters & Tools")
status_filter = st.sidebar.selectbox("Filter by status", ["All", "Available", "Sold"])
search_query = st.sidebar.text_input("Search by name")

# Filter items
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

filtered_items = filter_items(st.session_state.items, status_filter, search_query)

# Inventory display
st.subheader("📦 Inventory")
if filtered_items:
    for i, item in enumerate(filtered_items):
        cols = st.columns([2, 4, 1, 1])
        
        if item["photo_bytes"]:
            cols[0].image(item["photo_bytes"], width=80)
        else:
            cols[0].write("No photo")
        
        status = "✅ Sold" if item["sold"] else "🟢 Available"
        cols[1].markdown(
            f"**{item['name']}**  \n"
            f"Price: ${item['price']:.2f}  \n"
            f"*Added:* {item['added']}  \n"
            f"*Status:* {status}"
        )
        
        if cols[2].button("Toggle Sold", key=f"toggle_{i}"):
            # Find original index in session state items
            original_index = st.session_state.items.index(item)
            st.session_state.items[original_index]["sold"] = not item["sold"]
            st.experimental_rerun()
        
        if cols[3].button("🗑️ Delete", key=f"delete_{i}"):
            original_index = st.session_state.items.index(item)
            st.session_state.items.pop(original_index)
            st.experimental_rerun()
else:
    st.info("No items match your filters.")

# Export inventory CSV (no photos)
if st.session_state.items:
    df = pd.DataFrame([
        {
            "name": item["name"],
            "price": item["price"],
            "sold": item["sold"],
            "added": item["added"],
            "photo_name": item["photo_name"],
        }
        for item in st.session_state.items
    ])
    csv_data = df.to_csv(index=False)
    st.download_button(
        label="⬇️ Export Inventory to CSV",
        data=csv_data,
        file_name="inventory.csv",
        mime="text/csv"
    )

# Sidebar summary
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
