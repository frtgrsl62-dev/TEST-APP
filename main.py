import streamlit as st
import time
import json
import os
import math
from streamlit_cookies_manager import EncryptedCookieManager

from soru_bankasi import soru_bankasini_yukle, soru_bankasini_kaydet
from ders_konu_notlari import ders_konu_notlari
from deneme_sinavlari import deneme_sinavlari



import uuid


# ===============================
# SORU BANKASI (GLOBAL)
# ===============================
soru_bankasi = soru_bankasini_yukle()

ADMIN_USERS = ["a"]  # admin kullanıcı adları


cookies = EncryptedCookieManager(
    prefix="kpss_app",
    password="kpss_super_secret_2026"
)

if not cookies.ready():
    st.stop()


# ===============================
# Dosya yolları
# ===============================
DOSYA = "kullanicilar.json"
# AKTIF_DOSYA = "aktif_kullanici.json" # <-- KALDIRILDI: Bu dosya çoklu oturum sorununa neden oluyordu.

# ===============================
# Sabit kullanıcılar
# ===============================
sabit_kullanicilar = {
    "a": {"isim": "Yönetici", "sifre": "1"},
    "m": {"isim": "Misafir Kullanıcı", "sifre": "0"},
}

# ===============================
# Kullanıcı yükle / kaydet
# ===============================
def kullanicilari_yukle():
    if not os.path.exists(DOSYA):
        with open(DOSYA, "w", encoding="utf-8") as f:
            f.write("{}")
    with open(DOSYA, "r", encoding="utf-8") as f:
        # Dosya boşsa veya bozuksa oluşabilecek hatayı önle
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def kullanicilari_kaydet():
    with open(DOSYA, "w", encoding="utf-8") as f:
        json.dump(kullanicilar, f, ensure_ascii=False, indent=2)

# ===============================
# Aktif kullanıcı fonksiyonları KALDIRILDI
# Bu fonksiyonlar tek bir dosyaya bağımlı olduğu için çoklu oturumu engelliyordu.
# ===============================

# ===============================
# Sonuçları kullanıcıya kaydet
# ===============================
def kaydet_sonuclar_to_user(user):
    # Kullanıcı None ise veya sistemde kayıtlı değilse işlem yapma
    if not user or user not in kullanicilar:
        return
    kullanicilar[user]["sonuclar"] = st.session_state.get("sonuclar", {})
    kullanicilari_kaydet()

def kullanici_sonuclarini_yukle_to_session(user):
    if user in kullanicilar:
        st.session_state["sonuclar"] = kullanicilar[user].get("sonuclar", {})
    else:
        # Kullanıcının daha önce kaydedilmiş sonucu yoksa boş başlat
        st.session_state["sonuclar"] = {}


# ======================================================
# GLOBAL
# ======================================================
kullanicilar = kullanicilari_yukle()

# ===============================
# Global değişkenler
# ===============================
kullanicilar = kullanicilari_yukle()

# ===============================
# Login Sayfası
# ===============================
def login_page():
    st.markdown("<h1 style='text-align: center; color: orange;'>KPSS SORU ÇÖZÜM PLATFORMU</h1>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<h1>Giriş Ekranı</h1>", unsafe_allow_html=True)

    with st.form("login_form"):
        k_adi = st.text_input("Kullanıcı Adı", key="login_user")
        sifre = st.text_input("Şifre", type="password", key="login_pass")
        giris_btn = st.form_submit_button("🟢 Giriş Yap 🟢")
        kayit_btn = st.form_submit_button("🔹 Kayıt Ol 🔹")

    if giris_btn:
        if (k_adi in sabit_kullanicilar and sabit_kullanicilar[k_adi]["sifre"] == sifre) or \
           (k_adi in kullanicilar and kullanicilar[k_adi]["sifre"] == sifre):

            st.session_state["current_user"] = k_adi
            cookies["current_user"] = k_adi
            cookies.save()

            kullanici_sonuclarini_yukle_to_session(k_adi)
            st.session_state["page"] = "ders"
            st.rerun()
            
        else:
            st.error("❌ Hatalı kullanıcı adı veya şifre!")

    if kayit_btn:
        st.session_state["page"] = "kayit"
        st.rerun()

