# chatbot_basic.py
import random

def get_response(user_input: str) -> str:
    user_input = user_input.lower().strip()

    intents = {
        "greeting": ["hi", "hello", "hey"],
        "farewell": ["bye", "goodbye", "see you"],
        "thanks": ["thanks", "thank you"],
        "name": ["your name", "who are you"],
        "age": ["how old are you"],
    }

    responses = {
        "greeting": ["Hello!", "Hi there!", "Hey!"],
        "farewell": ["Goodbye!", "See you later!", "Bye!"],
        "thanks": ["You're welcome!", "No problem!", "Anytime!"],
        "name": ["I'm a simple chatbot.", "You can call me CodeBot."],
        "age": ["I'm timeless!", "I was born in code."]
    }

    for intent, keywords in intents.items():
        for keyword in keywords:
            if keyword in user_input:
                return random.choice(responses[intent])

    return "I'm not sure how to respond to that."

def chat():
    print("ChatBot: Hello! Type 'exit' to end the conversation.")
    while True:
        try:
            user_input = input("You: ")
        except EOFError:
            break
        if user_input.strip().lower() == "exit":
            print("ChatBot: Goodbye!")
            break
        response = get_response(user_input)
        print(f"ChatBot: {response}")

if __name__ == "__main__":
    chat()
