from sudachipy import Dictionary, SplitMode
from features_of_tokens import get_description, tokenize
import os
os.chdir(os.path.dirname(__file__))
with open(os.path.realpath('text_example.txt'), encoding='utf-8') as file:
    text = file.read()
tokenizer = Dictionary().create()


tokens = tokenize(tokenizer, text, 'B')
answers = set()
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
for token in tokens:
    subtokens = token.split(SplitMode.A)
    features = set(token.part_of_speech())
    for subtoken in subtokens:
        for subfeature in subtoken.part_of_speech():
            if subfeature not in features:
                descriptions = set()
                for i in subtoken.part_of_speech():
                    if i != '*':
                        description = get_description(i) if get_description(i) is not None else i
                    description = description[0] if type(description) is tuple else description
                    if i not in features:
                        description = '[' + description + ']'
                    descriptions.add(description)
                answers.add(tuple(descriptions))
for i in answers:
    print(*i)