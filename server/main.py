from fastapi import FastAPI
import uvicorn  # server
from tokens import tokenize
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os  # for environment variables

load_dotenv()

# Define origins list for CORS (Cross-Origin Resource Sharing)
app = FastAPI()

# Add CORS (Cross-Origin Resource Sharing) middleware to the FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv('FRONTEND_URL')],
    # Allow credentials (cookies, authorization headers)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all HTTP headers
)


# Define a route for handling GET requests to "/tokens"


@app.get("/tokens")
def tokens(text: str):
    """
    A route to tokenize text.

    Parameters:
    - text (str): The text to tokenize.

    Returns:
    - dict: A dictionary containing tokenized output.
    """
    return tokenize(text)


if __name__ == '__main__':
    # Run the FastAPI app using Uvicorn server
    uvicorn.run(
        app,
        # Get port number from environment variables
        port=int(os.getenv('PORT')),
        host=os.getenv('HOST')  # Get host address from environment variables
    )
