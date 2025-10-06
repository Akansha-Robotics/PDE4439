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
    # Runs through the data in triggers 
    for trig in entry["triggers"]:
        # Displays the trigger it is going to start working on 
        print(f"Embedding trigger '{trig}' (ID {intent_id})…")
        # Learning Point: I was getting stuck as the code kept crashing and not finishing the embedding 
        # Once I added this log display, I was able to see that Arabic text was getting parsed also which caused the issue 
        
        # Calls the Open AI API to start embedding and converting triggers to numerical vectors 
        resp = client.embeddings.create(
            # Sets the embedding model to use from Open AI
            model="text-embedding-ada-002",
            # Sets the triggers into the field of input for Open AI API to be applied 
            # This is a required parameter for using the embedding model
            input=trig
        )
        # Stored the embedding data into variable 
        emb = resp.data[0].embedding
        # Adding all the data into dictionary so it can be created into json  
        out.append({
            # Storing the variables as per chat file for ID Trigger and Answer  
            "id":        intent_id,
            "trigger":   trig,
            "answer":    answer,
            # Adding the embedding created from Open AI 
            "embedding": emb
        })

# Creating the json file with embedding 
# "w" means that the file is in write mode to add data
# encoding="utf-8" means that the encoding method is set to converted all text 
with open(EMB_JSON_OUT, "w", encoding="utf-8") as f:
    # indent = 2 ensures the nesting is properly done and readable
    # ensure_ascii=False - keeps the values intact and doesn't overwite it 
    json.dump(out, f, indent=2, ensure_ascii=False)

# Display message on terminal of how many embeddings generated
print(f"✅ Built {len(out)} trigger embeddings → {EMB_JSON_OUT}")