# ===============================
# Kayıt Sayfası
# ===============================
def kayit_page():
    st.markdown("<h1 style='text-align: center; color: orange; font-size:36px;'>KPSS SORU ÇÖZÜM PLATFORMU</h1>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<h1>Kayıt Ol</h1>", unsafe_allow_html=True)

    with st.form("kayit_form"):
        isim = st.text_input("İsim Soyisim", key="register_name")
        k_adi = st.text_input("Kullanıcı Adı", key="register_user")
        sifre = st.text_input("Şifre", type="password", key="register_pass")
        sifre_tekrar = st.text_input("Şifre Tekrar", type="password", key="register_pass2")
        kaydet_btn = st.form_submit_button("Kaydet ✅")
        geri_btn = st.form_submit_button("↩️ Geri Dön")

    if kaydet_btn:
        if not isim or not k_adi or not sifre or not sifre_tekrar:
            st.error("❌ Lütfen tüm alanları doldurun!")
            return
        if sifre != sifre_tekrar:
            st.error("❌ Şifreler uyuşmuyor!")
            return
        if k_adi in sabit_kullanicilar or k_adi in kullanicilar:
            st.error("❌ Bu kullanıcı adı zaten kayıtlı!")
            return
        kullanicilar[k_adi] = {"isim": isim, "sifre": sifre, "sonuclar": {}}
        kullanicilari_kaydet()
        st.success(f"✅ {isim} başarıyla kaydedildi! Lütfen giriş yapın.")
        time.sleep(1)
        st.session_state["page"] = "login"
        st.rerun()

    if geri_btn:
        st.session_state["page"] = "login"
        st.rerun()

# ===============================
# Ders Seçim Sayfası
# ===============================

def ders_secim_page():
    user = st.session_state.get("current_user")
    if user in ADMIN_USERS:
        if st.button("👨‍🏫 Admin Panel"):
            st.session_state.page = "admin"
            st.rerun()
    
    col1, col2 = st.columns([8, 2])
    with col2:
        user = st.session_state.get("current_user")
        if user:
            if st.button(f"👤 {user}"):
                st.session_state["page"] = "profil"
                st.rerun()

    st.markdown("<h1 style='font-size:38px;'>Ders Seçiniz</h1>", unsafe_allow_html=True)
    st.markdown("---")

    for ders in soru_bankasi.keys():
        if st.button(ders, key=f"ders_{ders}"):
            st.session_state["ders"] = ders
            st.session_state["page"] = "konu"
            st.rerun()

    if st.button("📝 Deneme Sınavları"):
        st.session_state["page"] = "deneme"
        st.rerun()

    if st.button("Genel Raporu Gör 📊"):
        st.session_state["page"] = "rapor"
        st.rerun()

    st.markdown("---")


    if st.button("🔻 Çıkış Yap 🔻"):
        # Sonuçları kaydet
        kaydet_sonuclar_to_user(st.session_state.get("current_user"))

        # COOKIE ve SESSION TAM TEMİZLE
        cookies.pop("current_user", None)
        cookies.save()

        st.session_state.current_user = None
        st.session_state.page = "login"

        # ⚠️ COOKIE AUT0 LOGIN BLOĞUNU ATLATMAK İÇİN FLAG
        st.session_state["logout"] = True

        st.rerun()

    st.markdown("---")
    st.markdown("<p style='text-align: center; color: orange; font-size:15px;'>KPSS SORU ÇÖZÜM PLATFORMU</p>", unsafe_allow_html=True)


# ===============================
# Konu Seçim Sayfası (Dairesel yüzde gösterimi)
# ===============================
from ders_konu_notlari import ders_konu_notlari

