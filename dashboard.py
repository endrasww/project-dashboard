import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Load data
path = '\data'

# Membaca dua data dari dataset Bike Sharing dan merubahnya menjadi DataFrame
bike_hour = pd.read_csv(path + "\hour.csv")
bike_day = pd.read_csv(path + "\day.csv")

# Mapping label dan nilai kategorikal
season_map = {1:'springer', 2:'summer', 3:'fall', 4:'winter'}
year_map = {0:'2011', 1:'2012'}
month_map = {
    1: 'January', 2: 'February', 3: 'March', 4: 'April',
    5: 'May', 6: 'June', 7: 'July', 8: 'August',
    9: 'September', 10: 'October', 11: 'November', 12: 'December'
}
day_map = {
    0: 'Sunday', 1: 'Monday', 2: 'Tuesday', 3: 'Wednesday',
    4: 'Thursday', 5: 'Friday', 6: 'Saturday'
}
weather_map = {
    1: 'Safe for Riding',
    2: 'Caution Advised',
    3: 'Poor Conditions',
    4: 'Extreme Weather',
}
workday_map = {0:'Weekend', 1:'Weekday'}
holiday_map = {0:'No Holiday', 1:'Holiday'}

# Ganti nilai sesuai mapping di bike_hour
bike_hour['season'] = bike_hour['season'].replace(season_map)
bike_hour['yr'] = bike_hour['yr'].replace(year_map)
bike_hour['mnth'] = bike_hour['mnth'].replace(month_map)
bike_hour['weekday'] = bike_hour['weekday'].replace(day_map)
bike_hour['weathersit'] = bike_hour['weathersit'].replace(weather_map)
bike_hour['workingday'] = bike_hour['workingday'].replace(workday_map)
bike_hour['holiday'] = bike_hour['holiday'].replace(holiday_map)
# Ganti nilai sesuai mapping di bike_day
bike_day['season'] = bike_day['season'].replace(season_map)
bike_day['yr'] = bike_day['yr'].replace(year_map)
bike_day['mnth'] = bike_day['mnth'].replace(month_map)
bike_day['weekday'] = bike_day['weekday'].replace(day_map)
bike_day['weathersit'] = bike_day['weathersit'].replace(weather_map)
bike_day['workingday'] = bike_day['workingday'].replace(workday_map)
bike_day['holiday'] = bike_day['holiday'].replace(holiday_map)
# Buat bin dan label untuk proses binning kategori jam
hr_bins = [0, 6, 9, 12, 14, 17, 20, 24]
hr_labels = [
    'Overnight',
    'Morning Commute',
    'Core Morning',
    'Lunch Break',
    'Core Afternoon',
    'Evening Commute',
    'Evening/Late'
]
# Buat kolom baru untuk menampung nilai binning jam
bike_hour['hr_bin'] = pd.cut(bike_hour['hr'],bins=hr_bins , labels=hr_labels, right=False)

# Bagian Sidebar
with st.sidebar:
    st.header("Dashboard Endraswara")
    st.subheader("Filter")
    
    # Filter tahun
    selected_year = st.multiselect(
        label='Pilih Tahun',
        options=bike_hour['yr'].unique(),
        default=bike_hour['yr'].unique()
        )

    # Filter hari
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    selected_day = st.sidebar.multiselect(
        label='Pilih Hari',
        options=days_order,
        default=days_order
        )

    # Filter kategori jam
    selected_hour = st.sidebar.multiselect(
        label='Pilih Kategori Jam',
        options=bike_hour['hr_bin'].unique(),
        default=bike_hour['hr_bin'].unique()
)
    
    # Filter hari libur
    selected_workingday = st.sidebar.multiselect(
        label='Pilih Jenis Hari',
        options=bike_hour['workingday'].unique(),
        default=bike_hour['workingday'].unique()
)

