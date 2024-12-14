import json
import re
import sys
from bs4 import BeautifulSoup

"""
This is not yet fully compatible with poorly structured HTML tags.
"""

def extract_text_and_readings(html_text):
    """
    Extract both regular text and readings from HTML, maintaining the correct order.
    """
    soup = BeautifulSoup(html_text, 'html.parser')
    text_parts = []

    for span in soup.find_all('span', class_='term'):
        ruby = span.find('ruby')
        if ruby:
            # Get the furigana
            rt = ruby.find('rt')
            if rt:
                furigana = rt.get_text().strip()
                # Get any text that follows the ruby element within the span
                following_text = ruby.next_sibling
                if following_text and isinstance(following_text, str):
                    text_parts.append(furigana + following_text.strip())
                else:
                    text_parts.append(furigana)
        else:
            # Handle non-ruby text within spans
            text = span.get_text().strip()
            if text:
                text_parts.append(text)

    return text_parts

def transliterate_to_romaji(text):
    """
    Transliterates a given text (hiragana/katakana) to romaji.
    """
    hiragana_to_romaji = {
        'あ': 'a', 'い': 'i', 'う': 'u', 'え': 'e', 'お': 'o',
        'か': 'ka', 'き': 'ki', 'く': 'ku', 'け': 'ke', 'こ': 'ko',
        'さ': 'sa', 'し': 'shi', 'す': 'su', 'せ': 'se', 'そ': 'so',
        'た': 'ta', 'ち': 'chi', 'つ': 'tsu', 'て': 'te', 'と': 'to',
        'な': 'na', 'に': 'ni', 'ぬ': 'nu', 'ね': 'ne', 'の': 'no',
        'は': 'ha', 'ひ': 'hi', 'ふ': 'fu', 'へ': 'he', 'ほ': 'ho',
        'ま': 'ma', 'み': 'mi', 'む': 'mu', 'め': 'me', 'も': 'mo',
        'や': 'ya', 'ゆ': 'yu', 'よ': 'yo',
        'ら': 'ra', 'り': 'ri', 'る': 'ru', 'れ': 're', 'ろ': 'ro',
        'わ': 'wa', 'を': 'wo', 'ん': 'n',
        'が': 'ga', 'ぎ': 'gi', 'ぐ': 'gu', 'げ': 'ge', 'ご': 'go',
        'ざ': 'za', 'じ': 'ji', 'ず': 'zu', 'ぜ': 'ze', 'ぞ': 'zo',
        'だ': 'da', 'ぢ': 'ji', 'づ': 'zu', 'で': 'de', 'ど': 'do',
        'ば': 'ba', 'び': 'bi', 'ぶ': 'bu', 'べ': 'be', 'ぼ': 'bo',
        'ぱ': 'pa', 'ぴ': 'pi', 'ぷ': 'pu', 'ぺ': 'pe', 'ぽ': 'po',
        'きゃ': 'kya', 'きゅ': 'kyu', 'きょ': 'kyo',
        'しゃ': 'sha', 'しゅ': 'shu', 'しょ': 'sho',
        'ちゃ': 'cha', 'ちゅ': 'chu', 'ちょ': 'cho',
        'にゃ': 'nya', 'にゅ': 'nyu', 'にょ': 'nyo',
        'ひゃ': 'hya', 'ひゅ': 'hyu', 'ひょ': 'hyo',
        'みゃ': 'mya', 'みゅ': 'myu', 'みょ': 'myo',
        'りゃ': 'rya', 'りゅ': 'ryu', 'りょ': 'ryo',
        'ぎゃ': 'gya', 'ぎゅ': 'gyu', 'ぎょ': 'gyo',
        'じゃ': 'ja', 'じゅ': 'ju', 'じょ': 'jo',
        'びゃ': 'bya', 'びゅ': 'byu', 'びょ': 'byo',
        'ぴゃ': 'pya', 'ぴゅ': 'pyu', 'ぴょ': 'pyo',
        'た': 'ta', 'ち': 'chi', 'つ': 'tsu', 'て': 'te', 'と': 'to',
        'っ': '',  # Small tsu doubles the following consonant
    }

    romaji_text = ""
    i = 0
    while i < len(text):
        # Handle small tsu (っ) for consonant doubling
        if i < len(text) - 1 and text[i] == 'っ':
            if i + 1 < len(text):
                next_char = text[i + 1]
                if next_char in hiragana_to_romaji:
                    next_romaji = hiragana_to_romaji[next_char]
                    if next_romaji[0] != 'n':  # Don't double 'n'
                        romaji_text += next_romaji[0]  # Double the consonant
            i += 1
            continue

        # Check for digraphs (e.g., きゃ, しゃ, etc.)
        if i + 1 < len(text) and text[i:i+2] in hiragana_to_romaji:
            romaji_text += hiragana_to_romaji[text[i:i+2]]
            i += 2
        elif text[i] in hiragana_to_romaji:
            romaji_text += hiragana_to_romaji[text[i]]
            i += 1
        else:
            romaji_text += text[i]  # For unsupported characters, retain as-is
            i += 1

    return romaji_text

def convert_html_to_romaji_srt(html_text):
    """
    Convert HTML ruby text into romaji with proper word spacing for SRT format.
    """
    text_parts = extract_text_and_readings(html_text)

    # Convert each part to romaji and join them
    romaji_parts = []
    for part in text_parts:
        romaji = transliterate_to_romaji(part)
        if romaji:  # Only add non-empty strings
            romaji_parts.append(romaji)

    return ' '.join(romaji_parts)

def read_srt_timings(srt_path):
    """
    Read timings from an existing SRT file.
    """
    timings = []
    with open(srt_path, 'r', encoding='utf-8') as srt_file:
        for line in srt_file:
            if '-->' in line:
                timings.append(line.strip())
    return timings

def process_json_to_srt(json_path, output_srt_path, timings_srt_path):
    """
    Process the JSON file and generate a .srt file with romaji, using timings from an existing SRT file.
    """
    with open(json_path, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)

    timings = read_srt_timings(timings_srt_path)

    with open(output_srt_path, 'w', encoding='utf-8') as srt_file:
        for i, (ruby_html, timing) in enumerate(zip(data, timings), 1):
            # Convert the HTML text to romaji
            romaji_text = convert_html_to_romaji_srt(ruby_html)

            # Write the SRT entry
            srt_file.write(f"{i}\n")
            srt_file.write(f"{timing}\n")
            srt_file.write(f"{romaji_text}\n\n")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py <input_json> <output_srt> <timings_srt>")
        sys.exit(1)

    input_json = sys.argv[1]
    output_srt = sys.argv[2]
    timings_srt = sys.argv[3]

    try:
        process_json_to_srt(input_json, output_srt, timings_srt)
        print(f"Subtitle file saved as {output_srt}")
    except Exception as e:
        print(f"An error occurred: {e}")