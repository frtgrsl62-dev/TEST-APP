"""
KPSS SORU ÇÖZÜM PLATFORMU
Geliştirilmiş Versiyon - 2026
Özellikler:
- Tema sistemi
- Resim desteği
- Güvenli kimlik doğrulama
- İstatistikler ve grafikler
- Modern UI/UX
"""

import streamlit as st
import time
import json
import os
import math
import uuid
from datetime import datetime
from streamlit_cookies_manager import EncryptedCookieManager
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Modüller
from soru_bankasi import soru_bankasini_yukle, soru_bankasini_kaydet
from ders_konu_notlari import ders_konu_notlari
from deneme_sinavlari import deneme_sinavlari
from theme_manager import theme_manager
from image_handler import image_handler
from config import Config

# ===============================
# SAYFA YAPILANDIRMASI
# ===============================
st.set_page_config(
    page_title="KPSS Soru Platformu",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===============================
# GLOBAL DEĞİŞKENLER
# ===============================
soru_bankasi = soru_bankasini_yukle()
ADMIN_USERS = ["a", "admin"]

# Cookie Manager
cookies = EncryptedCookieManager(
    prefix=Config.COOKIE_PREFIX,
    password=Config.COOKIE_PASSWORD
)

if not cookies.ready():
    st.stop()

# Dosya yolları
KULLANICILAR_DOSYA = Config.KULLANICILAR_DOSYA

# Sabit kullanıcılar (geliştirme için)
sabit_kullanicilar = {
    "a": {"isim": "Yönetici", "sifre": "1", "is_admin": True},
    "m": {"isim": "Misafir Kullanıcı", "sifre": "0", "is_admin": False},
}

# ===============================
# YARDIMCI FONKSİYONLAR
# ===============================

def kullanicilari_yukle():
    """Kullanıcıları JSON'dan yükle"""
    if not os.path.exists(KULLANICILAR_DOSYA):
        with open(KULLANICILAR_DOSYA, "w", encoding="utf-8") as f:
            f.write("{}")
    
    with open(KULLANICILAR_DOSYA, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def kullanicilari_kaydet(kullanicilar):
    """Kullanıcıları JSON'a kaydet"""
    with open(KULLANICILAR_DOSYA, "w", encoding="utf-8") as f:
        json.dump(kullanicilar, f, ensure_ascii=False, indent=2)

def kaydet_sonuclar_to_user(user, kullanicilar):
    """Kullanıcı sonuçlarını kaydet"""
    if not user or user not in kullanicilar:
        return
    kullanicilar[user]["sonuclar"] = st.session_state.get("sonuclar", {})
    kullanicilari_kaydet(kullanicilar)

def kullanici_sonuclarini_yukle_to_session(user, kullanicilar):
    """Kullanıcı sonuçlarını session'a yükle"""
    if user in kullanicilar:
        st.session_state["sonuclar"] = kullanicilar[user].get("sonuclar", {})
    else:
        st.session_state["sonuclar"] = {}

def get_progress_circle_html(percentage, size=60):
    """Dairesel ilerleme göstergesi HTML"""
    theme = theme_manager.get_theme(st.session_state.get("theme", "light"))
    
    return f"""
    <div style="
        width:{size}px; 
        height:{size}px; 
        border-radius:50%;
        background: conic-gradient(
            {theme['success']} {percentage}%, 
            {theme['border']} {percentage}%
        );
        display:flex; 
        align-items:center; 
        justify-content:center;
        font-weight:bold; 
        color:{theme['text']};
        font-size:14px;
        box-shadow: 0 2px 4px {theme['shadow']};
        position: relative;
    ">
        <div style="
            width:{size-8}px;
            height:{size-8}px;
            border-radius:50%;
            background:{theme['background']};
            display:flex;
            align-items:center;
            justify-content:center;
        ">
            {percentage}%
        </div>
    </div>
    """

def render_stat_card(title, value, icon, color="#FF6B35"):
    """İstatistik kartı"""
    return f"""
    <div class="card" style="text-align:center; border-left: 4px solid {color};">
        <div style="font-size:36px; margin-bottom:10px;">{icon}</div>
        <div style="font-size:28px; font-weight:bold; color:{color};">{value}</div>
        <div style="font-size:14px; color:#7F8C8D; margin-top:5px;">{title}</div>
    </div>
    """

# ===============================
# Global kullanıcılar
# ===============================
kullanicilar = kullanicilari_yukle()

# ===============================
# GİRİŞ SAYFASI
# ===============================
def login_page():
    """Modern giriş sayfası"""
    theme = theme_manager.get_theme(st.session_state.get("theme", "light"))
    
    # Merkezi container
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(f"""
        <div style="text-align:center; padding:40px 0;">
            <h1 style="
                font-size:48px; 
                color:{theme['primary']};
                margin-bottom:10px;
                text-shadow: 2px 2px 4px {theme['shadow']};
            ">
                📚 KPSS PLATFORMU
            </h1>
            <p style="
                font-size:18px; 
                color:{theme['text']};
                opacity:0.8;
            ">
                Başarıya giden yolda yanınızdayız
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div class='card fade-in'>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔐 Giriş Yap", "📝 Kayıt Ol"])
        
        with tab1:
            with st.form("login_form"):
                st.markdown("### Hoş Geldiniz!")
                k_adi = st.text_input("👤 Kullanıcı Adı", key="login_user")
                sifre = st.text_input("🔒 Şifre", type="password", key="login_pass")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    giris_btn = st.form_submit_button("🟢 Giriş Yap", use_container_width=True)
                with col_btn2:
                    misafir_btn = st.form_submit_button("👤 Misafir Girişi", use_container_width=True)
            
            if giris_btn:
                if (k_adi in sabit_kullanicilar and sabit_kullanicilar[k_adi]["sifre"] == sifre) or \
                   (k_adi in kullanicilar and kullanicilar[k_adi]["sifre"] == sifre):
                    
                    st.session_state["current_user"] = k_adi
                    cookies["current_user"] = k_adi
                    cookies.save()
                    
                    kullanici_sonuclarini_yukle_to_session(k_adi, kullanicilar)
                    st.session_state["page"] = "ders"
                    st.success("✅ Giriş başarılı! Yönlendiriliyorsunuz...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Hatalı kullanıcı adı veya şifre!")
            
            if misafir_btn:
                st.session_state["current_user"] = "m"
                cookies["current_user"] = "m"
                cookies.save()
                kullanici_sonuclarini_yukle_to_session("m", kullanicilar)
                st.session_state["page"] = "ders"
                st.rerun()
        
        with tab2:
            with st.form("kayit_form"):
                st.markdown("### Yeni Hesap Oluştur")
                isim = st.text_input("👤 İsim Soyisim", key="register_name")
                k_adi = st.text_input("📧 Kullanıcı Adı", key="register_user")
                sifre = st.text_input("🔒 Şifre", type="password", key="register_pass")
                sifre_tekrar = st.text_input("🔒 Şifre Tekrar", type="password", key="register_pass2")
                
                kaydet_btn = st.form_submit_button("✅ Kayıt Ol", use_container_width=True)
            
            if kaydet_btn:
                if not isim or not k_adi or not sifre or not sifre_tekrar:
                    st.error("❌ Lütfen tüm alanları doldurun!")
                elif sifre != sifre_tekrar:
                    st.error("❌ Şifreler uyuşmuyor!")
                elif k_adi in sabit_kullanicilar or k_adi in kullanicilar:
                    st.error("❌ Bu kullanıcı adı zaten kayıtlı!")
                else:
                    kullanicilar[k_adi] = {
                        "isim": isim, 
                        "sifre": sifre, 
                        "sonuclar": {},
                        "created_at": datetime.now().isoformat(),
                        "is_admin": False
                    }
                    kullanicilari_kaydet(kullanicilar)
                    st.success(f"✅ {isim} başarıyla kaydedildi! Giriş yapabilirsiniz.")
                    time.sleep(2)
                    st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

# ===============================
# DERS SEÇİM SAYFASI
# ===============================
def ders_secim_page():
    """Geliştirilmiş ders seçim sayfası"""
    theme = theme_manager.get_theme(st.session_state.get("theme", "light"))
    user = st.session_state.get("current_user")
    
    # Üst bar
    col1, col2, col3 = st.columns([2, 6, 2])
    
    with col1:
        if user in ADMIN_USERS:
            if st.button("👨‍🏫 Admin", use_container_width=True):
                st.session_state.page = "admin"
                st.rerun()
    
    with col3:
        if user:
            kullanici_isim = kullanicilar.get(user, {}).get("isim", user) if user not in sabit_kullanicilar else sabit_kullanicilar[user]["isim"]
            if st.button(f"👤 {kullanici_isim[:10]}", use_container_width=True):
                st.session_state["page"] = "profil"
                st.rerun()
    
    # Başlık
    st.markdown(f"""
    <div style="text-align:center; padding:20px 0;">
        <h1 style="
            font-size:42px; 
            color:{theme['primary']};
            margin-bottom:10px;
        ">
            📚 Ders Seçimi
        </h1>
        <p style="font-size:16px; color:{theme['text']}; opacity:0.7;">
            Çalışmak istediğiniz dersi seçin
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # İstatistik kartları
    sonuclar = st.session_state.get("sonuclar", {})
    toplam_dogru = sum(
        konu_data.get("dogru", 0)
        for ders_data in sonuclar.values()
        for konu_data in ders_data.values()
        if isinstance(konu_data, dict)
    )
    toplam_yanlis = sum(
        konu_data.get("yanlis", 0)
        for ders_data in sonuclar.values()
        for konu_data in ders_data.values()
        if isinstance(konu_data, dict)
    )
    toplam_soru = toplam_dogru + toplam_yanlis
    basari_orani = int((toplam_dogru / toplam_soru * 100)) if toplam_soru > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(render_stat_card("Toplam Soru", toplam_soru, "📝", theme['info']), unsafe_allow_html=True)
    with col2:
        st.markdown(render_stat_card("Doğru", toplam_dogru, "✅", theme['success']), unsafe_allow_html=True)
    with col3:
        st.markdown(render_stat_card("Yanlış", toplam_yanlis, "❌", theme['error']), unsafe_allow_html=True)
    with col4:
        st.markdown(render_stat_card("Başarı", f"%{basari_orani}", "🎯", theme['primary']), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Dersler - Grid layout
    ders_icons = {
        "📖 Türkçe": "📖",
        "➗ Matematik": "➗",
        "📜 Tarih": "📜",
        "🌍 Coğrafya": "🌍",
        "⚖️ Hukuk": "⚖️",
        "💼 İktisat": "💼",
        "🧪 Fen": "🧪"
    }
    
    cols = st.columns(3)
    for idx, ders in enumerate(soru_bankasi.keys()):
        with cols[idx % 3]:
            icon = ders_icons.get(ders, "📚")
            
            # Ders ilerleme hesapla
            ders_sonuc = sonuclar.get(ders, {})
            ders_dogru = sum(k.get("dogru", 0) for k in ders_sonuc.values() if isinstance(k, dict))
            ders_yanlis = sum(k.get("yanlis", 0) for k in ders_sonuc.values() if isinstance(k, dict))
            ders_toplam = ders_dogru + ders_yanlis
            ders_oran = int((ders_dogru / ders_toplam * 100)) if ders_toplam > 0 else 0
            
            st.markdown(f"""
            <div class="card fade-in" style="text-align:center; min-height:180px;">
                <div style="font-size:48px; margin-bottom:10px;">{icon}</div>
                <h3 style="color:{theme['text']}; margin-bottom:10px;">{ders.replace(icon, '').strip()}</h3>
                <div style="margin:15px 0;">
                    {get_progress_circle_html(ders_oran, 50)}
                </div>
                <p style="font-size:12px; color:{theme['text']}; opacity:0.7;">
                    {ders_toplam} soru çözüldü
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"Başla →", key=f"ders_{ders}", use_container_width=True):
                st.session_state["ders"] = ders
                st.session_state["page"] = "konu"
                st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Alt butonlar
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📝 Deneme Sınavları", use_container_width=True):
            st.session_state["page"] = "deneme"
            st.rerun()
    with col2:
        if st.button("📊 Genel Rapor", use_container_width=True):
            st.session_state["page"] = "rapor"
            st.rerun()
    with col3:
        if st.button("🚪 Çıkış Yap", use_container_width=True):
            kaydet_sonuclar_to_user(st.session_state.get("current_user"), kullanicilar)
            cookies.pop("current_user", None)
            cookies.save()
            st.session_state.current_user = None
            st.session_state.page = "login"
            st.session_state["logout"] = True
            st.rerun()

# ===============================
# KONU SEÇİM SAYFASI
# ===============================
def konu_secim_page(ders):
    """Geliştirilmiş konu seçim sayfası"""
    theme = theme_manager.get_theme(st.session_state.get("theme", "light"))
    
    # Geri butonu
    if st.button("🏠 Ana Menü", key="geri_ders"):
        st.session_state["page"] = "ders"
        st.rerun()
    
    st.markdown(f"""
    <div style="text-align:center; padding:20px 0;">
        <h2 style="font-size:36px; color:{theme['primary']};">
            {ders} - Konu Seçimi
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Ders notu linki
    ders_notu_link = ders_konu_notlari.get(ders, {}).get("__ders_notu__", "")
    if ders_notu_link:
        st.markdown(
            f"<div style='text-align:center; margin:20px 0;'><a href='{ders_notu_link}' target='_blank'>"
            f"<button style='background-color:{theme['primary']}; color:white; padding:10px 20px; "
            f"border:none; border-radius:8px; cursor:pointer; font-size:16px;'>"
            f"📚 Ders Notlarını Aç</button></a></div>",
            unsafe_allow_html=True
        )
    
    konular = list(soru_bankasi[ders].keys())
    sonuclar = st.session_state.get("sonuclar", {})
    
    # Konuları grid'de göster
    cols = st.columns(2)
    
    for idx, konu in enumerate(konular):
        with cols[idx % 2]:
            tum_sorular = soru_bankasi[ders][konu]
            soru_grubu_sayisi = 5
            toplam_test_sayisi = math.ceil(len(tum_sorular) / soru_grubu_sayisi)
            
            # Çözülen test sayısı
            testler = sonuclar.get(ders, {}).get(konu, {})
            cozulmus_test_sayisi = sum(
                1 for key in testler if key.startswith("test_")
            )
            
            yuzde = int(cozulmus_test_sayisi / toplam_test_sayisi * 100) if toplam_test_sayisi > 0 else 0
            
            # Konu kartı
            st.markdown(f"""
            <div class="card fade-in">
                <div style="display:flex; align-items:center; gap:15px;">
                    <div>
                        {get_progress_circle_html(yuzde, 50)}
                    </div>
                    <div style="flex:1;">
                        <h4 style="margin:0; color:{theme['text']};">{konu}</h4>
                        <p style="margin:5px 0 0 0; font-size:12px; color:{theme['text']}; opacity:0.7;">
                            {cozulmus_test_sayisi}/{toplam_test_sayisi} test tamamlandı
                        </p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"▶️ Başla", key=f"konu_{konu}", use_container_width=True):
                st.session_state["konu"] = konu
                st.session_state["page"] = "test"
                st.rerun()

# ===============================
# TEST SEÇİM SAYFASI
# ===============================
def test_secim_page(secilen_ders, secilen_konu):
    """Geliştirilmiş test seçim sayfası"""
    theme = theme_manager.get_theme(st.session_state.get("theme", "light"))
    
    if st.button("🔙 Geri", key="geri_konu"):
        st.session_state["page"] = "konu"
        st.rerun()
    
    st.markdown(f"""
    <div style="text-align:center; padding:15px 0;">
        <h3 style="font-size:28px; color:{theme['primary']};">
            {secilen_ders} - {secilen_konu}
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Konu notu
    konu_link = ders_konu_notlari.get(secilen_ders, {}).get(secilen_konu, "")
    if konu_link:
        st.markdown(
            f"<div style='text-align:center; margin:15px 0;'><a href='{konu_link}' target='_blank'>"
            f"<button style='background-color:{theme['secondary']}; color:white; padding:8px 16px; "
            f"border:none; border-radius:8px; cursor:pointer;'>"
            f"📕 Konu Notu</button></a></div>",
            unsafe_allow_html=True
        )
    
    tum_sorular = soru_bankasi[secilen_ders][secilen_konu]
    if not tum_sorular:
        st.info("Bu konu için henüz soru eklenmemiş.")
        return
    
    soru_grubu_sayisi = 5
    test_sayisi = math.ceil(len(tum_sorular) / soru_grubu_sayisi)
    sonuclar = st.session_state.get("sonuclar", {})
    
    # Testler
    cols = st.columns(3)
    for i in range(test_sayisi):
        with cols[i % 3]:
            baslangic = i * soru_grubu_sayisi
            bitis = min((i + 1) * soru_grubu_sayisi, len(tum_sorular))
            soru_sayisi = bitis - baslangic
            
            test_sonuc = sonuclar.get(secilen_ders, {}).get(secilen_konu, {}).get(f"test_{i+1}")
            
            if test_sonuc:
                dogru_sayi = test_sonuc.get('dogru', 0)
                oran = dogru_sayi / soru_sayisi
                simge = "✅" if oran >= 0.6 else "❌"
                renk = theme['success'] if oran >= 0.6 else theme['error']
                durum = f"{simge} {dogru_sayi}/{soru_sayisi}"
            else:
                simge = "⏺"
                renk = theme['border']
                durum = "Çözülmedi"
            
            st.markdown(f"""
            <div class="card" style="border-left: 4px solid {renk}; text-align:center;">
                <div style="font-size:32px; margin-bottom:10px;">{simge}</div>
                <h4 style="margin:5px 0; color:{theme['text']};">Test {i+1}</h4>
                <p style="font-size:14px; color:{theme['text']}; opacity:0.7; margin:5px 0;">
                    {soru_sayisi} Soru
                </p>
                <p style="font-size:16px; font-weight:bold; color:{renk}; margin:10px 0;">
                    {durum}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"▶️ Başla", key=f"test_{i}", use_container_width=True):
                # Önceki cevapları temizle
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

# ===============================
# SORU GÖSTER SAYFASI
# ===============================
def soru_goster_page():
    """Geliştirilmiş soru gösterimi"""
    theme = theme_manager.get_theme(st.session_state.get("theme", "light"))
    current = st.session_state["current_test"]
    secilen_test = current.get("test", [])
    index = current.get("index", 0)
    
    if not secilen_test or index < 0 or index > len(secilen_test):
        st.error("❌ Geçersiz test verisi!")
        return
    
    secilen_ders = current["ders"]
    secilen_konu = current["konu"]
    test_no = current["test_no"]
    
    # Geri butonu
    if st.button("🔙 Geri", key="geri_soru"):
        if secilen_ders == "📝 Deneme Sınavı":
            st.session_state["page"] = "deneme"
        else:
            st.session_state["page"] = "test"
        st.rerun()
    
    # Test tamamlandı mı?
    if index >= len(secilen_test):
        st.success("🎉 Test Tamamlandı!")
        
        # Sonuçları hesapla
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
        
        # Önceki sonuçları sıfırla
        onceki_test = sonuclar[secilen_ders][secilen_konu].get(f"test_{test_no}")
        if onceki_test:
            sonuclar[secilen_ders][secilen_konu]["dogru"] -= onceki_test.get("dogru", 0)
            sonuclar[secilen_ders][secilen_konu]["yanlis"] -= onceki_test.get("yanlis", 0)
        
        # Yeni sonuçları ekle
        sonuclar[secilen_ders][secilen_konu]["dogru"] += dogru
        sonuclar[secilen_ders][secilen_konu]["yanlis"] += yanlis
        sonuclar[secilen_ders][secilen_konu][f"test_{test_no}"] = {"dogru": dogru, "yanlis": yanlis}
        
        st.session_state["sonuclar"] = sonuclar
        kaydet_sonuclar_to_user(st.session_state.get("current_user"), kullanicilar)
        
        # Sonuç kartları
        toplam = dogru + yanlis
        basari = int((dogru / toplam * 100)) if toplam > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(render_stat_card("Doğru", dogru, "✅", theme['success']), unsafe_allow_html=True)
        with col2:
            st.markdown(render_stat_card("Yanlış", yanlis, "❌", theme['error']), unsafe_allow_html=True)
        with col3:
            st.markdown(render_stat_card("Başarı", f"%{basari}", "🎯", theme['primary']), unsafe_allow_html=True)
        
        if st.button("🏁 Bitir", use_container_width=True):
            if secilen_ders == "📝 Deneme Sınavı":
                st.session_state["page"] = "deneme"
            else:
                st.session_state["page"] = "test"
            st.rerun()
        return
    
    # Soruyu göster
    soru = secilen_test[index]
    
    # İlerleme çubuğu
    ilerleme = (index + 1) / len(secilen_test)
    st.progress(ilerleme)
    st.markdown(f"**Soru {index+1}/{len(secilen_test)}**")
    
    # Ders ve konu
    st.markdown(f"""
    <div class="card">
        <h4 style="color:{theme['primary']}; margin-bottom:10px;">
            {secilen_ders} - {secilen_konu}
        </h4>
        <div style="font-size:16px; line-height:1.6;">
            {soru['soru']}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Soru resmi varsa göster
    if "soru_resmi" in soru and soru["soru_resmi"]:
        image_handler.display_image(soru["soru_resmi"], width=400)
    
    # Maddeler varsa
    if "maddeler" in soru:
        for madde in soru["maddeler"]:
            st.markdown(f"<div style='margin:2px 0; padding-left:20px;'>• {madde}</div>", unsafe_allow_html=True)
    
    # Şıklar
    secenekler = [f"{harf}) {metin}" for harf, metin in soru["secenekler"].items()]
    cevap_key = f"cevap_{index}"
    
    if cevap_key in st.session_state:
        # Cevaplandı - göster
        secim = st.radio(
            label="Şıklar:",
            options=secenekler,
            index=[s.split(")")[0] for s in secenekler].index(st.session_state[cevap_key]),
            key=f"soru_radio_{index}",
            disabled=True
        )
        
        secilen_harf = st.session_state[cevap_key]
        if secilen_harf == soru["dogru_cevap"]:
            st.success("✅ Doğru Cevap!")
        else:
            st.error(f"❌ Yanlış! Doğru Cevap: {soru['dogru_cevap']}) {soru['secenekler'][soru['dogru_cevap']]}")
        
        st.info(f"**💡 Çözüm:** {soru['cozum']}")
        
        # Çözüm resmi varsa
        if "cozum_resmi" in soru and soru["cozum_resmi"]:
            image_handler.display_image(soru["cozum_resmi"], width=400)
    
    else:
        # Henüz cevapla madı
        secim = st.radio(
            label="Şıklar:",
            options=secenekler,
            key=f"soru_radio_{index}"
        )
        
        if st.button("🎯 Cevapla", key=f"cevapla_{index}", use_container_width=True):
            secilen_harf = secim.split(")")[0]
            st.session_state[cevap_key] = secilen_harf
            st.rerun()
    
    # Navigasyon butonları
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if index > 0:
            if st.button("⬅️ Önceki", use_container_width=True):
                current["index"] -= 1
                st.rerun()
    
    with col2:
        st.markdown(f"<div style='text-align:center; padding:10px;'>{index+1} / {len(secilen_test)}</div>", unsafe_allow_html=True)
    
    with col3:
        if index < len(secilen_test) - 1:
            if st.button("Sonraki ➡️", use_container_width=True):
                if cevap_key in st.session_state:
                    current["index"] += 1
                    st.rerun()
                else:
                    st.warning("⚠️ Lütfen önce cevap verin!")
        else:
            if st.button("Bitir 🏁", use_container_width=True):
                if cevap_key in st.session_state:
                    current["index"] += 1
                    st.rerun()
                else:
                    st.warning("⚠️ Lütfen önce cevap verin!")

# ===============================
# DENEME SINAVLARI
# ===============================
def deneme_secim_page():
    """Deneme sınavları sayfası"""
    theme = theme_manager.get_theme(st.session_state.get("theme", "light"))
    
    if st.button("🏠 Ana Menü", key="geri_deneme"):
        st.session_state["page"] = "ders"
        st.rerun()
    
    st.markdown(f"""
    <div style="text-align:center; padding:20px 0;">
        <h2 style="font-size:36px; color:{theme['primary']};">
            📝 Deneme Sınavları
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    sonuclar = st.session_state.get("sonuclar", {})
    
    for deneme_adi, alt_basliklar in deneme_sinavlari.items():
        with st.expander(f"📘 {deneme_adi}", expanded=False):
            cols = st.columns(2)
            col_idx = 0
            
            for alt_baslik, sorular in alt_basliklar.items():
                with cols[col_idx % 2]:
                    soru_sayisi = len(sorular)
                    ders_key = "📝 Deneme Sınavı"
                    konu_key = f"{deneme_adi} - {alt_baslik}"
                    
                    test_sonuc = None
                    if ders_key in sonuclar:
                        test_sonuc = sonuclar[ders_key].get(konu_key)
                        if test_sonuc is None:
                            test_sonuc = sonuclar[ders_key].get(deneme_adi, {}).get(alt_baslik)
                    
                    if test_sonuc:
                        dogru_sayi = test_sonuc.get("dogru", 0)
                        oran = dogru_sayi / soru_sayisi
                        simge = "✅" if oran >= 0.6 else "❌"
                        renk = theme['success'] if oran >= 0.6 else theme['error']
                        durum = f"{simge} {dogru_sayi}/{soru_sayisi}"
                    else:
                        simge = "⏺"
                        renk = theme['border']
                        durum = "Çözülmedi"
                    
                    st.markdown(f"""
                    <div class="card" style="border-left: 4px solid {renk};">
                        <h4 style="margin:5px 0; color:{theme['text']};">{alt_baslik}</h4>
                        <p style="font-size:14px; color:{theme['text']}; opacity:0.7; margin:5px 0;">
                            {soru_sayisi} Soru
                        </p>
                        <p style="font-size:16px; font-weight:bold; color:{renk}; margin:5px 0;">
                            {durum}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"▶️ Başla", key=f"deneme_{deneme_adi}_{alt_baslik}", use_container_width=True):
                        # Önceki cevapları temizle
                        cevap_keys = [k for k in list(st.session_state.keys()) if k.startswith("cevap_")]
                        for k in cevap_keys:
                            del st.session_state[k]
                        
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
                
                col_idx += 1

# ===============================
# RAPOR SAYFASI
# ===============================
def genel_rapor_page():
    """Geliştirilmiş rapor sayfası"""
    theme = theme_manager.get_theme(st.session_state.get("theme", "light"))
    
    if st.button("🏠 Ana Menü", key="geri_rapor"):
        st.session_state["page"] = "ders"
        st.rerun()
    
    st.markdown(f"""
    <div style="text-align:center; padding:20px 0;">
        <h2 style="font-size:36px; color:{theme['primary']};">
            📊 Genel Performans Raporu
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    sonuclar = st.session_state.get("sonuclar", {})
    
    if not sonuclar:
        st.info("Henüz herhangi bir test çözülmedi.")
        return
    
    # Genel istatistikler
    toplam_dogru = sum(
        konu_data.get("dogru", 0)
        for ders_data in sonuclar.values()
        for konu_data in ders_data.values()
        if isinstance(konu_data, dict)
    )
    toplam_yanlis = sum(
        konu_data.get("yanlis", 0)
        for ders_data in sonuclar.values()
        for konu_data in ders_data.values()
        if isinstance(konu_data, dict)
    )
    toplam_soru = toplam_dogru + toplam_yanlis
    basari_orani = int((toplam_dogru / toplam_soru * 100)) if toplam_soru > 0 else 0
    
    # Üst kartlar
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(render_stat_card("Toplam Soru", toplam_soru, "📝", theme['info']), unsafe_allow_html=True)
    with col2:
        st.markdown(render_stat_card("Doğru", toplam_dogru, "✅", theme['success']), unsafe_allow_html=True)
    with col3:
        st.markdown(render_stat_card("Yanlış", toplam_yanlis, "❌", theme['error']), unsafe_allow_html=True)
    with col4:
        st.markdown(render_stat_card("Başarı", f"%{basari_orani}", "🎯", theme['primary']), unsafe_allow_html=True)
    
    # Pasta grafik
    st.markdown("### 📈 Doğru/Yanlış Dağılımı")
    fig = go.Figure(data=[go.Pie(
        labels=['Doğru', 'Yanlış'],
        values=[toplam_dogru, toplam_yanlis],
        marker=dict(colors=[theme['success'], theme['error']]),
        hole=0.4
    )])
    fig.update_layout(
        showlegend=True,
        height=300,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Ders bazında detay
    st.markdown("### 📚 Ders Bazında Performans")
    
    ders_data = []
    for ders, konular in sonuclar.items():
        ders_dogru = sum(k.get("dogru", 0) for k in konular.values() if isinstance(k, dict))
        ders_yanlis = sum(k.get("yanlis", 0) for k in konular.values() if isinstance(k, dict))
        ders_toplam = ders_dogru + ders_yanlis
        ders_basari = int((ders_dogru / ders_toplam * 100)) if ders_toplam > 0 else 0
        
        ders_data.append({
            "Ders": ders,
            "Doğru": ders_dogru,
            "Yanlış": ders_yanlis,
            "Toplam": ders_toplam,
            "Başarı %": ders_basari
        })
    
    if ders_data:
        df = pd.DataFrame(ders_data)
        
        # Bar chart
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Doğru',
            x=df['Ders'],
            y=df['Doğru'],
            marker_color=theme['success']
        ))
        fig.add_trace(go.Bar(
            name='Yanlış',
            x=df['Ders'],
            y=df['Yanlış'],
            marker_color=theme['error']
        ))
        
        fig.update_layout(
            barmode='group',
            height=400,
            showlegend=True,
            xaxis_title="Dersler",
            yaxis_title="Soru Sayısı"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Tablo
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Konu detayları
    st.markdown("### 📖 Konu Bazında Detaylar")
    for ders, konular in sonuclar.items():
        with st.expander(f"📕 {ders}"):
            for konu, sonuc in konular.items():
                if not isinstance(sonuc, dict):
                    continue
                
                dogru = sonuc.get("dogru", 0)
                yanlis = sonuc.get("yanlis", 0)
                toplam = dogru + yanlis
                oran = int((dogru / toplam * 100)) if toplam > 0 else 0
                
                st.markdown(f"""
                <div class="card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <h4 style="margin:0; color:{theme['text']};">{konu}</h4>
                        </div>
                        <div style="text-align:right;">
                            <span style="color:{theme['success']}; font-weight:bold;">✅ {dogru}</span>
                            <span style="margin:0 10px;">|</span>
                            <span style="color:{theme['error']}; font-weight:bold;">❌ {yanlis}</span>
                            <span style="margin:0 10px;">|</span>
                            <span style="color:{theme['primary']}; font-weight:bold;">🎯 %{oran}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ===============================
# PROFİL SAYFASI
# ===============================
def profil_page():
    """Kullanıcı profili"""
    theme = theme_manager.get_theme(st.session_state.get("theme", "light"))
    user = st.session_state.get("current_user")
    
    if not user or (user not in kullanicilar and user not in sabit_kullanicilar):
        st.warning("❌ Kullanıcı bilgisi bulunamadı!")
        st.session_state["page"] = "login"
        st.rerun()
        return
    
    if st.button("🔙 Geri", key="geri_profil"):
        st.session_state["page"] = "ders"
        st.rerun()
    
    st.markdown(f"""
    <div style="text-align:center; padding:20px 0;">
        <h2 style="font-size:36px; color:{theme['primary']};">
            👤 Profil Bilgileri
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    if user in sabit_kullanicilar:
        bilgiler = sabit_kullanicilar[user]
    else:
        bilgiler = kullanicilar[user]
    
    isim = bilgiler.get("isim", "")
    sifre = bilgiler.get("sifre", "")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown(f"""
        <div class="card">
            <h3 style="color:{theme['primary']}; margin-bottom:20px;">Kullanıcı Bilgileri</h3>
            <p><strong>İsim Soyisim:</strong> {isim}</p>
            <p><strong>Kullanıcı Adı:</strong> {user}</p>
            <p><strong>Şifre:</strong> {'*' * len(sifre)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # İstatistikler
        sonuclar = st.session_state.get("sonuclar", {})
        toplam_dogru = sum(
            konu_data.get("dogru", 0)
            for ders_data in sonuclar.values()
            for konu_data in ders_data.values()
            if isinstance(konu_data, dict)
        )
        toplam_yanlis = sum(
            konu_data.get("yanlis", 0)
            for ders_data in sonuclar.values()
            for konu_data in ders_data.values()
            if isinstance(konu_data, dict)
        )
        toplam_soru = toplam_dogru + toplam_yanlis
        
        st.markdown(f"""
        <div class="card">
            <h3 style="color:{theme['primary']}; margin-bottom:20px;">İstatistikler</h3>
            <p><strong>Toplam Çözülen Soru:</strong> {toplam_soru}</p>
            <p><strong style="color:{theme['success']};">Doğru:</strong> {toplam_dogru}</p>
            <p><strong style="color:{theme['error']};">Yanlış:</strong> {toplam_yanlis}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Şifre değiştirme
    if user not in sabit_kullanicilar:
        with st.expander("🔑 Şifre Değiştir"):
            with st.form("sifre_degistir"):
                eski = st.text_input("Eski Şifre", type="password")
                yeni = st.text_input("Yeni Şifre", type="password")
                yeni2 = st.text_input("Yeni Şifre (Tekrar)", type="password")
                
                if st.form_submit_button("💾 Güncelle", use_container_width=True):
                    if eski != sifre:
                        st.error("❌ Eski şifre yanlış!")
                    elif not yeni or not yeni2:
                        st.error("❌ Yeni şifre alanları boş olamaz!")
                    elif yeni != yeni2:
                        st.error("❌ Yeni şifreler uyuşmuyor!")
                    else:
                        kullanicilar[user]["sifre"] = yeni
                        kullanicilari_kaydet(kullanicilar)
                        st.success("✅ Şifre başarıyla güncellendi!")

# ===============================
# ADMİN PANELİ
# ===============================
def admin_page():
    """Admin paneli - Soru yönetimi"""
    theme = theme_manager.get_theme(st.session_state.get("theme", "light"))
    
    st.title("👨‍🏫 Admin Paneli")
    
    if st.button("🏠 Ana Menü", key="geri_admin"):
        st.session_state["page"] = "ders"
        st.rerun()
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👥 Kullanıcılar",
        "➕ Soru Ekle",
        "✏️ Soru Düzenle",
        "🗑️ Soru Sil",
        "📊 İstatistikler"
    ])
    
    # TAB 1 - Kullanıcı Yönetimi
    with tab1:
        st.subheader("👥 Kullanıcı Yönetimi")
        
        if not kullanicilar:
            st.info("Kayıtlı kullanıcı yok.")
        else:
            # Kullanıcı listesi
            for k_adi, k_data in kullanicilar.items():
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.markdown(f"**{k_data.get('isim', 'İsimsiz')}** (@{k_adi})")
                
                with col2:
                    sonuc = k_data.get('sonuclar', {})
                    toplam = sum(
                        kd.get("dogru", 0) + kd.get("yanlis", 0)
                        for dd in sonuc.values()
                        for kd in dd.values()
                        if isinstance(kd, dict)
                    )
                    st.write(f"📊 {toplam} soru çözdü")
                
                with col3:
                    if st.button("❌", key=f"sil_{k_adi}"):
                        if st.session_state.get(f"confirm_{k_adi}"):
                            del kullanicilar[k_adi]
                            kullanicilari_kaydet(kullanicilar)
                            st.success(f"✅ {k_adi} silindi")
                            st.rerun()
                        else:
                            st.session_state[f"confirm_{k_adi}"] = True
                            st.warning("Tekrar tıklayın")
    
    # TAB 2 - Soru Ekle
    with tab2:
        st.subheader("➕ Yeni Soru Ekle")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            ders = st.selectbox("Ders", list(soru_bankasi.keys()), key="add_ders")
            konu_listesi = list(soru_bankasi[ders].keys())
            konu_secim = st.selectbox("Konu", konu_listesi + ["➕ Yeni Konu"], key="add_konu_sec")
            
            if konu_secim == "➕ Yeni Konu":
                konu = st.text_input("Yeni Konu Adı", key="add_yeni_konu")
            else:
                konu = konu_secim
        
        with col2:
            # Resim yükleme
            st.markdown("**📸 Soru Resmi (Opsiyonel)**")
            uploaded_file = st.file_uploader(
                "Resim seç",
                type=["jpg", "jpeg", "png", "gif"],
                key="soru_resim_upload"
            )
        
        st.markdown("---")
        
        soru_metni = st.text_area("Soru Metni", height=100, key="add_soru")
        
        col1, col2 = st.columns(2)
        with col1:
            a = st.text_input("A)", key="add_a")
            b = st.text_input("B)", key="add_b")
            c = st.text_input("C)", key="add_c")
        with col2:
            d = st.text_input("D)", key="add_d")
            e = st.text_input("E)", key="add_e")
        
        dogru = st.selectbox("Doğru Cevap", ["A", "B", "C", "D", "E"], key="add_dogru")
        cozum = st.text_area("Çözüm", height=100, key="add_cozum")
        
        if st.button("➕ Soruyu Kaydet", use_container_width=True):
            if not all([ders, konu, soru_metni, a, b, c, d, e, cozum]):
                st.warning("❌ Tüm alanları doldurun")
            else:
                # Soru objesi
                yeni_soru = {
                    "soru": soru_metni,
                    "secenekler": {
                        "A": a, "B": b, "C": c, "D": d, "E": e
                    },
                    "dogru_cevap": dogru,
                    "cozum": cozum
                }
                
                # Resim varsa kaydet
                if uploaded_file:
                    soru_id = str(uuid.uuid4())[:8]
                    resim_path = image_handler.upload_image(uploaded_file, soru_id)
                    if resim_path:
                        yeni_soru["soru_resmi"] = resim_path
                
                soru_bankasi.setdefault(ders, {})
                soru_bankasi[ders].setdefault(konu, [])
                soru_bankasi[ders][konu].append(yeni_soru)
                
                soru_bankasini_kaydet(soru_bankasi)
                st.success("✅ Soru başarıyla eklendi!")
                time.sleep(1)
                st.rerun()
    
    # TAB 3 - Soru Düzenle
    with tab3:
        st.subheader("✏️ Soru Düzenle")
        
        ders = st.selectbox("Ders", list(soru_bankasi.keys()), key="edit_ders")
        konu = st.selectbox("Konu", list(soru_bankasi[ders].keys()), key="edit_konu")
        
        sorular = soru_bankasi[ders][konu]
        
        if not sorular:
            st.info("Bu konuda soru yok")
        else:
            idx = st.selectbox(
                "Düzenlenecek Soru",
                range(len(sorular)),
                format_func=lambda i: f"{i+1}. {sorular[i]['soru'][:60]}...",
                key="edit_idx"
            )
            
            s = sorular[idx]
            
            soru_metni = st.text_area("Soru", s["soru"], key="edit_soru_text")
            
            col1, col2 = st.columns(2)
            with col1:
                a = st.text_input("A)", s["secenekler"]["A"], key="edit_a")
                b = st.text_input("B)", s["secenekler"]["B"], key="edit_b")
                c = st.text_input("C)", s["secenekler"]["C"], key="edit_c")
            with col2:
                d = st.text_input("D)", s["secenekler"]["D"], key="edit_d")
                e = st.text_input("E)", s["secenekler"]["E"], key="edit_e")
            
            dogru = st.selectbox(
                "Doğru",
                ["A", "B", "C", "D", "E"],
                index=["A","B","C","D","E"].index(s["dogru_cevap"]),
                key="edit_dogru"
            )
            cozum = st.text_area("Çözüm", s["cozum"], key="edit_cozum")
            
            if st.button("💾 Güncelle", use_container_width=True):
                sorular[idx] = {
                    "soru": soru_metni,
                    "secenekler": {
                        "A": a, "B": b, "C": c, "D": d, "E": e
                    },
                    "dogru_cevap": dogru,
                    "cozum": cozum
                }
                
                # Mevcut resimleri koru
                if "soru_resmi" in s:
                    sorular[idx]["soru_resmi"] = s["soru_resmi"]
                if "cozum_resmi" in s:
                    sorular[idx]["cozum_resmi"] = s["cozum_resmi"]
                
                soru_bankasini_kaydet(soru_bankasi)
                st.success("✅ Soru güncellendi!")
    
    # TAB 4 - Soru Sil
    with tab4:
        st.subheader("🗑️ Soru Sil")
        
        ders = st.selectbox("Ders", list(soru_bankasi.keys()), key="del_ders")
        konu = st.selectbox("Konu", list(soru_bankasi[ders].keys()), key="del_konu")
        
        sorular = soru_bankasi[ders][konu]
        
        if not sorular:
            st.info("Soru yok")
        else:
            idx = st.selectbox(
                "Silinecek Soru",
                range(len(sorular)),
                format_func=lambda i: f"{i+1}. {sorular[i]['soru'][:60]}...",
                key="del_idx"
            )
            
            st.warning(f"⚠️ Bu soruyu silmek istediğinizden emin misiniz?")
            st.write(f"**{sorular[idx]['soru']}**")
            
            if st.button("❌ Soruyu Sil", use_container_width=True):
                # Resim varsa sil
                if "soru_resmi" in sorular[idx]:
                    image_handler.delete_image(sorular[idx]["soru_resmi"])
                
                sorular.pop(idx)
                soru_bankasini_kaydet(soru_bankasi)
                st.success("🗑️ Soru silindi!")
                time.sleep(1)
                st.rerun()
    
    # TAB 5 - İstatistikler
    with tab5:
        st.subheader("📊 Soru Bankası İstatistikleri")
        
        # Toplam soru sayısı
        toplam_soru = sum(
            len(konular)
            for ders_konular in soru_bankasi.values()
            for konular in ders_konular.values()
        )
        
        toplam_ders = len(soru_bankasi)
        toplam_konu = sum(len(konular) for konular in soru_bankasi.values())
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(render_stat_card("Toplam Ders", toplam_ders, "📚", theme['primary']), unsafe_allow_html=True)
        with col2:
            st.markdown(render_stat_card("Toplam Konu", toplam_konu, "📖", theme['info']), unsafe_allow_html=True)
        with col3:
            st.markdown(render_stat_card("Toplam Soru", toplam_soru, "📝", theme['success']), unsafe_allow_html=True)
        
        # Ders bazında soru dağılımı
        st.markdown("### Ders Bazında Soru Dağılımı")
        
        ders_soru_counts = []
        for ders, konular in soru_bankasi.items():
            toplam = sum(len(sorular) for sorular in konular.values())
            ders_soru_counts.append({
                "Ders": ders,
                "Soru Sayısı": toplam,
                "Konu Sayısı": len(konular)
            })
        
        if ders_soru_counts:
            df = pd.DataFrame(ders_soru_counts)
            
            fig = px.bar(
                df,
                x="Ders",
                y="Soru Sayısı",
                color="Soru Sayısı",
                color_continuous_scale="Viridis"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(df, use_container_width=True, hide_index=True)

# ===============================
# SESSION İLK KURULUM
# ===============================
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.page = "login"
    st.session_state.current_user = None
    st.session_state.theme = "light"

# ===============================
# TEMA UYGULA
# ===============================
current_theme = st.session_state.get("theme", "light")
theme_manager.apply_theme_css(current_theme)

# Sidebar'da tema seçici
if st.session_state.get("current_user"):
    theme_manager.render_theme_selector()

# ===============================
# COOKIE OTOMATİK GİRİŞ
# ===============================
if not st.session_state.get("current_user") and not st.session_state.get("logout"):
    cookie_user = cookies.get("current_user")
    if cookie_user and (cookie_user in kullanicilar or cookie_user in sabit_kullanicilar):
        st.session_state.current_user = cookie_user
        kullanici_sonuclarini_yukle_to_session(cookie_user, kullanicilar)
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

