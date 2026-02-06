"""
KPSS Quiz App - Tema Yönetim Sistemi
Kullanıcıların tercihine göre tema değiştirme
"""

import streamlit as st
from typing import Dict, Literal

ThemeType = Literal["light", "dark", "blue", "green", "purple"]

class ThemeManager:
    """Tema yönetim sınıfı"""
    
    THEMES: Dict[ThemeType, Dict[str, str]] = {
        "light": {
            "primary": "#FF6B35",
            "secondary": "#F7931E",
            "background": "#FFFFFF",
            "text": "#2C3E50",
            "success": "#27AE60",
            "error": "#E74C3C",
            "warning": "#F39C12",
            "info": "#3498DB",
            "card_bg": "#F8F9FA",
            "border": "#E0E0E0",
            "shadow": "rgba(0,0,0,0.1)",
        },
        "dark": {
            "primary": "#FF6B35",
            "secondary": "#F7931E",
            "background": "#1E1E1E",
            "text": "#E0E0E0",
            "success": "#27AE60",
            "error": "#E74C3C",
            "warning": "#F39C12",
            "info": "#3498DB",
            "card_bg": "#2D2D2D",
            "border": "#404040",
            "shadow": "rgba(0,0,0,0.3)",
        },
        "blue": {
            "primary": "#2E86DE",
            "secondary": "#54A0FF",
            "background": "#F1F5F9",
            "text": "#1E293B",
            "success": "#10B981",
            "error": "#EF4444",
            "warning": "#F59E0B",
            "info": "#3B82F6",
            "card_bg": "#FFFFFF",
            "border": "#CBD5E1",
            "shadow": "rgba(46,134,222,0.1)",
        },
        "green": {
            "primary": "#27AE60",
            "secondary": "#2ECC71",
            "background": "#F0FDF4",
            "text": "#064E3B",
            "success": "#10B981",
            "error": "#EF4444",
            "warning": "#F59E0B",
            "info": "#3B82F6",
            "card_bg": "#FFFFFF",
            "border": "#86EFAC",
            "shadow": "rgba(39,174,96,0.1)",
        },
        "purple": {
            "primary": "#8B5CF6",
            "secondary": "#A78BFA",
            "background": "#FAF5FF",
            "text": "#4C1D95",
            "success": "#10B981",
            "error": "#EF4444",
            "warning": "#F59E0B",
            "info": "#3B82F6",
            "card_bg": "#FFFFFF",
            "border": "#DDD6FE",
            "shadow": "rgba(139,92,246,0.1)",
        }
    }
    
    @classmethod
    def get_theme(cls, theme_name: ThemeType = "light") -> Dict[str, str]:
        """Tema renklerini getir"""
        return cls.THEMES.get(theme_name, cls.THEMES["light"])
    
    @classmethod
    def apply_theme_css(cls, theme_name: ThemeType = "light"):
        """Temayı uygula"""
        theme = cls.get_theme(theme_name)
        
        css = f"""
        <style>
        /* Global Styles */
        .stApp {{
            background-color: {theme['background']};
            color: {theme['text']};
        }}
        
        /* Buttons */
        .stButton>button {{
            background-color: {theme['primary']};
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px {theme['shadow']};
        }}
        
        .stButton>button:hover {{
            background-color: {theme['secondary']};
            transform: translateY(-2px);
            box-shadow: 0 4px 8px {theme['shadow']};
        }}
        
        /* Cards */
        .card {{
            background-color: {theme['card_bg']};
            border: 1px solid {theme['border']};
            border-radius: 12px;
            padding: 20px;
            margin: 10px 0;
            box-shadow: 0 2px 8px {theme['shadow']};
            transition: all 0.3s ease;
        }}
        
        .card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 4px 12px {theme['shadow']};
        }}
        
        /* Progress Circle */
        .progress-circle {{
            width: 60px;
            height: 60px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            color: {theme['text']};
            box-shadow: 0 2px 4px {theme['shadow']};
        }}
        
        /* Success */
        .success {{
            color: {theme['success']};
            background-color: {theme['success']}20;
            padding: 10px;
            border-radius: 8px;
            border-left: 4px solid {theme['success']};
        }}
        
        /* Error */
        .error {{
            color: {theme['error']};
            background-color: {theme['error']}20;
            padding: 10px;
            border-radius: 8px;
            border-left: 4px solid {theme['error']};
        }}
        
        /* Warning */
        .warning {{
            color: {theme['warning']};
            background-color: {theme['warning']}20;
            padding: 10px;
            border-radius: 8px;
            border-left: 4px solid {theme['warning']};
        }}
        
        /* Info */
        .info {{
            color: {theme['info']};
            background-color: {theme['info']}20;
            padding: 10px;
            border-radius: 8px;
            border-left: 4px solid {theme['info']};
        }}
        
        /* Headers */
        h1, h2, h3 {{
            color: {theme['text']};
        }}
        
        /* Inputs */
        .stTextInput>div>div>input,
        .stTextArea>div>div>textarea {{
            border: 2px solid {theme['border']};
            border-radius: 8px;
            background-color: {theme['card_bg']};
            color: {theme['text']};
        }}
        
        .stTextInput>div>div>input:focus,
        .stTextArea>div>div>textarea:focus {{
            border-color: {theme['primary']};
            box-shadow: 0 0 0 2px {theme['primary']}30;
        }}
        
        /* Radio Buttons */
        .stRadio>div {{
            background-color: {theme['card_bg']};
            padding: 15px;
            border-radius: 8px;
            border: 1px solid {theme['border']};
        }}
        
        /* Expander */
        .streamlit-expanderHeader {{
            background-color: {theme['card_bg']};
            border: 1px solid {theme['border']};
            border-radius: 8px;
            color: {theme['text']};
        }}
        
        /* Sidebar */
        section[data-testid="stSidebar"] {{
            background-color: {theme['card_bg']};
            border-right: 1px solid {theme['border']};
        }}
        
        /* Animation */
        @keyframes fadeIn {{
            from {{
                opacity: 0;
                transform: translateY(10px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        .fade-in {{
            animation: fadeIn 0.3s ease-in;
        }}
        
        /* Scrollbar */
        ::-webkit-scrollbar {{
            width: 10px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: {theme['background']};
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: {theme['border']};
            border-radius: 5px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: {theme['primary']};
        }}
        </style>
        """
        
        st.markdown(css, unsafe_allow_html=True)
    
    @classmethod
    def render_theme_selector(cls):
        """Tema seçici widget'ı"""
        st.sidebar.markdown("### 🎨 Tema Seçimi")
        
        theme_options = {
            "☀️ Açık": "light",
            "🌙 Koyu": "dark",
            "💙 Mavi": "blue",
            "💚 Yeşil": "green",
            "💜 Mor": "purple"
        }
        
        current_theme = st.session_state.get("theme", "light")
        current_label = [k for k, v in theme_options.items() if v == current_theme][0]
        
        selected = st.sidebar.selectbox(
            "Tema",
            options=list(theme_options.keys()),
            index=list(theme_options.keys()).index(current_label),
            key="theme_selector"
        )
        
        new_theme = theme_options[selected]
        
        if new_theme != current_theme:
            st.session_state["theme"] = new_theme
            st.rerun()
        
        return new_theme

# Global theme manager instance
theme_manager = ThemeManager()
