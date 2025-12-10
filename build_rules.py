import json
import copy
from deep_translator import GoogleTranslator

# Config
SOURCE_FILE = 'rules_source.json'
OUTPUT_FILE = 'rules.json'

# Language mapping (File Key -> Google Translate Code)
# 'zh' in your file is usually Simplified Chinese ('zh-CN' in Google)
LANGUAGES = {
    'ko': 'ko',
    'zh': 'zh-CN',
    'tr': 'tr',
    'fr': 'fr',
    'es': 'es',
    'ar': 'ar'
}

def generate_html(sections, lang_code='en'):
    """
    Generates the HTML string from the JSON sections.
    Handles the continuous numbering logic automatically.
    """
    html_output = ""
    
    # Check for RTL (Right-to-Left) languages like Arabic
    if lang_code == 'ar':
        html_output += '<div style="direction: rtl; text-align: right;">\n'

    global_counter = 1
    
    for section in sections:
        html_output += f"\n<h3>{section['title']}</h3>\n"
        
        # Determine the start number for the ordered list
        if global_counter == 1:
            html_output += "<ol>\n"
        else:
            html_output += f'<ol start="{global_counter}">\n'
            
        for rule in section['rules']:
            html_output += f"  <li>{rule}</li>\n"
            global_counter += 1
            
        html_output += "</ol>\n"

    if lang_code == 'ar':
        html_output += '</div>\n'
        
    return html_output

def main():
    try:
        with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
            english_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find {SOURCE_FILE}. Make sure it is in the same folder.")
        return

    final_output = {}

    # 1. Process English (No translation needed)
    print("Processing: en (Original)")
    final_output['en'] = generate_html(english_data, 'en')

    # 2. Process Translations
    for file_key, google_code in LANGUAGES.items():
        print(f"Translating to: {file_key} ({google_code})...")
        
        # Deep copy to ensure we don't modify the original English data
        translated_sections = copy.deepcopy(english_data)
        translator = GoogleTranslator(source='en', target=google_code)
        
        for section in translated_sections:
            # Translate Title
            try:
                section['title'] = translator.translate(section['title'])
            except Exception as e:
                print(f"  Warning: Failed to translate title '{section['title']}' - {e}")

            # Translate Rules
            new_rules = []
            for rule in section['rules']:
                try:
                    # Translate the rule
                    translated_text = translator.translate(rule)
                    new_rules.append(translated_text)
                except Exception as e:
                    print(f"  Warning: Failed to translate rule - {e}")
                    new_rules.append(rule) # Fallback to English on error
            
            section['rules'] = new_rules

        # Generate HTML for this language
        final_output[file_key] = generate_html(translated_sections, file_key)

    # 3. Save to rules.json
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_output, f, ensure_ascii=False, indent=2)
    
    print(f"Success! Updated {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
