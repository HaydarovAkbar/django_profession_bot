from telegram.ext import CallbackContext
from telegram import Update
import static
from states import State as st
from keyboards import Keyboards
from db.models import User


def start(update: Update, context: CallbackContext):
    """Send a message when the command /start is issued."""
    if not User.objects.filter(chat_id=update.effective_chat.id).exists():
        User.objects.create(chat_id=update.effective_chat.id,
                            fullname=update.effective_chat.full_name,
                            lang='uz_latn',
                            phone='+998')
    update.message.reply_html(text=static.Messages.welcome_bot)
    return st.age


def get_user_age(update: Update, context: CallbackContext):
    """Send a message when the user age is issued."""
    age = update.message.text
    if not age.isdigit() or len(age) > 2:
        update.message.reply_html(text=static.Messages.user_age_error.replace('%age%', age))
        return st.age
    context.user_data['age'] = age
    update.message.reply_html(text=static.Messages.welcome_bot,
                              reply_markup=Keyboards.sex_button)
    return st.sex


def get_user_sex(update: Update, context: CallbackContext):
    """Send a message when the user sex is issued"""
    sex = update.callback_query.data
    print(sex)