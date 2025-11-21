import streamlit as st
import requests
from supabase import create_client, Client
import pandas as pd
from datetime import datetime

# ====================================
# SUPABASE CREDENTIALS - REPLACE THESE
# ====================================
SUPABASE_URL = "https://kwxsnefimgoxypobbrgr.supabase.co"  # Example: https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt3eHNuZWZpbWdveHlwb2JicmdyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjM2ODMwMzUsImV4cCI6MjA3OTI1OTAzNX0.yoXJUjChHiIT6NrdA6OTaB0Fn6nLnRVGjJCQvLgrl3s"  # Your anon/public key

# ====================================
# INITIALIZE SUPABASE CLIENT
# ====================================
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error(f"Failed to connect to Supabase: {e}")
    st.stop()

# ====================================
# PLATZI API BASE URL
# ====================================
PLATZI_API_URL = "https://api.escuelajs.co/api/v1"

# ====================================
# PAGE CONFIGURATION
# ====================================
st.set_page_config(
    page_title="Platzi API + Supabase App",
    page_icon="🛍️",
    layout="wide"
)

st.title("🛍️ Platzi API + Supabase Integration")
st.markdown("---")

# ====================================
# SIDEBAR NAVIGATION
# ====================================
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Choose a section:",
    ["Fetch Products from Platzi", "Save to Supabase", "View Supabase Data", "Delete from Supabase"]
)

# ====================================
# PAGE 1: FETCH PRODUCTS FROM PLATZI
# ====================================
if page == "Fetch Products from Platzi":
    st.header("📦 Fetch Products from Platzi API")
    
    col1, col2 = st.columns(2)
    
    with col1:
        limit = st.number_input("Number of products to fetch:", min_value=1, max_value=50, value=10)
    
    with col2:
        offset = st.number_input("Offset (skip products):", min_value=0, value=0)
    
    if st.button("Fetch Products", type="primary"):
        with st.spinner("Fetching products from Platzi API..."):
            try:
                response = requests.get(
                    f"{PLATZI_API_URL}/products",
                    params={"limit": limit, "offset": offset}
                )
                
                if response.status_code == 200:
                    products = response.json()
                    st.success(f"Successfully fetched {len(products)} products!")
                    
                    # Store in session state for later use
                    st.session_state['fetched_products'] = products
                    
                    # Display products
                    for product in products:
                        with st.expander(f"🏷️ {product['title']} - ${product['price']}"):
                            col1, col2 = st.columns([1, 2])
                            
                            with col1:
                                if product.get('images') and len(product['images']) > 0:
                                    st.image(product['images'][0], width=200)
                            
                            with col2:
                                st.write(f"**ID:** {product['id']}")
                                st.write(f"**Price:** ${product['price']}")
                                st.write(f"**Description:** {product['description']}")
                                st.write(f"**Category:** {product['category']['name']}")
                else:
                    st.error(f"Error fetching products: {response.status_code}")
            
            except Exception as e:
                st.error(f"An error occurred: {e}")

