"""
KPSS Quiz App - Resim Yönetimi Modülü
Sorulara resim ekleme, görüntüleme ve yönetme
"""

import os
import base64
import requests
from io import BytesIO
from PIL import Image
import streamlit as st
from typing import Optional, Dict, List

class ImageHandler:
    """Resim işleme sınıfı"""
    
    # Desteklenen resim formatları
    SUPPORTED_FORMATS = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
    
    # Maksimum dosya boyutu (MB)
    MAX_FILE_SIZE_MB = 5
    
    # Resim depolama klasörü
    IMAGE_FOLDER = "soru_resimleri"
    
    def __init__(self):
        # Resim klasörünü oluştur
        if not os.path.exists(self.IMAGE_FOLDER):
            os.makedirs(self.IMAGE_FOLDER)
    
    # ===============================
    # RESİM YÜKLEME
    # ===============================
    
    def upload_image(self, uploaded_file, soru_id: str) -> Optional[str]:
        """
        Yüklenen resmi kaydet
        Args:
            uploaded_file: Streamlit UploadedFile objesi
            soru_id: Soru ID (dosya adı için)
        Returns:
            Kaydedilen dosya yolu veya None
        """
        if uploaded_file is None:
            return None
        
        # Dosya boyutu kontrolü
        file_size_mb = uploaded_file.size / (1024 * 1024)
        if file_size_mb > self.MAX_FILE_SIZE_MB:
            st.error(f"❌ Dosya çok büyük! Max {self.MAX_FILE_SIZE_MB}MB")
            return None
        
        # Dosya uzantısı kontrolü
        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
        if file_ext not in self.SUPPORTED_FORMATS:
            st.error(f"❌ Desteklenmeyen format! Desteklenenler: {', '.join(self.SUPPORTED_FORMATS)}")
            return None
        
        # Dosya adı oluştur
        filename = f"{soru_id}{file_ext}"
        filepath = os.path.join(self.IMAGE_FOLDER, filename)
        
        # Resmi kaydet
        try:
            # PIL ile aç ve kaydet (format dönüşümü için)
            image = Image.open(uploaded_file)
            
            # EXIF oryantasyon düzeltmesi
            image = self._fix_image_orientation(image)
            
            # Boyut optimizasyonu (opsiyonel)
            image = self._optimize_image(image)
            
            # Kaydet
            image.save(filepath, quality=85, optimize=True)
            
            return filepath
            
        except Exception as e:
            st.error(f"❌ Resim kaydedilemedi: {e}")
            return None
    
    def _fix_image_orientation(self, image: Image.Image) -> Image.Image:
        """EXIF oryantasyon bilgisini düzelt"""
        try:
            from PIL import ExifTags
            
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break
            
            exif = dict(image._getexif().items()) if hasattr(image, '_getexif') and image._getexif() else {}
            
            if orientation in exif:
                if exif[orientation] == 3:
                    image = image.rotate(180, expand=True)
                elif exif[orientation] == 6:
                    image = image.rotate(270, expand=True)
                elif exif[orientation] == 8:
                    image = image.rotate(90, expand=True)
        except:
            pass
        
        return image
    
    def _optimize_image(self, image: Image.Image, max_width: int = 800) -> Image.Image:
        """Resmi optimize et (boyut küçültme)"""
        # Oranı koruyarak küçült
        if image.width > max_width:
            ratio = max_width / image.width
            new_height = int(image.height * ratio)
            image = image.resize((max_width, new_height), Image.Resampling.LANCZOS)
        
        # RGB'ye çevir (şeffaflık varsa beyaz arka plan)
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        
        return image
    
    # ===============================
    # RESİM GÖRÜNTÜLEME
    # ===============================
    
    def display_image(self, image_path: str, caption: str = "", width: int = None):
        """
        Resmi Streamlit'te göster
        Args:
            image_path: Dosya yolu, URL veya Google Drive linki
            caption: Resim başlığı
            width: Genişlik (px)
        """
        if not image_path:
            return
        
        try:
            # Google Drive linki mi?
            if "drive.google.com" in image_path:
                image_path = self._convert_gdrive_url(image_path)
            
            # URL mi?
            if image_path.startswith("http"):
                st.image(image_path, caption=caption, width=width)
            
            # Yerel dosya mı?
            elif os.path.exists(image_path):
                st.image(image_path, caption=caption, width=width)
            
            else:
                st.warning(f"⚠️ Resim bulunamadı: {image_path}")
                
        except Exception as e:
            st.error(f"❌ Resim gösterilemedi: {e}")
    
    def _convert_gdrive_url(self, url: str) -> str:
        """
        Google Drive paylaşım linkini direkt görüntüleme linkine çevir
        """
        # https://drive.google.com/file/d/FILE_ID/view?usp=sharing
        # -> https://drive.google.com/uc?export=view&id=FILE_ID
        
        if "/file/d/" in url:
            file_id = url.split("/file/d/")[1].split("/")[0]
            return f"https://drive.google.com/uc?export=view&id={file_id}"
        
        return url
    
    # ===============================
    # RESİM SİLME
    # ===============================
    
    def delete_image(self, image_path: str) -> bool:
        """
        Resmi sil
        Args:
            image_path: Silinecek dosya yolu
        Returns:
            Başarılı mı?
        """
        if not image_path or not os.path.exists(image_path):
            return False
        
        try:
            os.remove(image_path)
            return True
        except Exception as e:
            st.error(f"❌ Resim silinemedi: {e}")
            return False
    
    # ===============================
    # YARDIMCI FONKSİYONLAR
    # ===============================
    
    def get_image_info(self, image_path: str) -> Optional[Dict]:
        """Resim bilgilerini getir"""
        if not os.path.exists(image_path):
            return None
        
        try:
            image = Image.open(image_path)
            return {
                "format": image.format,
                "size": os.path.getsize(image_path),
                "width": image.width,
                "height": image.height,
                "mode": image.mode
            }
        except:
            return None
    
    def list_all_images(self) -> List[str]:
        """Tüm resimleri listele"""
        if not os.path.exists(self.IMAGE_FOLDER):
            return []
        
        images = []
        for filename in os.listdir(self.IMAGE_FOLDER):
            if any(filename.lower().endswith(ext) for ext in self.SUPPORTED_FORMATS):
                images.append(os.path.join(self.IMAGE_FOLDER, filename))
        
        return sorted(images)

