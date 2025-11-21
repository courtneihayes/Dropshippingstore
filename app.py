import streamlit as st
import requests
from supabase import create_client, Client
import pandas as pd
from datetime import datetime

# ====================================
# SUPABASE CREDENTIALS - REPLACE THESE
# ====================================
SUPABASE_URL = "https://kwxsnefimgoxypobbrgr.supabase.co"  # Example: https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY = "sb_publishable_MSmQunHItsa1NGhLOVTNDA_S6vFVn8s"  # Your anon/public key

# ====================================
# INITIALIZE SUPABASE CLIENT
# ====================================
try:
    supabase: Client = create_client(https://kwxsnefimgoxypobbrgr.supabase.co, eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt3eHNuZWZpbWdveHlwb2JicmdyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjM2ODMwMzUsImV4cCI6MjA3OTI1OTAzNX0.yoXJUjChHiIT6NrdA6OTaB0Fn6nLnRVGjJCQvLgrl3s)
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
    [
        "Fetch Products from Platzi",
        "Write to Supabase",
        "Read from Supabase",
        "Update Supabase",
        "Delete from Supabase"
    ]
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
# PAGE 2: WRITE TO SUPABASE
# ====================================
elif page == "Write to Supabase":
    st.header("✍️ Write to Supabase")
    
    st.info("💡 Insert new records into your Supabase database")
    
    tab1, tab2 = st.tabs(["Manual Entry", "Bulk Insert from API"])
    
    # TAB 1: Manual Entry
    with tab1:
        st.subheader("Single Product Entry")
        
        with st.form("manual_entry_form"):
            title = st.text_input("Product Title *")
            price = st.number_input("Price *", min_value=0.0, step=0.01)
            description = st.text_area("Description *")
            category = st.text_input("Category *")
            image_url = st.text_input("Image URL (optional)")
            
            submit_manual = st.form_submit_button("💾 Write to Supabase", type="primary")
            
            if submit_manual:
                if title and price and description and category:
                    try:
                        data = {
                            "title": title,
                            "price": price,
                            "description": description,
                            "category": category,
                            "image_url": image_url if image_url else None,
                            "created_at": datetime.now().isoformat()
                        }
                        
                        result = supabase.table("products").insert(data).execute()
                        st.success("✅ Product written to Supabase successfully!")
                        st.json(result.data)
                    
                    except Exception as e:
                        st.error(f"❌ Error writing to Supabase: {e}")
                else:
                    st.warning("⚠️ Please fill in all required fields marked with *")
    
    # TAB 2: Bulk Insert
    with tab2:
        st.subheader("Bulk Insert from Fetched Products")
        
        if 'fetched_products' in st.session_state and st.session_state['fetched_products']:
            st.write(f"📦 You have **{len(st.session_state['fetched_products'])}** fetched products ready to write.")
            
            if st.button("💾 Write All to Supabase", type="primary"):
                with st.spinner("Writing products to Supabase..."):
                    try:
                        success_count = 0
                        error_count = 0
                        
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        for idx, product in enumerate(st.session_state['fetched_products']):
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
                                st.warning(f"⚠️ Failed to write '{product['title']}': {e}")
                            
                            # Update progress
                            progress = (idx + 1) / len(st.session_state['fetched_products'])
                            progress_bar.progress(progress)
                            status_text.text(f"Processing: {idx + 1}/{len(st.session_state['fetched_products'])}")
                        
                        progress_bar.empty()
                        status_text.empty()
                        
                        st.success(f"✅ Successfully wrote {success_count} products to Supabase!")
                        if error_count > 0:
                            st.warning(f"⚠️ Failed to write {error_count} products.")
                    
                    except Exception as e:
                        st.error(f"❌ Error during bulk write: {e}")
        else:
            st.info("📭 No products fetched yet. Go to 'Fetch Products from Platzi' first!")

# ====================================
# PAGE 3: READ FROM SUPABASE
# ====================================
elif page == "Read from Supabase":
    st.header("📖 Read from Supabase")
    
    st.info("💡 Query and retrieve records from your Supabase database")
    
    tab1, tab2, tab3, tab4 = st.tabs(["All Records", "Filter by ID", "Filter by Price", "Search by Name"])
    
    # TAB 1: Read All
    with tab1:
        st.subheader("All Products")
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            if st.button("🔄 Refresh", key="refresh_all"):
                st.rerun()
        
        try:
            response = supabase.table("products").select("*").execute()
            
            if response.data:
                st.success(f"📊 Found **{len(response.data)}** products in database")
                
                # Display as DataFrame
                df = pd.DataFrame(response.data)
                st.dataframe(df, use_container_width=True)
                
                # Download option
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download as CSV",
                    data=csv,
                    file_name="products.csv",
                    mime="text/csv"
                )
            else:
                st.info("📭 No products found in database")
        
        except Exception as e:
            st.error(f"❌ Error reading from Supabase: {e}")
    
    # TAB 2: Filter by ID
    with tab2:
        st.subheader("Read Product by ID")
        
        product_id = st.number_input("Enter Product ID:", min_value=1, step=1)
        
        if st.button("🔍 Read by ID", type="primary"):
            try:
                response = supabase.table("products").select("*").eq("id", product_id).execute()
                
                if response.data:
                    st.success(f"✅ Found product with ID: {product_id}")
                    product = response.data[0]
                    
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        if product.get('image_url'):
                            st.image(product['image_url'], width=250)
                    
                    with col2:
                        st.write(f"**Title:** {product['title']}")
                        st.write(f"**Price:** ${product['price']}")
                        st.write(f"**Description:** {product['description']}")
                        st.write(f"**Category:** {product['category']}")
                        st.write(f"**Created:** {product['created_at']}")
                    
                    st.json(product)
                else:
                    st.warning(f"⚠️ No product found with ID: {product_id}")
            
            except Exception as e:
                st.error(f"❌ Error reading from Supabase: {e}")
    
    # TAB 3: Filter by Price
    with tab3:
        st.subheader("Read Products by Price Range")
        
        col1, col2 = st.columns(2)
        
        with col1:
            min_price = st.number_input("Min Price:", min_value=0.0, step=10.0, value=0.0)
        
        with col2:
            max_price = st.number_input("Max Price:", min_value=0.0, step=10.0, value=1000.0)
        
        if st.button("🔍 Read by Price Range", type="primary"):
            try:
                response = supabase.table("products").select("*").gte("price", min_price).lte("price", max_price).execute()
                
                if response.data:
                    st.success(f"📊 Found **{len(response.data)}** products between ${min_price} and ${max_price}")
                    
                    df = pd.DataFrame(response.data)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.warning(f"⚠️ No products found in price range ${min_price} - ${max_price}")
            
            except Exception as e:
                st.error(f"❌ Error reading from Supabase: {e}")
    
    # TAB 4: Search by Name
    with tab4:
        st.subheader("Search Products by Title")
        
        search_term = st.text_input("Search term:")
        
        if st.button("🔍 Search", type="primary"):
            if search_term:
                try:
                    response = supabase.table("products").select("*").ilike("title", f"%{search_term}%").execute()
                    
                    if response.data:
                        st.success(f"📊 Found **{len(response.data)}** products matching '{search_term}'")
                        
                        df = pd.DataFrame(response.data)
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.warning(f"⚠️ No products found matching '{search_term}'")
                
                except Exception as e:
                    st.error(f"❌ Error searching Supabase: {e}")
            else:
                st.warning("⚠️ Please enter a search term")

