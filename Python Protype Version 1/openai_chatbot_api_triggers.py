# Library for reading and creating json files 
import json
# Library for numerical calculation for embedding vectors 
import numpy as np
# Library for going API calls like .get() and .post() along with HTTPS requests
from fastapi import FastAPI, Request
# Import to allow code for calling Open AI API 
from openai import OpenAI
# Server to run the FastAPI and calls 
import uvicorn

# ─── Configuration ───────────────────────────────────────────────────────────
# Setting Open AI API key so it can be used to create embedding
OPENAI_API_KEY = "sk" 
# As I am placing this code on a Public GitHub Link, the above link is fake and needs to be replaced with your Open AI API
# Setting main directory file where final json is with trigger embeddings
EMB_PATH = "C:/Users/bhati/OneDrive/Desktop/Research/trigger_embeddings.json"
# ───────────────────────────────────────────────────────────────────────────────

# Setting Open AI API key so it can be used to create embedding
client = OpenAI(api_key=OPENAI_API_KEY)

# Loading the json file with the embedding 
with open(EMB_PATH, "r", encoding="utf-8") as f:
    # Stores the data in below variable  
    trigger_kb = json.load(f)
# Runs through the json file loaded 
for item in trigger_kb:
    # Extract the values from embedding and stores them in new variable to do the computation 
    item["vec"] = np.array(item["embedding"], dtype=float)

# Below function allows to find whether triggers have the similar context despite not having similar keywords. 
# For example, not feeling good and unwell would have a high cosine similarity resulting in their meaning to be similar  
def cosine(a, b):
    # Calculating the cosine similarity between two variables
        # .dot would multiple the vectors providing positive or negative value  
        # Positive is similar semantic direction while negative is vice versa

        # linalg.norm finds the length of the vector using linear algebra
        # By dividing dot product with their norms, we are able to normalize the values to become ranging from -1 to 1 
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
    # Value of cosine similarity is return as a float data type 

# Function for detecting the sentiment of user's input
def detect_sentiment(text: str) -> str:
    """Returns 'positive', 'negative', or 'neutral'."""
    # Uses Open AI API of ChatCompletion to detect the sentiment
    resp = client.chat.completions.create(
        # Using the basic Open AI model as it is a simple task
        model="gpt-3.5-turbo",
        # Sets the roles according to parameters of using API and model 
        messages=[
            {
            # System message will tell ChatGPT what it should do 
              "role":    "system",
              "content": "You are a sentiment analyzer.  "
                         "Classify the user message strictly as Positive, Negative, or Neutral."
            },
            {
            # Indicating below is user's input 
              "role":    "user",
            # Setting placeholder for receiving input and indicating API to reply with sentiment 
              "content": f"Message: “{text}”\nSentiment:"
            }
        ]
    )
    # stores the answer in resp variable - Removes white space and converts to lower case
    return resp.choices[0].message.content.strip().lower()

# Initializes the Fast API
app = FastAPI()

# Calling FastAPI POST request in the analyze function below 
@app.post("/analyze")
# Setting the function for doing a request - async allows for the user input reading 
async def analyze(request: Request):
    # Stores the json for user's input in data variable 
    data       = await request.json()
    # Extracts the value of user input and removes any unnecessary spaces with .strip()
    user_input = data.get("user_input", "").strip()
    # If the user input is empty
    if not user_input:
        # Then provides an error message for it 
        return {"error": "No input provided."}

    # ── 1) Sentiment check ────────────────────────────────────────────────
    # Applies the function for detecting sentiment using OpenAI API and stores the result in sent variable 
    sent = detect_sentiment(user_input)
    # If negative sentiment has been detected  
    if "negative" in sent:
        # The response is preset and sent to the robot to speak  
        return {
            # Stores the user's input in the correct key of dictionary 
            "input":      user_input,
            # Key below for storing the preset answer 
            "answer":     "I’m sorry you’re not feeling well. "
                          "I hope the issue gets resolved",
            # Set confidence to full as we are certain in matching the trigger to this answer
            "confidence": 1.0,
            # Stores the sentiment in the correct key 
            "sentiment":  sent
        }

    # ── 2) Trigger matching ───────────────────────────────────────────────
    # Converts the user inputs into embedding 
    # client.embeddings.create() allows for OpenAI embedding model to be applied 
    emb_resp = client.embeddings.create(
        # Sets the model to be used from OpenAI 
        model="text-embedding-ada-002",
        # Stores the user input in parameter for OpenAI to read
        input=user_input
    )
    # Receives the embedding vectors and stores it in python array 
    user_vec = np.array(emb_resp.data[0].embedding, dtype=float)
    # Setting best score at -1 so that this variable will be compared with every cosine similarity and updated when a better score is found 
    best_score = -1.0
    # Variable to store the answers that best matches with user's input 
    best_item  = None
    # Runs through the knowledge base 
    for item in trigger_kb:
        # Applies function to calculate the cosine similarity and stores it in score 
        score = cosine(user_vec, item["vec"])
        # If score received is better than best score 
        if score > best_score:
            # Updates the best score with new best score found 
            best_score = score
            # Stores the response of the best score
            best_item  = item

    # If the score is below 0.5 (threshold)
    if best_score < 0.5:
        # Then returns fallback response asking user to repeat themselves 
        return {
            # Stores the user's input 
            "input":      user_input,
            # Fallback answer for not finding any answer 
            "answer":     "I’m sorry, I didn’t fully understand.",
            # Stores confidence scores and rounds it to 3 decimals 
            "confidence": round(best_score, 3),
            # Stores the sentiment 
            "sentiment":  sent
        }
    # Return for if the response was found 
    return {
        # Stores the user's input 
        "input":           user_input,
        # Stores the trigger matched from knowledge base 
        "matched_trigger": best_item["trigger"],
        # Stores the ID of that matched trigger from chat file 
        "id":              best_item["id"],
        # Stores the answer for that matched trigger 
        "answer":          best_item["answer"],
        # Stores the confidence store rounded up to 3 decimals 
        "confidence":      round(best_score, 3),
        # Stores the sentiment 
        "sentiment":       sent
    }

# If this python script is being run 
if __name__ == "__main__":
    # Sets the FastAPI Server with localhost IP and port number 
    # reload allows the server to load the code again when changes has been done in code 
    uvicorn.run("openai_chatbot_api_triggers:app", host="127.0.0.1", port=8000, reload=True)