def konu_secim_page(ders):

    # Geri butonu
    if st.button("🏠 Geri"):
        st.session_state["page"] = "ders"
        st.rerun()
    
    st.markdown(
        f"<h2 style='font-size:30px;'>{ders} - Konu Seçimi</h2>",
        unsafe_allow_html=True
    )

    # 📚 Ders Notu butonu
    ders_notu_link = ders_konu_notlari.get(ders, {}).get("__ders_notu__", "")
    if ders_notu_link:
        st.markdown(
          f"<a href='{ders_notu_link}' target='_blank'><button style='background-color: transparent; color: ; padding:8px; border: 1px solid #007BFF; border-radius:8px; cursor:pointer;'>📚 Ders Notları</button></a>",      
            unsafe_allow_html=True
        )


    konular = list(soru_bankasi[ders].keys())
    sonuclar = st.session_state.get("sonuclar", {})

    for konu in konular:
        tum_sorular = soru_bankasi[ders][konu]
        soru_grubu_sayisi = 5
        toplam_test_sayisi = math.ceil(len(tum_sorular) / soru_grubu_sayisi)

        # Çözülen test sayısını bul
        testler = sonuclar.get(ders, {}).get(konu, {})
        cozulmus_test_sayisi = sum(
            1 for key in testler if key.startswith("test_")
        )

        # Yüzdeyi hesapla
        yuzde = int(cozulmus_test_sayisi / toplam_test_sayisi * 100) if toplam_test_sayisi > 0 else 0

        col1, col2, col3 = st.columns([1, 8, 2])
        with col1:
            # Dairesel progress
            st.markdown(f"""
            <div style="
                width:40px; height:40px; border-radius:40%;
                background: conic-gradient(#4CAF50 {yuzde}%, #E0E0E0 {yuzde}%);
                display:flex; align-items:center; justify-content:center;
                font-weight:bold; color:black;">
                {yuzde}%
            </div>
            """, unsafe_allow_html=True)

        with col2:
            if st.button(f"→ {konu}", key=f"konu_{konu}"):
                st.session_state["konu"] = konu
                st.session_state["page"] = "test"
                st.rerun()

 #       with col3:
 #           # Konu linki varsa Not butonu
 #           konu_link = ders_konu_notlari.get(ders, {}).get(konu, "")
 #           if konu_link:
 #              st.markdown(
 #                  f"<a href='{konu_link}' target='_blank' style='text-decoration:none; color:#007BFF;'>📕 pdf</a>",
 #                  unsafe_allow_html=True
 #               )  

    st.markdown("---")
    st.markdown("<h1 style='text-align: center; color: orange; font-size:15px;'>KPSS SORU ÇÖZÜM PLATFORMU</h1>", unsafe_allow_html=True)



# ===============================
# Test Seçim Sayfası
# ===============================
from ders_konu_notlari import ders_konu_notlari

def test_secim_page(secilen_ders, secilen_konu):
    # Geri butonu sol üst
    if st.button("🔙 Geri"):
        st.session_state["page"] = "konu"
        st.rerun()
    
    st.markdown(
        f"<h2 style='font-size:25px;'>{secilen_ders} - {secilen_konu} </h2>",
        unsafe_allow_html=True
    )

    # 📕 Konu Notu butonu
    konu_link = ders_konu_notlari.get(secilen_ders, {}).get(secilen_konu, "")
    if konu_link:  # Link varsa göster
        st.markdown(
            f"<a href='{konu_link}' target='_blank'><button style='background-color: transparent; color: ; padding:6px; border: 1px solid #007BFF; border-radius:8px; cursor:pointer;'>📕 Konu Notu</button></a>",
            unsafe_allow_html=True
        )
    else:  # Link yoksa bilgi ver
        st.info("Bu konu için henüz not eklenmemiştir.")

    tum_sorular = soru_bankasi[secilen_ders][secilen_konu]
    if not tum_sorular:
        st.info("Bu konu için henüz soru eklenmemiş.")
        if st.button("Geri"):
            st.session_state["page"] = "konu"
            st.rerun()
        return

    soru_grubu_sayisi = 5
    test_sayisi = math.ceil(len(tum_sorular) / soru_grubu_sayisi)

    sonuclar = st.session_state.get("sonuclar", {})

    for i in range(test_sayisi):
        baslangic = i * soru_grubu_sayisi
        bitis = min((i + 1) * soru_grubu_sayisi, len(tum_sorular))
        soru_sayisi = bitis - baslangic
        test_adi = f"Test {i+1}: ({soru_sayisi} Soru)"

        # Çözülmüş testleri renklendir: doğru oran >=0.6 ise ✅, değilse ❌
        test_sonuc = sonuclar.get(secilen_ders, {}).get(secilen_konu, {}).get(f"test_{i+1}")
        if test_sonuc:
            dogru_sayi = test_sonuc.get('dogru', 0)
            oran = dogru_sayi / soru_sayisi
            simge = "✅" if oran >= 0.6 else "❌"
            label = f"{test_adi} {simge} ({dogru_sayi}/{soru_sayisi})"
        else:
            label = f"{test_adi} ⏺"

        if st.button(label, key=f"testbtn_{i}", help=f"Test {i+1}"):

            # önceki cevapları temizle
            cevap_keys = [k for k in list(st.session_state.keys()) if k.startswith("cevap_")]
            for k in cevap_keys:
                del st.session_state[k]

            st.session_state["current_test"] = {
                "test": tum_sorular[baslangic:bitis],
                "index": 0,
                "ders": secilen_ders,
                "konu": secilen_konu,
                "test_no": i+1,
                "test_sayisi": test_sayisi
            }
            st.session_state["page"] = "soru"
            st.rerun()

    st.markdown("---")  # alt çizgi
    st.markdown("<h1 style='text-align: center; color: orange; font-size:15px;'>KPSS SORU ÇÖZÜM PLATFORMU</h1>", unsafe_allow_html=True)