# ====================================
# PAGE 4: UPDATE SUPABASE
# ====================================
elif page == "Update Supabase":
    st.header("✏️ Update Supabase Records")
    
    st.info("💡 Modify existing records in your Supabase database")
    
    # First, select product to update
    st.subheader("Step 1: Select Product to Update")
    
    try:
        response = supabase.table("products").select("id, title").execute()
        
        if response.data:
            product_options = {f"{p['id']} - {p['title']}": p['id'] for p in response.data}
            
            selected_product = st.selectbox("Select Product:", list(product_options.keys()))
            selected_id = product_options[selected_product]
            
            if st.button("📖 Load Product Data"):
                # Fetch full product data
                product_response = supabase.table("products").select("*").eq("id", selected_id).execute()
                
                if product_response.data:
                    st.session_state['update_product'] = product_response.data[0]
                    st.success("✅ Product data loaded!")
            
            # Step 2: Update form
            if 'update_product' in st.session_state:
                st.markdown("---")
                st.subheader("Step 2: Update Product Details")
                
                product = st.session_state['update_product']
                
                with st.form("update_form"):
                    new_title = st.text_input("Title", value=product['title'])
                    new_price = st.number_input("Price", value=float(product['price']), step=0.01)
                    new_description = st.text_area("Description", value=product['description'])
                    new_category = st.text_input("Category", value=product['category'])
                    new_image_url = st.text_input("Image URL", value=product.get('image_url', ''))
                    
                    submit_update = st.form_submit_button("💾 Update in Supabase", type="primary")
                    
                    if submit_update:
                        try:
                            updated_data = {
                                "title": new_title,
                                "price": new_price,
                                "description": new_description,
                                "category": new_category,
                                "image_url": new_image_url if new_image_url else None
                            }
                            
                            result = supabase.table("products").update(updated_data).eq("id", selected_id).execute()
                            st.success(f"✅ Product ID {selected_id} updated successfully!")
                            st.json(result.data)
                            
                            # Clear session state
                            del st.session_state['update_product']
                            st.rerun()
                        
                        except Exception as e:
                            st.error(f"❌ Error updating Supabase: {e}")
        else:
            st.info("📭 No products in database to update")
    
    except Exception as e:
        st.error(f"❌ Error fetching products: {e}")

# ====================================
# PAGE 5: DELETE FROM SUPABASE
# ====================================
elif page == "Delete from Supabase":
    st.header("🗑️ Delete from Supabase")
    
    st.info("💡 Remove records from your Supabase database")
    
    tab1, tab2 = st.tabs(["Delete by ID", "Delete All"])
    
    # TAB 1: Delete by ID
    with tab1:
