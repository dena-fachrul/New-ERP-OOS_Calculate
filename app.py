import streamlit as st
import pandas as pd
import io
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="OOS Data Processor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for professional dark theme
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    
    [data-testid="stHeader"] {
        background-color: #0d1117;
    }
    
    .main {
        background-color: #0d1117;
    }
    
    /* Header Styling */
    .header-section {
        background: linear-gradient(135deg, #1f77b4 0%, #0d47a1 100%);
        padding: 3rem 2rem;
        border-radius: 12px;
        margin-bottom: 2.5rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        text-align: center;
    }
    
    .header-title {
        color: #ffffff;
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    }
    
    .header-subtitle {
        color: rgba(255, 255, 255, 0.95);
        font-size: 1.2rem;
        font-weight: 500;
        letter-spacing: 0.5px;
    }
    
    /* Upload Section */
    .upload-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 2rem;
        margin-bottom: 2.5rem;
    }
    
    .upload-box {
        background-color: #161b22;
        border: 2px solid #30363d;
        border-radius: 12px;
        padding: 2rem;
        transition: all 0.3s ease;
    }
    
    .upload-box:hover {
        border-color: #1f77b4;
        box-shadow: 0 0 20px rgba(31, 119, 180, 0.2);
        transform: translateY(-2px);
    }
    
    .upload-title {
        color: #1f77b4;
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.7rem;
    }
    
    .upload-subtitle {
        color: #8b949e;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }
    
    /* Status Messages */
    .status-success {
        background-color: rgba(44, 160, 44, 0.15);
        border-left: 4px solid #2ca02c;
        padding: 1rem;
        border-radius: 6px;
        color: #85e89d;
        margin-top: 1rem;
        font-size: 0.9rem;
    }
    
    .status-error {
        background-color: rgba(214, 39, 40, 0.15);
        border-left: 4px solid #d62728;
        padding: 1rem;
        border-radius: 6px;
        color: #f85149;
        margin-top: 1rem;
        font-size: 0.9rem;
    }
    
    /* Section Title */
    .section-title {
        color: #1f77b4;
        font-size: 1.6rem;
        font-weight: 700;
        margin: 2.5rem 0 1.5rem 0;
        padding-bottom: 1rem;
        border-bottom: 2px solid #30363d;
        display: flex;
        align-items: center;
        gap: 0.8rem;
    }
    
    /* Button Styling */
    .stButton > button {
        background-color: #1f77b4 !important;
        color: white !important;
        border: none !important;
        padding: 0.75rem 2rem !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    
    .stButton > button:hover {
        background-color: #1a5f99 !important;
        box-shadow: 0 8px 16px rgba(31, 119, 180, 0.3) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Stats Grid */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .stat-box {
        background-color: #161b22;
        border-left: 5px solid #1f77b4;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease;
    }
    
    .stat-box:hover {
        transform: translateY(-4px);
    }
    
    .stat-label {
        color: #8b949e;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.8rem;
    }
    
    .stat-value {
        color: #1f77b4;
        font-size: 2.5rem;
        font-weight: 800;
    }
    
    .stat-box.success {
        border-left-color: #2ca02c;
    }
    
    .stat-box.success .stat-value {
        color: #2ca02c;
    }
    
    .stat-box.warning {
        border-left-color: #ff7f0e;
    }
    
    .stat-box.warning .stat-value {
        color: #ff7f0e;
    }
    
    /* Data Table */
    .dataframe {
        background-color: #161b22 !important;
        color: #c9d1d9 !important;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #8b949e;
        font-size: 0.9rem;
        margin-top: 3rem;
        padding-top: 2rem;
        border-top: 1px solid #30363d;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .upload-container {
            grid-template-columns: 1fr;
        }
        
        .header-title {
            font-size: 2rem;
        }
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
<div class="header-section">
    <div class="header-title">📊 OOS Data Processor</div>
    <div class="header-subtitle">Intelligent Out-of-Stock Inventory Analysis & Cross-Reference System</div>
</div>
""", unsafe_allow_html=True)

# Info Section
with st.expander("ℹ️ How to Use This Tool", expanded=False):
    st.markdown("""
    ### Processing Steps:
    
    **1. Upload Files**
    - **Data A (OOS1)**: Order data containing system product codes and online status
    - **Data B (OOS2)**: Inventory data with SKU and availability information
    
    **2. Automatic Processing**
    - Filters out PreSale and OnlineShip orders from Data A
    - Identifies SKUs with zero available inventory in Data B
    - Cross-references matching records
    
    **3. Download Results**
    - Export processed data as Excel file
    - Includes key columns: Order Number, Status, Platform, Store, SKU, Weight info
    
    ### Output Information:
    - **Data A Original**: Total records in uploaded file
    - **After Filter**: Records after removing PreSale/OnlineShip
    - **Zero Inventory SKUs**: Unique SKUs with 0 available inventory
    - **Final Result**: Matching records that meet all criteria
    """)

# Upload Section
st.markdown('<div class="section-title">📁 Upload Your Data Files</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="upload-box">', unsafe_allow_html=True)
    st.markdown('<div class="upload-title">📋 Data A (OOS1)</div>', unsafe_allow_html=True)
    st.markdown('<div class="upload-subtitle">Order data with status and SKU</div>', unsafe_allow_html=True)
    
    uploaded_file_a = st.file_uploader(
        "Upload Data A",
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
            <div class="status-success">
                ✅ {uploaded_file_a.name} loaded successfully
                <br><small>{len(st.session_state.data_a):,} rows × {len(st.session_state.data_a.columns)} columns</small>
            </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f"""
            <div class="status-error">
                ❌ Error: {str(e)}
            </div>
            """, unsafe_allow_html=True)
            st.session_state.data_a = None
    
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="upload-box">', unsafe_allow_html=True)
    st.markdown('<div class="upload-title">📋 Data B (OOS2)</div>', unsafe_allow_html=True)
    st.markdown('<div class="upload-subtitle">Inventory data with availability</div>', unsafe_allow_html=True)
    
    uploaded_file_b = st.file_uploader(
        "Upload Data B",
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
            <div class="status-success">
                ✅ {uploaded_file_b.name} loaded successfully
                <br><small>{len(st.session_state.data_b):,} rows × {len(st.session_state.data_b.columns)} columns</small>
            </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f"""
            <div class="status-error">
                ❌ Error: {str(e)}
            </div>
            """, unsafe_allow_html=True)
            st.session_state.data_b = None
    
    st.markdown('</div>', unsafe_allow_html=True)

# Process Section
st.markdown('<div class="section-title">⚙️ Process Data</div>', unsafe_allow_html=True)

col_process, col_reset = st.columns([3, 1])

with col_process:
    if st.button("🔄 Process Data", key='process_btn'):
        if st.session_state.data_a is None or st.session_state.data_b is None:
            st.markdown("""
            <div class="status-error">
                ❌ Please upload both Data A and Data B files before processing
            </div>
            """, unsafe_allow_html=True)
        else:
            try:
                with st.spinner('🔄 Processing data...'):
                    # Get column names
                    cols_a = st.session_state.data_a.columns.tolist()
                    cols_b = st.session_state.data_b.columns.tolist()
                    
                    # Find required columns
                    online_status_col = next((col for col in cols_a if 'Online Status' in col), None)
                    sku_col_a = next((col for col in cols_a if 'System Product Code' in col), None)
                    sku_col_b = next((col for col in cols_b if 'SKU' in col), None)
                    inventory_col = next((col for col in cols_b if 'Available inventory' in col), None)
                    
                    if not all([online_status_col, sku_col_a, sku_col_b, inventory_col]):
                        st.markdown(f"""
                        <div class="status-error">
                            ❌ Required columns not found in files
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
                        <div class="status-success">
                            ✅ Data processed successfully!
                        </div>
                        """, unsafe_allow_html=True)
                        
            except Exception as e:
                st.markdown(f"""
                <div class="status-error">
                    ❌ Processing error: {str(e)}
                </div>
                """, unsafe_allow_html=True)

with col_reset:
    if st.button("🔄 Reset", key='reset_btn'):
        st.session_state.data_a = None
        st.session_state.data_b = None
        st.session_state.result_data = None
        st.session_state.stats = None
        st.rerun()

# Display Statistics
if st.session_state.stats:
    st.markdown('<div class="section-title">📈 Processing Statistics</div>', unsafe_allow_html=True)
    
    stats = st.session_state.stats
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-label">Data A Original</div>
            <div class="stat-value">{stats['original']:,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-label">After Filter</div>
            <div class="stat-value">{stats['filtered']:,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-box warning">
            <div class="stat-label">Zero Inventory SKUs</div>
            <div class="stat-value">{stats['zero_inventory']:,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-box success">
            <div class="stat-label">Final Result</div>
            <div class="stat-value">{stats['result']:,}</div>
        </div>
        """, unsafe_allow_html=True)

# Display Results
if st.session_state.result_data is not None:
    st.markdown('<div class="section-title">📋 Result Preview</div>', unsafe_allow_html=True)
    
    st.dataframe(
        st.session_state.result_data,
        use_container_width=True,
        height=400
    )
    
    st.markdown('<div class="section-title">📥 Download Results</div>', unsafe_allow_html=True)
    
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
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    with col_info:
        st.metric("Total Rows", len(st.session_state.result_data))

# Footer
st.markdown("""
<div class="footer">
    <p>🚀 OOS Data Processor v2.0 | Professional Inventory Analysis Tool</p>
    <p>Built with Streamlit | Dark Theme | Production Ready</p>
</div>
""", unsafe_allow_html=True)
