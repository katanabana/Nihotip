## Logic

### Nihotip uses a special system of splitting the text tokens and their properties into levels:

- text # 
    - not a japanese word # 
        - punctuation
        - spaces
        - line breaks
        - string of not japanese characters
    - japanese word (part of speech) # 
        - big morpheme # 
            - small morpheme # 
                - **part by reading**
                    - one or multiple kanji (kana reading -> **part by reading**) # 
                    - digraph # 
                        - **big kana without tenten** # 
                        - **big kana with tenten** # 
                        - small kana (*respective* **big kana**) # 
                    - **kana without tenten** (romaji, association) # 
                    - **kana with tenten** (*respective* **kana without tenten**) # 

- **part by reading:**

    *Parts are gotten by cutting the reading of the word. They allow to determine the kana reading for each kanji. A part consists of multiple characters if the reading of a kanji along with the characters surrounding it can't be cut. For example, the part "大人" of the word "大人買い" uses a special reading "おとな" that can't be cut. That's why the "おとな" reading applies to the whole part.*

- **syllable:**

    Syllable can be either a single kana, digraph, kana with "っ" or "ー" and sometimes a single kanji.

## To Do:
* pros and cons of grouping the tags by levels of tokens? what should the color mean? is it needed? what are tags?
* add named entity recognition
* add possibility to choose language of tips (if japanese, create tips for tips)
* normalization of words
* understand the features of SudachiPy tokens
* add notes for words that can belong to several parts of speech or several subtypes within one part of speech (example: Note that some particles appear in two types. For example, kara is called a "case marker" where it describes where something is from or what happens after something; when it describes a cause it is called a "conjunctive particle".)
* add notes for individual particles (source: https://en.wikipedia.org/wiki/Japanese_particles)
* handle n pronunciation at the end of phrases
* hadle difference between pronunciations provided by SudachiPy and JmFurigana
* don't create a new tokenizer for each tokenization to improve the performance

## Thoughts:
* **Understanding SudachiPy**:
    * Possible values returned by `token.part_of_speech()` are the same for every split mode.
* **Splitting a word**:
    * sometimes SudachiPy smallest morphemes can be splitted into parts by reading with JmFurigana
    * sometimes a furigana part can be splitted further with SudachiPy if it consists of more than one morpheme
    * the word should be splitted using both JmdictFurigana and SudachiPy to get the smallest possible reading parts
* **Combining JmFurigana and SudachiPy**:

    JmdictFurigana contains readings written in both katakana and hiragana and sometimes even mixes them within one word. It also contains 3 entries containing non kana characters. They can be gotten by running the following code:
    ```
    from utils import DICTIONARY
    from wanakana import is_mixed, is_kana
    for item in DICTIONARY['furigana']:
        reading = item['reading']
        if not is_kana(reading) or is_mixed(reading):
            parts = item['furigana']
            reading_parts = [part.get('rt', part['ruby']) for part in parts]
            surface_parts = [part['ruby'] for part in parts]
            for line in (item['text'], reading, reading_parts, surface_parts, ''):
                print(line)
    ```
    ```
    死ぬ
    ﾀﾋぬ
    ['ﾀﾋ', 'ぬ']
    ['死', 'ぬ']

    わたし、定時で帰ります。
    わたし、ていじでかえります。
    ['わたし、', 'てい', 'じ', 'で', 'かえ', 'ります。']
    ['わたし、', '定', '時', 'で', '帰', 'ります。']

    わたし、定時で帰ります。
    わたし、ていじでかえります。
    ['わたし、', 'てい', 'じ', 'で', 'かえ', 'ります。']
    ['わたし、', '定', '時', 'で', '帰', 'ります。']
    ```
    On the other hand, SudachiPy provides only katakana readings.