# ===============================
# Deneme Sınavları
# ===============================
def deneme_secim_page():
    if st.button("🏠 Geri"):
        st.session_state["page"] = "ders"
        st.rerun()

    st.markdown("<h2>📝 Deneme Sınavları</h2>", unsafe_allow_html=True)

    sonuclar = st.session_state.get("sonuclar", {})

    for deneme_adi, alt_basliklar in deneme_sinavlari.items():
        with st.expander(f"📘 {deneme_adi}"):
            for alt_baslik, sorular in alt_basliklar.items():
                soru_sayisi = len(sorular)
                ders_key = "📝 Deneme Sınavı"
                konu_key = f"{deneme_adi} - {alt_baslik}"

                # Farklı olası kaydetme biçimlerine göre test sonucunu bul
                test_sonuc = None
                if ders_key in sonuclar:
                    # 1️⃣ Doğrudan konu adıyla kaydedilmiş olabilir
                    test_sonuc = sonuclar[ders_key].get(konu_key)
                    # 2️⃣ Veya alt başlık düzeyinde (örnek: sonuclar["📝 Deneme Sınavı"]["2023 KPSS Lisans"]["Genel Yetenek Türkçe"])
                    if test_sonuc is None:
                        test_sonuc = sonuclar[ders_key].get(deneme_adi, {}).get(alt_baslik)

                if test_sonuc:
                    dogru_sayi = test_sonuc.get("dogru", 0)
                    oran = dogru_sayi / soru_sayisi
                    simge = "✅" if oran >= 0.6 else "❌"
                    label = f"{alt_baslik} ({soru_sayisi} soru) {simge} ({dogru_sayi}/{soru_sayisi})"
                else:
                    label = f"{alt_baslik} ({soru_sayisi} soru) ⏺"

                if st.button(label, key=f"deneme_{deneme_adi}_{alt_baslik}"):

                    # Önceki cevapları temizle
                    cevap_keys = [k for k in list(st.session_state.keys()) if k.startswith("cevap_")]
                    for k in cevap_keys:
                        del st.session_state[k]

                    # Test bilgilerini kaydet
                    st.session_state["current_test"] = {
                        "test": sorular,
                        "index": 0,
                        "ders": ders_key,
                        "konu": konu_key,
                        "test_no": 1,
                        "test_sayisi": 1
                    }
                    st.session_state["page"] = "soru"
                    st.rerun()

    st.markdown("---")
    st.markdown(
        "<h1 style='text-align:center; color:orange; font-size:15px;'>KPSS SORU ÇÖZÜM PLATFORMU</h1>",
        unsafe_allow_html=True
    )


