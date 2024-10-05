import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

st.header('Dashbord Submission Kelas Data Analyst :sparkles:')
st.text('Create: Muhammad Hafiz Nur')

day_df = pd.read_csv("Data/day.xls")
hour_df = pd.read_csv("Data/hour.xls")

#Mengubah tipe data dteday menjadi datetime
day_df['dteday'] = pd.to_datetime(day_df['dteday'])
day_df['dteday'] = pd.to_datetime(hour_df['dteday'])

Q1 = hour_df['cnt'].quantile(0.25)
Q3 = hour_df['cnt'].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1 * IQR
upper_bound = Q3 + 1 * IQR

median_cnt = hour_df['cnt'].median()
hour_df['cnt'] = np.where((hour_df['cnt'] < lower_bound) | (hour_df['cnt'] > upper_bound), median_cnt, hour_df['cnt'])

#Menyiapkan fungsi untuk Workingday
def create_workingday_rent_df(df):
    workingday_rent_df = df.groupby(by='workingday').agg({
        'cnt': 'sum'
    }).reset_index()
    return workingday_rent_df

#Menyiapkan fungsi untuk Holiday
def create_holiday_rent_df(df):
    holiday_rent_df = df.groupby(by='holiday').agg({
        'cnt': 'sum'
    }).reset_index()
    return holiday_rent_df

#Menyiapkan fungsi untuk Cuaca
def create_weather_rent_df(df):
    weather_rent_df = df.groupby(by='weathersit').agg({
        'cnt': 'sum'
    })
    return weather_rent_df

#Mengubah nomor menjadi kategori di Cuaca
day_df['weathersit'] = day_df['weathersit'].map({
    1: 'Clean/Partly Cloudy',
    2: 'Misty/Cloudy',
    3: 'Light Snow/Rain',
    4: 'Severe Weather'
})

#Memberi nama-nama hari
day_df['weekday'] = day_df['weekday'].map({
    0: 'Sun', 1: 'Mon', 2: 'Tue', 3: 'Wed', 4: 'Thu', 5: 'Fri', 6: 'Sat'
})

day_df.groupby(by='weekday').agg({
    'cnt':['max','min','mean']
})

#PERTANYAAN 1
def cuaca_page():
    st.subheader('Pengaruh Cuaca terhadap Penggunaan Sepeda')

    #Mendapatkan daftar tahun yang ada di dataset
    tahun_list = day_df['yr'].unique().tolist()
    tahun_list.sort()

    #Pilih rentang tahun
    start_year, end_year = st.select_slider(
        'Pilih rentang tahun:',
        options=tahun_list,
        value=(min(tahun_list), max(tahun_list))
    )

    #Pilih rentang bulan
    bulan_list = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    start_month = st.selectbox('Pilih Bulan Awal:', bulan_list)
    end_month = st.selectbox('Pilih Bulan Akhir:', bulan_list)

    #Mengonversi bulan menjadi angka
    bulan_dict = {month: index + 1 for index, month in enumerate(bulan_list)}
    start_month_index = bulan_dict[start_month]
    end_month_index = bulan_dict[end_month]

    #Filter data berdasarkan tahun dan bulan yang dipilih
    filtered_day_df = day_df[
        (day_df['yr'] >= start_year) & 
        (day_df['yr'] <= end_year) & 
        (day_df['mnth'] >= start_month_index) & 
        (day_df['mnth'] <= end_month_index)
    ]

    #Mendapatkan pilihan jenis cuaca dari dropdown, ditambah dengan opsi untuk menampilkan 3 cuaca awal
    weathersit_options = day_df['weathersit'].unique()
    option_list = ['Tampilkan 3 cuaca awal'] + list(weathersit_options)

    #Dropdown untuk memilih cuaca
    selected_weather = st.selectbox('Pilih jenis cuaca:', option_list, index=0)

    #Logika untuk menampilkan grafik
    if selected_weather == 'Tampilkan 3 cuaca awal':
        #Menampilkan 3 cuaca pertama
        initial_display_options = weathersit_options[:3]
        filtered_day_df = filtered_day_df[filtered_day_df['weathersit'].isin(initial_display_options)]
    else:
        #Menampilkan data sesuai pilihan pengguna
        filtered_day_df = filtered_day_df[filtered_day_df['weathersit'] == selected_weather]

    #Membuat visualisasi menggunakan seaborn dan matplotlib
    fig, ax = plt.subplots(figsize=(6, 6))

    sns.barplot(
        x='weathersit',
        y='cnt',
        data=filtered_day_df,
        palette=['blue'],
        ax=ax
    )

    #Menambahkan judul dan label sumbu
    if selected_weather == 'Tampilkan 3 cuaca awal':
        ax.set_title('Jumlah Pengguna Sepeda berdasarkan 3 Kondisi Cuaca Pertama')
    else:
        ax.set_title(f'Jumlah Pengguna Sepeda pada Kondisi Cuaca: {selected_weather}')
    
    ax.set_xlabel(None)
    ax.set_ylabel(None)

    #Menampilkan plot di aplikasi Streamlit
    st.pyplot(fig)

    #Tombol untuk kembali ke landing page
    if st.button('Kembali ke Beranda'):
        st.session_state.page = 'landing'

