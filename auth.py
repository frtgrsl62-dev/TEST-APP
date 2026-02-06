"""
KPSS Quiz App - Kimlik Doğrulama ve Güvenlik Modülü
bcrypt ile şifre hashleme ve güvenli kullanıcı yönetimi
"""

import bcrypt
import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
from config import Config

class AuthManager:
    """Kimlik doğrulama yöneticisi"""
    
    def __init__(self):
        self.kullanicilar_dosya = Config.KULLANICILAR_DOSYA
        self.failed_attempts = {}  # Başarısız giriş denemeleri
    
    # ===============================
    # ŞİFRE HASHLEME
    # ===============================
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Şifreyi bcrypt ile hashle"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Şifreyi doğrula"""
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except Exception:
            return False
    
    # ===============================
    # KULLANICI YÖNETİMİ
    # ===============================
    
    def kullanicilari_yukle(self) -> Dict:
        """Kullanıcıları yükle"""
        if not os.path.exists(self.kullanicilar_dosya):
            return {}
        
        try:
            with open(self.kullanicilar_dosya, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    
    def kullanicilari_kaydet(self, kullanicilar: Dict):
        """Kullanıcıları kaydet"""
        with open(self.kullanicilar_dosya, "w", encoding="utf-8") as f:
            json.dump(kullanicilar, f, ensure_ascii=False, indent=2)
    
    # ===============================
    # KAYIT İŞLEMLERİ
    # ===============================
    
    def kayit_ol(self, kullanici_adi: str, isim: str, sifre: str, 
                 is_admin: bool = False) -> Tuple[bool, str]:
        """
        Yeni kullanıcı kaydı oluştur
        Returns: (başarılı_mı, mesaj)
        """
        kullanicilar = self.kullanicilari_yukle()
        
        # Kullanıcı adı kontrolü
        if kullanici_adi in kullanicilar:
            return False, "❌ Bu kullanıcı adı zaten kayıtlı!"
        
        # Şifre güvenlik kontrolü
        if len(sifre) < 6:
            return False, "❌ Şifre en az 6 karakter olmalı!"
        
        # Yeni kullanıcı oluştur
        hashed_password = self.hash_password(sifre)
        
        kullanicilar[kullanici_adi] = {
            "isim": isim,
            "sifre": hashed_password,
            "is_admin": is_admin,
            "sonuclar": {},
            "created_at": datetime.now().isoformat(),
            "last_login": None
        }
        
        self.kullanicilari_kaydet(kullanicilar)
        return True, f"✅ {isim} başarıyla kaydedildi!"
    
    # ===============================
    # GİRİŞ İŞLEMLERİ
    # ===============================
    
    def check_rate_limit(self, kullanici_adi: str) -> Tuple[bool, Optional[str]]:
        """
        Rate limiting kontrolü
        Returns: (izin_var_mı, kalan_süre_mesajı)
        """
        if kullanici_adi not in self.failed_attempts:
            return True, None
        
        attempt_data = self.failed_attempts[kullanici_adi]
        
        # Süre dolmuş mu kontrol et
        cooldown_end = attempt_data.get("cooldown_until")
        if cooldown_end:
            if datetime.now() < cooldown_end:
                remaining = cooldown_end - datetime.now()
                minutes = int(remaining.total_seconds() / 60)
                return False, f"⏰ {minutes} dakika sonra tekrar deneyin"
            else:
                # Süre dolmuş, temizle
                del self.failed_attempts[kullanici_adi]
                return True, None
        
        return True, None
    
    def record_failed_attempt(self, kullanici_adi: str):
        """Başarısız giriş denemesini kaydet"""
        if kullanici_adi not in self.failed_attempts:
            self.failed_attempts[kullanici_adi] = {
                "count": 0,
                "cooldown_until": None
            }
        
        self.failed_attempts[kullanici_adi]["count"] += 1
        
        # Limit aşıldı mı?
        if self.failed_attempts[kullanici_adi]["count"] >= Config.MAX_LOGIN_ATTEMPTS:
            cooldown_until = datetime.now() + timedelta(
                minutes=Config.LOGIN_COOLDOWN_MINUTES
            )
            self.failed_attempts[kullanici_adi]["cooldown_until"] = cooldown_until
    
    def clear_failed_attempts(self, kullanici_adi: str):
        """Başarılı girişte denemeleri temizle"""
        if kullanici_adi in self.failed_attempts:
            del self.failed_attempts[kullanici_adi]
    
    def giris_yap(self, kullanici_adi: str, sifre: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Kullanıcı girişi
        Returns: (başarılı_mı, mesaj, kullanici_bilgisi)
        """
        # Rate limiting kontrolü
        can_attempt, limit_message = self.check_rate_limit(kullanici_adi)
        if not can_attempt:
            return False, limit_message, None
        
        kullanicilar = self.kullanicilari_yukle()
        
        # Kullanıcı var mı?
        if kullanici_adi not in kullanicilar:
            self.record_failed_attempt(kullanici_adi)
            return False, "❌ Kullanıcı adı veya şifre hatalı!", None
        
        kullanici = kullanicilar[kullanici_adi]
        
        # Şifre doğrula
        if not self.verify_password(sifre, kullanici["sifre"]):
            self.record_failed_attempt(kullanici_adi)
            attempts_left = Config.MAX_LOGIN_ATTEMPTS - self.failed_attempts[kullanici_adi]["count"]
            return False, f"❌ Kullanıcı adı veya şifre hatalı! (Kalan deneme: {attempts_left})", None
        
        # Başarılı giriş
        self.clear_failed_attempts(kullanici_adi)
        
        # Son giriş tarihini güncelle
        kullanici["last_login"] = datetime.now().isoformat()
        kullanicilar[kullanici_adi] = kullanici
        self.kullanicilari_kaydet(kullanicilar)
        
        return True, "✅ Giriş başarılı!", kullanici
    
    # ===============================
    # ŞİFRE DEĞİŞTİRME
    # ===============================
    
    def sifre_degistir(self, kullanici_adi: str, eski_sifre: str, 
                       yeni_sifre: str) -> Tuple[bool, str]:
        """
        Kullanıcı şifresini değiştir
        Returns: (başarılı_mı, mesaj)
        """
        kullanicilar = self.kullanicilari_yukle()
        
        if kullanici_adi not in kullanicilar:
            return False, "❌ Kullanıcı bulunamadı!"
        
        kullanici = kullanicilar[kullanici_adi]
        
        # Eski şifre doğru mu?
        if not self.verify_password(eski_sifre, kullanici["sifre"]):
            return False, "❌ Eski şifre yanlış!"
        
        # Yeni şifre güvenlik kontrolü
        if len(yeni_sifre) < 6:
            return False, "❌ Yeni şifre en az 6 karakter olmalı!"
        
        # Şifreyi güncelle
        kullanici["sifre"] = self.hash_password(yeni_sifre)
        kullanicilar[kullanici_adi] = kullanici
        self.kullanicilari_kaydet(kullanicilar)
        
        return True, "✅ Şifre başarıyla güncellendi!"
    
    # ===============================
    # ADMİN KONTROLÜ
    # ===============================
    
    def is_admin(self, kullanici_adi: str) -> bool:
        """Kullanıcı admin mi kontrol et"""
        kullanicilar = self.kullanicilari_yukle()
        if kullanici_adi in kullanicilar:
            return kullanicilar[kullanici_adi].get("is_admin", False)
        return False
    
    def admin_yap(self, kullanici_adi: str) -> Tuple[bool, str]:
        """Kullanıcıya admin yetkisi ver"""
        kullanicilar = self.kullanicilari_yukle()
        
        if kullanici_adi not in kullanicilar:
            return False, "❌ Kullanıcı bulunamadı!"
        
        kullanicilar[kullanici_adi]["is_admin"] = True
        self.kullanicilari_kaydet(kullanicilar)
        return True, "✅ Admin yetkisi verildi!"
    
    # ===============================
    # MİGRASYON FONKSİYONLARI
    # ===============================
    
    def migrate_plain_passwords(self) -> Tuple[int, int]:
        """
        Düz metin şifreleri hash'e çevir
        Returns: (dönüştürülen_sayısı, toplam_sayı)
        """
        kullanicilar = self.kullanicilari_yukle()
        converted = 0
        total = len(kullanicilar)
        
        for kullanici_adi, kullanici_data in kullanicilar.items():
            sifre = kullanici_data.get("sifre", "")
            
            # Zaten hash'lenmiş mi kontrol et (bcrypt hash'leri $2b$ ile başlar)
            if not sifre.startswith("$2b$"):
                # Düz metin şifre, hashle
                kullanici_data["sifre"] = self.hash_password(sifre)
                
                # Admin flag yoksa ekle
                if "is_admin" not in kullanici_data:
                    kullanici_data["is_admin"] = False
                
                # Timestamp yoksa ekle
                if "created_at" not in kullanici_data:
                    kullanici_data["created_at"] = datetime.now().isoformat()
                if "last_login" not in kullanici_data:
                    kullanici_data["last_login"] = None
                
                converted += 1
        
        if converted > 0:
            self.kullanicilari_kaydet(kullanicilar)
        
        return converted, total
    
    def create_first_admin(self) -> bool:
        """İlk admin kullanıcısını oluştur"""
        kullanicilar = self.kullanicilari_yukle()
        
        # Zaten admin var mı kontrol et
        has_admin = any(
            user.get("is_admin", False) 
            for user in kullanicilar.values()
        )
        
        if has_admin:
            return False
        
        # İlk admin oluştur
        username = Config.FIRST_ADMIN_USERNAME
        password = Config.FIRST_ADMIN_PASSWORD
        
        self.kayit_ol(
            kullanici_adi=username,
            isim="Yönetici",
            sifre=password,
            is_admin=True
        )
        
        return True


# Global auth manager instance
auth_manager = AuthManager()