# ====================================
# PAGE 2: SAVE TO SUPABASE
# ====================================
elif page == "Save to Supabase":
    st.header("💾 Save Products to Supabase")
    
    st.info("Make sure you have a table named 'products' in your Supabase database with columns: id, title, price, description, category, image_url, created_at")
    
    # Manual entry option
    st.subheader("Option 1: Manual Entry")
    
    with st.form("manual_entry_form"):
        title = st.text_input("Product Title")
        price = st.number_input("Price", min_value=0.0, step=0.01)
        description = st.text_area("Description")
        category = st.text_input("Category")
        image_url = st.text_input("Image URL (optional)")
        
        submit_manual = st.form_submit_button("Save to Supabase")
        
        if submit_manual:
            if title and price and description and category:
                try:
                    data = {
                        "title": title,
                        "price": price,
                        "description": description,
                        "category": category,
                        "image_url": image_url,
                        "created_at": datetime.now().isoformat()
                    }
                    
                    result = supabase.table("products").insert(data).execute()
                    st.success("✅ Product saved to Supabase successfully!")
                    st.json(result.data)
                
                except Exception as e:
                    st.error(f"Error saving to Supabase: {e}")
            else:
                st.warning("Please fill in all required fields!")
    
    st.markdown("---")
    
    # Save fetched products option
    st.subheader("Option 2: Save Fetched Products")
    
    if 'fetched_products' in st.session_state and st.session_state['fetched_products']:
        st.write(f"You have {len(st.session_state['fetched_products'])} fetched products ready to save.")
        
        if st.button("Save All Fetched Products to Supabase", type="primary"):
            with st.spinner("Saving products to Supabase..."):
                try:
                    success_count = 0
                    error_count = 0
                    
                    for product in st.session_state['fetched_products']:
                        try:
                            data = {
                                "title": product['title'],
                                "price": product['price'],
                                "description": product['description'],
                                "category": product['category']['name'],
                                "image_url": product['images'][0] if product.get('images') else None,
                                "created_at": datetime.now().isoformat()
                            }
                            
                            supabase.table("products").insert(data).execute()
                            success_count += 1
                        
                        except Exception as e:
                            error_count += 1
                            st.warning(f"Failed to save '{product['title']}': {e}")
                    
                    st.success(f"✅ Saved {success_count} products successfully!")
                    if error_count > 0:
                        st.warning(f"⚠️ Failed to save {error_count} products.")
                
                except Exception as e:
                    st.error(f"Error during batch save: {e}")
    else:
        st.info("No products fetched yet. Go to 'Fetch Products from Platzi' first!")

# ====================================
# PAGE 3: VIEW SUPABASE DATA
# ====================================
elif page == "View Supabase Data":
    st.header("📊 View Data from Supabase")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("Products in Database")
    
    with col2:
        if st.button("🔄 Refresh Data"):
            st.rerun()
    
    try:
        # Fetch all products from Supabase
        response = supabase.table("products").select("*").execute()
        
        if response.data:
            st.success(f"Found {len(response.data)} products in database")
            
            # Convert to DataFrame for better display
            df = pd.DataFrame(response.data)
            
            # Display as interactive table
            st.dataframe(df, use_container_width=True)
            
            # Show individual products with details
            st.markdown("---")
            st.subheader("Detailed View")
            
            for product in response.data:
                with st.expander(f"🏷️ {product['title']} - ${product['price']}"):
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        if product.get('image_url'):
                            st.image(product['image_url'], width=200)
                    
                    with col2:
                        st.write(f"**ID:** {product['id']}")
                        st.write(f"**Price:** ${product['price']}")
                        st.write(f"**Description:** {product['description']}")
                        st.write(f"**Category:** {product['category']}")
                        st.write(f"**Created:** {product['created_at']}")
        else:
            st.info("No products found in database. Add some products first!")
    
    except Exception as e:
        st.error(f"Error fetching data from Supabase: {e}")

# ====================================
# PAGE 4: DELETE FROM SUPABASE
# ====================================
elif page == "Delete from Supabase":
    st.header("🗑️ Delete Products from Supabase")
    
    try:
        # Fetch all products
        response = supabase.table("products").select("*").execute()
        
        if response.data:
            st.write(f"Total products: {len(response.data)}")
            
            # Option 1: Delete by ID
            st.subheader("Delete by Product ID")
            
            product_ids = [str(p['id']) for p in response.data]
            
            selected_id = st.selectbox("Select Product ID to delete:", product_ids)
            
            if st.button("Delete Selected Product", type="primary"):
                try:
                    supabase.table("products").delete().eq("id", selected_id).execute()
                    st.success(f"✅ Product with ID {selected_id} deleted successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error deleting product: {e}")
            
            st.markdown("---")
            
            # Option 2: Delete all
            st.subheader("⚠️ Danger Zone")
            st.warning("This will delete ALL products from the database!")
            
            confirm = st.checkbox("I understand this action cannot be undone")
            
            if confirm:
                if st.button("Delete All Products", type="secondary"):
                    try:
                        # Delete all records
                        for product in response.data:
                            supabase.table("products").delete().eq("id", product['id']).execute()
                        
                        st.success("✅ All products deleted successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error deleting products: {e}")
        else:
            st.info("No products in database to delete.")
    
    except Exception as e:
        st.error(f"Error fetching products: {e}")

# ====================================
# FOOTER
# ====================================
st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip:** Make sure your Supabase credentials are correctly configured at the top of the script!")
