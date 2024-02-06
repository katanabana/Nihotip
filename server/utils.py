import MeCab
from wanakana import is_katakana, is_kanji, is_hiragana, is_kana, to_hiragana
import distinctipy
import random 
import json
import os
from collections import defaultdict


def to_hex(rgb):
    return "#{0:02x}{1:02x}{2:02x}".format(*rgb)


def to_rgb(floats):
    return tuple(map(lambda x: int(x * 255), floats))

def lighten(rgb):
    return tuple(map(lambda x: min(x + 100, 255), rgb))


def get_colors(n):
    float_colors = distinctipy.get_colors(n)
    rgb_colors = list(map(to_rgb, float_colors))
    lightened_colors = list(map(lighten, rgb_colors))
    hex_colors = list(map(to_hex, lightened_colors))
    return hex_colors


DICTIONARY = defaultdict(list)
directory = 'dictionaries'
for subdirectory in os.listdir(directory):
    for filename in os.listdir(os.path.join(directory, subdirectory)):
        path = os.path.join(directory, subdirectory, filename)
        with open(path, encoding='utf-8-sig') as file:
            DICTIONARY[subdirectory].extend(json.load(file))
            

PARTS_OF_SPEECH = {
    '動詞': 'verb',
    '形容詞': 'adjective',
    '形状詞': 'adjective',
    '連体詞': 'adjective',
    '名詞': 'noun',
    '代名詞': 'pronoun',
    '副詞': 'adverb',
    '前置詞': 'preposition',
    '接続詞': 'conjunction',
    '間投詞': 'interjection',
    '感動詞': 'interjection',
    '助詞': 'particle',
    '接尾辞': 'suffix',
    '接頭辞': 'prefix',
    '助動詞': 'auxiliary verb',
    '記号': 'symbol'
}


DEFINITE_WRITING_SYSTEMS = [is_hiragana, is_kanji, is_katakana]

def is_mixed(text):
    for character in text:
        for system in DEFINITE_WRITING_SYSTEMS:
            if system(character):
                break
        else:
            return False
    return True

POSSIBLE_WRITING_SYSTEMS = [*DEFINITE_WRITING_SYSTEMS, is_kana, is_mixed]


def get_system_name(function):
    return function.__name__.split('_')[1]

def get_writing_system(text):
    for function in POSSIBLE_WRITING_SYSTEMS:
        if function(text):
            return get_system_name(function)


TAGS = [*map(get_system_name, POSSIBLE_WRITING_SYSTEMS), *PARTS_OF_SPEECH.values()]
random.seed(0)
COLORS = get_colors(len(TAGS))

TAGS_TO_COLORS = {}
for tag, color in zip(TAGS, COLORS):
    TAGS_TO_COLORS[tag] = color

def get_subtoken(text, hiragana):
    return dict(text=text, hiragana=hiragana, tag=get_writing_system(text))

def get_subtokens(text, hiragana):
    if any(map(is_kanji, text)):
        for item in DICTIONARY['furigana']:
            if item['text'] == text and item['reading'] == hiragana:
                subtokens = []
                for furigana in item['furigana']:
                    subtext = furigana['ruby']
                    subhiragana = furigana.get('rt', subtext)
                    subtokens.append(get_subtoken(subtext, subhiragana))
                return subtokens
        # if a hiragana from the furigana dictionary that matches the hiragana of the word wasn't found 
        return [get_subtoken(text, hiragana)]
    length = min(map(len, [text, hiragana]))
    subtokens = []
    i = 0
    while i < length:
        subtext = text[i]
        subhiragana = hiragana[i]
        if text[i:i + 2] in DICTIONARY['digraphs']:
            subtext += text[i + 1]
            subhiragana += hiragana[i + 1]
            i += 1
        subtokens.append(get_subtoken(subtext, subhiragana))
        i += 1
    return subtokens


def get_tokens(string):
    parser = MeCab.Tagger()
    tokens = []
    for token_string in parser.parse(string).split('\n')[:-2]:
        token_items = token_string.split()
        text = token_items[0]
        token = dict(text=text)
        tokens.append(token)
        if get_writing_system(text) and text not in 'ーっッ':
            hiragana = to_hiragana(token_items[1])
            token['subtokens'] = get_subtokens(text, hiragana)
            part_of_speech = token_items[4].split('-')[0]
            token['tag'] = PARTS_OF_SPEECH.get(part_of_speech)
    return tokens