# ===============================
# Soru Gösterim Sayfası (Radyo başta seçili gelmez)
# ===============================
def soru_goster_page():
    current = st.session_state["current_test"]
    secilen_test = current.get("test", [])
    index = current.get("index", 0)

    if not secilen_test or index < 0 or index > len(secilen_test):
        st.error("❌ Geçersiz test verisi!")
        if st.button("🔙 Geri Dön"):
            # Hatalı test durumunda yönlendirme
            if current.get("ders") == "📝 Deneme Sınavı":
                st.session_state["page"] = "deneme"
            else:
                st.session_state["page"] = "test"
            st.rerun()
        return

    secilen_ders = current["ders"]
    secilen_konu = current["konu"]
    test_no = current["test_no"]
    test_sayisi = current["test_sayisi"]

    # ===== Sol üst geri butonu =====
    if st.button("🔙 Geri"):
        # Eğer deneme sınavıysa, deneme sayfasına dön
        if secilen_ders == "📝 Deneme Sınavı":
            st.session_state["page"] = "deneme"
        else:
            st.session_state["page"] = "test"
        st.rerun()

    # ===== Test tamamlandıysa =====
    if index >= len(secilen_test):
        st.success("Test tamamlandı!")

        if "sonuclar" not in st.session_state:
            st.session_state["sonuclar"] = {}
        sonuclar = st.session_state["sonuclar"]
        if secilen_ders not in sonuclar:
            sonuclar[secilen_ders] = {}
        if secilen_konu not in sonuclar[secilen_ders]:
            sonuclar[secilen_ders][secilen_konu] = {"dogru": 0, "yanlis": 0}

        # Cevapları topla
        cevap_keys = [k for k in st.session_state.keys() if k.startswith("cevap_")]
        dogru = 0
        yanlis = 0
        for k in cevap_keys:
            secilen_harf = st.session_state[k]
            soru_index = int(k.split("_")[1])
            if soru_index < len(secilen_test):
                soru = secilen_test[soru_index]
                if secilen_harf == soru["dogru_cevap"]:
                    dogru += 1
                else:
                    yanlis += 1

        # Önceki test sonuçlarını sıfırla
        onceki_test = sonuclar[secilen_ders][secilen_konu].get(f"test_{test_no}")
        if onceki_test:
            sonuclar[secilen_ders][secilen_konu]["dogru"] -= onceki_test.get("dogru", 0)
            sonuclar[secilen_ders][secilen_konu]["yanlis"] -= onceki_test.get("yanlis", 0)

        # Yeni sonuçları ekle
        sonuclar[secilen_ders][secilen_konu]["dogru"] += dogru
        sonuclar[secilen_ders][secilen_konu]["yanlis"] += yanlis
        sonuclar[secilen_ders][secilen_konu][f"test_{test_no}"] = {"dogru": dogru, "yanlis": yanlis}

        st.session_state["sonuclar"] = sonuclar
        kaydet_sonuclar_to_user(st.session_state.get("current_user"))

        st.markdown(f"✅ Doğru: {dogru}  |  ❌ Yanlış: {yanlis}")

        if st.button("Testi Bitir 🏁"):
            # st.session_state["page"] = "test"
            if secilen_ders == "📝 Deneme Sınavı":
                st.session_state["page"] = "deneme"
            else:
                st.session_state["page"] = "test"            
            st.rerun()
        return

    # ===== Soruyu Göster =====
    soru = secilen_test[index]
    st.markdown(f"<h2 style='font-size:20px;'>{secilen_ders} - {secilen_konu}</h2>", unsafe_allow_html=True)
    st.markdown(f"**Soru {index+1}/{len(secilen_test)}:**")   
    st.markdown(f"{soru['soru']}")

    # Eğer maddeler varsa liste halinde göster
    if "maddeler" in soru:
        for madde in soru["maddeler"]:
            # st.markdown(f"- {madde}")
             st.markdown(f"<div style='margin:2px 0'>{madde}</div>", unsafe_allow_html=True)

    secenekler = [f"{harf}) {metin}" for harf, metin in soru["secenekler"].items()]
    cevap_key = f"cevap_{index}"

    # Radyo butonu
    if cevap_key in st.session_state:
        secim = st.radio(
            label="",
            options=secenekler,
            index=[s.split(")")[0] for s in secenekler].index(st.session_state[cevap_key]),
            key=f"soru_radio_{index}"
        )
    else:
        secim = st.radio(
            label="",
            options=secenekler + [None],
            index=len(secenekler),
            format_func=lambda x: "" if x is None else x,
            key=f"soru_radio_{index}"
        )

    # Cevap kontrol ve kaydetme
    if cevap_key in st.session_state:
        secilen_harf = st.session_state[cevap_key]
        if secilen_harf == soru["dogru_cevap"]:
            st.success("✅ Doğru!")
        else:
            st.error(f"❌ Yanlış! Doğru Cevap: {soru['dogru_cevap']}) {soru['secenekler'][soru['dogru_cevap']]}")
        st.info(f"**Çözüm:** {soru['cozum']}")
    else:
        if st.button("🎯 Cevapla", key=f"cevapla_{index}"):
            if secim is None:
                st.warning("⚠️ Lütfen bir seçenek seçin!")
            else:
                secilen_harf = secim.split(")")[0]
                st.session_state[cevap_key] = secilen_harf
                st.rerun()

    # ===== Alt kısım: Önceki / Sonraki / Testi Bitir =====
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if index > 0 and st.button("⬅️ Önceki Soru"):
            current["index"] -= 1
            st.rerun()
    with col2:
        if index < len(secilen_test) - 1 and st.button("Sonraki Soru ➡️"):
            if cevap_key in st.session_state:
                current["index"] += 1
                st.rerun()
            else:
                st.warning("⚠️ Lütfen önce bu soruyu cevaplayın!")
    with col3:
        if index == len(secilen_test) - 1 and st.button("Testi Bitir 🏁"):
            if cevap_key in st.session_state:
                current["index"] += 1
                st.rerun()
            else:
                st.warning("⚠️ Lütfen önce bu soruyu cevaplayın!")

    st.markdown("---")
    st.markdown("<h1 style='text-align: center; color: orange; font-size:15px;'>KPSS SORU ÇÖZÜM PLATFORMU</h1>", unsafe_allow_html=True)



