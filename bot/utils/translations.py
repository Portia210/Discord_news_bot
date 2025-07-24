import json
import os
from typing import Dict, Any, Optional
from pathlib import Path

class TranslationManager:
    """Manages translations for the Discord bot with bilingual support"""
    
    def __init__(self, default_language: str = "en"):
        self.default_language = default_language
        self.current_language = default_language
        self.translations = {}
        self.translations_path = Path(__file__).parent.parent / "translations"
        self._load_translations()
    
    def _load_translations(self):
        """Load all translation files"""
        if not self.translations_path.exists():
            self.translations_path.mkdir(parents=True, exist_ok=True)
            return
        
        for json_file in self.translations_path.glob("*.json"):
            module_name = json_file.stem
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    self.translations[module_name] = json.load(f)
            except Exception as e:
                print(f"Error loading translation file {json_file}: {e}")
    
    def set_language(self, language: str):
        """Set the current language preference"""
        if language in ["en", "he"]:
            self.current_language = language
        else:
            print(f"Warning: Language '{language}' not supported, using default '{self.default_language}'")
            self.current_language = self.default_language
    
    def get(self, module: str, key: str, **kwargs) -> str:
        """
        Get a translated string
        
        Args:
            module: The module name (e.g., 'notifications', 'general')
            key: The translation key
            **kwargs: Format parameters for the string
        
        Returns:
            The translated string, or the key if not found
        """
        try:
            # Get the translation object
            if (module in self.translations and 
                key in self.translations[module]):
                
                translation_obj = self.translations[module][key]
                
                # If it's a string, return as is (for simple keys)
                if isinstance(translation_obj, str):
                    text = translation_obj
                    return text.format(**kwargs) if kwargs else text
                
                # If it's an object with language keys
                if isinstance(translation_obj, dict):
                    # Try current language first
                    if self.current_language in translation_obj:
                        text = translation_obj[self.current_language]
                        return text.format(**kwargs) if kwargs else text
                    
                    # Fallback to default language
                    if self.default_language in translation_obj:
                        text = translation_obj[self.default_language]
                        return text.format(**kwargs) if kwargs else text
                    
                    # If no language found, return the first available
                    if translation_obj:
                        first_lang = list(translation_obj.keys())[0]
                        text = translation_obj[first_lang]
                        return text.format(**kwargs) if kwargs else text
            
            # If not found, return the key
            return key
            
        except Exception as e:
            print(f"Error getting translation for {module}.{key}: {e}")
            return key
    
    def get_bilingual(self, module: str, key: str, **kwargs) -> str:
        """
        Get both languages side by side
        
        Args:
            module: The module name
            key: The translation key
            **kwargs: Format parameters for the string
        
        Returns:
            String with both languages separated by separator
        """
        try:
            if (module in self.translations and 
                key in self.translations[module]):
                
                translation_obj = self.translations[module][key]
                
                if isinstance(translation_obj, dict) and len(translation_obj) >= 2:
                    en_text = translation_obj.get("en", "")
                    he_text = translation_obj.get("he", "")
                    
                    # Apply formatting to both
                    if kwargs:
                        en_text = en_text.format(**kwargs)
                        he_text = he_text.format(**kwargs)
                    
                    return f"{en_text} | {he_text}"
                
                # Fallback to regular get
                return self.get(module, key, **kwargs)
            
            return key
            
        except Exception as e:
            print(f"Error getting bilingual translation for {module}.{key}: {e}")
            return key
    
    def get_languages(self) -> list:
        """Get list of available languages"""
        return ["en", "he"]
    
    def reload(self):
        """Reload all translation files"""
        self.translations = {}
        self._load_translations()

# Global translation manager instance
translations = TranslationManager()

def t(module: str, key: str, **kwargs) -> str:
    """Shortcut function to get translations"""
    return translations.get(module, key, **kwargs)

def t_bilingual(module: str, key: str, **kwargs) -> str:
    """Shortcut function to get bilingual translations"""
    return translations.get_bilingual(module, key, **kwargs)

def set_language(language: str):
    """Shortcut function to set language"""
    translations.set_language(language)

def get_languages() -> list:
    """Shortcut function to get available languages"""
    return translations.get_languages()

# Smart translation function that automatically handles language mode
def smart_t(module: str, key: str, language_mode: str = None, **kwargs) -> str:
    """
    Smart translation function that automatically chooses the right translation method
    based on the language mode.
    
    Args:
        module: The module name
        key: The translation key
        language_mode: Language mode ("en", "he", "bilingual", or None to auto-detect)
        **kwargs: Format parameters for the string
    
    Returns:
        The appropriate translated string
    """
    if language_mode is None:
        # Auto-detect from current language setting
        from config import Config
        language_mode = Config.LANGUAGE.BOT_LANGUAGE
    
    if language_mode == "bilingual":
        return t_bilingual(module, key, **kwargs)
    else:
        return t(module, key, **kwargs) 