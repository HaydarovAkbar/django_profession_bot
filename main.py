import sys
import django
import os
import logging
from states import StatesBase as st
from settings import TOKEN
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from methods.base import start, echo

sys.dont_write_bytecode = True
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

updater = Updater(TOKEN, use_context=True)

dp = updater.dispatcher

bot_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        st.age: [CommandHandler('start', start),
                 MessageHandler(Filters.text, echo)
                 ],
        # st.object: [CommandHandler('start', start),
        #             MessageHandler(Filters.regex('^({})$'.format('|'.join(kbt.object_txt[lang.uz_latn][0]))),
        #                            add_object_func),
        #             MessageHandler(Filters.regex('^(' + kbt.object_txt[lang.uz_cyrl][0] + ')$'), add_object_func),
        #             MessageHandler(Filters.regex('^(' + kbt.object_txt[lang.ru][0] + ')$'), add_object_func),
        #             MessageHandler(Filters.regex('^(' + kbt.object_txt[lang.en][0] + ')$'), add_object_func),
        #             # ... other handlers
        #             MessageHandler(Filters.all, echo)
        #             ],

        st.add_object_property: [CommandHandler('start', start), ]
    },
    fallbacks=[CommandHandler('cancel', start)]
)

dp.add_handler(handler=bot_handler)

updater.start_polling()
print('started polling')
updater.idle()
