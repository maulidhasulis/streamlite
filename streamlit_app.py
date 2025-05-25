import streamlit as st
from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
from urllib.parse import urlparse
from bson.objectid import ObjectId
from wordcloud import WordCloud
import nltk
from nltk.corpus import stopwords

# --- Unduh stopwords bahasa Indonesia ---
nltk.download('stopwords')
stop_words = set(stopwords.words('indonesian'))

# --- Konfigurasi Halaman ---
st.set_page_config(page_title="Jenis-jenis Gerakan Trampolin", layout="wide")

# --- Header ---
st.title("Jenis-jenis Gerakan Trampolin")

# --- Koneksi ke MongoDB Atlas (Cloud) ---
client = MongoClient("mongodb+srv://maulidhafia0:Akumaulidha123@prajekcapstone.z3344wk.mongodb.net/?retryWrites=true&w=majority&appName=prajekcapstone")
db = client["trampolin_db"]
collection = db["artikel_gerakan"]

# --- Ambil dan Proses Data ---
data = list(collection.find())
df = pd.DataFrame(data)

if df.empty:
    st.warning("Tidak ada data artikel yang tersedia di database.")
    st.stop()

# Ekstrak domain dari URL
df['domain'] = df['url'].apply(lambda x: urlparse(x).netloc if pd.notnull(x) else "Unknown")

# --- Statistik Umum ---
st.markdown("### Statistik Umum")
col1, col2 = st.columns(2)
col1.metric("Total Artikel", len(df))
col2.metric("Jumlah Domain", df['domain'].nunique())

# --- Daftar Artikel ---
with st.expander("Lihat Daftar Artikel"):
    st.dataframe(df[['title', 'url']], use_container_width=True)

# --- Grafik Jumlah Artikel per Domain ---
st.markdown("### Jumlah Artikel per Domain")
st.bar_chart(df['domain'].value_counts())

# --- Word Cloud Judul Artikel ---
st.markdown("### ☁ Word Cloud Judul Artikel")
if df['title'].notnull().any():
    # Gabungkan semua judul artikel
    title_text = " ".join(df['title'].dropna())

    # Filter kata menggunakan stopwords bahasa Indonesia
    filtered_words = [word for word in title_text.split() if word.lower() not in stop_words]
    filtered_text = " ".join(filtered_words)

    # Buat Word Cloud
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(filtered_text)

    # Tampilkan Word Cloud
    fig_wc, ax_wc = plt.subplots()
    ax_wc.imshow(wordcloud, interpolation='bilinear')
    ax_wc.axis('off')
    st.pyplot(fig_wc)
else:
    st.info("⚠ Tidak ada judul artikel untuk dibuat Word Cloud.")

# --- Detail Artikel Berdasarkan Kata Kunci ---
st.markdown("### 🔍 Pencarian Artikel berdasarkan Kata Kunci")
with st.expander("Cari Artikel berdasarkan Kata Kunci"):
    keyword_input = st.text_input("Masukkan kata kunci untuk mencari artikel:")
    if keyword_input:
        # Gunakan regex case-insensitive untuk mencari di title dan content
        query = {
            "$or": [
                {"title": {"$regex": keyword_input, "$options": "i"}},
                {"content": {"$regex": keyword_input, "$options": "i"}}
            ]
        }
        matching_articles = list(collection.find(query))

        if matching_articles:
            st.success(f"✅ Ditemukan {len(matching_articles)} artikel yang cocok.")
            for article in matching_articles:
                st.markdown("---")
                st.markdown(f"**📰 Judul:** {article.get('title', 'Tidak tersedia')}")
                st.markdown(f"**📖 Konten:** {article.get('content', 'Tidak tersedia')}")
                url = article.get('url', '')
                if url:
                    st.markdown(f"**🔗 URL:** [{url}]({url})")
        else:
            st.warning("Tidak ada artikel yang cocok dengan kata kunci tersebut.")
