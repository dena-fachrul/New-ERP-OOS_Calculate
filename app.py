import streamlit as st
import pandas as pd
import io
from typing import Tuple, Optional

# Page configuration
st.set_page_config(
    page_title="OOS Data Processor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .upload-section {
        background-color: #f0f2f6;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .info-box {
        background-color: #e3f2fd;
        padding: 1rem;
        border-left: 4px solid #1f77b4;
        border-radius: 4px;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #e8f5e9;
        padding: 1rem;
        border-left: 4px solid #4caf50;
        border-radius: 4px;
        margin-bottom: 1rem;
    }
    .warning-box {
        background-color: #fff3e0;
        padding: 1rem;
        border-left: 4px solid #ff9800;
        border-radius: 4px;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

def load_excel_file(uploaded_file) -> Optional[pd.DataFrame]:
    """Load Excel file and return DataFrame"""
    try:
        df = pd.read_excel(uploaded_file)
        return df
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None

def process_data(data_a: pd.DataFrame, data_b: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    """
    Process Data A and Data B according to business logic:
    1. Filter Data A to exclude rows where ' Online Status' contains 'PreSale' or 'OnlineShip'
    2. Cross-reference with Data B: match column AQ with column B (SKU)
    3. Only keep rows where Data B's 'Available inventory' (column E) = 0
    4. Return selected columns from Data A
    """
    
    stats = {
        'data_a_original': len(data_a),
        'data_a_after_filter': 0,
        'data_a_after_crossref': 0,
        'data_b_matching': 0
    }
    
    try:
        # Step 1: Filter Data A - exclude rows containing 'PreSale' or 'OnlineShip' in ' Online Status'
        # Create mask for rows to exclude
        mask_presale = data_a[' Online Status'].astype(str).str.contains('PreSale', case=False, na=False)
        mask_onlineship = data_a[' Online Status'].astype(str).str.contains('OnlineShip', case=False, na=False)
        mask_exclude = mask_presale | mask_onlineship
        
        # Filter Data A
        data_a_filtered = data_a[~mask_exclude].copy()
        stats['data_a_after_filter'] = len(data_a_filtered)
        
        # Step 2: Prepare Data B - filter for rows where 'Available inventory' = 0
        data_b_zero_inventory = data_b[data_b['Available inventory'] == 0].copy()
        stats['data_b_matching'] = len(data_b_zero_inventory)
        
        # Create a set of SKUs from Data B with zero inventory for faster lookup
        sku_set = set(data_b_zero_inventory['SKU'].astype(str).str.strip())
        
        # Step 3: Cross-reference - keep only rows from Data A where AQ matches SKU in Data B (with zero inventory)
        data_a_filtered[' System Product Code'] = data_a_filtered[' System Product Code'].astype(str).str.strip()
        mask_match = data_a_filtered[' System Product Code'].isin(sku_set)
        data_a_final = data_a_filtered[mask_match].copy()
        stats['data_a_after_crossref'] = len(data_a_final)
        
        # Step 4: Select required columns
        required_columns = [' Original Order Number', ' ERP Order Number', ' Order Status', 
                          ' Online Status', ' Warehouse', ' Warehouse Dispatch Time',
                          ' Online Product Code', ' Logistics Tracking Number', ' AQ',
                          ' Carrier', ' Shipping Method', ' Warehouse']
        
        # Map the requested columns (A, B, C, K, L, N, X, Z, AQ, CA, CB, CC) to actual column names
        # Based on Excel column positions: A=0, B=1, C=2, K=10, L=11, N=13, X=22, Z=24, AQ=42, CA=52, CB=53, CC=54
        column_mapping = {
            'A': ' Original Order Number',      # 0
            'B': ' ERP Order Number',           # 1
            'C': ' Order Status',               # 2
            'K': ' Platform',                   # 10
            'L': ' Store',                      # 11
            'N': ' Store Group',                # 13
            'X': ' Order Type',                 # 22
            'Z': ' Creator',                    # 24
            'AQ': ' System Product Code',       # 42
            'CA': ' Estimated Total Order Weight',  # 52
            'CB': ' Actual Order Weight',       # 53
            'CC': ' Weight Unit'                # 54
        }
        
        output_columns = [col for col in column_mapping.values() if col in data_a_final.columns]
        data_a_final = data_a_final[output_columns]
        
        return data_a_final, stats
        
    except Exception as e:
        st.error(f"Error processing data: {str(e)}")
        raise

def main():
    # Header
    st.markdown('<div class="main-header">📊 OOS Data Processor</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Process and filter OOS data with intelligent cross-referencing</div>', unsafe_allow_html=True)
    
    # Info box
    st.markdown("""
    <div class="info-box">
    <strong>How it works:</strong><br>
    1. Upload Data A (OOS1) and Data B (OOS2) files<br>
    2. System filters Data A to exclude PreSale and OnlineShip orders<br>
    3. Cross-references with Data B to match SKUs with zero inventory<br>
    4. Displays results and allows download as Excel
    </div>
    """, unsafe_allow_html=True)
    
    # Upload section
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📁 Data A (OOS1)")
        uploaded_file_a = st.file_uploader(
            "Upload Data A file",
            type=['xlsx', 'xls', 'csv'],
            key='data_a',
            help="Upload the OOS1 Excel file"
        )
    
    with col2:
        st.subheader("📁 Data B (OOS2)")
        uploaded_file_b = st.file_uploader(
            "Upload Data B file",
            type=['xlsx', 'xls', 'csv'],
            key='data_b',
            help="Upload the OOS2 Excel file"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Process button
    if st.button("🔄 Process Data", type="primary", use_container_width=True):
        if uploaded_file_a is None or uploaded_file_b is None:
            st.error("❌ Please upload both Data A and Data B files")
        else:
            with st.spinner("Processing data..."):
                # Load files
                data_a = load_excel_file(uploaded_file_a)
                data_b = load_excel_file(uploaded_file_b)
                
                if data_a is not None and data_b is not None:
                    # Process data
                    result_df, stats = process_data(data_a, data_b)
                    
                    # Store in session state
                    st.session_state.result_df = result_df
                    st.session_state.stats = stats
                    st.session_state.processed = True
    
    # Display results if processed
    if 'processed' in st.session_state and st.session_state.processed:
        st.markdown("---")
        
        # Statistics
        st.subheader("📈 Processing Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        stats = st.session_state.stats
        with col1:
            st.metric("Data A Original", f"{stats['data_a_original']:,}")
        with col2:
            st.metric("After Filter", f"{stats['data_a_after_filter']:,}")
        with col3:
            st.metric("Data B (Zero Inv)", f"{stats['data_b_matching']:,}")
        with col4:
            st.metric("Final Result", f"{stats['data_a_after_crossref']:,}")
        
        # Results preview
        st.subheader("👁️ Results Preview")
        result_df = st.session_state.result_df
        
        if len(result_df) > 0:
            st.markdown(f'<div class="success-box">✅ Found <strong>{len(result_df):,}</strong> matching records</div>', unsafe_allow_html=True)
            
            # Show data table
            st.dataframe(result_df, use_container_width=True, height=400)
            
            # Download section
            st.subheader("⬇️ Download Results")
            
            # Convert to Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                result_df.to_excel(writer, sheet_name='Results', index=False)
                
                # Auto-adjust column widths
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
            
            output.seek(0)
            
            st.download_button(
                label="📥 Download as Excel",
                data=output.getvalue(),
                file_name="oos_processed_results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        else:
            st.markdown('<div class="warning-box">⚠️ No matching records found after processing</div>', unsafe_allow_html=True)
        
        # Reset button
        if st.button("🔄 Process Another File", use_container_width=True):
            st.session_state.processed = False
            st.rerun()

if __name__ == "__main__":
    main()
