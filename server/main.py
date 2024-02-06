from fastapi import FastAPI, Request
import uvicorn
from utils import get_words, TAGS_TO_COLORS
from fastapi.middleware.cors import CORSMiddleware


origins = [
    "http://192.168.1.62:3000",
    "http://localhost:3000"
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/tokenize")
def tokenize(request: Request):
    label_to_tokens = {}
    for label, sentence_or_line in request.query_params.items():
        label_to_tokens[label] = get_words(sentence_or_line)
    return label_to_tokens

@app.get("/tags_to_colors")
def tags_to_colors():
    return TAGS_TO_COLORS


if __name__ == '__main__':
    uvicorn.run(app, port=3001, host='0.0.0.0')