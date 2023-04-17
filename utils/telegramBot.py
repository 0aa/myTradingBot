import requests
'''config file needs to be created with the api keys/tokens'''
import config


class TelegramBot:

    def __init__(self):
        """config file needs to be created with the api keys/tokens"""
        self.url = f"https://api.telegram.org/bot{config.BOT_API_TOKEN}/"
        self.chat_id = config.CHAT_ID

    def get_all_updates(self):  # receive all the messages for the last 24h
        response = requests.get(self.url + 'getUpdates')
        print(response.json())
        return response.json()

    def send_message(self, text):
        params = {'chat_id': self.chat_id, 'text': text}  # <= not ideal
        response = requests.post(self.url + 'sendMessage', data=params)
        return response

    def get_last_message(self, all_updates):  # get the last message
        try:
            a = len(all_updates['result']) - 1
        except:
            print("need more messages")
        try:
            message_text = all_updates['result'][a]['message']["text"]
        except:
            message_text = None
        try:
            message_id = all_updates['result'][a]['message']["message_id"]
        except:
            message_id = None
        try:
            chat_id = all_updates['result'][a]['message']["from"]["id"]
        except:
            chat_id = None
        print("id",chat_id,"text",message_text)
        return message_id, message_text, chat_id


'''
bot = Bot()
upd = bot.get_all_updates()
bot.get_last_message(upd)
bot.send_message(-1001808333933, "test123")
'''