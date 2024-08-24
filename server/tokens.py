# Import necessary functions from wanakana for Japanese text processing
from wanakana import to_hiragana, to_romaji, is_kana, is_kanji, is_katakana, is_hiragana, is_japanese
# Import necessary functions and classes from sudachipy for morphological analysis
from sudachipy import SplitMode, Morpheme

# Import custom utility functions and constants
from utils import DICTIONARY, TOKENIZER, WORD_PROPERTIES, KANA_MAPPING, BATCH_LENGTH


def combine_levels(token_dict: dict):
    """
    Recursively combine subtokens into a single token dictionary.

    Parameters:
    - token_dict (dict): The token dictionary to combine.

    Returns:
    - None
    """
    subtokens = token_dict.get('subtokens')
    if subtokens is None or len(subtokens) > 1:
        return
    token_dict.pop('subtokens')
    token_dict.update(subtokens[0])
    combine_levels(token_dict)


def token(text, subtokens: list = False, **features) -> dict:
    """
    Create a token dictionary with specified features.

    Parameters:
    - text (str): The text for the token.
    - subtokens (list): A list of subtokens (default is False).
    - **features: Additional features for the token.

    Returns:
    - dict: A dictionary representing the token.
    """
    data = {'text': text}
    if subtokens:
        data['subtokens'] = subtokens
    for key, value in features.items():
        if value is not None:
            data[key] = value
    combine_levels(data)
    return data


def get_character(character, previous=None):
    """
    Get the character token with its features, such as writing system and romaji.

    Parameters:
    - character (str): The character to analyze.
    - previous (str): The previous character (default is None).

    Returns:
    - dict: A dictionary representing the character token.
    """
    step = 1 if is_katakana(previous) else -1
    features = {}
    for is_system in [is_katakana, is_hiragana][::step]:
        if is_system(character):
            system = is_system
            features['romaji'] = to_romaji(character)
            break
    else:
        system = is_kanji
    features['writing system'] = system.__name__[3:]
    return token(character, **features)


def get_characters(string):
    """
    Get a list of character tokens from a given string.

    Parameters:
    - string (str): The string to analyze.

    Returns:
    - list: A list of dictionaries representing character tokens.
    """
    characters = []
    for i, symbol in enumerate(string):
        character = get_character(symbol, string[i - 1] if i else None)
        for modified_kana, initial_kana in KANA_MAPPING:
            index = modified_kana.find(symbol)
            if index != -1:
                character['initial'] = get_character(initial_kana[index])
                break
        characters.append(character)
    return characters


def append_digraph_or_single(subtokens, kana_string, i):
    """
    Append a digraph or single kana character to the subtokens list.

    Parameters:
    - subtokens (list): The list of subtokens to append to.
    - kana_string (str): The string containing kana characters.
    - i (int): The current index in the kana string.

    Returns:
    - list: The updated list of subtokens.
    """
    kwargs = {}
    if kana_string[i:i + 2] in DICTIONARY['digraphs']:
        subtoken_text = kana_string[i:i + 2]
        kwargs['note'] = 'digraph'
    else:
        subtoken_text = kana_string[i]
    subtokens.append(
        token(subtoken_text, get_characters(subtoken_text), **kwargs))
    return subtokens


def append_not_japanese_word(tokens, text):
    """
    Append non-Japanese text to the tokens list.

    Parameters:
    - tokens (list): The list of tokens to append to.
    - text (str): The non-Japanese text to append.

    Returns:
    - None
    """
    if tokens and isinstance(tokens[-1], str):
        tokens[-1] += text
    else:
        tokens.append(text)


