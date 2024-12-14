import json
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import re


class ImageSubtitleCreator:
    def __init__(self, font_name, font_size, ruby_size, vertical_margin, text_color, stroke_color, stroke_width, output_dir):
        self.font_name = font_name
        self.font_size = font_size
        self.ruby_size = ruby_size
        self.vertical_margin = vertical_margin
        self.text_color = text_color
        self.stroke_color = stroke_color
        self.stroke_width = stroke_width
        self.output_dir = output_dir

    def render_sentence_image(self, kanji_ruby_pairs, index):
        """Render a single image with kanji and ruby for the entire sentence."""
        # Load fonts
        font_path = f"{self.font_name}.ttf"
        font_kanji = ImageFont.truetype(font_path, self.font_size)
        font_ruby = ImageFont.truetype(font_path, self.ruby_size)

        # Calculate image dimensions
        width, height = 1920, 1080
        image = Image.new("RGBA", (width, height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)

        # Calculate total sentence width to center horizontally
        x_offset = 50  # Starting x-position
        line_width = 0
        line_height = self.font_size + self.ruby_size + 10  # Combined height for ruby and kanji
        for pair in kanji_ruby_pairs:
            kanji = pair["kanji"]
            kanji_width, _ = draw.textbbox((0, 0), kanji, font=font_kanji)[2:4]
            line_width += kanji_width + 20  # Add spacing between characters

        x_start = (width - line_width) // 2  # Center horizontally
        y_offset = height - self.vertical_margin  # Vertical alignment

        # Render each kanji-ruby pair sequentially
        for pair in kanji_ruby_pairs:
            kanji = pair["kanji"]
            ruby = pair["ruby"]

            # Measure text sizes
            ruby_width, ruby_height = draw.textbbox((0, 0), ruby, font=font_ruby)[2:4]
            kanji_width, kanji_height = draw.textbbox((0, 0), kanji, font=font_kanji)[2:4]

            # Adjust horizontal alignment for ruby
            ruby_x = x_start + (kanji_width - ruby_width) / 2

            # Draw ruby above kanji
            draw.text((ruby_x, y_offset - ruby_height), ruby, fill=self.text_color, font=font_ruby,
                    stroke_width=self.stroke_width, stroke_fill=self.stroke_color)
            # Draw kanji below ruby
            draw.text((x_start, y_offset), kanji, fill=self.text_color, font=font_kanji,
                    stroke_width=self.stroke_width, stroke_fill=self.stroke_color)

            # Move x_start for the next kanji-ruby pair
            x_start += kanji_width + 20  # Add spacing between characters

        # Save the image
        output_path = os.path.join(self.output_dir, f"sentence_{index + 1}.png")
        image.save(output_path)
        print(f"Saved: {output_path}")
        return output_path

    def generate_images(self, parsed_data):
        """Generate images for each sentence in the parsed data."""
        image_paths = []
        for index, sentence in enumerate(parsed_data):
            kanji_ruby_pairs = sentence["kanji_ruby_pairs"]
            image_path = self.render_sentence_image(kanji_ruby_pairs, index)
            image_paths.append(image_path)
        return image_paths


def parse_json(input_data):
    """Parse the JSON input into a list of sentences with kanji and ruby components."""
    parsed_data = []
    ruby_pattern = re.compile(r"<ruby>(.*?)<rt>(.*?)</rt></ruby>")

    for html in input_data:
        kanji_ruby_pairs = []
        # Split into terms while preserving order
        terms = re.split(r"(<ruby>.*?</ruby>)", html)

        for term in terms:
            if ruby_pattern.match(term):
                # Extract kanji and ruby
                kanji, ruby = ruby_pattern.findall(term)[0]
                kanji_ruby_pairs.append({"kanji": kanji.strip(), "ruby": ruby.strip()})
            else:
                # Plain text outside ruby tags
                plain_text = re.sub(r"<.*?>", "", term).strip()  # Remove any stray HTML tags
                if plain_text:
                    kanji_ruby_pairs.append({"kanji": plain_text, "ruby": ""})

        parsed_data.append({"kanji_ruby_pairs": kanji_ruby_pairs})
    return parsed_data



def process_subtitles(input_json, output_dir, font_name, font_size, ruby_size, vertical_margin, text_color, stroke_color, stroke_width):
    """Process subtitles and create images."""
    with open(input_json, 'r', encoding='utf-8') as f:
        input_data = json.load(f)

    parsed_data = parse_json(input_data)

    creator = ImageSubtitleCreator(
        font_name, font_size, ruby_size, vertical_margin, text_color, stroke_color, stroke_width, output_dir
    )
    image_paths = creator.generate_images(parsed_data)
    return image_paths


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Render furigana subtitles as images.")
    parser.add_argument("input_json", help="Path to the input JSON file.")
    parser.add_argument("output_dir", help="Path to the output directory.")
    parser.add_argument("--font", required=True, help="Font name (without extension).")
    parser.add_argument("--font-size", type=int, default=48, help="Font size for kanji.")
    parser.add_argument("--ruby-size", type=int, default=24, help="Font size for ruby text.")
    parser.add_argument("--vertical-margin", type=int, default=100, help="Vertical margin for the text.")
    parser.add_argument("--text-color", default="black", help="Color of the text.")
    parser.add_argument("--stroke-color", default="white", help="Color of the stroke.")
    parser.add_argument("--stroke-width", type=int, default=2, help="Width of the stroke.")
    args = parser.parse_args()

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    # Process subtitles
    process_subtitles(
        args.input_json,
        args.output_dir,
        args.font,
        args.font_size,
        args.ruby_size,
        args.vertical_margin,
        args.text_color,
        args.stroke_color,
        args.stroke_width
    )


if __name__ == "__main__":
    main()
