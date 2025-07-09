# Libary for reading the data in excel sheet and doing data manipulation
import pandas as pd
# Libary for reading and creating json files 
# This json would be need to convert the excel chat file into triggers the robot can read
import json
# Libary for reading and creating files 
# Needed for store json file in a specific folder path
import os

# ─── Configuration ───────────────────────────────────────────────────────────
# Setting main directory file where chat file and json is stored
WORK_DIR = "C:/Users/bhati/Expert Hub Robotics Dropbox/Research/Code"

# Since the folder path is set above, we just need to enter file names for below


# Setting location to find excel file
EXCEL_PATH  = os.path.join(WORK_DIR, "Chat_Co2_REx623_20250621192734.xlsx")
# Setting location to save the json file 
JSON_OUT    = os.path.join(WORK_DIR, "knowledge_base.json")

# Setting column for collecting triggers and answers 
TRIGGERS_COL = "Max 100 Characters"
ANSWER_COL   = "Max 400 Characters"
# Learning Point: The names of column is Question and Answer 
# but there is a character limit text in the first row so we need to take the titles for that 
# ───────────────────────────────────────────────────────────────────────────────

# Load the sheet
df = pd.read_excel(EXCEL_PATH)

# Create an empty list to hold the triggers and answers being converted into json format
kb = []

# For loop to go through each and every row
for idx, row in df.iterrows():

    # Gets the data in the trigger row and stores in variable
    raw_trigs = row.get(TRIGGERS_COL, "")
    # Gets the data in the answer row and stores in variable
    answer    = row.get(ANSWER_COL, "")

    # if the data is not a valid string (such as arabic text)
    if not isinstance(raw_trigs, str) or not isinstance(answer, str):
        # it will get skipped
        continue
        # Learning Point: Making sure your data is properly stored is an extremely important step
        # as the arabic text was messing up the trigger matching and no answers were being given by bot

    # In the excel file, the list of triggers are seperated with a semi colon 
    # so the below loop captures the ; and replaces it with a space
    triggers = [t.strip() for t in raw_trigs.split(";") if t.strip()]

    # if it is not a trigger - that means there is no semi colon 
    if not triggers:
        # so the loop skips that data
        continue

    # Setting up a dictionary with data collected 
    entry = {
        # creating unique ID for triggers and answers
        "id":       str(idx + 1),
        # storing trigger values 
        "triggers": triggers,
        # storing answer values 
        # .strip ensures the string values doesnt have unnecessary characters or spaces to clean up data
        "answer":   answer.strip()
    }

    # adds entry into knowledge base 
    kb.append(entry)

# Converts it to json format
with open(JSON_OUT, "w", encoding="utf-8") as f:
    # indent = 2 ensures the nesting is properly done and readable
    # ensure_ascii=False - keeps the values intact and doesn't overwite it 
    json.dump(kb, f, indent=2, ensure_ascii=False)

# Display message on terminal of how many entries in json file
print(f"✅ Wrote {len(kb)} entries to {JSON_OUT}")