def get_syllables(kana_string):
    """
    Get a list of syllable tokens from a kana string.

    Parameters:
    - kana_string (str): The string containing kana characters.

    Returns:
    - list: A list of dictionaries representing syllable tokens.
    """
    syllables = []
    i = 0
    total_length = len(kana_string)
    while i < total_length:

        subtokens = append_digraph_or_single([], kana_string, i)
        text = subtokens[-1]['text']
        i += len(text)

        if text in 'っッ' and i < total_length:
            subtokens[-1].pop('romaji')
            subtokens[-1]['note'] = 'doubles the consonant after'
            append_digraph_or_single(subtokens, kana_string, i)
            text += subtokens[-1]['text']
            i += len(text)

        if kana_string[i:i + 1] == 'ー':
            note = 'prolongs the vowel before'
            subtokens.append(token('ー', get_characters('ー'), note=note))
            subtokens[-1].pop('romaji')
            i += 1
            text += 'ー'

        if is_japanese(text):
            romaji = to_romaji(text)
            # wanakana.to_romaji:
            # 1) converts ー to - => - should be replaced with the preceding sound
            romaji = romaji.replace('-', romaji[-2:-1])
            # 2) doesn't modify romaji of ん and ン depending on the sound after => it should be changed manually
            if text in ['ん', 'ン']:
                if i < total_length - 1:
                    next_sound = to_romaji(kana_string[i])[0]
                    if next_sound in 'bpm':
                        romaji = 'm'
                    elif next_sound in 'kg':
                        romaji = 'ng'
                romaji = token(
                    romaji, note='pronunciation depends on the sound after')

            syllables.append(token(text, subtokens, romaji=romaji))
        else:
            append_not_japanese_word(syllables, text)
    return syllables


def get_unambiguous_parts(surface, reading):
    """
    Get unambiguous parts from the surface and reading strings.

    Parameters:
    - surface (str): The surface string.
    - reading (str): The reading string.

    Returns:
    - list: A list of tuples containing unambiguous parts of the surface and reading strings.
    """
    start_length = 0
    for character in surface:
        if is_kana(character):
            start_length += 1
        else:
            break

    parts = [[surface[:start_length], reading[:start_length]]]
    if start_length != len(surface):
        end_length = 0
        for character in surface[::-1]:
            if is_kana(character):
                end_length += 1
            else:
                break

        surface_middle = surface[start_length:-end_length]
        reading_middle = reading[start_length:-end_length]

        for surface_i, character in enumerate(surface_middle[1:-1]):
            if is_kana(character) and reading_middle[1:-1].count(character) == 1:
                reading_i = reading_middle[1:-1].find(character)
                start = get_unambiguous_parts(
                    surface_middle[:surface_i + 1], reading_middle[:reading_i + 1])
                end = get_unambiguous_parts(
                    surface_middle[surface_i + 2:], reading_middle[reading_i + 2:])

                parts.extend(start)
                if is_kana(start[-1][0]):
                    start[-1][0] += character
                    start[-1][1] += character
                else:
                    parts.append((character, character))
                first = 0
                if is_kana(end[0][0]):
                    parts[-1][0] += end[0][0]
                    parts[-1][1] += end[0][1]
                    first = 1
                parts.extend(end[first:])
                break
        else:
            parts.append((surface_middle, reading_middle))
        parts.append((surface[-end_length:], reading[-end_length:]))
    return [i for i in parts if i[0]]


def get_parts(morpheme: Morpheme):
    """
    Get the best subdivision of a morpheme using SudachiPy and JmFurigana dictionaries.

    Parameters:
    - morpheme (Morpheme): The morpheme to process.

    Returns:
    - list: A list of tokens representing the best subdivision of the morpheme.
    """
    parts = []
    # Split the morpheme using SudachiPy's SplitMode.A
    for submorpheme in morpheme.split(SplitMode.A):
        reading = submorpheme.reading_form()
        subparts = get_unambiguous_parts(submorpheme.surface(), reading)
        # Combine consecutive kana parts
        if parts and is_kana(parts[-1][0]) and is_kana(subparts[0][0]):
            last_surface = parts[-1][0] + subparts[0][0]
            last_reading = parts[-1][1] + subparts[0][1]
            parts[-1] = last_surface, last_reading
            subparts = subparts[1:]
        parts.extend(subparts)

    # Check for furigana parts in JmFurigana dictionary
    key = morpheme.surface(), morpheme.reading_form()
    jmdict_parts = DICTIONARY['furigana'].get(str(key))

    # Use JmFurigana parts if they are more detailed
    if jmdict_parts and len(jmdict_parts) > len(parts):
        parts = jmdict_parts

    tokens = []
    for text, reading in parts:
        if not is_katakana(text):
            reading = to_hiragana(reading)
        subtokens = get_syllables(reading)
        if reading == text:
            tokens.extend(subtokens)
        else:
            characters = get_characters(text)
            part = token(text, subtokens=characters, reading=subtokens)
            tokens.append(part)
    return tokens


