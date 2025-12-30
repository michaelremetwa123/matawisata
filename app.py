import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Sistem Pakar Wisata Kei", layout="wide")

st.title("🧪 Portal Analisis Pakar - Matawisata")
st.markdown("""
Pada halaman ini, Pakar dapat menentukan **Lokasi Wisata** yang akan dinilai dan memberikan **Poin Kriteria** secara langsung. 
Sistem akan melakukan perhitungan peringkat menggunakan metode **TOPSIS**.
""")

# --- LANGKAH 1: INPUT DATA WISATA & KRITERIA OLEH PAKAR ---
st.header("1. Manajemen Data & Poin Wisata")
st.info("💡 **Petunjuk:** Pakar bisa menambah baris baru di bawah tabel, mengubah nama lokasi, dan mengisi nilai kriteria (1-10 atau angka lainnya).")

# Data awal sebagai template
data_template = {
    'Nama Lokasi': ['Ngurbloat', 'Ohoililir', 'Ohoidertawun'],
    'Harga (C)': [5000, 10000, 5000],   # Cost
    'Fasilitas (B)': [5, 4, 3],          # Benefit
    'Akses (B)': [5, 4, 3],               # Benefit
    'Keindahan (B)': [5, 5, 4],           # Benefit
    'Jarak (C)': [12, 10, 15]            # Cost
}

# Membuat tabel interaktif (Data Editor)
# num_rows="dynamic" memungkinkan pakar menambah/menghapus baris sendiri
df_pakar = st.data_editor(
    pd.DataFrame(data_template), 
    num_rows="dynamic", 
    use_container_width=True,
    key="editor_pakar"
)

# --- LANGKAH 2: INPUT BOBOT KEPENTINGAN (AHP) ---
st.header("2. Penentuan Bobot Kepentingan")
st.write("Tentukan tingkat kepentingan untuk masing-masing kriteria (Skala 1-9):")

col_w = st.columns(5)
with col_w[0]: w_harga = st.number_input("Harga", 1, 9, 5)
with col_w[1]: w_fasilitas = st.number_input("Fasilitas", 1, 9, 7)
with col_w[2]: w_akses = st.number_input("Akses", 1, 9, 6)
with col_w[3]: w_keindahan = st.number_input("Keindahan", 1, 9, 9)
with col_w[4]: w_jarak = st.number_input("Jarak", 1, 9, 4)

# --- LANGKAH 3: PROSES ANALISA ---
if st.button("🚀 Jalankan Analisa Peringkat"):
    # Cek jika data kosong
    if df_pakar.empty:
        st.error("Data lokasi wisata masih kosong! Harap isi minimal satu lokasi.")
    else:
        # Menyiapkan Bobot
        w_array = np.array([w_harga, w_fasilitas, w_akses, w_keindahan, w_jarak])
        weights = w_array / w_array.sum()

        # Ambil matriks keputusan (hanya kolom angka)
        matrix = df_pakar.iloc[:, 1:].values
        
        # 1. Normalisasi Matriks
        norm_matrix = matrix / np.sqrt((matrix**2).sum(axis=0))
        
        # 2. Matriks Terbobot
        weighted_matrix = norm_matrix * weights

        # 3. Solusi Ideal Positif (A+) & Negatif (A-)
        # Index 0 & 4 adalah Cost (Harga & Jarak), sisanya Benefit
        ideal_pos = [
            np.min(weighted_matrix[:,0]), np.max(weighted_matrix[:,1]), 
            np.max(weighted_matrix[:,2]), np.max(weighted_matrix[:,3]), 
            np.min(weighted_matrix[:,4])
        ]
        ideal_neg = [
            np.max(weighted_matrix[:,0]), np.min(weighted_matrix[:,1]), 
            np.min(weighted_matrix[:,2]), np.min(weighted_matrix[:,3]), 
            np.max(weighted_matrix[:,4])
        ]

        # 4. Jarak Euclidean (D+ dan D-)
        d_pos = np.sqrt(((weighted_matrix - ideal_pos)**2).sum(axis=1))
        d_neg = np.sqrt(((weighted_matrix - ideal_neg)**2).sum(axis=1))

        # 5. Skor Preferensi Akhir (V)
        df_pakar['Skor Akhir'] = d_neg / (d_pos + d_neg)

        # Tampilkan Hasil
        st.divider()
        st.subheader("📊 Hasil Analisa Rekomendasi")
        
        hasil_urut = df_pakar[['Nama Lokasi', 'Skor Akhir']].sort_values(by='Skor Akhir', ascending=False)
        
        c1, c2 = st.columns([1, 1])
        with c1:
            st.write("**Tabel Peringkat:**")
            st.dataframe(hasil_urut.reset_index(drop=True), use_container_width=True)
        with c2:
            st.write("**Visualisasi Skor:**")
            st.bar_chart(hasil_urut.set_index('Nama Lokasi'))

        # Fitur Tambahan: Download Hasil
        csv = hasil_urut.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Hasil Analisa (CSV)",
            data=csv,
            file_name='hasil_analisa_wisata.csv',
            mime='text/csv',
        )
