import streamlit as st
import pandas as pd
import openpyxl
import io
from datetime import datetime

# Configure page
st.set_page_config(
    page_title="OOS Data Processor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Dark theme CSS - Simple and Clear
st.markdown("""
<style>
    /* Main background */
    [data-testid="stAppViewContainer"] {
        background-color: #1a1a1a;
    }
    
    [data-testid="stHeader"] {
        background-color: #1a1a1a;
    }
    
    /* Text colors */
    body {
        color: #e0e0e0;
    }
    
    /* Header styling */
    .header-container {
        background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
        padding: 2.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
    }
    
    .header-title {
        color: #ffffff;
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .header-subtitle {
        color: #e0e0e0;
        font-size: 1rem;
        margin-top: 0.5rem;
    }
    
    /* Upload boxes */
    .upload-section {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .upload-box {
        background-color: #2a2a2a;
        border: 2px solid #3a3a3a;
        border-radius: 8px;
        padding: 1.5rem;
        transition: all 0.3s ease;
    }
    
    .upload-box:hover {
        border-color: #2563eb;
        box-shadow: 0 0 15px rgba(37, 99, 235, 0.2);
    }
    
    .box-title {
        color: #2563eb;
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .box-subtitle {
        color: #888888;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }
    
    /* Status messages */
    .status-box {
        padding: 1rem;
        border-radius: 6px;
        margin-top: 0.5rem;
        font-size: 0.9rem;
    }
    
    .status-success {
        background-color: rgba(34, 197, 94, 0.15);
        border-left: 4px solid #22c55e;
        color: #86efac;
    }
    
    .status-error {
        background-color: rgba(239, 68, 68, 0.15);
        border-left: 4px solid #ef4444;
        color: #fca5a5;
    }
    
    /* Section titles */
    .section-title {
        color: #2563eb;
        font-size: 1.4rem;
        font-weight: bold;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #3a3a3a;
    }
    
    /* Stats grid */
    .stats-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin-bottom: 2rem;
    }
    
    .stat-card {
        background-color: #2a2a2a;
        border-left: 4px solid #2563eb;
        padding: 1.2rem;
        border-radius: 6px;
        text-align: center;
    }
    
    .stat-label {
        color: #888888;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
    }
    
    .stat-value {
        color: #2563eb;
        font-size: 2rem;
        font-weight: bold;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #2563eb !important;
        color: white !important;
        border: none !important;
        padding: 0.7rem 1.5rem !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    
    .stButton > button:hover {
        background-color: #1d4ed8 !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
    }
    
    /* Data table */
    .stDataFrame {
        background-color: #2a2a2a !important;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #666666;
        font-size: 0.85rem;
        margin-top: 2rem;
        padding-top: 1.5rem;
        border-top: 1px solid #3a3a3a;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .upload-section {
            grid-template-columns: 1fr;
        }
        
        .stats-container {
            grid-template-columns: repeat(2, 1fr);
        }
        
        .header-title {
            font-size: 1.8rem;
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
<div class="header-container">
    <h1 class="header-title">📊 OOS Data Processor</h1>
    <p class="header-subtitle">Filter and cross-reference inventory data with intelligent processing</p>
</div>
""", unsafe_allow_html=True)

# Info section
with st.expander("ℹ️ How it works"):
    st.markdown("""
    **Step 1:** Upload Data A (OOS1) - Order data with status and SKU information
    
    **Step 2:** Upload Data B (OOS2) - Inventory data with availability status
    
    **Step 3:** Click "Process Data" to:
    - Filter out PreSale and OnlineShip orders from Data A
    - Find SKUs with zero available inventory in Data B
    - Cross-reference and match records
    
    **Step 4:** Download the results as Excel file
    """)

# Upload section
st.markdown('<div class="section-title">📁 Upload Your Files</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="upload-box">', unsafe_allow_html=True)
    st.markdown('<div class="box-title">📋 Data A (OOS1)</div>', unsafe_allow_html=True)
    st.markdown('<div class="box-subtitle">Order data with status and SKU</div>', unsafe_allow_html=True)
    
    file_a = st.file_uploader("Upload Data A", type=['xlsx', 'xls', 'csv'], key='file_a', label_visibility='collapsed')
    
    if file_a is not None:
        try:
            # Use openpyxl engine explicitly for Excel files
            if file_a.name.endswith(('.xlsx', '.xls')):
                st.session_state.data_a = pd.read_excel(file_a, engine='openpyxl')
            else:
                st.session_state.data_a = pd.read_csv(file_a)
            
            st.markdown(f"""
            <div class="status-box status-success">
                ✅ Loaded: {file_a.name} ({len(st.session_state.data_a):,} rows)
            </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f"""
            <div class="status-box status-error">
                ❌ Error: {str(e)}
            </div>
            """, unsafe_allow_html=True)
            st.session_state.data_a = None
    
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="upload-box">', unsafe_allow_html=True)
    st.markdown('<div class="box-title">📋 Data B (OOS2)</div>', unsafe_allow_html=True)
    st.markdown('<div class="box-subtitle">Inventory data with availability</div>', unsafe_allow_html=True)
    
    file_b = st.file_uploader("Upload Data B", type=['xlsx', 'xls', 'csv'], key='file_b', label_visibility='collapsed')
    
    if file_b is not None:
        try:
            # Use openpyxl engine explicitly for Excel files
            if file_b.name.endswith(('.xlsx', '.xls')):
                st.session_state.data_b = pd.read_excel(file_b, engine='openpyxl')
            else:
                st.session_state.data_b = pd.read_csv(file_b)
            
            st.markdown(f"""
            <div class="status-box status-success">
                ✅ Loaded: {file_b.name} ({len(st.session_state.data_b):,} rows)
            </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f"""
            <div class="status-box status-error">
                ❌ Error: {str(e)}
            </div>
            """, unsafe_allow_html=True)
            st.session_state.data_b = None
    
    st.markdown('</div>', unsafe_allow_html=True)

# Process section
st.markdown('<div class="section-title">⚙️ Process Data</div>', unsafe_allow_html=True)

col_btn1, col_btn2 = st.columns([3, 1])

with col_btn1:
    if st.button("🔄 Process Data", key='process'):
        if st.session_state.data_a is None or st.session_state.data_b is None:
            st.markdown("""
            <div class="status-box status-error">
                ❌ Please upload both Data A and Data B files
            </div>
            """, unsafe_allow_html=True)
        else:
            try:
                with st.spinner('Processing...'):
                    # Get column names
                    cols_a = st.session_state.data_a.columns.tolist()
                    cols_b = st.session_state.data_b.columns.tolist()
                    
                    # Find columns
                    online_status_col = next((c for c in cols_a if 'Online Status' in c), None)
                    sku_col_a = next((c for c in cols_a if 'System Product Code' in c), None)
                    sku_col_b = next((c for c in cols_b if 'SKU' in c), None)
                    inventory_col = next((c for c in cols_b if 'Available inventory' in c), None)
                    
                    if not all([online_status_col, sku_col_a, sku_col_b, inventory_col]):
                        st.markdown("""
                        <div class="status-box status-error">
                            ❌ Required columns not found
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        # Filter Data A
                        original_count = len(st.session_state.data_a)
                        filtered_a = st.session_state.data_a[
                            ~st.session_state.data_a[online_status_col].astype(str).str.contains('PreSale|OnlineShip', case=False, na=False)
                        ].copy()
                        filtered_count = len(filtered_a)
                        
                        # Find zero inventory SKUs
                        zero_inventory_skus = st.session_state.data_b[
                            st.session_state.data_b[inventory_col] == 0
                        ][sku_col_b].unique().tolist()
                        zero_inventory_count = len(zero_inventory_skus)
                        
                        # Cross-reference
                        result = filtered_a[filtered_a[sku_col_a].isin(zero_inventory_skus)].copy()
                        result_count = len(result)
                        
                        # Select output columns
                        output_cols = [c for c in [
                            next((x for x in cols_a if 'Original Order Number' in x), None),
                            next((x for x in cols_a if 'ERP Order Number' in x), None),
                            next((x for x in cols_a if 'Order Status' in x), None),
                            next((x for x in cols_a if 'Platform' in x), None),
                            next((x for x in cols_a if 'Store' in x and 'Group' not in x), None),
                            next((x for x in cols_a if 'Store Group' in x), None),
                            next((x for x in cols_a if 'Order Type' in x), None),
                            next((x for x in cols_a if 'Creator' in x), None),
                            sku_col_a,
                            next((x for x in cols_a if 'Estimated' in x and 'Weight' in x), None),
                            next((x for x in cols_a if 'Actual' in x and 'Weight' in x), None),
                            next((x for x in cols_a if 'Weight Unit' in x), None),
                        ] if c is not None]
                        
                        st.session_state.result_data = result[output_cols]
                        st.session_state.stats = {
                            'original': original_count,
                            'filtered': filtered_count,
                            'zero_inventory': zero_inventory_count,
                            'result': result_count
                        }
                        
                        st.markdown("""
                        <div class="status-box status-success">
                            ✅ Processing complete!
                        </div>
                        """, unsafe_allow_html=True)
                        
            except Exception as e:
                st.markdown(f"""
                <div class="status-box status-error">
                    ❌ Error: {str(e)}
                </div>
                """, unsafe_allow_html=True)

with col_btn2:
    if st.button("🔄 Reset", key='reset'):
        st.session_state.data_a = None
        st.session_state.data_b = None
        st.session_state.result_data = None
        st.session_state.stats = None
        st.rerun()

# Display statistics
if st.session_state.stats:
    st.markdown('<div class="section-title">📊 Statistics</div>', unsafe_allow_html=True)
    
    stats = st.session_state.stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Original</div>
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
        <div class="stat-card">
            <div class="stat-label">Zero Inventory</div>
            <div class="stat-value">{stats['zero_inventory']:,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Final Result</div>
            <div class="stat-value">{stats['result']:,}</div>
        </div>
        """, unsafe_allow_html=True)

# Display results
if st.session_state.result_data is not None:
    st.markdown('<div class="section-title">📋 Results Preview</div>', unsafe_allow_html=True)
    
    st.dataframe(st.session_state.result_data, use_container_width=True, height=400)
    
    st.markdown('<div class="section-title">📥 Download Results</div>', unsafe_allow_html=True)
    
    # Create Excel file using openpyxl
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        st.session_state.result_data.to_excel(writer, sheet_name='Results', index=False)
        
        # Auto-adjust column widths
        workbook = writer.book
        worksheet = writer.sheets['Results']
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    excel_buffer.seek(0)
    
    col_download, col_info = st.columns([3, 1])
    
    with col_download:
        st.download_button(
            label="📥 Download as Excel",
            data=excel_buffer.getvalue(),
            file_name=f"OOS_Results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    with col_info:
        st.metric("Total Rows", len(st.session_state.result_data))

# Footer
st.markdown("""
<div class="footer">
    <p>OOS Data Processor v2.0 | Built with Streamlit</p>
</div>
""", unsafe_allow_html=True)
