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