def get_word(morpheme):
    """
    Get a word token with its properties from a morpheme.

    Parameters:
    - morpheme (Morpheme): The morpheme to process.

    Returns:
    - dict: A dictionary representing the word token.
    """
    features = set()
    for feature in morpheme.part_of_speech():
        feature = feature.split('-')[0]
        # Extract subtype from feature if present
        for subtype, translation in WORD_PROPERTIES['subtype'].items():
            if feature.endswith(subtype):
                feature = feature[len(subtype):]
                features.add(subtype)
        features.add(feature)

    properties = {}
    # Map features to their translations in WORD_PROPERTIES
    for feature in features:
        for name, features_to_translations in WORD_PROPERTIES.items():
            translation = features_to_translations.get(feature)
            if translation:
                properties[name] = translation

    subtokens = get_parts(morpheme)
    part_of_speech = 'particle'
    if properties.get('part of speech') == part_of_speech:
        # Adjust romaji for certain particles
        for kana, correct_romaji in [('は', 'wa'), ('を', 'o')]:
            if morpheme.surface() == kana:
                initial_romaji = subtokens[0]['romaji']
                note = f'{kana} pronounced as "{correct_romaji}" when a {part_of_speech}, otherwise as "{initial_romaji}"'
                subtokens[0]['romaji'] = token(correct_romaji, note=note)

    return token(morpheme.surface(), subtokens, **properties)


def handle_final_ng(tokens):
    """
    Adjust the romaji for the final 'ん' or 'ン' character in tokens.

    Parameters:
    - tokens (list): The list of tokens to adjust.

    Returns:
    - None
    """
    if tokens:
        last_token = tokens[-1]
        if isinstance(last_token, dict) and last_token['text'][-1] in ['ん', 'ン']:
            while 'romaji' not in last_token:
                last_token = last_token['subtokens'][-1]
            note = '"ん" and "ン" are pronounced differently (have "ng" romaji) at the end of a phrase'
            last_token['romaji'] = token('ng', note=note)


def tokenize(text, padding=5):
    """
    Tokenize a given text into a list of tokens, handling both Japanese and non-Japanese parts.

    Parameters:
    - text (str): The text to tokenize.
    - padding (int): The padding length for batch processing (default is 5).

    Returns:
    - list: A list of tokens representing the tokenized text.
    """
    tokens = []
    text_length = len(text)
    batch_start = 0

    while batch_start < text_length:
        words = []

        # Process text in batches
        batch = text[batch_start:batch_start + BATCH_LENGTH]
        morphemes = list(TOKENIZER.tokenize(batch))
        batch_start += BATCH_LENGTH
        if batch_start < text_length:  # Apply padding only if it's not the end of the text
            for morpheme in morphemes[-padding:]:
                batch_start -= len(morpheme.surface())
            morphemes = morphemes[:-padding]

        for morpheme in morphemes:
            # Check if morpheme contains at least one kana or kanji character
            for character in morpheme.surface():
                if is_kana(character) or is_kanji(character):
                    word = get_word(morpheme)
                    tokens.append(word)
                    if 'part of speech' in word:
                        words.append(word)
                    break
            else:
                # Handle non-Japanese text and adjust final 'ng' pronunciation if necessary
                handle_final_ng(tokens)
                append_not_japanese_word(tokens, morpheme.surface())

    handle_final_ng(tokens)
    return tokens
