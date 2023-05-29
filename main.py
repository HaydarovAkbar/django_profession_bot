import os
import sys

import django

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
import logging
import settings
from methods import *
from states import State as st

sys.dont_write_bytecode = True
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

# Create the Updater and pass it your bot's token.
updater = Updater(settings.TOKEN, use_context=True)

# Get the dispatcher to register handlers
dp = updater.dispatcher


def help(update, context):
    """Send a message when the command /help is issued."""
    context.bot.send_message(chat_id=update.effective_chat.id, text='Help!')


all_handle = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        st.age: [CommandHandler('start', start),
                 MessageHandler(Filters.text, get_user_age)],

    },
    fallbacks=[CommandHandler('cancel', start)]
)

dp.add_handler(handler=all_handle)

updater.start_polling()
print('started polling')
updater.idle()
