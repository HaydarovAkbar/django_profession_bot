import time
from telegram.ext import CallbackContext
from telegram import Update, ReplyKeyboardRemove
from states import StatesBase as st
from keyboards.base_keyboards import BaseKeyboards as kb
from static_files.base_message import MessageText as msg
from static_files.lang import Language as lang
from db.models import User, Channel, Question, Category, UserResult, TestEvaluation
from methods.check_channel import is_subscribed, is_not_subscribed
import random


def start(update: Update, context: CallbackContext):
    user = update.effective_user
    User.objects.get_or_create(chat_id=user.id)
    update.message.reply_text("salom", reply_markup=kb.number(10))
    update.message.reply_text(text=msg.base_txt.get(lang.uz_latn).replace('%fullname%', user.full_name))
    update.message.reply_text(text=msg.first_question_txt.get(lang.uz_latn), reply_markup=kb.age(lang.uz_latn))
    return st.age


def get_user_old(update: Update, context: CallbackContext):
    query = update.callback_query
    context.chat_data['age'] = query.data
    query.delete_message(timeout=1)
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg.enter_gender_txt.get(lang.uz_latn),
                             reply_markup=kb.gender(lang.uz_latn))
    return st.gender


def get_user_gender(update: Update, context: CallbackContext):
    query = update.callback_query
    user = update.effective_user
    if not User.objects.filter(chat_id=user.id).exists():
        User.objects.create(
            chat_id=user.id,
            username=user.username,
            fullname=user.full_name,
            age=context.chat_data['age'],
            gender=query.data
        )
    context.chat_data['gender'] = query.data
    query.delete_message(timeout=1)
    # channels = Channel.objects.filter(status=True)
    # is_subscribed_ = is_subscribed(channels, user.id)
    # if is_subscribed_ is False:
    #     time.sleep(0.7)
    #     return is_not_subscribed(update, context)
    context.bot.send_message(chat_id=user.id, text=msg.menu.get(lang.uz_latn),
                             parse_mode='HTML',
                             reply_markup=kb.base(lang.uz_latn))
    return st.menu


def start_test(update: Update, context: CallbackContext):
    user = update.effective_user
    channels = Channel.objects.filter(status=True)
    is_subscribed_ = is_subscribed(channels, user.id)
    if is_subscribed_ is False:
        time.sleep(0.7)
        return is_not_subscribed(update, context)
    del_msg = update.message.reply_text(text=msg.start_test.get(lang.uz_latn), reply_markup=ReplyKeyboardRemove())
    del_msg.delete(timeout=1)
    questions = Question.objects.all()
    question_list = list(questions)
    random.shuffle(question_list)
    context.chat_data['questions'], context.chat_data['counter'] = question_list, 0
    first_question = question_list[0]
    keyboard = kb.question(first_question.categories_a, first_question.categories_b)
    context.bot.send_photo(chat_id=user.id, photo=first_question.image_url, caption=msg.test.get(lang.uz_latn),
                           reply_markup=keyboard)
    return st.test


def get_test(update: Update, context: CallbackContext):
    query = update.callback_query
    user = update.effective_user
    channels = Channel.objects.filter(status=True)
    is_subscribed_ = is_subscribed(channels, user.id)
    if is_subscribed_ is False:
        time.sleep(0.7)
        return is_not_subscribed(update, context)
    questions = context.chat_data['questions']
    counter = context.chat_data['counter']
    if context.chat_data.get(query.data, False):
        context.chat_data[query.data] += 1
    else:
        context.chat_data[query.data] = 1
    time.sleep(0.4)
    query.delete_message(timeout=1)
    if counter == len(questions) - 1:
        return get_result(update, context)
    counter += 1
    context.chat_data['counter'] = counter
    question = questions[counter]
    keyboard = kb.question(question.categories_a, question.categories_b)
    context.bot.send_photo(chat_id=user.id, photo=question.image_url, caption=msg.test.get(lang.uz_latn),
                           reply_markup=keyboard)
    return st.test


