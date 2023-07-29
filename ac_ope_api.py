import openai
import json

# Set up your OpenAI API key
openai.api_key = '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'

# Define the conversation with initial user and system messages
conversation = [
    {'role': 'system', 'content': 'You are a Conversational Chatbot API.'},
    {'role': 'user', 'content': 'I am user, you work as a Conversational Chatbot API that analyzes the user command, nearby conversation that happened in a room and simplifies and analyzes them. Initially, you have to ask the user about location, room size, and other necessary information that you want. You have to release a JSON response that contains "ac mode [cooling, heating, fan only, sleep, power saving, party]", fan speed [0 to 255], temperature [14 to 35 *C], on/off, an output response that will be converted to Text to voice, and if any other required."'}
]

# Send a message and retrieve the model's response
response = openai.ChatCompletion.create(
    model='gpt-3.5-turbo',
    messages=conversation
)

# Extract the model's reply
answer = response['choices'][0]['message']['content']

# 4191 8802 4105 2956 776
# Create the JSON response
json_response = {
    "ac mode": "cooling",
    "fan speed": 100,
    "temperature": 24,
    "on/off": True,
    "output response": answer
}

# Convert the JSON response to a string
json_response_string = json.dumps(json_response)

# Print the JSON response
print(json_response_string)
