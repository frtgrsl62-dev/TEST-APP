"""
KPSS Quiz App - Yapılandırma Yöneticisi
Güvenli ayar yönetimi için .env dosyası kullanır
"""

import os
from dotenv import load_dotenv
import secrets

# .env dosyasını yükle
load_dotenv()

class Config:
    """Uygulama yapılandırma sınıfı"""
    
    # Cookie Ayarları
    COOKIE_PREFIX = "kpss_app"
    COOKIE_PASSWORD = os.getenv("COOKIE_PASSWORD", secrets.token_urlsafe(32))
    
    # Session Ayarları
    SESSION_LIFETIME_HOURS = int(os.getenv("SESSION_LIFETIME_HOURS", "24"))
    
    # Güvenlik Ayarları
    MAX_LOGIN_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
    LOGIN_COOLDOWN_MINUTES = int(os.getenv("LOGIN_COOLDOWN_MINUTES", "15"))
    
    # Uygulama Ayarları
    APP_NAME = os.getenv("APP_NAME", "KPSS SORU ÇÖZÜM PLATFORMU")
    DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"
    
    # Dosya Yolları
    KULLANICILAR_DOSYA = "kullanicilar.json"
    SORU_BANKASI_DOSYA = "soru_bankasi.json"
    
    # İlk Admin Ayarları
    FIRST_ADMIN_USERNAME = os.getenv("FIRST_ADMIN_USERNAME", "admin")
    FIRST_ADMIN_PASSWORD = os.getenv("FIRST_ADMIN_PASSWORD", "Admin123!")
    
    @classmethod
    def validate_config(cls):
        """Yapılandırma doğrulaması"""
        errors = []
        
        # Cookie şifresi kontrolü
        if len(cls.COOKIE_PASSWORD) < 32:
            errors.append("⚠️ COOKIE_PASSWORD en az 32 karakter olmalı!")
        
        # Admin şifresi kontrolü
        if len(cls.FIRST_ADMIN_PASSWORD) < 8:
            errors.append("⚠️ FIRST_ADMIN_PASSWORD en az 8 karakter olmalı!")
        
        return errors
    
    @classmethod
    def generate_secure_password(cls, length=32):
        """Güvenli rastgele şifre üretir"""
        return secrets.token_urlsafe(length)

# Yapılandırma doğrulama
def check_config():
    """Başlangıçta yapılandırmayı kontrol et"""
    errors = Config.validate_config()
    if errors:
        print("=" * 60)
        print("⚠️  YAPILANDIRMA UYARILARI")
        print("=" * 60)
        for error in errors:
            print(error)
        print("\n💡 Çözüm: .env dosyasını kontrol edin")
        print("Örnek için .env.example dosyasına bakın\n")
        print("=" * 60)
    return len(errors) == 0

# İlk yüklemede kontrol et
if __name__ == "__main__":
    if check_config():
        print("✅ Yapılandırma başarıyla doğrulandı!")
    else:
        print("❌ Yapılandırma hataları var!")
