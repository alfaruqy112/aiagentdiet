import streamlit as st
import google.generativeai as genai
from datetime import datetime
import random

# === PAGE CONFIG ===
st.set_page_config(page_title="AI Diet Assistant", page_icon="🥗")

# === SHARED STATE ===
if "food_log" not in st.session_state:
    st.session_state.food_log = []

# =========================================================
# PAGE 1: CHAT (AI Diet Assistant)
# =========================================================
def chat_page():
    st.title("💬 Chat dengan AI Diet Assistant")
    st.caption("Tanya seputar rencana makan, strategi diet, atau pola hidup sehat ✨")

    # --- API Key ---
    try:
        google_api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=google_api_key)
    except KeyError:
        st.error("🛑 GOOGLE_API_KEY belum diset di `.streamlit/secrets.toml`.")
        st.stop()

    # --- SYSTEM PROMPT UNTUK AI DIET ASSISTANT ---
    system_prompt = """
    Anda adalah "AI Diet Assistant", seorang asisten nutrisi dan perencana diet pribadi yang ramah, cerdas, dan berbasis ilmu gizi modern.

    TUJUAN: Membantu pengguna membuat rencana diet harian yang sehat, realistis, dan sesuai tujuan (menurunkan berat badan, menambah massa otot, atau menjaga pola makan seimbang).

    IKUTI ALUR INI SECARA KONSISTEN:

    --- FASE 1: PENGUMPULAN DATA ---
    Langkah 1: Mulailah dengan sapaan hangat. (Contoh: "Halo! Saya AI Diet Assistant, siap bantu kamu capai target diet dengan sehat.")
    Lalu ajukan pertanyaan pertama.

    Langkah 2: Tanyakan pertanyaan berikut SATU PER SATU. Jangan tanya lebih dari satu pertanyaan sekaligus.
        1 Apa tujuan utama diet kamu? (contoh: menurunkan berat, menambah massa otot, menjaga pola makan sehat)
        2 Boleh tahu berat badan, tinggi badan, dan usia kamu? (contoh: 68kg, 170cm, 27 tahun)
        3 Seberapa aktif kamu sehari-hari? (contoh: duduk seharian, aktif ringan, atau sangat aktif)
        4 Ada pantangan atau preferensi makanan? (contoh: halal only, vegetarian, alergi seafood, dll)

    --- FASE 2: RENCANA DIET OTOMATIS ---
    Langkah 3: Setelah data terkumpul lengkap, konfirmasi dulu ke pengguna.
    Contoh: "Data kamu sudah lengkap, saya akan buatkan rencana diet personal berdasarkan profil kamu..."

    Langkah 4: Buat rencana diet rinci:
        - Kalori harian yang disarankan (dengan alasan singkat)
        - Rincian makronutrisi (karbo, protein, lemak)
        - Menu harian (pagi, siang, malam, snack)
        - Tips gaya hidup pendukung (air putih, tidur, aktivitas fisik)
    Gunakan **Markdown dan tabel** agar hasilnya rapi.

    Langkah 5: Setelah selesai, sampaikan pesan penutup seperti:
    "Rencana diet kamu sudah siap! Gunakan tombol di sidebar jika ingin mulai lagi atau ubah tujuan dietmu."

    PENTING:
    - Jangan pernah menyimpang ke topik non-diet.
    - Gunakan bahasa ramah, edukatif, dan tidak menghakimi.
    - Jangan memberikan saran medis ekstrem (misal diet terlalu rendah kalori tanpa dokter).
    """

    # --- Inisialisasi Model ---
    if "diet_model" not in st.session_state:
        st.session_state.diet_model = genai.GenerativeModel(
            model_name="models/gemini-2.5-flash",
            system_instruction=system_prompt
        )
        st.session_state.diet_chat = st.session_state.diet_model.start_chat(history=[])

    # --- Tampilkan Riwayat Chat ---
    if "diet_messages" not in st.session_state:
        st.session_state.diet_messages = []

    for msg in st.session_state.diet_messages:
        role = "user" if msg["role"] == "user" else "assistant"
        with st.chat_message(role):
            st.markdown(msg["content"])

    # --- Input Pengguna ---
    user_input = st.chat_input("Ketik pesan kamu di sini...")

    if user_input:
        st.session_state.diet_messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        try:
            with st.chat_message("assistant"):
                with st.spinner("AI Diet Assistant sedang berpikir..."):
                    response = st.session_state.diet_chat.send_message(user_input)
                    answer = response.text
                    st.markdown(answer)
                    st.session_state.diet_messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            st.error(f"Terjadi error: {e}")

# =========================================================
# PAGE 2: TRACKING MAKANAN
# =========================================================
def tracking_page():
    st.title("🍱 Tracking Makanan Harian")
    st.caption("Catat makananmu hari ini dan lihat estimasi kalorinya.")

    food = st.text_input("Tulis makanan (contoh: ayam bakar, nasi putih, tempe goreng):")
    if st.button("Hitung Kalori", key="calc_btn"):
        if food:
            estimated_cal = 300 + len(food) * 2
            entry = {
                "Waktu": datetime.now().strftime("%H:%M"),
                "Makanan": food,
                "Kalori": f"{estimated_cal} kkal"
            }
            st.session_state.food_log.append(entry)
            st.success(f"Estimasi: {estimated_cal} kkal — catatan disimpan ✅")

    if st.session_state.food_log:
        st.markdown("### 📋 Riwayat Hari Ini")
        st.table(st.session_state.food_log)
        total = sum(int(row["Kalori"].replace(" kkal", "")) for row in st.session_state.food_log)
        st.info(f"🔥 Total kalori hari ini: **{total} kkal**")
    else:
        st.info("Belum ada makanan yang dicatat 🍽️")

# =========================================================
# PAGE 3: MOTIVASI
# =========================================================
def motivation_page():
    st.title("💡 Motivasi Harian")
    st.caption("Sedikit dorongan biar semangat diet kamu tetap jalan 💪")

    if st.button("🎯 Dapatkan Tips Hari Ini"):
        tips = [
            "Konsistensi kecil hari ini = perubahan besar bulan depan 💪",
            "Air putih dulu sebelum makan — simple tapi efektif 💧",
            "Gagal diet bukan akhir, itu cuma data baru buat strategi berikutnya 📈",
            "Makan sehat gak harus fancy, yang penting niatnya stabil 🍎",
            "Tubuhmu investasi jangka panjang, rawat dia seperti aset 🔥"
        ]
        st.success(random.choice(tips))

# =========================================================
# SIDEBAR NAVIGATION
# =========================================================
pages = [
    st.Page(chat_page, title="💬 Chat AI Diet"),
    st.Page(tracking_page, title="🍱 Tracking Makanan"),
    st.Page(motivation_page, title="💡 Motivasi Harian")
]

pg = st.navigation(pages)

with st.sidebar:
    st.markdown("## 🥗 AI Diet Assistant")
    st.caption("Teman dietmu yang realistis dan santai.")
    st.divider()
    st.info("Gunakan menu di atas untuk berpindah fitur.")
    if st.button("🔄 Reset Semua Data"):
        st.session_state.clear()
        st.success("Data berhasil direset 🔁")

pg.run()
