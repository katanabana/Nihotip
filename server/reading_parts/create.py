import os
import json
import sys
from wanakana import to_katakana


def main():
    initial_directory, transformed_directory = sys.argv[1:3]
    encoding = 'utf-8-sig'

    for filename in os.listdir(initial_directory):

        initial_path = os.path.join(initial_directory, filename)
        transformed_filename = filename.replace('.', '_transformed.')
        transformed_path = os.path.join(
            transformed_directory, transformed_filename)
        for line in ['', 'transforming', initial_path, 'to', transformed_path]:
            print(line)

        with open(initial_path, encoding=encoding) as initial_file:
            initial_dictionary = json.load(initial_file)

        transformed_dictionary = {}
        for item in initial_dictionary:
            key = str((item['text'], to_katakana(item['reading'])))
            parts = []
            for part in item['furigana']:
                reading = part.get('rt', part['ruby'])
                part = [part['ruby'], to_katakana(reading)]
                parts.append(part)
            if key not in transformed_dictionary or len(transformed_dictionary[key]) < len(parts):
                transformed_dictionary[key] = parts

        with open(transformed_path, 'w+', encoding=encoding) as transformed_file:
            json.dump(transformed_dictionary,
                      transformed_file, ensure_ascii=False)


if __name__ == '__main__':
    main()
