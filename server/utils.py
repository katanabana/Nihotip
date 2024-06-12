import json
import os

from wanakana import to_hiragana
from sudachipy import Dictionary
from g4f.client import Client


WORD_PROPERTIES = {
    'part of speech': {
        '動詞': 'verb',
        '形容詞': 'adjective',
        '形状詞': 'adjective',
        '連体詞': 'prenominal',
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
        '助数詞': 'counter',
    },
    'label': {
        '地名': 'place',
        '人名': 'person',
        '国': 'country',
        '数詞': 'numeral',
        '姓': 'surname',
        '名': 'given name'
    },
    'subtype': {
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
}

KANA_MAPPING = [
    (lambda kana: kana, 'ぁぃぅぇぉっゃゅょゎァィゥェォヵㇰヶㇱㇲッㇳㇴㇵㇶㇷㇷ゚ㇸㇹㇺャュョㇻㇼㇽㇾㇿヮ',
     'あいうえおつやゆよわアイウエオカクケシスツトヌハヒフプヘホムヤユヨラリルレロワ'),
    (to_hiragana, 'がぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽ', 'かきくけこさしすせそたちつてとはひふへほはひふへほ')
]


# LOAD DICTIONARIES:

DICTIONARY = {}
DIRECTORY = 'dictionaries'
previous_directory = os.curdir
os.chdir(os.path.dirname(__file__))
for subdirectory in os.listdir(DIRECTORY):
    for filename in os.listdir(os.path.join(DIRECTORY, subdirectory)):
        path = os.path.join(DIRECTORY, subdirectory, filename)
        with open(path, encoding='utf-8-sig') as file:
            data = json.load(file)
            methods = {list: 'extend', dict: 'update'}
            method = methods[type(data)]
            if subdirectory not in DICTIONARY:
                DICTIONARY[subdirectory] = type(data)()
            add = getattr(DICTIONARY[subdirectory], method)
            add(data)
os.chdir(previous_directory)

# CREATE TOKENIZER:

TOKENIZER = Dictionary().create()
# max size of a string in bytes in utf-8 that sydachipy tokenizer accepts:
TOKENIZER_MAX_TEXT_SIZE = 49149
# max possible size of a character in bytes in utf-8:
TOKENIZER_CHARACTER_SIZE = 4
# max length of a string that tokenizer can process:
TOKENIZER_MAX_TEXT_LENGTH = TOKENIZER_MAX_TEXT_SIZE // TOKENIZER_CHARACTER_SIZE


# GPT:

def get_gpt_answer(question):
    client = Client()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": question}]
    )
    return response.choices[0].message.content


GPT_MAX_QUERY_LENGTH = 100000

# OTHER:

BATCH_LENGTH = min(TOKENIZER_MAX_TEXT_LENGTH, GPT_MAX_QUERY_LENGTH)
