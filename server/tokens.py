import threading
from wanakana import to_hiragana, to_katakana, to_romaji, is_kana, is_kanji, is_katakana, is_hiragana, is_japanese, is_kana
from sudachipy import SplitMode, Morpheme
import json

from utils import DICTIONARY, TOKENIZER, WORD_PROPERTIES, KANA_MAPPING, get_gpt_answer, BATCH_LENGTH


def combine_levels(token: dict):
    subtokens = token.get('subtokens')
    if subtokens is None or len(subtokens) > 1:
        return
    token.pop('subtokens')
    token.update(subtokens[0])
    combine_levels(token)


def token(text, subtokens: list = False, **features) -> dict:
    data = {'text': text}
    if subtokens:
        data['subtokens'] = subtokens
    for key, value in features.items():
        if value is not None:
            data[key] = value
    combine_levels(data)
    return data


def get_character(character, previous=None):
    # if the character can be both katakana and hiragana, its system is determined by the previous character
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
    characters = []
    for i, symbol in enumerate(string):
        character = get_character(symbol, string[i - 1] if i else None)
        for transform, modified_kana, initial_kana in KANA_MAPPING:
            index = modified_kana.find(transform(symbol))
            if index != -1:
                character['initial'] = get_character(initial_kana[index])
                break
        characters.append(character)
    return characters


def append_digraph_or_single(subtokens, kana_string, i):
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
    if tokens and isinstance(tokens[-1], str):
        tokens[-1] += text
    else:
        tokens.append(text)


def get_syllables(kana_string):
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
                    romaji, note='pronuciation depends on the sound after')

            syllables.append(token(text, subtokens, romaji=romaji))
        else:
            append_not_japanese_word(text)
    return syllables


def get_unambiguous_parts(surface, reading):

    start_length = 0
    for character in surface:
        if is_kana(character):
            start_length += 1
        else:
            break

    parts = [(surface[:start_length], reading[:start_length])]
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
    # choose the best subdivision of the morheme between the ones provided by SudachiPy and from transformed JmFurigana dictionaries

    parts = []
    for submorpheme in morpheme.split(SplitMode.A):
        reading = submorpheme.reading_form()
        subparts = get_unambiguous_parts(submorpheme.surface(), reading)
        if parts and is_kana(parts[-1][0]) and is_kana(subparts[0][0]):
            last_surface = parts[-1][0] + subparts[0][0]
            last_reading = parts[-1][1] + subparts[0][1]
            parts[-1] = last_surface, last_reading
            subparts = subparts[1:]
        parts.extend(subparts)

    key = morpheme.surface(), morpheme.reading_form()
    jmdict_parts = DICTIONARY['furigana'].get(str(key))

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
    properties = set()
    for property in morpheme.part_of_speech():
        property = property.split('-')[0]
        # some features contain both part of speech and its subtype
        for subtype, translation in WORD_PROPERTIES['subtype'].items():
            if property.endswith(subtype):
                property = property[len(subtype):]
                properties.add(subtype)
        properties.add(property)

    features = {}
    for property in properties:
        for name in WORD_PROPERTIES:
            translation = WORD_PROPERTIES[name].get(property)
            if translation:
                features[name] = translation

    subtokens = get_parts(morpheme)
    # change romaji where it depends on the context:
    part_of_speech = 'particle'
    if features.get('part of speech') == part_of_speech:
        for kana, correct_romaji in [('は', 'wa'), ('を', 'o')]:
            if morpheme.surface() == kana:
                initial_romaji = subtokens[0]['romaji']
                note = f'{kana} pronounced as "{correct_romaji}" when a {part_of_speech}, otherwise as "{initial_romaji}"'
                subtokens[0]['romaji'] = token(correct_romaji, note=note)

    return token(morpheme.surface(), subtokens, **features)


def handle_final_ng(tokens):
    if tokens:
        last_token = tokens[-1]
        if isinstance(last_token, dict) and last_token['text'][-1] in ['ん', 'ン']:
            # token is a word and ends with one of the special characters
            while 'romaji' not in last_token:
                last_token = last_token['subtokens'][-1]
            note = '"ん" and "ン" are pronounced differently (have "ng" romaji) at the end of a phrase'
            last_token['romaji'] = token('ng', note=note)


