import { toKatakana, toRomaji } from 'wanakana'

const smallKana = 'ぁぃぅぇぉっゃゅょゎァィゥェォヵㇰヶㇱㇲッㇳㇴㇵㇶㇷㇷ゚ㇸㇹㇺャュョㇻㇼㇽㇾㇿヮ'
const bigKana = 'あいうえおつやゆよわアイウエオカクケシスツトヌハヒフプヘホムヤユヨラリルレロワ'
const hiragana = 'あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん'
const katakana = toKatakana(hiragana)
const basicKana = hiragana + katakana

const specialHiragana = {
    'っ': <div>Prolongs the consonant after (adds glottal stop).</div>,
    'ん':
        <>
            <div>Pronunciation depends on the syllable after. It's pronuonced as:
                <ul>
                    <li>"m" before syllables "bi" or "pi"</li>
                    <li>"ng" before syllable that statrs with "g"</li>
                    <li>"n" in other cases</li>
                </ul>
            </div>
        </>,
    'を': <div>The particle “wo”, usually pronounced “o”, marks the object of the action. It's written between the verb of the action and the word denoting the object that receives action.</div>
}
var specialKatakana = {}
for (const [char, note] in Object.entries(specialHiragana)) {
    specialKatakana[toKatakana(char)] = note
}
specialKatakana['ー'] = 'Prolongs the vowel before.'
const specialKana = Object.assign({}, specialHiragana, specialKatakana)


function isDigraph(text) {
    return text.length == 2 && !smallKana.includes(text[0]) && smallKana.includes(text[1]) && !(text[1] in specialKana)
}


function basicCharacter(character) {

    let shift = 0

    function get() {
        if (basicKana.includes(character)) {
            return character
        }
        const index = smallKana.indexOf(character)
        if (index != -1) {
            character = bigKana[index]
            return get()
        }
        if (shift > -2) {
            character = String.fromCharCode(character.charCodeAt() - 1)
            shift--
            return get()
        }
    }

    return get()
}

function romaji(text, i) {
    const current = text[i]
    const next = text[i + 1]
    if ('んン'.includes(current)) {
        if (next == 'g') {
            return 'ng'
        } else if ('bp'.includes(current) && next == 'i') {
            return 'm'
        } else {
            return 'n'
        }
    } else {
        return toRomaji(text, { customRomajiMapping: { 'を': 'o', 'ヲ': 'o', 'ー': '' } })
    }
}

function getRomaji(text) {
    let romajiText = ''
    for (let i = 0; i < text.length; i++) {
        romajiText += romaji(text, i)
    }
    return romajiText
}


export { isDigraph, getRomaji, basicCharacter, specialKana }