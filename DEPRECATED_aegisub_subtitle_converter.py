import json
import re
from bs4 import BeautifulSoup
import argparse
from pathlib import Path

class SubtitleConverter:
    def __init__(self, font_name="Arial", font_size=48, ruby_size=24, vertical_margin=50):
        self.style_template = f"""[Script Info]
Title: Converted Subtitles
ScriptType: v4.00+
PlayDepth: 0
ScaledBorderAndShadow: yes
Collisions: Normal
PlayResX: 1280
PlayResY: 720

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font_name},{font_size},&H00FFFFFF,&H000000FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,2,0,2,10,10,{vertical_margin},1
Style: Ruby,{font_name},{ruby_size},&H00FFFFFF,&H000000FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,1,0,8,10,10,{vertical_margin},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        self.font_name = font_name
        self.font_size = font_size
        self.ruby_size = ruby_size

    def process_ruby(self, ruby_tag):
        """Extract base text and ruby text from a ruby tag."""
        base = ''
        rt = ''

        # Get all direct text nodes and non-rt elements for base text
        for child in ruby_tag.children:
            if child.name != 'rt':
                if isinstance(child, str):
                    base += child.strip()
                elif child.string:
                    base += child.string.strip()

        # Get rt text
        rt_tag = ruby_tag.find('rt')
        if rt_tag:
            rt = rt_tag.string.strip()

        return base, rt

    def convert_html_to_aegisub(self, html_text):
        """Convert HTML-like ruby text to Aegisub format with ruby text floating above kanji."""
        soup = BeautifulSoup(html_text, 'html.parser')
        result = ""

        for element in soup.find_all(['ruby']):
            if element.name == 'ruby':
                base, rt = self.process_ruby(element)
                if base and rt:
                    # Adjust positions for ruby text and kanji
                    # We will position both at the same x position (centered) but with different vertical offsets
                    ruby_y_position = 300  # Adjust this value to float the ruby text above the kanji
                    kanji_y_position = 350  # The kanji will be positioned just below the ruby text

                    # Position the ruby text (furigana) above the kanji
                    result += f"{{\\fs{self.ruby_size}\\pos(640,{ruby_y_position})}}{rt}{{\\N}}"
                    # Position the kanji below the ruby text
                    result += f"{{\\fs{self.font_size}\\pos(640,{kanji_y_position})}}{base}"
            else:
                for child in element.children:
                    if child.name == 'ruby':
                        base, rt = self.process_ruby(child)
                        if base and rt:
                            result += f"{{\\fs{self.ruby_size}\\pos(640,300)}}{rt}{{\\N}}"
                            result += f"{{\\fs{self.font_size}\\pos(640,350)}}{base}"
                    elif isinstance(child, str):
                        result += child.strip()

        return result


    def process_subtitles_file(self, srt_file, json_file, output_file):
        """Align SRT timings with JSON subtitle data and output an ASS file."""
        with open(srt_file, 'r', encoding='utf-8') as srt, open(json_file, 'r', encoding='utf-8') as json_file:
            srt_lines = srt.readlines()
            subtitles = json.load(json_file)

        # Create ASS file with style information
        ass_content = self.style_template

        # Parse SRT timings
        timings = self.extract_srt_timings(srt_lines)

        for i, (start_time, end_time) in enumerate(timings):
            if i < len(subtitles):  # Prevent index out-of-range
                aegisub_text = self.convert_html_to_aegisub(subtitles[i])
                line = f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{aegisub_text}\n"
                ass_content += line

        # Write the ASS file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(ass_content)

    def extract_srt_timings(self, srt_lines):
        """Extract timings from an SRT file."""
        timings = []
        time_pattern = re.compile(r"(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})")

        for line in srt_lines:
            match = time_pattern.match(line)
            if match:
                start_time = match.group(1).replace(',', '.')
                end_time = match.group(2).replace(',', '.')
                timings.append((start_time, end_time))

        return timings

def main():
    parser = argparse.ArgumentParser(description='Convert HTML-style Japanese subtitles to Aegisub ASS format')
    parser.add_argument('srt_file', help='Input SRT file for timings')
    parser.add_argument('json_file', help='Input JSON file containing subtitle content')
    parser.add_argument('output_file', help='Output ASS file')
    parser.add_argument('--font', default='Arial', help='Font name to use')
    parser.add_argument('--font-size', type=int, default=48, help='Main font size')
    parser.add_argument('--ruby-size', type=int, default=24, help='Ruby text font size')
    parser.add_argument('--vertical-margin', type=int, default=50, help='Vertical margin for placement')

    args = parser.parse_args()

    converter = SubtitleConverter(args.font, args.font_size, args.ruby_size, args.vertical_margin)
    converter.process_subtitles_file(args.srt_file, args.json_file, args.output_file)

if __name__ == "__main__":
    main()
