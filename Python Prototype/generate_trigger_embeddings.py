# Library for reading and creating json files 
import json
# Library for mathematical tasks related to embedding and number ID
import numpy as np
# Library for reading and creating files in specific folder
import os
# Import to allow code for calling Open AI API 
from openai import OpenAI

# ─── Configuration ───────────────────────────────────────────────────────────
# Setting main directory file where chat file and json is stored
WORK_DIR = "C:/Users/bhati/OneDrive/Desktop/Research"
# Setting path to get the chat bot excel file converted to json
KB_JSON_IN    = os.path.join(WORK_DIR, "knowledge_base.json")
# Setting path to store new json file after embedding are added 
EMB_JSON_OUT  = os.path.join(WORK_DIR, "trigger_embeddings.json")

# Setting Open AI API key so it can be used to create embedding
client = OpenAI(api_key="sk")
# As I am placing this code on a Public GitHub Link, the above link is fake and needs to be replaced with your Open AI API
# ───────────────────────────────────────────────────────────────────────────────

# Reading and loading the json of chat file
# encoding="utf-8" makes sure any special characters does not get loaded, such as the arabic text
with open(KB_JSON_IN, "r", encoding="utf-8") as f:
    # Stores the loaded json in kb variable 
    kb = json.load(f)

# Creates list to store the embedding coming out 
out = []
# Runs through all the entries in the chat file 
for entry in kb:
    # Extracts the data from chat file and stores id of each row in variable 
    intent_id = entry["id"]
    # Extracts the data from chat file and stores answers of each row in variable 
    answer    = entry["answer"]
