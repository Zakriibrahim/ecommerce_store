# Translation module
import json
import os

TRANSLATIONS_DIR = os.path.dirname(__file__)

def load_translations(lang='en'):
    """Load translations for specified language"""
    filepath = os.path.join(TRANSLATIONS_DIR, f'{lang}.json')
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        # Fallback to English
        with open(os.path.join(TRANSLATIONS_DIR, 'en.json'), 'r', encoding='utf-8') as f:
            return json.load(f)

def get_available_languages():
    """Get list of available languages"""
    languages = []
    for file in os.listdir(TRANSLATIONS_DIR):
        if file.endswith('.json'):
            languages.append(file.replace('.json', ''))
    return sorted(languages)
