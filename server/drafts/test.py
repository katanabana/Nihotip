from sys import path
path.append('A:\\Programming\\Nihotip\\server')
from wanakana import is_mixed, is_kana, is_katakana, is_kanji, is_hiragana, to_katakana
from collections import defaultdict
from utils import DICTIONARY
# from sudachipy import Dictionary, SplitMode
# from features_of_tokens import get_description, tokenize
# import os
# os.chdir(os.path.dirname(__file__))
# with open(os.path.realpath('text_example.txt'), encoding='utf-8') as file:
#     text = file.read()
# tokenizer = Dictionary().create()


answers = set()

# tokens = tokenize(tokenizer, text)
# for token in tokens:
#     subtokens = token.split(SplitMode.A)
#     features = set(token.part_of_speech())
#     for subtoken in subtokens:
#         for subfeature in subtoken.part_of_speech():
#             if subfeature not in features:
#                 descriptions = set()
#                 for i in subtoken.part_of_speech():
#                     if i != '*':
#                         description = get_description(i) if get_description(i) is not None else i
#                     description = description[0] if type(description) is tuple else description
#                     if i not in features:
#                         description = '[' + description + ']'
#                     descriptions.add(description)
#                 answers.add(tuple(descriptions))


# tokens = tokenize(tokenizer, text, SplitMode.B)
# for token in tokens:
#     subtokens = token.split(SplitMode.A)
#     features = set(token.part_of_speech())
#     for subtoken in subtokens:
#         for subfeature in subtoken.part_of_speech():
#             if subfeature not in features:
#                 descriptions = set()
#                 for i in subtoken.part_of_speech():
#                     if i != '*':
#                         description = get_description(i) if get_description(i) is not None else i
#                     description = description[0] if type(description) is tuple else description
#                     if i not in features:
#                         description = '[' + description + ']'
#                     descriptions.add(description)
#                 answers.add(tuple(descriptions))


texts_to_readings = defaultdict(set)

CONDITIONS = {'text': lambda item: item['text'],
              'pronunciation': lambda item: to_katakana(item['reading'])}


def check_input(items):
    for item in items:
        for property, transform in CONDITIONS.items():
            if transform(items[0]) != transform(item):
                raise Exception(
                    f'All items should have the same {property} so their readings can be compared.')


def get_closest(items):
    check_input(items)
    closest = []
    best_score = None
    for item in items:
        score = 0
        for furigana in item['furigana']:
            if 'rt' in item:
                for i, j in zip(furigana['ruby'], item['rt']):
                    if i != j:
                        score += 1
        if best_score is None or best_score > score:
            best_score = score
            closest = [item]
        elif best_score == score:
            closest.append(item)
    return closest


def get_groups_by_pronunciations():
    keys_to_groups = defaultdict(list)
    for item in DICTIONARY['furigana']:
        key = tuple([transform(item) for transform in CONDITIONS.values()])
        keys_to_groups[key].append(item)
    groups = []
    for group in keys_to_groups.values():
        distinct = [] # items are dictionaries (unhashable) so set(items) can't be used
        for item in group:
            if item not in distinct:
                distinct.append(item)
        if len(distinct) > 1:
            groups.append(distinct)
    return groups


# for group in get_groups_by_pronunciations():
#     closest = get_closest(group)
#     readings = []
#     for item in group:
#         reading = item['reading']
#         if item in closest:
#             reading = f'[{reading}]'
#         else:
#             print(True)
#         readings.append(reading)
# items = []
from sudachipy import Dictionary, SplitMode
t = Dictionary().create()
count = 0
for item in DICTIONARY['furigana']:
    ms = t.tokenize(item['text'])
    if len(ms) > 1:
        count += 1
print(count, '/', len(DICTIONARY['furigana']))
        