def get_result(update: Update, context: CallbackContext):
    user = update.effective_user
    keys = list({cat.key: context.chat_data.get(cat.key, 0)} for cat in Category.objects.all())
    answers = sorted(keys, key=lambda x: list(x.values())[0], reverse=True)
    first_key = list(answers[0].keys())[0]
    result_category = Category.objects.get(key=first_key)
    caption_image = msg.direction.get(lang.uz_latn).get(result_category.key)
    context.bot.send_photo(chat_id=user.id,
                           photo=result_category.image_url,
                           caption=caption_image,
                           parse_mode='HTML',
                           reply_markup=kb.base(lang.uz_latn))
    context.chat_data['category_key'] = result_category.key
    job_txt = msg.all_jobs.get(lang.uz_latn).get(result_category.key)
    UserResult.objects.create(
        user=User.objects.get(chat_id=user.id),
        category=result_category,
        status=True)
    context.bot.send_message(chat_id=user.id,
                             text=msg.base_job_msg.get(lang.uz_latn) + "\n\n" + job_txt,
                             parse_mode='HTML',
                             reply_markup=ReplyKeyboardRemove())
    direction_count = len(msg.all_jobs_helper.get(result_category.key))
    context.bot.send_message(chat_id=user.id,
                             text=msg.choose_profession.get(lang.uz_latn),
                             parse_mode='HTML',
                             reply_markup=kb.number(direction_count))

    return st.number


def get_number(update: Update, context: CallbackContext):
    user = update.effective_user
    query = update.callback_query
    context.chat_data['number'] = query.data
    user_result = UserResult.objects.filter(user=User.objects.get(chat_id=user.id)).order_by('-date_of_created')[0]
    category_key = context.chat_data['category_key']
    user_result.number = msg.all_jobs_helper.get(category_key)[query.data - 1]
    user_result.save()
    query.delete_message(timeout=1)
    time.sleep(2)
    context.bot.send_message(chat_id=user.id,
                             text=msg.test_like.get(lang.uz_latn),
                             parse_mode='HTML',
                             reply_markup=kb.number(10))
    return st.test_like


def test_like(update: Update, context: CallbackContext):
    user = update.effective_user
    query = update.callback_query
    context.chat_data['number'] = query.data
    query.delete_message(timeout=1)
    TestEvaluation.objects.create(
        user=User.objects.get(chat_id=user.id),
        gradge=query.data
    )
    query.delete_message(timeout=1)
    context.bot.send_message(chat_id=user.id,
                             text=msg.choose_menu.get(lang.uz_latn),
                             parse_mode='HTML',
                             reply_markup=kb.base(lang.uz_latn))
    return st.menu


def test_evaluation(update: Update, context: CallbackContext):
    user = update.effective_user
    query = update.callback_query
    TestEvaluation.objects.create(
        user=User.objects.get(chat_id=user.id),
        gradge=query.data
    )
    query.delete_message(timeout=1)
    context.bot.send_message(chat_id=user.id,
                             text=msg.choose_menu.get(lang.uz_latn),
                             parse_mode='HTML',
                             reply_markup=kb.base(lang.uz_latn))
    return st.menu


def statistics(update: Update, context: CallbackContext):
    user = update.effective_user
    channels = Channel.objects.filter(status=True)
    is_subscribed_ = is_subscribed(channels, user.id)
    if is_subscribed_ is False:
        time.sleep(0.7)
        return is_not_subscribed(update, context)
    user_results = UserResult.objects.filter(user=User.objects.get(chat_id=user.id))
    if user_results.exists():
        result = user_results.order_by('-date_of_created')[0:5]
    else:
        result = list()
    stats_msg = "🫵🏻 <b>Sizning oxirgi 5 ta test natijangiz:</b>\n\n"
    if not result:
        stats_msg = "Yo'q\n\n"
    for item in result:
        stats_msg += f"<code>{item.category.name}:</code> {item.date_of_created.strftime('%d.%m.%Y')}\n"
    global_stats = "\n\n🌎 <b>Bu umumiy Statistika</b>\n\n"
    for item in Category.objects.all():
        count = UserResult.objects.filter(category=item).count()
        global_stats += f"<code>{item.name}:</code> {count}\n"
    result_msg = stats_msg + global_stats
    context.bot.send_message(chat_id=user.id, text=result_msg, parse_mode='HTML',
                             reply_markup=kb.base(lang.uz_latn))
    return st.menu


def telegraph(update: Update, context: CallbackContext):
    user = update.effective_user
    channels = Channel.objects.filter(status=True)
    is_subscribed_ = is_subscribed(channels, user.id)
    if is_subscribed_ is False:
        time.sleep(0.7)
        return is_not_subscribed(update, context)
    context.bot.send_message(chat_id=user.id, text=msg.telegraph_txt.get(lang.uz_latn),
                             parse_mode='HTML',
                             reply_markup=kb.base(lang.uz_latn))
    return st.menu


def echo(update: Update, context: CallbackContext):
    update.message.copy(chat_id=update.message.chat_id,
                        )
    return st.menu
