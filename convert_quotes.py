import sys
import json
import os

def convert_quotes(input_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        content = file.read()

    # Replace double quotes with single quotes and split by newline
    converted_content = content.replace("\"", "'").split("\n")

    # Save the converted content to a new JSON file
    output_file = os.path.splitext(input_file)[0] + '_converted.json'
    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(converted_content, json_file, indent=4, ensure_ascii=False)

    print(f"Converted file saved as {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python convert_quotes.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    try:
        convert_quotes(input_file)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
