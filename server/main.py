from fastapi import FastAPI
import uvicorn  # server
from tokens import tokenize
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import psutil
import os

load_dotenv()

# Define origins list for CORS (Cross-Origin Resource Sharing)
app = FastAPI()

# Add CORS (Cross-Origin Resource Sharing) middleware to the FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL")],
    # Allow credentials (cookies, authorization headers)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all HTTP headers
)


@app.get("/")
async def root():
    return {"message": "connected to backend successfully"}


@app.get("/tokens")
def tokens(text: str) -> list:
    """
    A route to tokenize text.

    Parameters:
    - text (str): The text to tokenize.

    Returns:
    - list: A list containing tokenized output.
    """
    return tokenize(text)


if __name__ == "__main__":
    process = psutil.Process(os.getpid())
    memory_usage = process.memory_info().rss
    print(f"Current memory usage: {memory_usage / 1024 / 1024:.2f} MB")

    uvicorn.run(
        app,
        # Get port number from environment variables
        port=int(os.getenv("PORT")),
        host=os.getenv("HOST"),  # Get host address from environment variables
    )