#PERTANYAAN 2
def workingday_holiday_page():
    st.subheader('Pengguna Sepeda berdasarkan Kategori (Workingday, Holiday, atau Keduanya)')

# Mendapatkan daftar kategori
    kategori_list = ['workingday', 'holiday', 'workingday dan holiday']

# Dropdown untuk memilih kategori
    selected_category = st.selectbox('Pilih kategori:', kategori_list, index=0)

# Pilih rentang bulan
    bulan_list = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    start_month = st.selectbox('Pilih Bulan Awal:', bulan_list, index=0)
    end_month = st.selectbox('Pilih Bulan Akhir:', bulan_list, index=len(bulan_list) - 1)

# Mengonversi bulan menjadi angka
    bulan_dict = {month: index + 1 for index, month in enumerate(bulan_list)}
    start_month_index = bulan_dict[start_month]
    end_month_index = bulan_dict[end_month]

    # Filter data berdasarkan bulan yang dipilih
    filtered_day_df = day_df[
        (day_df['mnth'] >= start_month_index) & 
        (day_df['mnth'] <= end_month_index)
    ]

    # Filter data berdasarkan kategori yang dipilih
    if selected_category == 'workingday':
        filtered_day_df = filtered_day_df[filtered_day_df['workingday'] == 1]
    elif selected_category == 'holiday':
        filtered_day_df = filtered_day_df[filtered_day_df['holiday'] == 1]
    elif selected_category == 'workingday dan holiday':
        filtered_day_df = filtered_day_df[(filtered_day_df['workingday'] == 1) | (filtered_day_df['holiday'] == 1)]

# Membuat visualisasi menggunakan seaborn dan matplotlib
    fig, ax = plt.subplots(figsize=(6, 6))

# Menggunakan satu warna untuk semua batang
    sns.barplot(
        data=filtered_day_df,
        x='workingday' if selected_category != 'holiday' else 'holiday',
        y='cnt',
        color='darkblue',  # Menggunakan warna tetap
        ax=ax
    )

    # Menambahkan judul dan label sumbu
    if selected_category == 'workingday dan holiday':
        ax.set_title('Jumlah Penyewa Sepeda berdasarkan Workingday dan Holiday')
    elif selected_category == 'workingday':
        ax.set_title('Jumlah Penyewa Sepeda pada Workingday')
    elif selected_category == 'holiday':
        ax.set_title('Jumlah Penyewa Sepeda pada Holiday')

    ax.set_xlabel('Workingday = 1, Holiday = 0' if selected_category == 'workingday dan holiday' else selected_category.capitalize())
    ax.set_ylabel('Jumlah Pengguna')

    # Menampilkan plot di aplikasi Streamlit
    st.pyplot(fig)

    #Tombol untuk kembali ke landing page
    if st.button('Kembali ke Beranda'):
        st.session_state.page = 'landing'

