import streamlit as st
import pandas as pd
import io
from datetime import datetime

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="OOS Cross-Reference Tool",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CUSTOM CSS (DARK THEME) ---
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    /* Header Styling */
    .main-header {
        background: linear-gradient(90deg, #FF4B4B 0%, #CC0000 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(255, 75, 75, 0.2);
        text-align: center;
    }
    
    .header-title {
        color: white;
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0;
    }
    
    .header-subtitle {
        color: #FFE5E5;
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
    
    /* Upload Areas */
    .upload-container {
        background-color: #262730;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #363945;
        height: 100%;
    }
    
    .upload-label {
        font-size: 1.2rem;
        font-weight: 600;
        color: #FF4B4B;
        margin-bottom: 10px;
    }
    
    /* Metrics */
    div[data-testid="stMetric"] {
        background-color: #262730;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #363945;
    }
    
    div[data-testid="stMetricLabel"] {
        color: #A3A8B8;
    }
    
    div[data-testid="stMetricValue"] {
        color: #FF4B4B;
    }

    /* Buttons */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
        padding: 0.75rem 1rem;
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
<div class="main-header">
    <h1 class="header-title">⚡ OOS Data Matcher</h1>
    <p class="header-subtitle">Filter Data A & Cross-Reference dengan Data B (Zero Inventory)</p>
</div>
""", unsafe_allow_html=True)

# --- INISIALISASI SESSION STATE ---
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None

# --- BAGIAN UPLOAD ---
col1, col2 = st.columns(2)

with col1:
    with st.container():
        st.markdown('<div class="upload-container">', unsafe_allow_html=True)
        st.markdown('<p class="upload-label">📂 Upload Data A (Orders)</p>', unsafe_allow_html=True)
        st.info("File yang akan difilter (Kolom X: Status, Kolom AQ: SKU)")
        file_a = st.file_uploader("Pilih file Data A (Excel/CSV)", type=['xlsx', 'xls', 'csv'], key='file_a')
        st.markdown('</div>', unsafe_allow_html=True)

with col2:
    with st.container():
        st.markdown('<div class="upload-container">', unsafe_allow_html=True)
        st.markdown('<p class="upload-label">📂 Upload Data B (Inventory)</p>', unsafe_allow_html=True)
        st.info("File referensi stok (Kolom B: SKU, Kolom E: Inventory)")
        file_b = st.file_uploader("Pilih file Data B (Excel/CSV)", type=['xlsx', 'xls', 'csv'], key='file_b')
        st.markdown('</div>', unsafe_allow_html=True)

# --- FUNGSI PEMBACA FILE ---
def load_file(uploaded_file):
    if uploaded_file.name.endswith(('.xlsx', '.xls')):
        return pd.read_excel(uploaded_file)
    return pd.read_csv(uploaded_file)

# --- LOGIKA PROSES UTAMA ---
if file_a and file_b:
    st.markdown("---")
    if st.button("🚀 PROSES DATA", type="primary"):
        try:
            with st.spinner('Sedang memproses... Mengecek Kolom X dan Inventory Data B...'):
                # 1. Load Data
                df_a = load_file(file_a)
                df_b = load_file(file_b)

                # --- VALIDASI KOLOM DATA A ---
                # Kita butuh minimal sampai kolom CC (Indeks 80)
                if df_a.shape[1] < 81:
                    st.error(f"❌ Data A Error: File hanya memiliki {df_a.shape[1]} kolom. Diperlukan minimal 81 kolom (sampai kolom CC).")
                    st.stop()

                # --- VALIDASI KOLOM DATA B ---
                # Kita butuh minimal sampai kolom E (Indeks 4)
                if df_b.shape[1] < 5:
                    st.error("❌ Data B Error: File kurang kolom. Pastikan ada Kolom A sampai E.")
                    st.stop()

                # 2. LOGIKA DATA A (FILTERING)
                # Kolom X adalah indeks ke-23 (0-based index: A=0, X=23)
                col_x_idx = 23
                
                # Pastikan kolom dibaca sebagai string untuk pencarian kata
                df_a_filtered = df_a.copy()
                
                # Buat mask untuk kata-kata terlarang (Case Insensitive)
                # "PreSale" atau "OnlineShip"
                mask_exclude = df_a_filtered.iloc[:, col_x_idx].astype(str).str.contains('PreSale|OnlineShip', case=False, na=False)
                
                # Ambil kebalikannya (Hapus yang contain kata tersebut)
                df_a_clean = df_a_filtered[~mask_exclude]

                # 3. LOGIKA DATA B (ZERO INVENTORY)
                # Kolom E (Inventory) adalah indeks ke-4 (A=0, E=4)
                # Kolom B (SKU) adalah indeks ke-1 (A=0, B=1)
                
                # Ambil hanya baris di Data B dimana Inventory (Kolom E) == 0
                zero_stock_df = df_b[df_b.iloc[:, 4] == 0]
                
                # Buat list SKU yang inventory-nya 0
                zero_stock_skus = zero_stock_df.iloc[:, 1].astype(str).unique().tolist()

                # 4. CROSS REFERENCE
                # Cek Kolom AQ di Data A (Indeks 42) apakah ada di list zero_stock_skus
                col_aq_idx = 42
                
                final_result = df_a_clean[df_a_clean.iloc[:, col_aq_idx].astype(str).isin(zero_stock_skus)]

                # 5. PILIH KOLOM OUTPUT
                # A(0), B(1), C(2), K(10), L(11), N(13), X(23), Z(25), AQ(42), CA(78), CB(79), CC(80)
                target_indices = [0, 1, 2, 10, 11, 13, 23, 25, 42, 78, 79, 80]
                
                # Pastikan output hanya kolom yang diminta
                output_df = final_result.iloc[:, target_indices]

                # Simpan ke session state
                st.session_state.processed_data = output_df
                
                # Simpan juga statistik untuk overview
                st.session_state.stats = {
                    'total_awal': len(df_a),
                    'setelah_filter_status': len(df_a_clean),
                    'total_inventory_nol': len(zero_stock_skus),
                    'hasil_akhir': len(output_df)
                }

        except Exception as e:
            st.error(f"Terjadi kesalahan teknis: {str(e)}")

# --- HASIL & DOWNLOAD ---
if st.session_state.processed_data is not None:
    st.markdown("### 📊 Overview Hasil")
    
    # Tampilkan Statistik
    stats = st.session_state.stats
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Data Awal", stats['total_awal'])
    m2.metric("Lolos Filter Status", stats['setelah_filter_status'])
    m3.metric("SKU Stok 0 (Data B)", stats['total_inventory_nol'])
    m4.metric("✅ Hasil Final", stats['hasil_akhir'])
    
    # Preview Data
    st.markdown("#### Preview Data (Top 5 baris)")
    st.dataframe(st.session_state.processed_data.head(), use_container_width=True)
    
    # Download Button
    st.markdown("### 📥 Download")
    
    # Export to Excel buffer
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        st.session_state.processed_data.to_excel(writer, index=False, sheet_name='OOS_Result')
    
    date_str = datetime.now().strftime("%Y-%m-%d_%H%M")
    
    st.download_button(
        label="📄 Download File Excel (.xlsx)",
        data=buffer.getvalue(),
        file_name=f"OOS_Processed_{date_str}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary"
    )
    
    # Tombol Reset
    if st.button("🔄 Reset / Mulai Ulang"):
        st.session_state.processed_data = None
        st.rerun()

# --- FOOTER ---
st.markdown("""
<div style='text-align: center; color: #666; margin-top: 50px; padding: 20px; border-top: 1px solid #333;'>
    <small>OOS Processor Tool | Built with Streamlit</small>
</div>
""", unsafe_allow_html=True)