# Global image handler instance
image_handler = ImageHandler()


# ===============================
# SORU YAPISI GÜNCELLEMELERİ
# ===============================

def create_image_question_structure():
    """
    Resimli soru için JSON yapısı örneği
    """
    return {
        "soru": "Aşağıdaki haritada işaretli bölge hangi coğrafi bölgemizdir?",
        
        # Soru resmi (opsiyonel)
        "soru_resmi": "soru_resimleri/cografya_001.jpg",
        # veya Google Drive linki
        # "soru_resmi": "https://drive.google.com/file/d/...",
        
        # Maddeler (opsiyonel)
        "maddeler": [],
        
        # Şıklar
        "secenekler": {
            "A": "Marmara Bölgesi",
            "B": "Ege Bölgesi",
            "C": "İç Anadolu Bölgesi",
            "D": "Akdeniz Bölgesi",
            "E": "Karadeniz Bölgesi"
        },
        
        # Şık resimleri (opsiyonel - her şık için ayrı resim)
        "secenekler_resimleri": {
            # "A": "soru_resimleri/secenek_A.jpg",
            # "B": "soru_resimleri/secenek_B.jpg",
        },
        
        "dogru_cevap": "A",
        "cozum": "Haritada işaretli bölge Marmara Bölgesidir...",
        
        # Çözüm resmi (opsiyonel)
        "cozum_resmi": ""
    }


def get_question_images(soru: Dict) -> Dict[str, str]:
    """
    Sorudaki tüm resimleri çıkar
    Returns:
        {
            'soru': 'path/to/image.jpg',
            'secenek_A': 'path/to/A.jpg',
            'cozum': 'path/to/solution.jpg'
        }
    """
    images = {}
    
    # Soru resmi
    if "soru_resmi" in soru and soru["soru_resmi"]:
        images["soru"] = soru["soru_resmi"]
    
    # Şık resimleri
    if "secenekler_resimleri" in soru:
        for harf, resim in soru["secenekler_resimleri"].items():
            if resim:
                images[f"secenek_{harf}"] = resim
    
    # Çözüm resmi
    if "cozum_resmi" in soru and soru["cozum_resmi"]:
        images["cozum"] = soru["cozum_resmi"]
    
    return images

