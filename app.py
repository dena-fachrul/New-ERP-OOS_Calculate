import streamlit as st
import pandas as pd
import io
from datetime import datetime

# Configure Streamlit page
st.set_page_config(
    page_title="OOS Data Processor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Dark Theme CSS
st.markdown("""
<style>
    :root {
        --primary: #1f77b4;
        --secondary: #ff7f0e;
        --success: #2ca02c;
        --danger: #d62728;
        --dark-bg: #0e1117;
        --card-bg: #161b22;
        --border: #30363d;
        --text-primary: #c9d1d9;
        --text-secondary: #8b949e;
    }
    
    body, .main {
        background-color: var(--dark-bg);
        color: var(--text-primary);
    }
    
    .header-container {
        background: linear-gradient(135deg, #1f77b4 0%, #1a5f99 100%);
        padding: 2.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.4);
    }
    
    .header-title {
        color: white;
        font-size: 2.8rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .header-subtitle {
        color: rgba(255, 255, 255, 0.95);
        font-size: 1.15rem;
        margin-top: 0.5rem;
        font-weight: 500;
    }
    
    .upload-card {
        background-color: var(--card-bg);
        border: 2px solid var(--border);
        border-radius: 12px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
    }
    
    .upload-card:hover {
        border-color: var(--primary);
        box-shadow: 0 0 20px rgba(31, 119, 180, 0.2);
    }
    
    .card-title {
        color: var(--primary);
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.7rem;
    }
    
    .card-subtitle {
        color: var(--text-secondary);
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 1.2rem;
        margin-bottom: 2rem;
    }
    
    .stat-card {
        background-color: var(--card-bg);
        border-left: 5px solid var(--primary);
        padding: 1.8rem;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-4px);
    }
    
    .stat-label {
        color: var(--text-secondary);
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.8rem;
    }
    
    .stat-value {
        color: var(--primary);
        font-size: 2.2rem;
        font-weight: 800;
    }
    
    .stat-card.success {
        border-left-color: var(--success);
    }
    
    .stat-card.success .stat-value {
        color: var(--success);
    }
    
    .stat-card.warning {
        border-left-color: var(--secondary);
    }
    
    .stat-card.warning .stat-value {
        color: var(--secondary);
    }
    
    .stat-card.danger {
        border-left-color: var(--danger);
    }
    
    .stat-card.danger .stat-value {
        color: var(--danger);
    }
    
    .info-banner {
        background-color: rgba(31, 119, 180, 0.15);
        border-left: 5px solid var(--primary);
        padding: 1.2rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        color: var(--text-primary);
    }
    
    .info-banner.success {
        background-color: rgba(44, 160, 44, 0.15);
        border-left-color: var(--success);
    }
    
    .info-banner.error {
        background-color: rgba(214, 39, 40, 0.15);
        border-left-color: var(--danger);
    }
    
    .section-title {
        color: var(--primary);
        font-size: 1.5rem;
        font-weight: 700;
        margin: 2rem 0 1.5rem 0;
        padding-bottom: 0.8rem;
        border-bottom: 2px solid var(--border);
    }
    
    .button-group {
        display: flex;
        gap: 1rem;
        margin-bottom: 2rem;
    }
    
    .footer-text {
        text-align: center;
        color: var(--text-secondary);
        font-size: 0.9rem;
        margin-top: 3rem;
        padding-top: 2rem;
        border-top: 1px solid var(--border);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data_a' not in st.session_state:
    st.session_state.data_a = None
if 'data_b' not in st.session_state:
    st.session_state.data_b = None
if 'result_data' not in st.session_state:
    st.session_state.result_data = None
if 'stats' not in st.session_state:
    st.session_state.stats = None

# Header
st.markdown("""
<div class="header-container">
    <h1 class="header-title">📊 OOS Data Processor</h1>
    <p class="header-subtitle">Intelligent Out-of-Stock Data Analysis & Cross-Reference Tool</p>
</div>
""", unsafe_allow_html=True)

# Instructions
with st.expander("ℹ️ How It Works", expanded=False):
    st.markdown("""
    **Processing Steps:**
    
    1. **Upload Data A (OOS1)** - Order data with system product codes and online status
    2. **Upload Data B (OOS2)** - Inventory data with SKU and availability information
    3. **Automatic Processing**:
       - Filters out PreSale and OnlineShip orders from Data A
       - Identifies SKUs with zero available inventory in Data B
       - Cross-references matching records
    4. **Download Results** - Export processed data as Excel file
    
    **Output Columns**: Original Order Number, ERP Order Number, Order Status, Platform, Store, Store Group, Order Type, Creator, System Product Code, Estimated Weight, Actual Weight, Weight Unit
    """)

# Upload Section
st.markdown('<h2 class="section-title">📁 Upload Your Data Files</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

# Data A Upload
with col1:
    st.markdown('<div class="upload-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📋 Data A (OOS1)</div>', unsafe_allow_html=True)
    st.markdown('<div class="card-subtitle">Order data with status and SKU information</div>', unsafe_allow_html=True)
    
    uploaded_file_a = st.file_uploader(
        "Choose Data A file",
        type=['xlsx', 'xls', 'csv'],
        key='file_a',
        label_visibility='collapsed'
    )
    
    if uploaded_file_a is not None:
        try:
            if uploaded_file_a.name.endswith('.csv'):
                st.session_state.data_a = pd.read_csv(uploaded_file_a)
            else:
                st.session_state.data_a = pd.read_excel(uploaded_file_a, engine='openpyxl')
            
            st.markdown(f"""
            <div class="info-banner success">
                ✅ <strong>{uploaded_file_a.name}</strong> loaded successfully
                <br><small>{len(st.session_state.data_a):,} rows × {len(st.session_state.data_a.columns)} columns</small>
            </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f"""
            <div class="info-banner error">
                ❌ Error: {str(e)}
            </div>
            """, unsafe_allow_html=True)
            st.session_state.data_a = None
    
    st.markdown('</div>', unsafe_allow_html=True)

# Data B Upload
with col2:
    st.markdown('<div class="upload-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📋 Data B (OOS2)</div>', unsafe_allow_html=True)
    st.markdown('<div class="card-subtitle">Inventory data with SKU and availability</div>', unsafe_allow_html=True)
    
    uploaded_file_b = st.file_uploader(
        "Choose Data B file",
        type=['xlsx', 'xls', 'csv'],
        key='file_b',
        label_visibility='collapsed'
    )
    
    if uploaded_file_b is not None:
        try:
            if uploaded_file_b.name.endswith('.csv'):
                st.session_state.data_b = pd.read_csv(uploaded_file_b)
            else:
                st.session_state.data_b = pd.read_excel(uploaded_file_b, engine='openpyxl')
            
            st.markdown(f"""
            <div class="info-banner success">
                ✅ <strong>{uploaded_file_b.name}</strong> loaded successfully
                <br><small>{len(st.session_state.data_b):,} rows × {len(st.session_state.data_b.columns)} columns</small>
            </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f"""
            <div class="info-banner error">
                ❌ Error: {str(e)}
            </div>
            """, unsafe_allow_html=True)
            st.session_state.data_b = None
    
    st.markdown('</div>', unsafe_allow_html=True)

# Process Section
st.markdown('<h2 class="section-title">⚙️ Process Data</h2>', unsafe_allow_html=True)

col_process, col_reset = st.columns([3, 1])

with col_process:
    if st.button("🔄 Process Data", use_container_width=True, key='process_btn', type='primary'):
        if st.session_state.data_a is None or st.session_state.data_b is None:
            st.markdown("""
            <div class="info-banner error">
                ❌ Please upload both Data A and Data B files before processing
            </div>
            """, unsafe_allow_html=True)
        else:
            try:
                with st.spinner('🔄 Processing data...'):
                    # Get column names
                    cols_a = st.session_state.data_a.columns.tolist()
                    cols_b = st.session_state.data_b.columns.tolist()
                    
                    # Find the correct columns
                    online_status_col = next((col for col in cols_a if 'Online Status' in col or 'online' in col.lower()), None)
                    sku_col_a = next((col for col in cols_a if 'System Product Code' in col or 'sku' in col.lower()), None)
                    sku_col_b = next((col for col in cols_b if 'SKU' in col or 'sku' in col.lower()), None)
                    inventory_col = next((col for col in cols_b if 'Available inventory' in col or 'available' in col.lower()), None)
                    
                    if not all([online_status_col, sku_col_a, sku_col_b, inventory_col]):
                        st.markdown(f"""
                        <div class="info-banner error">
                            ❌ Could not find required columns:
                            <br>• Online Status: {online_status_col}
                            <br>• SKU (Data A): {sku_col_a}
                            <br>• SKU (Data B): {sku_col_b}
                            <br>• Available Inventory: {inventory_col}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        # Step 1: Filter Data A
                        original_count = len(st.session_state.data_a)
                        filtered_a = st.session_state.data_a[
                            ~st.session_state.data_a[online_status_col].astype(str).str.contains('PreSale|OnlineShip', case=False, na=False)
                        ].copy()
                        filtered_count = len(filtered_a)
                        
                        # Step 2: Find zero-inventory SKUs
                        zero_inventory_skus = st.session_state.data_b[
                            st.session_state.data_b[inventory_col] == 0
                        ][sku_col_b].unique().tolist()
                        zero_inventory_count = len(zero_inventory_skus)
                        
                        # Step 3: Cross-reference
                        result = filtered_a[
                            filtered_a[sku_col_a].isin(zero_inventory_skus)
                        ].copy()
                        result_count = len(result)
                        
                        # Select output columns
                        output_cols = [col for col in [
                            next((c for c in cols_a if 'Original Order Number' in c), None),
                            next((c for c in cols_a if 'ERP Order Number' in c), None),
                            next((c for c in cols_a if 'Order Status' in c), None),
                            next((c for c in cols_a if 'Platform' in c), None),
                            next((c for c in cols_a if 'Store' in c and 'Group' not in c), None),
                            next((c for c in cols_a if 'Store Group' in c), None),
                            next((c for c in cols_a if 'Order Type' in c), None),
                            next((c for c in cols_a if 'Creator' in c), None),
                            sku_col_a,
                            next((c for c in cols_a if 'Estimated' in c and 'Weight' in c), None),
                            next((c for c in cols_a if 'Actual' in c and 'Weight' in c), None),
                            next((c for c in cols_a if 'Weight Unit' in c), None),
                        ] if col is not None]
                        
                        st.session_state.result_data = result[output_cols] if output_cols else result
                        st.session_state.stats = {
                            'original': original_count,
                            'filtered': filtered_count,
                            'zero_inventory': zero_inventory_count,
                            'result': result_count
                        }
                        
                        st.markdown("""
                        <div class="info-banner success">
                            ✅ Data processed successfully!
                        </div>
                        """, unsafe_allow_html=True)
                        
            except Exception as e:
                st.markdown(f"""
                <div class="info-banner error">
                    ❌ Processing error: {str(e)}
                </div>
                """, unsafe_allow_html=True)

with col_reset:
    if st.button("🔄 Reset", use_container_width=True, key='reset_btn'):
        st.session_state.data_a = None
        st.session_state.data_b = None
        st.session_state.result_data = None
        st.session_state.stats = None
        st.rerun()

# Display Statistics
if st.session_state.stats:
    st.markdown('<h2 class="section-title">📈 Processing Statistics</h2>', unsafe_allow_html=True)
    
    stats = st.session_state.stats
    
    st.markdown('<div class="stats-grid">', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Data A Original</div>
            <div class="stat-value">{stats['original']:,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">After Filter</div>
            <div class="stat-value">{stats['filtered']:,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card warning">
            <div class="stat-label">Zero Inventory SKUs</div>
            <div class="stat-value">{stats['zero_inventory']:,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card success">
            <div class="stat-label">Final Result</div>
            <div class="stat-value">{stats['result']:,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Display Results
if st.session_state.result_data is not None:
    st.markdown('<h2 class="section-title">📋 Result Preview</h2>', unsafe_allow_html=True)
    
    st.dataframe(
        st.session_state.result_data,
        use_container_width=True,
        height=400
    )
    
    st.markdown('<h2 class="section-title">📥 Download Results</h2>', unsafe_allow_html=True)
    
    # Create Excel file
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        st.session_state.result_data.to_excel(writer, sheet_name='Results', index=False)
    
    excel_buffer.seek(0)
    
    col_download, col_info = st.columns([3, 1])
    
    with col_download:
        st.download_button(
            label="📥 Download Results as Excel",
            data=excel_buffer.getvalue(),
            file_name=f"OOS_Results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            type='primary'
        )
    
    with col_info:
        st.metric("Total Rows", len(st.session_state.result_data))

# Footer
st.markdown("""
<div class="footer-text">
    <p>🚀 OOS Data Processor v2.0 | Professional Inventory Analysis Tool</p>
    <p>Built with Streamlit | Dark Theme | Last Updated: 2026</p>
</div>
""", unsafe_allow_html=True)
