import json
import os

from wanakana import to_katakana
from sudachipy import Dictionary

WORD_PROPERTIES = {
    "part of speech": {
        "動詞": "verb",
        "形容詞": "adjective",
        "形状詞": "adjective",
        "連体詞": "prenominal",
        "名詞": "noun",
        "代名詞": "pronoun",
        "副詞": "adverb",
        "前置詞": "preposition",
        "接続詞": "conjunction",
        "間投詞": "interjection",
        "感動詞": "interjection",
        "助詞": "particle",
        "接尾辞": "suffix",
        "接頭辞": "prefix",
        "助動詞": "auxiliary verb",
        "助数詞": "counter",
    },
    "label": {
        "地名": "place",
        "人名": "person",
        "国": "country",
        "数詞": "numeral",
        "姓": "surname",
        "名": "given name",
    },
    "subtype": {
        # noun:
        "固有": "proper",
        "普通": "common",
        # verb:
        "自": "intransitive",
        "他": "transitive",
        # particle:
        "副": "adverbial",
        "係": "linking",
        "接続": "conjuctive",
        "終": "sentence-final",
        "準体": "phrasal",
        "格": "case marker",
        "並立": "parallel marker",
        "間投": "interjectory",
        # symbol:
        "補助": "auxiliary",
        # all:
        "文語": "literary",
    },
}

KANA_MAPPING = [
    (
        "ぁぃぅぇぉっゃゅょゎァィゥェォヵㇰヶㇱㇲッㇳㇴㇵㇶㇷㇷ゚ㇸㇹㇺャュョㇻㇼㇽㇾㇿヮ",
        "あいうえおつやゆよわアイウエオカクケシスツトヌハヒフプヘホムヤユヨラリルレロワ",
    ),
    (
        "がぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽ",
        "かきくけこさしすせそたちつてとはひふへほはひふへほ",
    ),
]
KANA_MAPPING.append(tuple(map(to_katakana, KANA_MAPPING[-1])))

# LOAD DICTIONARIES:

DICTIONARY = {}
DIRECTORY = "dictionaries"
for json_file in os.listdir(DIRECTORY):
    path = os.path.join(DIRECTORY, json_file)
    with open(path, encoding="utf-8-sig") as file:
        DICTIONARY[json_file.split('.')[0]] = json.load(file)

# CREATE TOKENIZER:

TOKENIZER = Dictionary().create()
# max size of a string in bytes in utf-8 that sydachipy tokenizer accepts:
TOKENIZER_MAX_TEXT_SIZE = 49149
# max possible size of a character in bytes in utf-8:
TOKENIZER_CHARACTER_SIZE = 4
# max length of a string that tokenizer can process:
BATCH_LENGTH = TOKENIZER_MAX_TEXT_SIZE // TOKENIZER_CHARACTER_SIZE
