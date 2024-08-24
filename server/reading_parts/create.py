import os
import json
import sys
from wanakana import to_katakana


def main():
    # Retrieve initial_directory and transformed_directory from command-line arguments
    initial_directory, transformed_directory = sys.argv[1:3]
    encoding = 'utf-8-sig'  # Specify UTF-8 encoding with BOM (Byte Order Mark)

    # Iterate through files in initial_directory
    for filename in os.listdir(initial_directory):
        # Construct paths for initial and transformed files
        initial_path = os.path.join(initial_directory, filename)
        transformed_filename = filename.replace('.', '_transformed.')
        transformed_path = os.path.join(transformed_directory, transformed_filename)

        # Print information about current transformation process
        for line in ['', 'transforming', initial_path, 'to', transformed_path]:
            print(line)

        # Load initial JSON dictionary file
        with open(initial_path, encoding=encoding) as initial_file:
            initial_dictionary = json.load(initial_file)

        transformed_dictionary = {}

        # Process each item in the initial dictionary
        for item in initial_dictionary:
            # Create a key combining text and its reading transformed to katakana
            key = str((item['text'], to_katakana(item['reading'])))
            parts = []

            # Process furigana parts in each item
            for part in item['furigana']:
                reading = part.get('rt', part['ruby'])  # Use 'rt' if available, else 'ruby'
                part = [part['ruby'], to_katakana(reading)]  # Transform part reading to katakana
                parts.append(part)

            # Choose parts with the maximum length for the same key
            if key not in transformed_dictionary or len(transformed_dictionary[key]) < len(parts):
                transformed_dictionary[key] = parts

        # Write transformed dictionary to a new JSON file
        with open(transformed_path, 'w+', encoding=encoding) as transformed_file:
            json.dump(transformed_dictionary, transformed_file, ensure_ascii=False)


if __name__ == '__main__':
    main()
