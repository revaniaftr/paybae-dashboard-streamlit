import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime

# 1. KONFIGURASI HALAMAN & THEME PROFESSIONAL
st.set_page_config(page_title="PAYBAE AI Analytics Dashboard", page_icon="💳", layout="wide")

# Custom CSS untuk UI/UX Dashboard yang Clean
st.markdown("""
    <style>
    div[data-testid="metric-container"] {
        background-color: #fcfcfc;
        border: 1px solid #e6e8ea;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 3px 3px 8px rgba(0,0,0,0.03);
    }
    .business-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #e3e8ed;
        border-left: 6px solid #228be6;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    .ai-tag {
        background-color: #e7f5ff;
        color: #1c7ed6;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# 2. DATA PIPELINE (LOAD & WRANGLING)
@st.cache_data
def load_financial_data():
    # Membaca dataset utama hasil tracking
    df = pd.read_csv('dataset_paybae_clean.csv')
    df['Date'] = pd.to_datetime(df['Date'])

    # Standardisasi nama kolom sesuai kebutuhan dashboard
    df.rename(columns={'amount': 'nominal', 'type': 'tipe', 'category': 'kategori'}, inplace=True)
    df['tipe'] = df['tipe'].replace({'INCOME': 'Pemasukan', 'EXPENSE': 'Pengeluaran'})

    # Mengisi missing value pada kategori secara logis
    df['kategori'] = df['kategori'].fillna('Lain-lain / Belum Dikategorikan')

    # Fitur Ekstraksi Waktu
    df['Tahun'] = df['Date'].dt.year
    df['Bulan-Tahun'] = df['Date'].dt.to_period('M').astype(str)
    df['Hari_ke'] = df['Date'].dt.day
    df['Is_Weekend'] = df['Date'].dt.dayofweek.isin([5, 6]).astype(int)

    return df

try:
    df = load_financial_data()
except FileNotFoundError:
    st.error("❌ File 'dataset_paybae.csv' tidak ditemukan. Pastikan file berada di folder yang sama.")
    st.stop()

# 3. HEADER UTAMA INTERAKTIF
st.title("💳 PAYBAE Advanced Financial Intelligence Dashboard")
st.markdown("### *Analisis Deskriptif Historis & Pemetaan Strategis Pondasi Model AI*")
st.write("Platform manajemen finansial cerdas bagi masyarakat untuk mendeteksi anomali, memprediksi cashflow, dan memberikan rekomendasi anggaran.")

# 4. SIDEBAR KONTROL (SESUAI REQUEST GAMBAR 1)
st.sidebar.header("⚙️ Kontrol & Filter Data")

# --- Fitur 1: Rentang Tanggal ---
st.sidebar.markdown("**Rentang Waktu**")
min_date = df['Date'].min().date()
max_date = df['Date'].max().date()
date_range = st.sidebar.date_input(
    "Pilih Rentang Waktu:",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
    label_visibility="collapsed"
)

if len(date_range) == 2:
    start_date, end_date = date_range
    df_filtered = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]
else:
    df_filtered = df

# --- Fitur 2: Filter Kategori Pengeluaran ---
list_kategori = df[df['tipe'] == 'Pengeluaran']['kategori'].unique().tolist()
selected_kategori = st.sidebar.multiselect(
    "Filter Kategori Pengeluaran",
    options=list_kategori,
    default=list_kategori
)
# Terapkan filter kategori (hanya memfilter pengeluaran, pemasukan tetap masuk)
df_filtered = df_filtered[(df_filtered['kategori'].isin(selected_kategori)) | (df_filtered['tipe'] == 'Pemasukan')]


# --- Fitur 3: Filter Hari (Semua, Weekday, Weekend) ---
filter_hari = st.sidebar.radio(
    "Filter Hari",
    options=["Semua", "Weekday (Senin-Jumat)", "Weekend (Sabtu-Minggu)"]
)
if filter_hari == "Weekday (Senin-Jumat)":
    df_filtered = df_filtered[df_filtered['Is_Weekend'] == 0]
elif filter_hari == "Weekend (Sabtu-Minggu)":
    df_filtered = df_filtered[df_filtered['Is_Weekend'] == 1]


# 5. KARTU METRIK UTAMA
total_pemasukan = df_filtered[df_filtered['tipe'] == 'Pemasukan']['nominal'].sum()
total_pengeluaran = df_filtered[df_filtered['tipe'] == 'Pengeluaran']['nominal'].sum()
saldo_bersih = total_pemasukan - total_pengeluaran
saving_rate = (saldo_bersih / total_pemasukan * 100) if total_pemasukan > 0 else 0

st.markdown("#### **Ringkasan Finansial**")

# Baris 1: Pemasukan & Pengeluaran
col_m1, col_m2 = st.columns(2)
with col_m1:
    st.metric(label="Total Pemasukan (Income) 📈", value=f"Rp {total_pemasukan:,.0f}")
with col_m2:
    st.metric(label="Total Pengeluaran (Expense) 📉", value=f"Rp {total_pengeluaran:,.0f}")

st.write("")

# Baris 2: Saldo & Status
col_m3, col_m4 = st.columns(2)
with col_m3:
    st.metric(label="Sisa Saldo Bersih (Net Balance) 💰", value=f"Rp {saldo_bersih:,.0f}", delta=f"Rasio Tabungan: {saving_rate:.1f}%")
with col_m4:
    status_kesehatan = "SEHAT (≥20%)" if saving_rate >= 20 else "PERLU INTERVENSI AI"
    st.metric(label="Status Kesehatan Finansial 🩺", value=status_kesehatan)

st.divider()

# 6. VISUALISASI JAWABAN PERTANYAAN BISNIS
st.subheader("📊 Analisis Data Berdasarkan Pertanyaan Bisnis")

# P1: Distribusi Kategori
st.markdown("##### **Pertanyaan 1: Bagaimana distribusi dan pola pengeluaran pengguna berdasarkan kategori dan waktu transaksi?**")
df_exp = df_filtered[df_filtered['tipe'] == 'Pengeluaran']
cat_trend = df_exp.groupby(['Bulan-Tahun', 'kategori'])['nominal'].sum().reset_index()
fig_p1 = px.bar(cat_trend, x='Bulan-Tahun', y='nominal', color='kategori',
                color_discrete_sequence=px.colors.qualitative.Pastel,
                title="Distribusi Pola Pengeluaran per Kategori Sepanjang Waktu",
                labels={'nominal': 'Total Pengeluaran (Rp)', 'Bulan-Tahun': 'Waktu'})
st.plotly_chart(fig_p1, use_container_width=True)

# P2: Tren Arus Kas
st.markdown("##### **Pertanyaan 2: Bagaimana tren arus kas pengguna berdasarkan pemasukan dan pengeluaran?**")
trend_data = df_filtered.groupby(['Bulan-Tahun', 'tipe'])['nominal'].sum().reset_index()
fig_p2 = px.line(trend_data, x='Bulan-Tahun', y='nominal', color='tipe',
                 color_discrete_map={'Pemasukan': '#2ca02c', 'Pengeluaran': '#d62728'},
                 markers=True, title="Tren Arus Kas (Pemasukan vs Pengeluaran)",
                 labels={'nominal': 'Total (Rp)', 'Bulan-Tahun': 'Waktu'})
st.plotly_chart(fig_p2, use_container_width=True)

# P3: Fluktuasi Kategori
st.markdown("##### **Pertanyaan 3: Kategori pengeluaran apa yang mengalami perubahan dan fluktuasi terbesar?**")
st.write("*Grafik Boxplot di bawah ini menunjukkan seberapa besar rentang fluktuasi (naik-turun) tiap kategori. Kotak yang lebih panjang menandakan fluktuasi yang lebih ekstrem.*")
fig_p3 = px.box(df_exp, x='kategori', y='nominal', color='kategori',
                title="Sebaran dan Fluktuasi Nominal Pengeluaran per Kategori",
                labels={'nominal': 'Nominal Transaksi (Rp)', 'kategori': 'Kategori Pengeluaran'})
st.plotly_chart(fig_p3, use_container_width=True)

st.divider()

# 7. MODEL AI PONDASI & BUSINESS QUESTIONS (DIUPDATE TANPA PARENTS)
st.subheader("🤖 Blueprint & Pondasi Model AI PAYBAE")
col_ai1, col_ai2 = st.columns(2)

with col_ai1:
    st.markdown("""
    <div class="business-card">
        <span class="ai-tag">REGRESI / TIME-SERIES</span>
        <h4>Q1: Berapa prediksi total pengeluaran pengguna di esok hari atau minggu depan?</h4>
        <p><b>Masalah Bisnis:</b> Pengguna (pelajar, mahasiswa, atau pekerja) sering kehabisan uang di tengah bulan karena tidak memiliki proyeksi pengeluaran masa depannya.</p>
        <p><b>Pondasi Fitur (Notebook):</b> Menggunakan fitur lag <code>pengeluaran_1sebelumnya</code>, <code>pengeluaran_7sebelumnya</code>, dan rata-rata bergerak <code>rata-rata_7hari</code> untuk mendeteksi momentum pola transaksi.</p>
        <p><b>Target Evaluasi:</b> Target Mean Absolute Error (MAE) sekecil mungkin.</p>
    </div>
    <div class="business-card">
        <span class="ai-tag">DETEKSI ANOMALI</span>
        <h4>Q2: Bagaimana mendeteksi adanya transaksi impulsif yang tidak wajar (Outlier)?</h4>
        <p><b>Masalah Bisnis:</b> Deteksi dini pengeluaran boros yang tidak disadari untuk sistem peringatan mandiri <i>(Personal Smart Alert)</i> agar pengguna segera menyadari kebiasaan impulsifnya.</p>
        <p><b>Pondasi Fitur (Notebook):</b> Memanfaatkan fitur variabel <code>std_seminggu</code> dan <code>std_sebulan</code>. Jika pengeluaran saat ini melampaui batas deviasi standar historisnya, AI akan memberi label anomali.</p>
        <p><b>Algoritma Rencana:</b> Isolation Forest atau Z-Score Thresholding.</p>
    </div>
    """, unsafe_allow_html=True)

with col_ai2:
    st.markdown("""
    <div class="business-card">
        <span class="ai-tag">KLASIFIKASI / CONTEXT-AWARE</span>
        <h4>Q3: Apakah pola pengeluaran sangat dipengaruhi oleh hari gajian atau akhir pekan?</h4>
        <p><b>Masalah Bisnis:</b> Mengetahui pemicu psikologis (trigger) terbesar pengguna dalam menghabiskan uang secara impulsif.</p>
        <p><b>Pondasi Fitur (Notebook):</b> Mengeksploitasi kolom biner <code>is_payday</code> (tanggal 1-5) dan <code>weekend_encoded</code> untuk melihat apakah ada lonjakan belanja signifikan pada periode tersebut.</p>
        <p><b>Output AI:</b> Mengirimkan notifikasi pengingat otomatis ("Sabar, baru gajian, jangan langsung boros ya!").</p>
    </div>
    <div class="business-card">
        <span class="ai-tag">SISTEM REKOMENDASI OPTIMASI</span>
        <h4>Q4: Kategori pengeluaran apa yang paling mendesak untuk dikurangi guna mencapai target hemat?</h4>
        <p><b>Masalah Bisnis:</b> Pengguna membutuhkan arahan konkret (kategori mana yang harus dipangkas), bukan sekadar grafik angka.</p>
        <p><b>Pondasi Fitur (Notebook):</b> Menggabungkan visualisasi distribusi kategori dengan nilai <code>ema_7</code> (Exponential Moving Average) per kategori untuk melihat tren kategori pengeluaran yang sedang meningkat.</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# 8. INSIGHT & KESIMPULAN STRATEGIS (DIUPDATE TANPA PARENTS)
st.subheader("💡 Insight Data Historis & Rekomendasi Bisnis")
col_in1, col_in2 = st.columns(2)

with col_in1:
    st.info("""
    **📊 Kesimpulan Utama Analisis Data:**
    * **Identifikasi Missing Kategori:** Sebanyak 928 transaksi tidak memiliki kategori saat pertama kali diinput. Ini membuktikan pentingnya fitur **Auto-Categorization berbasis AI** pada aplikasi PAYBAE agar pengguna tidak malas mencatat manual.
    * **Pola Siklus Bulanan:** Terdapat lonjakan pengeluaran yang polanya berulang di awal bulan, berkolerasi kuat dengan tanggal kiriman bulanan / gajian (`is_payday`).
    """)

with col_in2:
    st.warning("""
    **⚠️ Strategi Intervensi Aplikasi PAYBAE:**
    * **Fitur Smart Budgeting Limit:** Pengguna dapat menetapkan limit harian cerdas mereka sendiri berdasarkan metrik `rata-rata_30hari` ditambah batas toleransi standar deviasi pengeluarannya. Sistem akan mengingatkan jika hampir melampaui limit, menjaga fleksibilitas tanpa overspending.
    * **Targeting Sektor Utama:** Karena pos *Food & Drinks* dan *Transport* mendominasi frekuensi harian, modul promo/edukasi finansial di dalam aplikasi harus diprioritaskan pada trik hemat kuliner dan transportasi.
    """)

# 9. AUDIT DATA (TRANSAKSI TERBARU)
st.subheader("🕒 Riwayat 10 Transaksi Terakhir")
st.dataframe(df_filtered.sort_values('Date', ascending=False).head(10)[['Date', 'deskripsi', 'kategori', 'tipe', 'nominal']], use_container_width=True)