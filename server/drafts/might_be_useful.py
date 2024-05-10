STEM_FORMS = {
    '仮定形': ('Hypothetical form',
            '-e',
            'is used for conditional and subjunctive forms, using the -ba '
            'ending.'),
    '命令形': ('Imperative form',
            '-e',
            'is used to turn verbs into commands. Adjectives do not have an '
            'imperative stem form.'),
    '未然形': ('Irrealis form',
            '-a (and -ō)',
            'is used for plain negative (of verbs), causative and passive '
            'constructions. The most common use of this form is with the -nai '
            'auxiliary that turns verbs into their negative (predicate) form. '
            '(See Verbs below.) The -ō version is used for volitional expression '
            'and formed by a euphonic change (音便, onbin).'),
    '終止形': ('Terminal (predicative) form',
            '-u',
            'is used at the ends of clauses in predicate positions. This form is '
            'also variously known as plain form (基本形, kihonkei) or dictionary '
            'form (辞書形, jishokei) - it is the form that verbs are listed under in '
            'a dictionary.'),
    '連体形': ('Attributive form',
            '-u',
            'is prefixed to nominals and is used to define or classify the noun, '
            'similar to a relative clause in English. In modern Japanese it is '
            'practically identical to the terminal form, except that verbs are '
            'generally not inflected for politeness; in old Japanese these forms '
            'differed. Further, na-nominals behave differently in terminal and '
            'attributive positions; see Adjectival verbs and nouns, below.'),
    '連用形': ('Continuative (conjunctive) form',
            '-i',
            'is used in a linking role (a kind of serial verb construction). This '
            'is the most productive stem form, taking on a variety of endings and '
            'auxiliaries, and can even occur independently in a sense similar to '
            'the -te ending. This form is also used to negate adjectives.'),
    '意志推量形': ('Volitional form', "is used to express the speaker's will or intention, or to make a guess or推量 (suiryō) about something. It is formed by adding the助動詞 (joshi) う (u) or よう (yō) to the 未然形 (mizenkei) of the verb.")
}

GROUPS_OF_VERBS = {
    '上一段': ('Group 2a', 'lit. upper 1-row', 'verbs with a stem ending in -i. The terminal stem form always rhymes with -iru. Examples: miru (見る, "to see"), kiru (着る, "to wear").'),
    '下一段': ('Group 2b', 'lit. lower 1-row', 'verbs with a stem ending in -e. The terminal stem form always rhymes with -eru. Examples: taberu (食べる, "to eat"), kureru (くれる, "to give" (to someone of lower or more intimate status)). (Some Group 1 verbs resemble Group 2b verbs, but their stems end in r-, not -e.)'),
    '五段': ('Group 1', 'lit. 5-row', 'verbs with a stem ending in a consonant. When this is r- and the verb ends in -eru, it is not apparent from the terminal form whether the verb is Group 1 or Group 2b, e.g. kaeru (帰る, "to return"). If the stem ends in w-, that consonant sound only appears in before the final -a of the irrealis form.'),
    'カ行変格': ('verbs that are conjugated in a special way that is different from the regular verb conjugations. There is only one カ行変格 verb, which is 来る (kuru), meaning "to come."'),
    'サ行変格': ('verbs that are conjugated in a special way that is different from the regular verb conjugations. There are four サ行変格 verbs: する (suru) - to do, 食べる (taberu) - to eat, 寝る (neru) - to sleep, 行く (iku) - to go')
}


DISCOURSE_MARKERS = {
    'フィラー': ('filler', 'Used to pause and collect thoughts (e.g., あの [ano], えーと [eeto]).')
}

PARTICLES = {'並立': {'か', 'や', 'と', 'なり', 'に', 'の', 'やら', 'だの'},
             '係': {'だに', 'も', 'は', 'さえ', 'しか', 'でも', 'こそ'},
             '副': {'など', 'だけ', 'まで', 'ほど', 'なり', 'くらい', 'ばかり', 'やら'},
             '接続': {'から',
                    'が',
                    'くせに',
                    'けれども',
                    'て',
                    'ところが',
                    'ので',
                    'のに',
                    'ば',
                    'や'},
             '格': {'へ', 'と', 'を', 'から', 'に', 'が', 'の', 'で', 'より'},
             '準体': {'から', 'の'},
             '終': {'か', 'わ', 'や', 'とも', 'な', 'かしら', 'の'},
             '間投': {'よ', 'さ', 'ね'}}

FIELDS = {
    '原形': ('base form', "verb's dictionary form or the root of the word before conjugation"),
    '表面': ('spelling', 'the actual surface form of the word as it appears in the text'),
    '読み': ('reading', ' the pronunciation of the word, written in either hiragana, katakana, or romaji')
}


PUNCTUATION = {
    '読点': 'same as comma (",") within a sentence',
    '句点': 'same as full stop (".") at the end of a sentence',
    '空白': 'blank character',
    '括弧開': 'opening bracket',
    '括弧閉': 'closing bracket',
}


{'文語': ('literary', 'word that is no longer used in everyday speech, but is still used in a number of contexts, such as in formal writing, in poetry, and in traditional Japanese arts, classical Japanese (文語, bungo) texts, such as literature from the Heian period (794-1185).')}

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


{'記号': 'symbol',}