#PERTANYAAN 3
def tren_penggunaan_sepeda_page():
    st.subheader('Tren Penggunaan Sepeda per Bulan dan Tahun')

    # Input bulan awal dan bulan akhir
    bulan_awal = st.selectbox('Pilih Bulan Awal', options=list(range(1, 13)), index=0)
    bulan_akhir = st.selectbox('Pilih Bulan Akhir', options=list(range(1, 13)), index=11)

    # Memastikan bulan akhir lebih besar dari bulan awal
    if bulan_akhir < bulan_awal:
        st.error("Bulan akhir harus lebih besar atau sama dengan bulan awal.")
    else:
        # Mengelompokkan data
        agg_year_month_df = day_df.groupby(by=['yr', 'mnth']).agg({
            'cnt': 'sum'
        }).reset_index()

        # Memfilter berdasarkan rentang bulan
        agg_year_month_df = agg_year_month_df[
            (agg_year_month_df['mnth'] >= bulan_awal) & (agg_year_month_df['mnth'] <= bulan_akhir)
        ]

        # Membuat visualisasi menggunakan seaborn dan matplotlib
        fig, ax = plt.subplots(figsize=(12, 8))

        # Membuat lineplot dengan marker di setiap titik data
        sns.lineplot(
            data=agg_year_month_df,
            x='mnth',
            y='cnt',
            hue='yr',
            marker='o',
            errorbar=None,
            palette='viridis',
            ax=ax
        )

        # Menambahkan judul dan label sumbu
        ax.set_title('Tren Penggunaan Sepeda Tiap Bulan dan Tahun')
        ax.set_xlabel(None)
        ax.set_ylabel(None)
        ax.set_xticks(range(bulan_awal, bulan_akhir + 1))
        ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][bulan_awal - 1:bulan_akhir])

        # Menambahkan legenda
        ax.legend(title='Year', labels=['2011', '2012'])

        # Garis horizontal dan vertikal untuk setiap titik
        line_colors = ['lightgrey', 'lightblue', 'lightgreen']
        for index, row in agg_year_month_df.iterrows():
            color = line_colors[index % len(line_colors)]
            ax.axhline(y=row['cnt'], color=color, linestyle='--', linewidth=0.5)

        for month in range(bulan_awal, bulan_akhir + 1):
            ax.axvline(x=month, color='lightgrey', linestyle='--', linewidth=0.5)

        # Menampilkan plot di aplikasi Streamlit
        st.pyplot(fig)

    #Tombol untuk kembali ke landing page
    if st.button('Kembali ke Beranda'):
        st.session_state.page = 'landing'

#PERTANYAAN 4
def pengguna_sepeda_per_hari_page():
    st.subheader('Pengguna Sepeda berdasarkan Hari dalam Seminggu')

    #Menampilkan filter tanggal
    start_date = st.date_input("Pilih tanggal mulai", value=pd.to_datetime('2011-01-01'))
    end_date = st.date_input("Pilih tanggal akhir", value=pd.to_datetime('2012-12-31'))

    #Memastikan start date >= end date
    if start_date > end_date:
        st.error("Tanggal mulai harus lebih kecil atau sama dengan tanggal akhir.")
        return

    #Memfilter dataset berdasarkan rentang tanggal
    filtered_day_df = day_df[(day_df['dteday'] >= pd.to_datetime(start_date)) & 
                             (day_df['dteday'] <= pd.to_datetime(end_date))]

    #Membuat visualisasi menggunakan seaborn dan matplotlib
    fig, ax = plt.subplots(figsize=(10, 6))

    sns.lineplot(
        x='weekday',
        y='cnt',
        data=filtered_day_df,
        ax=ax,  #Menggunakan ax tanpa indeks
        marker='o'  #Opsional: menambahkan penanda pada setiap titik data
    )

    #Menambahkan judul dan label sumbu
    ax.set_title(f'Jumlah Pengguna Sepeda dari {start_date} hingga {end_date}')
    ax.set_xlabel(None)
    ax.set_ylabel(None)

    #Menampilkan plot di aplikasi Streamlit
    st.pyplot(fig)
    #Tombol untuk kembali ke landing page
    if st.button('Kembali ke Beranda'):
        st.session_state.page = 'landing'


#Fungsi untuk landing page
def landing_page():
    st.title('Dashboard Pengguna Sepeda')
    st.write("Selamat datang di dashboard! Silakan pilih salah satu menu di bawah.")
    
    #Tombol untuk navigasi ke halaman Pengguna Sepeda berdasarkan Workingday dan Holiday
    if st.button('Pengguna Sepeda berdasarkan Cuaca'):
        st.session_state.page = 'cuaca'
    elif st.button('Pengguna Sepeda berdasarkan Workingday dan Holiday'):
        st.session_state.page = 'workingday_holiday'
    elif st.button('Pengguna Sepeda tiap Bulan dan Tahun'):
        st.session_state.page = 'tren_penggunaan_sepeda'
    elif st.button('Pengguna Sepeda Setiap Hari'):
        st.session_state.page = 'pengguna_sepeda_per_hari'

#Inisialisasi halaman
if 'page' not in st.session_state:
    st.session_state.page = 'landing'

#Logika untuk navigasi antar halaman
if st.session_state.page == 'landing':
    landing_page()
elif st.session_state.page == 'cuaca':
    cuaca_page()
elif st.session_state.page == 'workingday_holiday':
    workingday_holiday_page()
elif st.session_state.page == 'tren_penggunaan_sepeda':
    tren_penggunaan_sepeda_page()
elif st.session_state.page == 'pengguna_sepeda_per_hari':
    pengguna_sepeda_per_hari_page()

st.caption('Copyright © Muhammad Hafiz Nur, 2024')