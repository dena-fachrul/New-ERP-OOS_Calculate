import streamlit as st
import pandas as pd
import io
from datetime import datetime

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="OOS Data Matcher",
    layout="wide"
)

# --- JUDUL APLIKASI ---
st.title("⚡ OOS Data Matcher")
st.markdown("Upload Data A (Order) dan Data B (Inventory) untuk memproses data.")

# --- BAGIAN UPLOAD (2 KOLOM) ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📂 Data A (Orders)")
    file_a = st.file_uploader("Upload file Excel/CSV", type=['xlsx', 'xls', 'csv'], key='file_a')

with col2:
    st.subheader("📂 Data B (Inventory)")
    file_b = st.file_uploader("Upload file Excel/CSV", type=['xlsx', 'xls', 'csv'], key='file_b')

# --- FUNGSI LOAD DATA ---
def load_data(file):
    if file.name.endswith('.csv'):
        return pd.read_csv(file)
    else:
        # Engine openpyxl wajib untuk xlsx
        return pd.read_excel(file, engine='openpyxl') 

# --- TOMBOL PROSES ---
if st.button("🚀 Proses Data", type="primary"):
    if file_a is None or file_b is None:
        st.error("⚠️ Mohon upload kedua file (Data A dan Data B) terlebih dahulu.")
    else:
        try:
            with st.spinner('Sedang memproses data...'):
                # 1. Baca Data
                df_a = load_data(file_a)
                df_b = load_data(file_b)

                # Validasi jumlah kolom minimal
                if df_a.shape[1] < 81:
                    st.error(f"❌ Data A kurang kolom! Terdeteksi: {df_a.shape[1]}, Butuh minimal: 81 (sampai kolom CC).")
                    st.stop()
                
                if df_b.shape[1] < 5:
                    st.error("❌ Data B kurang kolom! Pastikan ada kolom A sampai E.")
                    st.stop()

                # 2. Filter Data A (Buang PreSale/OnlineShip)
                # Kolom X = index 23
                col_x_idx = 23
                mask_exclude = df_a.iloc[:, col_x_idx].astype(str).str.contains('PreSale|OnlineShip', case=False, na=False)
                df_a_clean = df_a[~mask_exclude]

                # 3. Cek Inventory Nol di Data B
                # Kolom B (SKU) = index 1, Kolom E (Qty) = index 4
                zero_stock_df = df_b[df_b.iloc[:, 4] == 0]
                zero_stock_skus = zero_stock_df.iloc[:, 1].astype(str).unique().tolist()

                # 4. Cross Reference (Cari SKU Data A di list stok nol)
                # Kolom AQ (SKU di A) = index 42
                final_result = df_a_clean[df_a_clean.iloc[:, 42].astype(str).isin(zero_stock_skus)]

                # 5. Pilih Kolom Output
                # A, B, C, K, L, N, X, Z, AQ, CA, CB, CC
                target_indices = [0, 1, 2, 10, 11, 13, 23, 25, 42, 78, 79, 80]
                output_df = final_result.iloc[:, target_indices]

                # --- TAMPILKAN HASIL ---
                st.success("✅ Proses Selesai!")
                
                # Metrics Sederhana
                m1, m2, m3 = st.columns(3)
                m1.metric("Total Awal", len(df_a))
                m2.metric("Stok Nol (Data B)", len(zero_stock_skus))
                m3.metric("Hasil Final", len(output_df))

                # Preview Tabel
                st.dataframe(output_df.head(10), use_container_width=True)

                # --- DOWNLOAD ---
                buffer = io.BytesIO()
                # Menggunakan engine xlsxwriter atau openpyxl untuk save
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    output_df.to_excel(writer, index=False, sheet_name='Result')
                
                st.download_button(
                    label="📥 Download Excel Result",
                    data=buffer.getvalue(),
                    file_name=f"OOS_Result_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        except Exception as e:
            st.error(f"Terjadi Kesalahan Teknis: {e}")
