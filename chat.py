import asyncio
import json
from ollama import AsyncClient

# Function to log the conversation to a JSON file
def log_conversation_to_json(conversation_data):
    with open("conversation_log.json", "w") as f:
        json.dump(conversation_data, f, indent=4)

# Function to handle chat responses
async def chat(model, message, conversation_data):
    # Streaming the response and printing parts in real-time
    response_content = ""
    async for part in await AsyncClient().chat(model=model, messages=[message], stream=True):
        content_part = part['message']['content']
        response_content += content_part
        print(content_part, end='', flush=True)  # Print real-time response
    
    # Add the model's response to the conversation data
    conversation_data.append({
        'role': model,
        'content': response_content
    })
    print()  # Move to the next line after the response
    return response_content  # Return the model's response

async def conversation(initial_message):
    models = ['Darth', 'Yy']
    n = 0
    m = 0
    response = initial_message
    conversation_data = [{'role': 'user', 'content': initial_message}]  # Start the conversation with the user's initial message

    while True:
        if n == 0:
            if m == 0:
                previous_message = {'role': 'user', 'content': response}
                print("[ushan] : ", end='', flush=True)  # Indicate the start of Ushan's turn
                response = await chat(models[0], previous_message, conversation_data)  # Use model index
                m += 1
                n += 1
            else:
                previous_message = {'role': 'user', 'content': response}
                print("[ushan] : ", end='', flush=True)  # Indicate the start of Ushan's turn
                response = await chat(models[0], previous_message, conversation_data)  # Use model index
                m += 1
                n += 1
        elif n == 1:
            previous_message = {'role': 'user', 'content': response}
            print("[disanya] : ", end='', flush=True)  # Indicate the start of Disanya's turn
            response = await chat(models[1], previous_message, conversation_data)  # Use model index
            m += 1
            n -= 1
        
        # Log the conversation to a JSON file after each response
        log_conversation_to_json(conversation_data)

# Define the initial message (replace "Why is the sky blue?" with your desired prompt)
initial_message = "*started raining"

# Run the conversation
asyncio.run(conversation(initial_message))
