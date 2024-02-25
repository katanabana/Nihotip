from sys import path
path.append('A:\\Programming\\Nihotip\\server')
from collections import defaultdict
import server.tokens as tokens
from sudachipy import Dictionary, SplitMode, Morpheme
from requests import get
from pprint import pprint
from wanakana import to_katakana
import random
import os


def get_description(feature):
    feature = feature.split('-')[0]
    if feature in tokens.PARTS_OF_SPEECH:
        return tokens.PARTS_OF_SPEECH[feature]
    for property, description in tokens.PROPERTIES.items():
        if feature.startswith(property):
            if feature[len(property):] in tokens.PARTS_OF_SPEECH:
                return description
    for dictionary in (tokens.STEM_FORMS, tokens.GROUPS_OF_VERBS, tokens.NER_LABELS, tokens.PUNCTUATION, tokens.DISCOURSE_MARKERS):
        if feature in dictionary:
            return dictionary[feature]


def get_random_kana_string(length=20):
    small_kana = 'ぁぃぅぇぉっゃゅょゎァィゥェォヵㇰヶㇱㇲッㇳㇴㇵㇶㇷㇷ゚ㇸㇹㇺャュョㇻㇼㇽㇾㇿヮ'
    big_hiragana = 'あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん'
    possible_characters = small_kana + big_hiragana + to_katakana(big_hiragana)
    string = ''
    for _ in range(length):
        string += random.choice(possible_characters)
    return string

def tokenize(tokenizer, text, level='C', padding=5) -> list[Morpheme]:
    max_size = 49149  # max size of a string in bytes in utf-8 that sydachipy tokenizer accepts
    char_size = 4  # max possible size of a character in bytes in utf-8
    batch_length = max_size // char_size
    text_length = len(text)
    batch_start = 0
    tokens = []
    mode = 'C' if level == 'D' else level
    split_mode = getattr(SplitMode, mode)
    while batch_start < text_length:
        batch_text = text[batch_start:batch_start + batch_length]
        batch_tokens = list(tokenizer.tokenize(batch_text, split_mode))
        batch_start += batch_length

        if batch_start < text_length:  # apply padding only if it's not the end of the text
            for token in batch_tokens[-padding:]:
                batch_start -= len(token.surface())
            batch_tokens = batch_tokens[:-padding]

        tokens.extend(batch_tokens)
    return tokens


if __name__ == '__main__':
    tokenizer = Dictionary().create()
    with open(os.path.join(os.path.dirname(__file__), 'text_example.txt'), encoding="utf-8") as file:
        text = file.read()
    text += get_random_kana_string(50)
    features = [set() for _ in range(6)]
    col_length = 0
    with_dashes = defaultdict(set)

    test = set()
    test1 = defaultdict(list)
    for mode in 'ABC':
        for token in tokenize(tokenizer, text, mode):
            for i, feature in enumerate(token.part_of_speech()):

                if feature in ['サ変可能', '非自立可能', '副詞可能', '助数詞可能', '形状詞可能', 'サ変形状詞可能']:
                    test.add((token.surface(), token.part_of_speech()))

                if feature.endswith('的'):
                    for f in token.part_of_speech():
                        if f in tokens.PARTS_OF_SPEECH:
                            test1[feature].append(f)

                if feature == '*':
                    continue

                if '-' in feature:
                    feature, *after = feature.split('-')
                    with_dashes[feature].add(' : '.join(after))

                if get_description(feature) is None:
                    features[i].add(feature)
                    col_length = max(col_length, len(feature) + 1)

    all_possible = set(
        (feature for feature_set in features for feature in feature_set))
    formatted_all_possible = []
    for feature in all_possible:
        respective_part_of_speech = ''
        for part_of_speech in tokens.PARTS_OF_SPEECH:
            if feature.endswith(part_of_speech):
                if len(respective_part_of_speech) < len(part_of_speech):
                    respective_part_of_speech = part_of_speech
        if respective_part_of_speech:
            n = len(respective_part_of_speech)
            feature = feature[:-n] + ' (' + feature[-n:] + ')'
        formatted_all_possible.append(feature)
    all_possible = sorted(formatted_all_possible, key=lambda x: x[::-1])
    print(len(all_possible), 'from', sum(map(len, features)))
    for feature in all_possible:
        print(feature, [i for i in range(
            len(features)) if feature in features[i]])

    print()

    for feature, values in sorted(with_dashes.items(), key=lambda key_and_value: key_and_value[0][::-1]):
        print(feature, ':', ', '.join(values))

    print()
    p_to_f = defaultdict(list)
    for i in test:
        for f in i[1]:
            if f.endswith('可能'):
                p_to_f[i[1][0]].append(f)
    for k, v in p_to_f.items():
        print(k, set(v), [v.count(i) for i in set(v)])

    print()
    for k, v in test1.items():
        print(k, set(v), len(v))
