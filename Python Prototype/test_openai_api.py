# Library for requesting HTTP calls 
import requests
# The below code is just loading the chat interface but there is a another code that has the logic and brain of system 
# so we can create HTTP calls, we are communicating with the code that has the logic to provide response 


# Creates infinite loop to keep the conversation ongoing
while True:
    # Collects user input from terminal and stores in variable q (question) 
    q = input("You: ")

    # If q variable is empty by user clicking enter
    if not q:
        # end the infinite loop
        break
    # if value exist in q 

    # Converts the user input from q variable in JSON as as the triggers are in that format 
    # POST request is sent to chat bot API for processing 
    res = requests.post("http://127.0.0.1:8000/analyze", json={"user_input": q})
    
    # Learning Point: ALWAYS check the IP link matches when you start the server 

    # Static string of Bot to be displayed along with response from chat bot api to be printed
    print("Bot:", res.json())