def get_translation_alignment(text, words):
    array = []
    for word in words:
        array.append([word['text'], word['part of speech']])
    array_string = json.dumps(array, ensure_ascii=False)

    translation = get_gpt_answer(
        'Translate the japanese text below in english:\n' + text)

    question = '\n'.join([
        f'The japanese text "{text}"  is translated as "{translation}" in english.',
        'In the input array:',
        array_string,
        'replace part of speech with a corresponding english tranlation of the word, if it has one in the given translation of the text.',
        'For example, if the given text is "私はいい人です。", the given translation is "I am a nice person.", the given array is:',
        '[', '["私", "pronoun"]', '["は", "particle"]', '["いい", "adjective"]', '["人", "noun"]', '["です", "auxiliary verb"]', ']',
        'Then the ouput array should be:',
        '[', '["私", "I"]', '["は", null]', '["いい", "nice"]', '["人", "person"]', '["です", "am"]', ']',
        "The output array should not contain words that aren't present in the input dictionary.",
        'The output array should not contain parts of speech.'
        'The output array should contain strictly all of the words from the input array in the exact same order as in the input array.',
        f'The output array should be a proper json array with length {len(array)}.',
        'The output array should have the below format:',
        '[', '["japanese_word", ("english_translation" or null value)],', '...', ']',
        'Each item of the output array should be an array with two elements: japanese word and its translation or null value',
        'Return only json array without additional text.'
    ])
    print(question)
    answer = get_gpt_answer(question)
    for string in ['json', '```']:
        answer = answer.replace(string, '')
    answer = answer.strip()
    if answer.endswith(',\n]'):
        answer = answer[:-3] + '\n]'
    if answer.count('[') > 1:
        answer = answer[:answer.find('[\n', 1)]
        if not answer.endswith('\n]'):
            answer += '\n]'
    try:
        return json.loads(answer)
    except json.decoder.JSONDecodeError:
        print('ERROR (bad json ouput):\n' + answer)


def add_translations(text, words):
    translation_alignment = get_translation_alignment(text, words)
    if translation_alignment:
        print(len(translation_alignment), len(words))
        from pprint import pprint
        pprint(translation_alignment)
        for i, (word, (word_text, translation)) in enumerate(zip(words, translation_alignment)):
            if word['text'] == word_text:
                word['translation'] = translation
    else:
        print('ERROR')
        print(translation_alignment)


def tokenize(text, padding=5):
    tokens = []

    text_length = len(text)
    batch_start = 0

    while batch_start < text_length:
        words = []

        batch = text[batch_start:batch_start + BATCH_LENGTH]
        morphemes = list(TOKENIZER.tokenize(batch))
        batch_start += BATCH_LENGTH
        if batch_start < text_length:  # apply padding only if it's not the end of the text
            for morpheme in morphemes[-padding:]:
                batch_start -= len(morpheme.surface())
            morphemes = morphemes[:-padding]

        for morpheme in morphemes:
            # a morheme is considered japanese word if it contains at least one kana or kanji character
            for character in morpheme.surface():
                if is_kana(character) or is_kanji(character):
                    word = get_word(morpheme)
                    tokens.append(word)
                    if 'part of speech' in word:
                        words.append(word)
                    break
            else:
                # current morpheme isn't a japanese word => last token ends the japanese phrase if it's a word
                handle_final_ng(tokens)
                append_not_japanese_word(tokens, morpheme.surface())

        #add_translations(batch, words)

    handle_final_ng(tokens)
    return tokens


# tokenize("""
# ちっちゃな頃から優等生
# 気づいたら大人になっていた
# ナイフの様な思考回路
# 持ち合わせる訳もなく
# でも遊び足りない 何か足りない
# 困っちまうこれは誰かのせい
# あてもなくただ混乱するエイデイ
# それもそっか
# 最新の流行は当然の把握
# 経済の動向も通勤時チェック
# 純情な精神で入社しワーク
# 社会人じゃ当然のルールです
# はぁ？
# はぁ？ うっせぇうっせぇうっせぇわ
# あなたが思うより健康です
# 一切合切凡庸な
# あなたじゃ分からないかもね
# 嗚呼よく似合う
# その可もなく不可もないメロディー
# うっせぇうっせぇうっせぇわ
# 頭の出来が違うので問題はナシ
# つっても私模範人間
# 殴ったりするのはノーセンキュー
# だったら言葉の銃口を
# その頭に突きつけて撃てば
# マジヤバない？止まれやしない
# 不平不満垂れて成れの果て
# サディスティックに変貌する精神
# クソだりぃな
# 酒が空いたグラスあれば直ぐに注ぎなさい
# 皆がつまみ易いように串外しなさい
# 会計や注文は先陣を切る
# 不文律最低限のマナーです
# はぁ？うっせぇうっせぇうっせぇわ
# くせぇ口塞げや限界です
# 絶対絶対現代の代弁者は私やろがい
# もう見飽きたわ
# 二番煎じ言い換えのパロディ
# うっせぇうっせぇうっせぇわ
# 丸々と肉付いたその顔面にバツ
# うっせぇうっせぇうっせぇわ
# 私が俗に言う天才です
# うっせぇうっせぇうっせぇわ
# あなたが思うより健康です
# 一切合切凡庸な
# あなたじゃ分からないかもね
# 嗚呼つまらねぇ
# 何回聞かせるんだそのメモリー
# うっせぇうっせぇうっせぇわ
# アタシも大概だけど
# どうだっていいぜ問題はナシ
# 正しさとは 愚かさとは
# それが何か見せつけてやる

