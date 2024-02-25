from collections import defaultdict
import json
import os

import distinctipy
from wanakana import is_hiragana, is_katakana, is_kanji

# TOKEN FEATURES:

PARTS_OF_SPEECH = {
    '動詞': 'verb',
    '形容詞': 'adjective',
    '形状詞': 'adjective',
    '連体詞': 'prenominals',
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
    '記号': 'symbol',
    '助数詞': 'counter',
}


NER_LABELS = {
    '地名': 'place',
    '人名': 'person',
    '国': 'country',
    '数詞': 'numeral',
    '姓': 'surname',
    '名': 'given name'
}

PROPERTIES = {
    # noun:
    '固有': 'proper',
    '普通': 'common',
    # verb:
    '自': 'intransitive',
    '他': 'transitive',
    # particle:
    '副': 'adverbial',
    '係': 'linking',
    '接続': 'conjuctive',
    '終': 'sentence-final',
    '準体': 'phrasal',
    '格': 'case marker',
    '並立': 'parallel marker',
    '間投': 'interjectory',
    # symbol:
    '補助': 'auxiliary',
    # all:
    '文語': 'literary'
}

# LOAD DICTIONARIES:

DICTIONARY = defaultdict(list)
DIRECTORY = 'dictionaries'
previous_directory = os.curdir
os.chdir(os.path.dirname(__file__))
for subdirectory in os.listdir(DIRECTORY):
    for filename in os.listdir(os.path.join(DIRECTORY, subdirectory)):
        path = os.path.join(DIRECTORY, subdirectory, filename)
        with open(path, encoding='utf-8-sig') as file:
            DICTIONARY[subdirectory].extend(json.load(file))
os.chdir(previous_directory)

# COLORS:


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


# WRITING SYSTEMS:

WRITING_SYSTEMS = (is_hiragana, is_katakana, is_kanji)


def get_system_name(function):
    return function.__name__.split('_')[1]


def get_writing_system(text):
    for function in WRITING_SYSTEMS:
        if function(text):
            return get_system_name(function)
