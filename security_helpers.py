"""
KPSS Quiz App - Güvenlik Yardımcı Fonksiyonlar
main.py'de kullanılmak üzere güvenli wrapper fonksiyonlar
"""

from auth import auth_manager
from config import Config
import streamlit as st

# ===============================
# KULLANICI YÖNETİMİ
# ===============================

def get_all_users():
    """Tüm kullanıcıları getir"""
    return auth_manager.kullanicilari_yukle()

def save_all_users(users_dict):
    """Tüm kullanıcıları kaydet"""
    auth_manager.kullanicilari_kaydet(users_dict)

def is_user_admin(username):
    """Kullanıcı admin mi?"""
    return auth_manager.is_admin(username)

# ===============================
# SONUÇ YÖNETİMİ (UYUMLU)
# ===============================

def kaydet_sonuclar_to_user_secure(user):
    """Kullanıcı sonuçlarını güvenli kaydet"""
    if not user:
        return
    
    users = get_all_users()
    if user not in users:
        return
    
    users[user]["sonuclar"] = st.session_state.get("sonuclar", {})
    save_all_users(users)

def kullanici_sonuclarini_yukle_to_session_secure(user):
    """Kullanıcı sonuçlarını session'a güvenli yükle"""
    users = get_all_users()
    if user in users:
        st.session_state["sonuclar"] = users[user].get("sonuclar", {})
    else:
        st.session_state["sonuclar"] = {}

# ===============================
# KULLANICI BİLGİLERİ
# ===============================

def get_user_info(username):
    """Kullanıcı bilgilerini getir"""
    users = get_all_users()
    return users.get(username)

def update_user_info(username, **kwargs):
    """Kullanıcı bilgilerini güncelle"""
    users = get_all_users()
    if username in users:
        for key, value in kwargs.items():
            users[username][key] = value
        save_all_users(users)
        return True
    return False

# ===============================
# KULLANICI SİLME (ADMİN)
# ===============================

def delete_user_secure(username):
    """Kullanıcıyı güvenli sil"""
    users = get_all_users()
    if username in users:
        del users[username]
        save_all_users(users)
        return True
    return False

# ===============================
# UYUMLULUK FONKSİYONLARI
# ===============================

# Eski kodla uyumluluk için
def kullanicilari_yukle():
    """ESKİ FONKSİYON UYUMLULUĞU"""
    return get_all_users()

def kullanicilari_kaydet(users_dict):
    """ESKİ FONKSİYON UYUMLULUĞU"""
    save_all_users(users_dict)

# main.py'de kullanılmak üzere global erişim
kaydet_sonuclar_to_user = kaydet_sonuclar_to_user_secure
kullanici_sonuclarini_yukle_to_session = kullanici_sonuclarini_yukle_to_session_secure
