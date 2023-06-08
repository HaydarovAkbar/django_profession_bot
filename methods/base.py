from telegram.ext import CallbackContext
from telegram import Update, ReplyKeyboardRemove
from states import StatesBase as st
from keyboards.base_keyboards import BaseKeyboards as kb
from static_files.base_message import MessageText as msg
from static_files.error_message import ErrorMessage as err
from static_files.lang import Language as lang
from db.models import User


# from db.models import User


def start(update: Update, context: CallbackContext):
    user = update.effective_user
    update.message.reply_text(text=msg.base_txt.get(lang.uz_latn).replace('%fullname%', user.full_name))
    update.message.reply_text(text=msg.first_question_txt.get(lang.uz_latn))
    return st.age


def get_user_old(update: Update, context: CallbackContext):
    user_age = update.message.text
    if not user_age.isdigit() or int(user_age) < 0 or int(user_age) > 100:
        update.message.reply_text(text=err.age_error_txt.get(lang.uz_latn))
        return st.age
    context.chat_data['age'] = user_age
    update.message.reply_text(text=msg.enter_gender_txt.get(lang.uz_latn), reply_markup=kb.gender(lang.uz_latn))
    return st.gender


def get_user_gender(update: Update, context: CallbackContext):
    query = update.callback_query

    if not User.objects.filter(user_id=update.effective_user.id):
        User.objects.get_or_create(
            user_id=update.effective_user.id,
            username=update.effective_user.username,
            first_name=update.effective_user.first_name,
            last_name=update.effective_user.last_name,
            age=context.chat_data['age'],
            gender=query.data
        )
    context.chat_data['gender'] = query.data
    query.delete_message(timeout=1)
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg.acsess_to_channel_txt.get(lang.uz_latn),
                             reply_markup=)


def echo(update: Update, context: CallbackContext):
    update.message.copy(chat_id=update.message.chat_id,
                        )
    return st.base
