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
