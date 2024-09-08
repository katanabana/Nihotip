# Nihotip

Nihotip is a web application designed to help users explore the intricacies of the Japanese language through a dynamic
and interactive interface. With a React frontend and a Python backend, Nihotip provides a convenient way to tokenize
Japanese text and delve into detailed information about words, symbols, and their respective properties via tooltips.
Nihotip offers a robust solution for analyzing Japanese text at multiple levels of granularity.

![Demo](demo.gif)

## ✨ Features

- **Japanese Text Tokenization:**
  Input Japanese text and have it automatically tokenized into words and symbols.

- **Detailed Word and Symbol Insights:**
  Hover over words or symbols to access detailed tooltips that explain the structure, readings, and associated
  properties of each token.

- **Level-based Token Breakdown:**
  Nihotip organizes tokenized text into multiple hierarchical levels for easy navigation (features of different levels
  of tokens are listed inside brackets):
    - text
        - not a japanese word
            - punctuation
            - space
            - line break
            - string of not japanese characters
        - japanese word (part of speech)
            - **part by reading**
                - one or multiple kanji (kana reading -> **part by reading**)
                - digraph
                    - **big kana without tenten**
                    - **big kana with tenten**
                    - small kana (_respective_ **big kana**)
                - **kana without tenten** (romaji, association)
                - **kana with tenten** (_respective_ **kana without tenten**)

- **part by reading:**

  _Parts are gotten by cutting the reading of the word. They allow to determine the kana reading for each kanji. A part
  consists of multiple characters if the reading of a kanji along with the characters surrounding it can't be cut. For
  example, the part "大人" of the word "大人買い" uses a special reading "おとな" that can't be cut. That's why the "おとな"
  reading applies to the whole part._

- **syllable:**

    - single kana
    - digraph
    - kana with "っ", "ッ" or "ー"
    - single kanji

- **Tooltip insights:**
  Show how readings map to individual characters and provide additional details like romaji and kana associations.

## 🛠️ Getting Started

To run the application locally, follow these steps:

To run the application locally, follow these steps:

1. Clone the repository and navigate into the project directory.

2. **Set up Environmental Variables:**

   Create `.env` files in the respective directories with the following content:

   - **client/.env**

     Create a file named `client/.env` and add:
     ```plaintext
     REACT_APP_BACKEND_URL=http://localhost:3001
     ```

   - **server/.env**

     Create a file named `server/.env` and add:
     ```plaintext
     PORT=3001
     HOST=localhost
     FRONTEND_URL=http://localhost:3000
     ```

3. Open two terminal windows and run the following commands in separate terminals:

   ```bash
   # Start the frontend (React)
   cd client
   npm start
   ```

   ```bash
   # Start the backend (Python)
   cd server
   python main.py
   ```

4. Open your browser and visit `http://localhost:3000` to start interacting with Nihotip.

## 🚀 Upcoming Features

- **Multilingual Tooltips:**
  Add the option to choose the language for tooltips to enhance accessibility for non-Japanese speakers.

- **Word Normalization:**
  Implement word normalization for more accurate tokenization results.

- **Notes for Ambiguous Words:**
  Provide detailed notes for words that belong to multiple parts of speech or have different interpretations based on
  context.

## 🤝 Contributing

We welcome contributions! If you'd like to contribute to Nihotip, feel free to submit issues or pull requests on the
GitHub repository.
