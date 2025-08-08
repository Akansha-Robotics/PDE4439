# Library for reading and creating files in specific folder
import os
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

# ─── 0) CONFIG ───────────────────────────────────────────────────────────────
# Setting Open AI API key so it can be used to create embedding
OPENAI_API_KEY        = os.getenv("OPENAI_API_KEY", "sk")
# As I am placing this code on a Public GitHub Link, the above link is fake and needs to be replaced with your Open AI API

# Learning Point: Upon integrating the generate_embeddings.py code within API of Expert Hub, I found out that the values of embedding vectors are different in the API and python code 
# I struggled for 3 days trying to figure why the different was there. However, I realised it would just be better to create the python code again using the same json created from API 

# Setting the json file taken from API of Expert Hub 
EMB_PATH = "C:/Users/bhati/OneDrive/Desktop/Research/NCC_NRC_json_response_22_07.json"

# Setting the threshold value to decided whether answer should be taken from Knowledge Base
SIMILARITY_THRESHOLD  = 0.85
# Setting the Open AI API key in the variable 
client = OpenAI(api_key=OPENAI_API_KEY)

# ─── 1) LOAD & NORMALIZE KB ──────────────────────────────────────────────────
# Opens the file at that path preset and assigns it to variable f
with open(EMB_PATH, "r", encoding="utf-8") as f:
    # Loads and stores the json file in data variable 
    data = json.load(f)
# If loop to filter out other keys in dictionary and only take QNAASSISTANT where knowledge base info is stored
if isinstance(data, dict) and "QNAASSISTANT" in data:
    # Stores that values of knowledge base in raw variable 
    raw = data["QNAASSISTANT"]
# Applies the same if loop condition of finding QNAASSISTANT when it is a list 
elif isinstance(data, list) and len(data) == 1 and isinstance(data[0], dict) and "QNAASSISTANT" in data[0]:
    # Stores that values of knowledge base in raw variable 
    raw = data[0]["QNAASSISTANT"]
# the last resort of extracting the data would be taking the json file as is to ensure the data is stored when loading the json  
elif isinstance(data, list):
    # Stores it in raw variable 
    raw = data
# If all fails 
else:
    # It will display the below error 
    raise RuntimeError("Unrecognized JSON structure for KB")

# Creates an empty list to store triggers in knowledge base 
trigger_kb = []

# Runs through the rows in the knowledge base 
for e in raw:
    # Stores the ID into the variable or takes empty string if ID is not there 
    entry_id = str(e.get("ID") or e.get("id", ""))
    # Stores the answer that robot would give and make sure there are no unnecessary spaces with .strip() 
    answer   = (e.get("Answer") or e.get("answer") or "").strip()
    # Stores the triggers from the chat file
    raw_q    = (e.get("Question") or e.get("question") or "")
    # Further processes the triggers by making lower case and removing semi colon along with removing spaces - for loop to run through all triggers
    triggers = [t.strip().lower() for t in raw_q.split(";") if t.strip()]
    # Stores the embedding vectors created in API of Expert Hub 
    emb_list = e.get("Embedding") or e.get("embedding")
    # If the triggers, ID or embedding is missing 
    if not entry_id or not triggers or not isinstance(emb_list, list):
        # that entry will be skipped 
        continue
    # Converts the embedding received from API using NumPy to allow for calculations to be done on it 
    vec = np.array(emb_list, dtype=np.float32)
    # Final list is being made below with below field being added 
    trigger_kb.append({
        "id":       entry_id,
        "triggers": triggers,
        "answer":   answer,
        "vec":      vec
    })

# Displays the number of entries taken from knowledge base 
print(f"✅ Loaded {len(trigger_kb)} KB entries")
# Learning Point: I was facing an issue where the chat bot was not working due to knowledge base entries not being properly loaded 
# So above check on number of entries and for loop was made to solve for that  

# ─── 2) HELPERS ───────────────────────────────────────────────────────────────
# Creating function to calculation cosine similarity 
def cosine(a: np.ndarray, b: np.ndarray) -> float:
    # Using same formula as the last code to do calculation 
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

# Function for detecting sentiment of user input 
async def detect_sentiment(text: str) -> str:
    # Calls Open AI API model for this detection
    resp = client.chat.completions.create(
        # Sets the model to use from Open AI
        model="gpt-3.5-turbo",
        # Sets the message to send to Open AI following the parameters required 
        messages=[
            # Indicates the role of Open AI is to classify the sentiment of the user 
            {"role":"system",
             # Clear instruction is given to properly classify it into 3 categories 
             "content":"You are a sentiment analyzer. Classify strictly as Positive, Negative, or Neutral."},
            # User input is stored in text variable and process to output sentiment classification 
            {"role":"user","content":f"Message: “{text}”\nSentiment:"}
        ]
    )
    # Final reply from model is stored along with spaces removed and made lower case to standardize the values
    return resp.choices[0].message.content.strip().lower()

# ─── 3) FASTAPI APP ───────────────────────────────────────────────────────────
# Initializes FastAPI to handle requests 
app = FastAPI()

