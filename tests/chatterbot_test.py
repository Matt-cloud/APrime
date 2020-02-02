from chatterbot import ChatBot

bot = ChatBot(
    "Dimitri"
)

while True:
    try:
        response = bot.get_response(input("You: "))
        print(response)
    except KeyboardInterrupt:
        quit()
