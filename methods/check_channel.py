from db.models import User, Channel
from telegram.ext import CallbackContext
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from states.states_basic import StatesBase as stb
from keyboards.base_keyboards import BaseKeyboards as kyb
from static_files.lang import Language as lang
from settings import TOKEN
import telebot

bot_help = telebot.TeleBot(TOKEN)


def channel_batton(user_id):
    channels = Channel.objects.filter(status=True)
    batton = []
    for channel in channels:
        name = channel.name
        if bot_help.get_chat_member(channel.channel_id, user_id).status != 'left':
            continue
        batton.append([InlineKeyboardButton(text=name, url=f'{channel.channel_url}')])
    batton.append([InlineKeyboardButton(text="A'zolikni tekshirib ko'rish ♻️", callback_data='check')])
    return InlineKeyboardMarkup(batton)


def is_not_subscribed(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    context.bot.send_message(chat_id=user_id,
                             text="Botdan foydalanish uchun barcha kanallarimizga a'zo bo'ling",
                             reply_markup=channel_batton(user_id)
                             )
    return stb.chan_mem


def is_subscribed(channels, user_id):
    try:

        members = list(map(lambda ch: bot_help.get_chat_member(ch.channel_id, user_id).status != 'left', channels))
        if not all(members):
            return False
        return True
    except Exception:
        return False


def check_is_subscribed(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == 'check':
        user = update.effective_chat
        channels = Channel.objects.filter(status=True)
        is_subscribed_ = is_subscribed(channels, user.id)
        if is_subscribed_ is False:
            query.delete_message(timeout=1)
            return is_not_subscribed(update, context)
        query.delete_message(timeout=1)
        context.bot.send_message(chat_id=user.id, text="<b> Botdan foydalanishingiz mumkin 👇</b>",
                                 parse_mode="HTML", reply_markup=kyb.base(lang.uz_latn))
        return stb.base
