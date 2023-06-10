import sys

sys.dont_write_bytecode = True
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import django

django.setup()

import logging
from states import StatesBase as st
from settings import TOKEN
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
from methods import *
from static_files.keyboards_files import KeyboardsText as kbt
from static_files.admin import MessageText as adm_msg
from static_files.lang import Language as lang
from methods.admin import admin, reklama, back_user, reklama_type, get_button_link, \
    send_reklama_audio, send_reklama_voice, send_reklama_text, send_reklama_photo, send_reklama_video, \
    get_forward_message, get_not_link_batton, admin_stats, add_admin, get_new_admin_chat_id, admin_lists, del_admin, \
    add_channel, add_channel_name, add_channel_link, status_channels, channel_status, status_edit_channel

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

updater = Updater(TOKEN, use_context=True)

dp = updater.dispatcher
bot_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start),
                  CommandHandler('admin', admin),

                  MessageHandler(Filters.regex('^(' + kbt.base_txt[lang.uz_latn][0] + ')$'), start_test),
                  MessageHandler(Filters.regex('^(' + kbt.base_txt[lang.uz_latn][1] + ')$'), telegraph),
                  MessageHandler(Filters.regex('^(' + kbt.base_txt[lang.uz_latn][2] + ')$'), statistics),

                  ],
    states={
        st.age: [CommandHandler('start', start),
                 CommandHandler('admin', admin),
                 MessageHandler(Filters.text, get_user_old)
                 ],
        st.gender: [CommandHandler('start', start),
                    CallbackQueryHandler(get_user_gender),
                    ],
        st.menu: [CommandHandler('start', start),
                  CommandHandler('admin', admin),
                  MessageHandler(Filters.regex('^(' + kbt.base_txt[lang.uz_latn][0] + ')$'), start_test),
                  MessageHandler(Filters.regex('^(' + kbt.base_txt[lang.uz_latn][1] + ')$'), telegraph),
                  MessageHandler(Filters.regex('^(' + kbt.base_txt[lang.uz_latn][2] + ')$'), statistics),
                  # ... other handlers
                  MessageHandler(Filters.all, echo)
                  ],
        st.test: [CommandHandler('start', start),
                  CallbackQueryHandler(get_test),
                  MessageHandler(Filters.regex('^(' + kbt.base_txt[lang.uz_latn][0] + ')$'), start_test),
                  MessageHandler(Filters.regex('^(' + kbt.base_txt[lang.uz_latn][1] + ')$'), telegraph),
                  MessageHandler(Filters.regex('^(' + kbt.base_txt[lang.uz_latn][2] + ')$'), statistics),
                  ],
        st.chan_mem: [
            CommandHandler('start', start),
            CallbackQueryHandler(check_is_subscribed, run_async=True),
        ],
        st.admin: [
            CommandHandler('start', start),

            MessageHandler(Filters.regex('^(' + kbt.admin_button[lang.uz_latn][2] + ')$'), reklama),
            MessageHandler(Filters.regex('^(' + kbt.admin_button[lang.uz_latn][3] + ')$'), admin_stats),
            MessageHandler(Filters.regex('^(' + kbt.admin_button[lang.uz_latn][4] + ')$'), add_channel),
            MessageHandler(Filters.regex('^(' + kbt.admin_button[lang.uz_latn][5] + ')$'), status_channels),
            MessageHandler(Filters.regex('^(' + kbt.admin_button[lang.uz_latn][6] + ')$'), add_admin),
            MessageHandler(Filters.regex('^(' + kbt.admin_button[lang.uz_latn][7] + ')$'), admin_lists),
            MessageHandler(Filters.regex('^(' + kbt.admin_button[lang.uz_latn][8] + ')$'), start),
        ],
        st.reklama: [
            CommandHandler('start', start),
            MessageHandler(Filters.regex('^(' + kbt.rek_type[lang.uz_latn][0] + ')$'), reklama_type),
            MessageHandler(Filters.regex('^(' + kbt.rek_type[lang.uz_latn][1] + ')$'), get_not_link_batton),
            MessageHandler(Filters.regex('^(' + kbt.rek_type[lang.uz_latn][2] + ')$'), back_user),
        ],
        st.inline_button: [
            CommandHandler('start', start),
            CommandHandler('admin', admin),
            MessageHandler(Filters.regex('^(' + adm_msg.back[lang.uz_latn] + ')$'),
                           back_user),
            MessageHandler(Filters.regex('^(' + adm_msg.back[lang.uz_cyrl] + ')$'),
                           back_user),
            MessageHandler(Filters.regex('^(' + adm_msg.back[lang.ru] + ')$'),
                           back_user),

            MessageHandler(Filters.text, get_button_link),
        ],
        st.send_ads: [
            CommandHandler('start', start),
            CommandHandler('admin', admin),
            MessageHandler(Filters.regex('^(' + adm_msg.back[lang.uz_latn] + ')$'),
                           back_user),
            MessageHandler(Filters.regex('^(' + adm_msg.back[lang.uz_cyrl] + ')$'),
                           back_user),
            MessageHandler(Filters.regex('^(' + adm_msg.back[lang.ru] + ')$'),
                           back_user),

            MessageHandler(Filters.forwarded, get_forward_message),
            MessageHandler(Filters.photo, send_reklama_photo),
            MessageHandler(Filters.video, send_reklama_video),
            MessageHandler(Filters.audio, send_reklama_audio),
            MessageHandler(Filters.voice, send_reklama_voice),

            MessageHandler(Filters.text, send_reklama_text),
        ],
        st.new_admin: [
            CommandHandler('start', start),
            CommandHandler('admin', admin),
            MessageHandler(Filters.regex('^(' + adm_msg.back[lang.uz_latn] + ')$'),
                           back_user),
            MessageHandler(Filters.regex('^(' + adm_msg.back[lang.uz_cyrl] + ')$'),
                           back_user),
            MessageHandler(Filters.regex('^(' + adm_msg.back[lang.ru] + ')$'),
                           back_user),
            MessageHandler(Filters.text, get_new_admin_chat_id),
        ],
        st.del_admin: [
            CommandHandler('start', start),
            CommandHandler('admin', admin),
            MessageHandler(Filters.regex('^(' + adm_msg.back[lang.uz_latn] + ')$'),
                           back_user),
            MessageHandler(Filters.regex('^(' + adm_msg.back[lang.uz_cyrl] + ')$'),
                           back_user),
            MessageHandler(Filters.regex('^(' + adm_msg.back[lang.ru] + ')$'),
                           back_user),
            MessageHandler(Filters.text, del_admin),
        ],
        st.add_channel: [
            CommandHandler('start', start),
            CommandHandler('admin', admin),
            MessageHandler(Filters.regex('^(' + adm_msg.back[lang.uz_latn] + ')$'),
                           back_user),
            MessageHandler(Filters.regex('^(' + adm_msg.back[lang.uz_cyrl] + ')$'),
                           back_user),
            MessageHandler(Filters.regex('^(' + adm_msg.back[lang.ru] + ')$'),
                           back_user),
            MessageHandler(Filters.text, add_channel_name),
        ],
        st.add_channel_name: [
            CommandHandler('start', start),
            CommandHandler('admin', admin),
            MessageHandler(Filters.regex('^(' + adm_msg.back[lang.uz_latn] + ')$'),
                           back_user),
            MessageHandler(Filters.regex('^(' + adm_msg.back[lang.uz_cyrl] + ')$'),
                           back_user),
            MessageHandler(Filters.regex('^(' + adm_msg.back[lang.ru] + ')$'),
                           back_user),
            MessageHandler(Filters.text, add_channel_link),
        ],
        st.status_channel: [
            CommandHandler('start', start),
            CommandHandler('admin', admin),
            MessageHandler(Filters.regex('^(' + adm_msg.back[lang.uz_latn] + ')$'),
                           back_user),
            MessageHandler(Filters.regex('^(' + adm_msg.back[lang.uz_cyrl] + ')$'),
                           back_user),
            MessageHandler(Filters.regex('^(' + adm_msg.back[lang.ru] + ')$'),
                           back_user),
            MessageHandler(Filters.text, channel_status),
        ],

        st.status_type: [
            CommandHandler('start', start),
            CommandHandler('admin', admin),
            MessageHandler(Filters.regex('^(' + kbt.status[lang.uz_cyrl][0] + ')$'),
                           status_edit_channel),
            MessageHandler(Filters.regex('^(' + kbt.status[lang.ru][1] + ')$'),
                           back_user),

            MessageHandler(Filters.text, channel_status),
        ],
    },
    fallbacks=[CommandHandler('cancel', start)]
)

dp.add_handler(handler=bot_handler)

updater.start_polling()
print('started polling')
updater.idle()
