import streamlit as st
import pandas as pd
import numpy as np

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Matawisata Kei", layout="wide")
st.title("🏝️ Sistem Rekomendasi Wisata Kei")
st.markdown("Aplikasi ini menghitung rekomendasi pantai terbaik berdasarkan kepentingan kriteria yang Anda tentukan sendiri.")

# 2. DATA DASAR (Berdasarkan Google Sheets Anda)
# Data ini mencakup 5 kriteria: Harga, Fasilitas, Akses, Keindahan, Jarak
data_wisata = {
    'Nama Pantai': ['Ngurbloat', 'Ohoililir', 'Ohoidertawun'],
    'Harga Tiket (Rp)': [15000, 10000, 25000],   # Cost (Makin murah makin bagus)
    'Fasilitas': [5, 4, 3],                   # Benefit (Skala 1-5)
    'Aksesibilitas': [5, 4, 3],               # Benefit (Skala 1-5)
    'Keindahan Alam': [5, 5, 4],              # Benefit (Skala 1-5)
    'Jarak dari Kota (Km)': [12, 10, 15]      # Cost (Makin dekat makin bagus)
}
df = pd.DataFrame(data_wisata)

# 3. SIDEBAR - INPUT USER (PENGGANTI AHP)
st.sidebar.header("Atur Prioritas Anda")
st.sidebar.write("Geser slider untuk menentukan seberapa penting kriteria bagi Anda (1 = Tidak Penting, 9 = Sangat Penting)")

w1 = st.sidebar.slider("Pentingnya Harga Murah", 1, 9, 5)
w2 = st.sidebar.slider("Pentingnya Fasilitas Lengkap", 1, 9, 7)
w3 = st.sidebar.slider("Pentingnya Akses Jalan Mudah", 1, 9, 6)
w4 = st.sidebar.slider("Pentingnya Keindahan Alam", 1, 9, 9)
w5 = st.sidebar.slider("Pentingnya Jarak Dekat", 1, 9, 4)

# Normalisasi Bobot secara otomatis
weights_input = np.array([w1, w2, w3, w4, w5])
weights = weights_input / weights_input.sum()

# 4. PROSES PERHITUNGAN TOPSIS
# Mengambil hanya kolom angka
matrix = df.iloc[:, 1:].values

# Normalisasi Matriks
norm_matrix = matrix / np.sqrt((matrix**2).sum(axis=0))

# Matriks Terbobot
weighted_matrix = norm_matrix * weights

# Menentukan Solusi Ideal Positif (A+) dan Negatif (A-)
# Ingat: Harga (Kolom 0) dan Jarak (Kolom 4) adalah COST
ideal_pos = [
    np.min(weighted_matrix[:, 0]), # Harga (Min)
    np.max(weighted_matrix[:, 1]), # Fasilitas (Max)
    np.max(weighted_matrix[:, 2]), # Akses (Max)
    np.max(weighted_matrix[:, 3]), # Keindahan (Max)
    np.min(weighted_matrix[:, 4])  # Jarak (Min)
]

ideal_neg = [
    np.max(weighted_matrix[:, 0]), # Harga (Max)
    np.min(weighted_matrix[:, 1]), # Fasilitas (Min)
    np.min(weighted_matrix[:, 2]), # Akses (Min)
    np.min(weighted_matrix[:, 3]), # Keindahan (Min)
    np.max(weighted_matrix[:, 4])  # Jarak (Max)
]

# Menghitung Jarak Euclidean (D+ dan D-)
d_pos = np.sqrt(((weighted_matrix - ideal_pos)**2).sum(axis=1))
d_neg = np.sqrt(((weighted_matrix - ideal_neg)**2).sum(axis=1))

# Menghitung Skor Akhir (V)
df['Skor Rekomendasi'] = d_neg / (d_pos + d_neg)

# 5. TAMPILKAN HASIL
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🏆 Peringkat Pantai")
    # Mengurutkan dari skor tertinggi
    hasil_final = df[['Nama Pantai', 'Skor Rekomendasi']].sort_values(by='Skor Rekomendasi', ascending=False)
    st.dataframe(hasil_final.reset_index(drop=True), use_container_width=True)

with col2:
    st.subheader("📊 Grafik Perbandingan Skor")
    st.bar_chart(data=hasil_final.set_index('Nama Pantai'))

st.divider()
st.caption("Aplikasi ini menggunakan metode AHP untuk pembobotan dan TOPSIS untuk perangkingan.")
