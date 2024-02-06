Nihotip uses a special system of splitting the tokens into levels:

- **text**
    - **sentence_or_line**

        *The line breaks and the distinctions between sentences are lost after parsing a string with Mecab. That's why they should be memorized before parsing.*
        - word
            1. Part of speech
            - **part**

                *Parts are gotten by cutting the reading of the word and allow to determine the kana reading for each kanji. A part consists of multiple characters if the reading of a kanji along with the characters surrounding it can't be cut. For example, the part "大人" of the word "大人買い" uses a special reading "おとな" that can't be cut. That's why the "おとな" reading applies to the whole part.*
                - **character_or_digraph**

To Do:
* keep spaces between stanzes and paragraphs
* prove the correctness or the falsity of the statement "The line breaks and the distinctions between sentences are lost after parsing a string with Mecab and can't be restored." and modify Nihotip according to the vedict.
* pros and cons of grouping the tags by levels of tokens