# 半端なら K.O. ふわふわしたいならどうぞ
# 開演準備しちゃおうか 泣いても笑っても愛してね
# ほら say no 低音響かせろ
# なんだかな ってつまんないこともあるでしょう
# ロンリー論理のノート ハンディー本気脱走
# やんなっちゃって泥に bad ご法度だろうが溺れて堕ちて ay そろそろいっか
# もっと頑張って アガるまでもっと頑張って
# 繋がろうひとりよりふたり 増えたら安心 心配ないや
# Alright 任せて don't mind
# 波あり難題 みんなで乗っかっちゃえば
# Ha 案外さくっと行っちゃいそう
# 半端なら K.O. ふわふわしたいならどうぞ
# 開演準備しちゃおうか 泣いても笑っても愛してね
# ほら say no (say no) 低音響かせろ
# 今宵は暗転パーティー
# Woah, woah 踊りだせ 踊りだせ 孤独は殺菌 満員御礼
# Woah, woah 痛みまで おシェアで ここらでバイバイ let go (ah!)
# どんな劣等感だとて 即興の血小板で
# 抑え込んで 突っ込んで 仕舞っちゃうでしょ ah yeah
# Up and down なテンション (oh)
# ねえまいっちゃってんの相当 (yeah)
# ドバっと噴き出すのは 本音の独り言
# 「別に興味ない」(ない)
# 「特に関係ない」(ないない)
# 塞ぎ込んで 舌鋒絶頂へ
# 合図を奏でて prr prr prr prr yeah
# ほら集まって夜行だ ay yeah 鳴いていこう
# パランパンパンパランランパン パンパンランパンパランパン
# パランパンパンパランランパン パラパランパンパラン
# 半端なら K.O. yeah yeah yeah yeah yeah yeah ah
# Woah, woah 踊りだせ 踊りだせ 孤独は殺菌 満員御礼
# Woah, woah 痛みまで おシェアで 今宵も暗転パーティーだ
# Woah, yeah, woah, ugh またのお越しを きっと ooh
# Woah, woah 次回までお元気で ここらでバイバイ let go
# Lyrics
# Εκ λόγου άλλος εκβαίνει λόγος
# 水面に映る自分が言った
# 「ああ わたしは悪いサメです」
# ずっと恐れていた 赤く光るその目
# 海の底 暗闇に消えていく
# どうして (Your tired eyes)
# 泣くのよ (Begin to fall)
# 欲しいものなら全部手に入れた
# 教えて (Your darkest thoughts)
# わたしは (Unleash them all)
# 望んでいたわたしになれたかな
# 嘘はつかない でも本当じゃない
# 本音は言わない方が楽じゃない？
# いつかは (A time and place)
# どこかで (For darker days)
# 分かり合える時が来るの？
# Look at this so-called "gem of the sea"
# Odd and scrawny, don't you see what I mean?
# Return to what you know, it ain't much I know
# Heh, it shows
# わたしはあなたとは違うの
# やめてよ
# 決めつけはもう大っ嫌い（大っ嫌い）
# 理想の姿じゃなくていいの
# わたしらしくあれば
# ただわかって欲しいだけよ
# Heh! 理想通りじゃなきゃ意味なんてない
# 希望も夢すらなくて
# 辛い 辛い 辛い 辛い
# あなたらしさ
# あるのかしら？
# 諦めて楽になろう
# さあ
# ずっと追い求めた わたしなりの答え
# 自分には嘘はつきたくないの
# ごめんね (One story ends)
# 今まで (Begin again)
# 気付かなかったことがあるんだけど
# こうして (While hand-in-hand)
# あなたが (Until the end)
# いてくれたから今のわたしがいる
# 過去はいらない？そんなことはない
# 未来は見えない方がマシじゃない？
# ここから (No matter where)
# 静かに (Watch over me)
# わたしを見守っていてね
# So, you think that's all huh?
# Just gonna leave like it's nothing?
# Going without me?
# I don't know what you're thinking!
# Return to the sea
# A shark is all you'll ever be
# さよなら (Our story ends)
# ありがとう (Begin again)
# 隠していたわたしはもういない
# さよなら (Once hand-in-hand)
# ありがとう (Until the end)
# 全て受け入れて生きていくから
# 海の底はつまらないけど
# あなたのことは忘れないから
# いつでも (No matter where)
# どこでも (Watch over me)
# わたしらしく生きていこう
# Ουδέν κακόν αμιγές καλού
# """)