# Memilah data berdasarkan filter
filtered_bike_hour = bike_hour[
    (bike_hour['yr'].isin(selected_year)) &
    (bike_hour['weekday'].isin(selected_day)) &
    (bike_hour['hr_bin'].isin(selected_hour)) &
    (bike_hour['workingday']).isin(selected_workingday)
]

filtered_bike_day = bike_day[
    (bike_day['yr'].isin(selected_year)) &
    (bike_day['weekday'].isin(selected_day)) &
    (bike_day['workingday']).isin(selected_workingday)
]

# Bagian visualisasi
st.title("Bike Sharing Analytics Dashboard")

# visualisasi 1
st.subheader("1. Tren Penyewaan: Casual vs Registered per Hari")

# Mengecek apakah data kosong akibat filter
if filtered_bike_hour.empty:
    st.warning("Data kosong. Silakan sesuaikan kembali filter di sidebar.")
else:
    # Melt dataframe khusus untuk data yang sudah difilter
    melted_bike = filtered_bike_hour.melt(
        id_vars=['hr_bin', 'yr'],
        value_vars=['casual', 'registered'],
        var_name='user_type',
        value_name='total_rental'
    )
    
    # Membuat lineplot dari data melt
    fig1, ax1 = plt.subplots(figsize=(14, 6))
    sns.lineplot(
        data=melted_bike, x='hr_bin', y='total_rental', hue='user_type', 
        style='yr', markers=True, dashes=True, palette=['#ff7f0e', '#1f77b4'],
        linewidth=2.5, errorbar=None, ax=ax1
    )
    ax1.set_title("Rata-rata Penyewaan Berdasarkan Kategori Jam", fontsize=16, fontweight='bold', pad=15)
    ax1.set_xlabel("Kategori Jam", fontsize=12)
    ax1.set_ylabel("Rata-rata Penyewaan", fontsize=12)
    ax1.legend(title='Keterangan', fontsize=11)
    
    # Render plot ke Streamlit
    st.pyplot(fig1)

st.divider()

# Visualisasi 2
st.subheader("2. Dampak Kondisi Cuaca terhadap Penyewaan")

# Mengecek apakah data kosong akibat filter
if filtered_bike_day.empty:
    st.warning("Data kosong. Silakan sesuaikan kembali filter di sidebar.")
else:
    # Membuat catplot
    cplot = sns.catplot(
    data= filtered_bike_day,
    x='weathersit',
    y='cnt',
    hue='workingday',
    col='yr',
    kind='bar',
    palette='viridis',
    errorbar=None,
    height=6,
    aspect=1.2
)

   # Looping untuk menambahkan angka ke grafik kiri dan kanan
    for ax in cplot.axes.flat:
        for p in ax.patches:
            height = p.get_height()
            if not pd.isna(height) and height > 0:
                ax.annotate(f'{height:,.0f}',
                            (p.get_x() + p.get_width() / 2., height),
                            ha='center', va='bottom',
                            xytext=(0, 5),
                            textcoords='offset points',
                            fontsize=11, fontweight='bold', color='black')

        # Meningkatkan batas atas sumbu Y di setiap grafik agar angka tidak terpotong
        ax.set_ylim(0, bike_day['cnt'].max() * 1.15)

    # Menambahkan judul
    cplot.figure.suptitle('Dampak Cuaca terhadap Penyewaan: Hari Kerja vs Libur\n(Perbandingan Tahun 2011 vs 2012)',
                fontsize=18, fontweight='bold', y=1.08)

    # Label sumbu X dan Y
    cplot.set_axis_labels('Kondisi Cuaca', 'Rata-rata Penyewaan Harian')

    # Mengubah kata yr menjadi Tahun
    cplot.set_titles("Tahun {col_name}", size=14, fontweight='bold')

    # Menyesuaikan judul Legenda
    cplot.legend.set_title('Tipe Hari')
    
    # Render plot ke Streamlit
    st.pyplot(cplot)


st.caption("Copyright © Endraswara Wiryawan 2026")