# ===============================
# Genel Rapor
# ===============================
def genel_rapor_page():
   # ===== Butonun stilini tanımlıyoruz =====
    st.markdown(
        """
        <style>
        /* Sidebar görünür olsun */
        div[data-testid="stSidebar"] {visibility: visible;}
        
        /* Butonu sol üst köşeye sabitle */
        .top-left {
            position: fixed;
            top: 15px;    /* Üstten boşluk */
            left: 10px;   /* Soldan boşluk */
            z-index: 9999; /* Diğer elementlerin üstünde olsun */
        }

        /* Butonun temel stil ayarları */
        .stButton>button {
            background-color: transparent;   /* Arka plan rengi */
            color: ;               /* Yazı rengi */
            border: none;               /* Kenarlık yok */
            border-radius: 12px;        /* Köşelerin yuvarlanması */
            padding: 2px 1px;          /* İç boşluk (üst/alt 8px, sağ/sol 14px) */
            font-size: 14px;            /* Yazı boyutu */
            font-weight: bold;          /* Yazıyı kalın yap */
        }

        /* Hover efekti */
        .stButton>button:hover {
            background-color: ; /* Üzerine gelince arka plan rengi  darkorange  */
            color: white;                 /* Üzerine gelince yazı rengi */
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Konteyner ile sabitle
    top_left = st.container()
    with top_left:
        col1, col2 = st.columns([0.2, 0.8])
        with col1:
            if st.button("🏠 Ana Menüye Dön"):
                st.session_state["page"] = "ders"
                st.rerun()

    st.header("📊 Genel Rapor")
    sonuclar = st.session_state.get("sonuclar", {})

    if not sonuclar:
        st.info("Henüz herhangi bir test çözülmedi.")
    else:
        for ders, konular in sonuclar.items():
            with st.expander(f" {ders}"):    #📕📙📚📘📗#
                for konu, sonuc in konular.items():
                    if not isinstance(sonuc, dict):
                        continue

                    dogru = sonuc.get("dogru", 0)
                    yanlis = sonuc.get("yanlis", 0)
                    toplam = dogru + yanlis
                    oran = f"{dogru / toplam * 100:.0f}%" if toplam > 0 else "0%"

                    st.markdown(f"- **{konu}** → ✅ {dogru} | ❌ {yanlis} | Başarı: {oran}")

#                    testler = {k: v for k, v in sonuc.items() if k.startswith("test_")}
#                    if testler:
#                        with st.expander(f"📑 Test Detayları"):
#                           for test_no, t_sonuc in testler.items():
#                               st.write(f"➡️ {test_no}: ✅ {t_sonuc['dogru']} | ❌ {t_sonuc['yanlis']}")

    st.markdown("---")
    st.markdown("<h1 style='text-align: center; color: orange; font-size:15px;'>KPSS SORU ÇÖZÜM PLATFORMU</h1>", unsafe_allow_html=True)


# ===============================
# Profil Sayfası
# ===============================
def profil_page():
    user = st.session_state.get("current_user")
    if not user or user not in kullanicilar:
        st.warning("❌ Kullanıcı bilgisi bulunamadı!")
        st.session_state["page"] = "login"
        st.rerun()
        return

    # Sol üst geri butonu
    if st.button("🔙 Geri"):
        st.session_state["page"] = "ders"
        st.rerun()

    st.markdown("<h2>👤 Kullanıcı Bilgileri</h2>", unsafe_allow_html=True)

    bilgiler = kullanicilar[user]
    isim = bilgiler.get("isim", "")
    k_adi = user
    sifre = bilgiler.get("sifre", "")

    st.write(f"**İsim Soyisim:** {isim}")
    st.write(f"**Kullanıcı Adı:** {k_adi}")
    st.write(f"**Şifre:** {'*' * len(sifre)}")

    # Şifre değiştirme formu
    with st.expander("🔑 Şifre Değiştir"):
        eski = st.text_input("Eski Şifre", type="password", key="old_pass")
        yeni = st.text_input("Yeni Şifre", type="password", key="new_pass")
        yeni2 = st.text_input("Yeni Şifre (Tekrar)", type="password", key="new_pass2")
        if st.button("Şifreyi Güncelle"):
            if eski != sifre:
                st.error("❌ Eski şifre yanlış!")
            elif not yeni or not yeni2:
                st.error("❌ Yeni şifre alanları boş olamaz!")
            elif yeni != yeni2:
                st.error("❌ Yeni şifreler uyuşmuyor!")
            else:
                kullanicilar[user]["sifre"] = yeni
                kullanicilari_kaydet()
                st.success("✅ Şifre başarıyla güncellendi!")

    st.markdown("---")
    st.markdown("<h1 style='text-align:center; color:orange; font-size:15px;'>KPSS SORU ÇÖZÜM PLATFORMU</h1>", unsafe_allow_html=True)


# ===============================
# ADMIN PANEL
# ===============================

def admin_page():
    st.title("👨‍🏫 Admin Paneli")

    # 🔙 Geri
    if st.button("🏠 Ana Menüye Dön"):
        st.session_state["page"] = "ders"
        st.rerun()

    tab1, tab2, tab3, tab4 = st.tabs([
        "👥 Kullanıcı Yönetimi",
        "➕ Soru Ekle",
        "✏️ Soru Düzenle",
        "🗑️ Soru Sil"
    ])

    # ==================================================
    # 👥 KULLANICI YÖNETİMİ
    # ==================================================
    with tab1:
        st.subheader("👥 Kullanıcı Sil")

        if not kullanicilar:
            st.info("Kayıtlı kullanıcı yok.")
        else:
            silinecek = st.selectbox(
                "Silinecek kullanıcı",
                list(kullanicilar.keys())
            )

            if st.button("❌ Kullanıcıyı Sil"):
                st.session_state["kullanici_onay"] = silinecek

            if "kullanici_onay" in st.session_state:
                st.warning(f"⚠️ **{st.session_state['kullanici_onay']}** silinsin mi?")
                col1, col2 = st.columns(2)

                with col1:
                    if st.button("✅ Onayla"):
                        del kullanicilar[st.session_state["kullanici_onay"]]
                        kullanicilari_kaydet()
                        st.error("👤 Kullanıcı silindi")
                     #   del st.session_state["kullanici_onay"]
                     #  st.rerun()

                with col2:
                    if st.button("❌ İptal"):
                        del st.session_state["kullanici_onay"]
                        st.info("İşlem iptal edildi")

    # ==================================================
    # ➕ SORU EKLE
    # ==================================================
    with tab2:
        st.subheader("➕ Yeni Soru Ekle")

        ders = st.selectbox("Ders", list(soru_bankasi.keys()))
        konu_listesi = list(soru_bankasi[ders].keys())

        konu_secim = st.selectbox("Konu", konu_listesi + ["➕ Yeni Konu"])

        if konu_secim == "➕ Yeni Konu":
            konu = st.text_input("Yeni Konu Adı")
        else:
            konu = konu_secim

        st.markdown("---")

        soru = st.text_area("Soru Metni")
        a = st.text_input("A")
        b = st.text_input("B")
        c = st.text_input("C")
        d = st.text_input("D")
        e = st.text_input("E")

        dogru = st.selectbox("Doğru Cevap", ["A", "B", "C", "D", "E"])
        cozum = st.text_area("Çözüm")

        if st.button("➕ Soruyu Kaydet"):
            if not all([ders, konu, soru, a, b, c, d, e, cozum]):
                st.warning("❌ Tüm alanları doldurun")
                return

            soru_bankasi.setdefault(ders, {})
            soru_bankasi[ders].setdefault(konu, [])

            soru_bankasi[ders][konu].append({
                "soru": soru,
                "secenekler": {
                    "A": a, "B": b, "C": c, "D": d, "E": e
                },
                "dogru_cevap": dogru,
                "cozum": cozum
            })

            soru_bankasini_kaydet(soru_bankasi)
            st.success("✅ Soru başarıyla eklendi")

    # ==================================================
    # ✏️ SORU DÜZENLE
    # ==================================================
    with tab3:
        st.subheader("✏️ Soru Düzenle")

        ders = st.selectbox("Ders", list(soru_bankasi.keys()), key="edit_ders")
        konu = st.selectbox(
            "Konu",
            list(soru_bankasi[ders].keys()),
            key="edit_konu"
        )

        sorular = soru_bankasi[ders][konu]

        if not sorular:
            st.info("Bu konuda soru yok")
        else:
            idx = st.selectbox(
                "Düzenlenecek Soru",
                range(len(sorular)),
                format_func=lambda i: f"{i+1}. {sorular[i]['soru'][:60]}..."
            )

            s = sorular[idx]

            soru = st.text_area("Soru", s["soru"])
            a = st.text_input("A", s["secenekler"]["A"])
            b = st.text_input("B", s["secenekler"]["B"])
            c = st.text_input("C", s["secenekler"]["C"])
            d = st.text_input("D", s["secenekler"]["D"])
            e = st.text_input("E", s["secenekler"]["E"])
            dogru = st.selectbox(
                "Doğru",
                ["A", "B", "C", "D", "E"],
                index=["A","B","C","D","E"].index(s["dogru_cevap"])
            )
            cozum = st.text_area("Çözüm", s["cozum"])

            if st.button("💾 Güncelle"):
                sorular[idx] = {
                    "soru": soru,
                    "secenekler": {
                        "A": a, "B": b, "C": c, "D": d, "E": e
                    },
                    "dogru_cevap": dogru,
                    "cozum": cozum
                }

                soru_bankasini_kaydet(soru_bankasi)
                st.success("✅ Soru güncellendi")

     # ==================================================
    # 🗑️ SORU SİL
    # ==================================================
    with tab4:
        st.subheader("🗑️ Soru Sil")

        ders = st.selectbox("Ders", list(soru_bankasi.keys()), key="sil_ders")
        konu = st.selectbox(
            "Konu",
            list(soru_bankasi[ders].keys()),
            key="sil_konu"
        )

        sorular = soru_bankasi[ders][konu]

        if not sorular:
            st.info("Soru yok")
        else:
            idx = st.selectbox(
                "Silinecek Soru",
                range(len(sorular)),
                format_func=lambda i: f"{i+1}. {sorular[i]['soru'][:60]}..."
            )

            if st.button("❌ Soruyu Sil"):
                sorular.pop(idx)
                soru_bankasini_kaydet(soru_bankasi)
                st.success("🗑️ Soru silindi")




# ===============================
# SESSION İLK KURULUM
# ===============================
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.page = "login"
    st.session_state.current_user = None

# ===============================
# COOKIE'DEN OTOMATİK GİRİŞ (TEK VE KONTROLLÜ)
# ===============================
if not st.session_state.get("current_user") and not st.session_state.get("logout"):
    cookie_user = cookies.get("current_user")
    if cookie_user and cookie_user in kullanicilar:
        st.session_state.current_user = cookie_user
        kullanici_sonuclarini_yukle_to_session(cookie_user)
        st.session_state.page = "ders"
# ===============================
# ROUTER
# ===============================
page = st.session_state.page

korumali_sayfalar = [
    "ders", "konu", "test", "soru", "rapor", "profil", "deneme", "admin"
]

if page in korumali_sayfalar and not st.session_state.get("current_user"):
    st.session_state.page = "login"
    st.rerun()

# ===============================
# SAYFA YÖNLENDİRME
# ===============================
if page == "login":
    login_page()
elif page == "kayit":
    kayit_page()
elif page == "ders":
    ders_secim_page()
elif page == "konu":
    if "ders" in st.session_state:
        konu_secim_page(st.session_state["ders"])
    else:
        st.session_state.page = "ders"
        st.rerun()
elif page == "test":
    if "ders" in st.session_state and "konu" in st.session_state:
        test_secim_page(st.session_state["ders"], st.session_state["konu"])
    else:
        st.session_state.page = "ders"
        st.rerun()
elif page == "deneme":
    deneme_secim_page()
elif page == "soru":
    soru_goster_page()
elif page == "rapor":
    genel_rapor_page()
elif page == "profil":
    profil_page()
elif page == "admin":
    admin_page()
















































