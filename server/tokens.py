import MeCab
from wanakana import is_kanji, to_hiragana, to_romaji


def get_token(type, text, tokens=None, **features):
    token = {'type': type, 'text': text, **features}
    if tokens is not None:
        token['tokens'] = tokens
    return token


def get_characters(string):
    tokens = []
    for character in string:
        tokens.append(get_token('character', character,
                      writing_system=get_writing_system(character)))
    return tokens


def get_syllables(kana_string):
    syllables = []
    i = 0
    length = len(kana_string)
    while i < length:

        start = i
        if kana_string[i] in 'っッ':  # double the consonant after
            i += 1
        if kana_string[i:i + 2] in DICTIONARY['digraphs']:
            i += 1
        if kana_string[i + 1] == 'ー':  # prolongs the vowel before
            i += 1
        i += 1
        syllable_text = kana_string[start:i]

        # wanakana.to_romaji doesn't modify ん and ン pronunciations depending on the next syllable
        if syllable_text in ['ん', 'ン'] and i < length - 1:
            if kana_string[i] in 'bp':
                romaji = 'm'
            elif kana_string[i] in 'kg':
                romaji = 'ng'
            else:
                romaji = 'n'
        else:
            romaji = to_romaji(syllable_text)

        characters = get_characters(syllable_text)
        syllables.append(get_token('syllable', syllable_text,
                         characters, romaji=romaji))
    return syllables


def get_part_token_from(text_of_part, hiragana_of_part):
    syllables = get_syllables(hiragana_of_part)
    return get_token('part_of_word', text_of_part, hiragana=get_token('hiragana_for_part_of_word', hiragana_of_part, syllables))


def get_parts_by_pronunciation(word, hiragana):
    if any(map(is_kanji, word)):  # avoid unreasonable iteration through the furigana dictionary if there isn't a single kanji in the word anyway
        for item in DICTIONARY['furigana']:
            if item['text'] == word and item['reading'] == hiragana:
                parts = []
                for furigana in item['furigana']:
                    text_of_part = furigana['ruby']
                    hiragana_of_part = furigana.get('rt', text_of_part)
                    parts.append(get_part_token_from(
                        text_of_part, hiragana_of_part))
                return parts
    # if a hiragana from the furigana dictionary that matches the hiragana of the word wasn't found or there isn't a kanji in the word,
    # the word is considered inseparable into parts by pronunciation (consists of a single part)
    return [get_part_token_from(word, hiragana)]


def get_words(text):
    parser = MeCab.Tagger()
    tokens = []
    new_token_start = 0
    # two last lines of parsing result are always "EOS" and "" (blank line)
    for token_string in parser.parse(text).split('\n')[:-2]:
        token_items = token_string.split()
        # Some characters (e.g., ' ', '　', '\n') are lost during parsing.
        # To make it possible to restore the initial text from tokens,
        # the missing parts should be found:
        new_token_text = token_items[0]
        missed_token_text = ''
        while text[new_token_start] != new_token_text[0]:
            missed_token_text += text[new_token_start]
            new_token_start += 1
        if missed_token_text:
            tokens.append(get_token('not_a_word', missed_token_text))
        new_token_start += len(new_token_text)

        # check if the token is a word and　if it is, add respective info to the token dictionary:
        token = get_token('not_a_word', new_token_text)
        if len(token_items) >= 4:
            part_of_speech = PARTS_OF_SPEECH.get(token_items[4].split('-')[0])
            if part_of_speech:
                # There is only the katakana pronunciation among the token items,
                # so the hiragana pronunciation is gotten by converting the katakana one to hiragana:
                katakana = token_items[1]
                hiragana = to_hiragana(katakana)
                parts = get_parts_by_pronunciation(token['text'], hiragana)

                if part_of_speech == 'partile':
                    syllable = parts[0]['tokens'][0]
                    if token['text'] == 'は':
                        syllable['romaji'] = 'wa'
                    elif token['text'] == 'を':
                        syllable['text'] = 'o'

                token = get_token('word', new_token_text, parts,
                                  part_of_speech=part_of_speech)
        tokens.append(token)
    return tokens