# Calling FastAPI POST request in the analyze function below 
@app.post("/analyze")
# Setting the function for doing a request - async allows for the user input reading 
async def analyze(request: Request):
    # Parses the request of user input and stores it in body 
    body       = await request.json()
    # Extracts the user input and removes any spaces - if no value is found, makes it an empty string 
    user_input = (body.get("user_input") or "").strip()
    # If no value is found in user input 
    if not user_input:
        # Display below error message 
        return {"error": "No input provided."}

    # 3a) sentiment check - empathic GPT reply
    # Uses the function created to detected sentiment of user input and stores it in variable 
    sent = await detect_sentiment(user_input)
    # If negative sentiment is found 
    if "negative" in sent:
        # Calls Open AI API model for this detection
        gpt_resp = client.chat.completions.create(
            # Sets the model to use from Open AI
            model="gpt-3.5-turbo",
            # Indicates the role of Open AI is to create a response that is appropriate to user input but also vague to not give any statement 
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a compassionate assistant. "
                        "When the user expresses negative sentiment, "
                        "respond in a kind and empathetic tone, "
                        "acknowledge their feelings, "
                        "and offer support in 1–2 sentences. "
                        # Learning Point: When I was testing the response for negative sentiment, the answer would be too long and provide details solutions
                        # Therefore, the below text was added with character count to keep in short and simple 
                        "Do NOT provide long explanations or technical details."
                        "Respond with a maximum of 200 characters"
                    )
                },
                # User input is stored for the model to use 
                {"role": "user", "content": user_input}
            ]
        )
        # Provides the final response to be given to API and spoken by robot 
        return {
            "input":      user_input,
            # Reply from Open AI stored here 
            "answer":     gpt_resp.choices[0].message.content.strip(),
            # confidence score is set to 1.0 the highest to ensure this response is given by robot 
            "confidence": 1.0,
            "sentiment":  sent
        }


    # Converts the user input into to lower case to standardize the values 
    ui_l = user_input.lower()

    # 3b) exact trigger match
    # Runs through the each row in knowledge base 
    for item in trigger_kb:
        # Runs through each word in the user's input 
        for trig in item["triggers"]:
            # If the trigger word is found in the user's input 
            # For example, "company" trigger word would be found in user's input of "tell me about your company"
            if trig in ui_l:
                # then provide the corresponding response for that trigger 
                return {
                    "input":           user_input,
                    "matched_trigger": trig,
                    "id":              item["id"],
                    "answer":          item["answer"],
                    # confidence score set to 1 to make sure the answer is spoken by robot 
                    "confidence":      1.0,
                    "sentiment":       sent
                }


    # 3c) semantic match via embeddings
    # If 3b trigger matching was not successful - Then it would move to matching with embedding 
    # Initializes Open AI API call 
    emb_resp = client.embeddings.create(
        # Sets the model to be used 
        model="text-embedding-ada-002",
        # Stores the user input 
        input=user_input
    )
    # Convert values using NumPy to allow calculation of cosine similarity to be done 
    user_vec = np.array(emb_resp.data[0].embedding, dtype=np.float32)

    # Sets the best score to lowest so that when a better score comes - it can be saved and compared with score received 
    best_score, best_item = -1.0, None
    # Run through all entries in knowledge base 
    for item in trigger_kb:
        # Applies the function for cosine similarity to get the score  
        score = cosine(user_vec, item["vec"])
        # If score received is better than best score saved 
        if score > best_score:
            # Stores the score and correspondingly values from best item 
            best_score, best_item = score, item

    # 4) Decide: KB answer vs GPT fallback
    # If the best score is greater than the threshold 
    if best_score >= SIMILARITY_THRESHOLD:
        # Then knowledge base trigger is choose - and the answer for that is spoken by robot 
        return {
            "input":           user_input,
            "matched_trigger": best_item["triggers"][0],
            "id":              best_item["id"],
            "answer":          best_item["answer"],
            # Rounds to 3 decimals just to keep the clean value of score received 
            "confidence":      round(best_score, 3),
            "sentiment":       sent
        }

    # GPT‐fallback for anything else
    # If the best score was lower than threshold - Then request Open AI API for answer 
    gpt_resp = client.chat.completions.create(
        # Selects the model to use 
        model="gpt-3.5-turbo",
        # Sets the message to provide what the system should do 
        messages=[
            {"role":"system",
             "content":"You are a knowledgeable assistant. Answer the user’s question directly."
             "If the user’s message contains a proper name or place, assume they spelled it correctly. "
            # Learning point: When I was testing, the speech converted to text by robot would sometimes have spelling mistakes due to speech recognition limitations  
            # and that would be called out by GPT saying I made a typo despite not typing anything 
            "Do NOT mention typos or spelling mistakes. "
            "Answer the user’s question in 100 words or less, clearly and concisely."
            # Had to character limit as sometimes the answers were too long 
            "Respond with a maximum of 200 characters"
             },
             # Send the user input to Open AI
            {"role":"user","content": user_input}
        ]
    )
    # Provides the response to be spoken by robot
    return {
        "input":      user_input,
        "answer":     gpt_resp.choices[0].message.content.strip(),
        "confidence": round(best_score, 3),
        "sentiment":  sent
    }

# ─── 5) RUN SERVER ────────────────────────────────────────────────────────────
# Runs the FastAPI Server when this python script is ran 
if __name__ == "__main__":
    uvicorn.run(
        # Python code to set the format of how the terminal should be - Allowing for User input and displaying response 
        "test_openai_api_22_07:app",
        # Sets the server configurations  
        host="127.0.0.1",
        port=8000,
        reload=True
    )
