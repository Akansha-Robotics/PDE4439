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
# but there is a character limit in the first row so we need to take the titles for that 
# ───────────────────────────────────────────────────────────────────────────────

# Load the sheet
df = pd.read_excel(EXCEL_PATH)
