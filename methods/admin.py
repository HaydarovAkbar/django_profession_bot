from time import sleep
from telegram.ext import CallbackContext
from telegram import Update
from states import StatesBase as st
from decouple import config
from django.conf import settings
from static_files.lang import Language as lang
from static_files.admin import MessageText as adm_msg
from db.models import User, Channel, Admin, Category, Reklama, Question
from keyboards.admin_keyboards import Button as adm_kb
import telebot

bot_help = telebot.TeleBot(settings.TOKEN)
status_number = int(config('NUMBER_OF_USERS'))


def admin(update: Update, context: CallbackContext):
    user = update.effective_user
    if Admin.objects.filter(chat_id=user.id).exists():
        update.message.reply_text(text=adm_msg.menu.get(lang.uz_latn).replace('%admin%', user.full_name),
                                  reply_markup=adm_kb.menu(lang.uz_latn))
        return st.admin


def insert_data(update: Update, context: CallbackContext):
    photo, caption = update.message.photo[-1].file_id, update.message.caption
    key_a, key_b = caption.split(',')
    Question.objects.create(
        categories_a=key_a,
        categories_b=key_b,
        image_url=photo
    )

    update.message.reply_text(text="Ma'lumotlar bazasiga muvaffaqiyatli qo'shildi")
    return st.help


def back_user(update, context):
    user = update.effective_user
    if Admin.objects.filter(chat_id=user.id).exists():
        update.message.reply_text(text=adm_msg.menu.get(lang.uz_latn).replace('%admin%', user.full_name),
                                  reply_markup=adm_kb.menu(lang.uz_latn))
        return st.admin


def reklama(update, context):
    update.message.reply_html(text=adm_msg.choose_type.get(lang.uz_latn),
                              reply_markup=adm_kb.rek_type(lang.uz_latn))
    return st.reklama


def reklama_type(update, context):
    update.message.reply_html(text=adm_msg.inline_button.get(lang.uz_latn), reply_markup=adm_kb.back(lang.uz_latn))
    return st.inline_button


def get_button_link(update: Update, context: CallbackContext):
    text = update.message.text
    batton_lists = []
    batton_list = [item for item in text.split(' - ')]
    for item in batton_list:
        if '\n' in item:
            for i in item.split('\n'):
                batton_lists.append(i)
        else:
            batton_lists.append(item)
    context.chat_data['buttons'] = batton_lists
    rek_txt = """
<b>Reklama xabarini yuboring!</b> 

Forward Message (buning uchun xabarni forward qiling va kanalga botni admin qiling)
"""
    update.message.reply_html(
        text=rek_txt,
        reply_markup=adm_kb.back(lang.uz_latn))
    return st.send_ads


def get_not_link_batton(update: Update, context: CallbackContext):
    batton_lists = list()
    context.chat_data['buttons'] = batton_lists
    rek_txt = """
    <b>Reklama xabarini yuboring!</b> 

    Forward Message (buning uchun xabarni forward qiling va kanalga botni admin qiling)
    """
    update.message.reply_html(
        text=rek_txt,
        reply_markup=adm_kb.back(lang.uz_latn))
    return st.send_ads


def send_aktiv_user_to_admins(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    aktiv_count = context.chat_data['aktiv']
    all_count = context.chat_data['all']
    admin_txt = f"<b>Xabaringiz:\n\n<code> {all_count}</code> obunachidan --> <code>{aktiv_count}</code> obunachiga yuborildi\n\n🕐 Yuborish davom ettirilmoqda...</b>"
    end_txt = f"<b>Xabaringiz:\n\n<code>{all_count}</code> obunachidan --> <code>{aktiv_count}</code> obunachiga yuborildi\n\n✅ Yuborish yakunlandi...</b>"
    for admin in Admin.objects.all():
        try:

            send_stats_to_admin = end_txt if context.chat_data['ended'] else admin_txt
            context.bot.send_message(chat_id=admin.chat_id, text=send_stats_to_admin, parse_mode="HTML")
        except Exception:
            pass
    if context.chat_data['ended']:
        Reklama.objects.create(
            owner_id=Admin.objects.get(chat_id=user_id),
            send_user=all_count,
            aktiv_user=aktiv_count,
        )
    return st.menu


def send_reklama_text(update: Update, context: CallbackContext):
    rek_text = update.message.text
    aktiv_count, stats_count = 0, 0
    context.bot.send_message(chat_id=update.effective_user.id,
                             text=f"Xabar yuborilmoqda...\n\nBiroz kuting har {status_number} ta foydalanuvchiga yuborib bo'lib statistika jo'natiladi!")
    context.chat_data['ended'] = False
    all_user = User.objects.all()
    all_user_count = all_user.count()
    if context.chat_data['buttons']:
        for user in all_user:
            stats_count += 1
            try:
                if stats_count % status_number == 0:
                    context.chat_data['aktiv'] = aktiv_count
                    context.chat_data['all'] = all_user_count
                    send_aktiv_user_to_admins(update, context)
                if '#firstname' in rek_text:
                    _rek_text = rek_text.replace('#firstname', user.fullname)
                    update.message.bot.send_message(chat_id=user.chat_id,
                                                    message=update.message,
                                                    reply_markup=adm_kb.link_button(context.chat_data['buttons']))
                else:
                    update.message.copy(chat_id=user.chat_id,
                                        reply_markup=adm_kb.link_button(context.chat_data['buttons']))
                sleep(0.07)
                aktiv_count += 1
            except Exception:
                pass
    else:
        for user in all_user:
            stats_count += 1
            try:
                if stats_count % status_number == 0:
                    context.chat_data['aktiv'] = aktiv_count
                    context.chat_data['all'] = all_user_count
                    send_aktiv_user_to_admins(update, context)
                if '#firstname' in rek_text:
                    _rek_text = rek_text.replace('#firstname', user.fullname)
                    context.bot.send_message(chat_id=user.chat_id,
                                             text=_rek_text, )
                else:
                    update.message.copy(chat_id=user.chat_id)
                sleep(0.07)
                aktiv_count += 1
            except Exception:
                pass

    context.chat_data['ended'] = True
    context.chat_data['all'] = stats_count
    context.chat_data['aktiv'] = aktiv_count
    return send_aktiv_user_to_admins(update, context)


def send_reklama_photo(update: Update, context: CallbackContext):
    photo, caption = update.message.photo[-1].file_id, update.message.caption
    aktiv_count, stats_count = 0, 0
    context.bot.send_message(chat_id=update.effective_user.id,
                             text=f"Xabar yuborilmoqda...\n\nBiroz kuting har {status_number} ta foydalanuvchiga yuborib bo'lib statistika jo'natiladi!")
    context.chat_data['ended'] = False
    all_user = User.objects.all()
    all_user_count = all_user.count()

    if context.chat_data['buttons']:
        for user in all_user:
            stats_count += 1
            try:
                if stats_count % status_number == 0:
                    context.chat_data['aktiv'] = aktiv_count
                    context.chat_data['all'] = all_user_count
                    send_aktiv_user_to_admins(update, context)
                if "#firstname" in caption:
                    _caption = caption.replace('#firstname', user.fullname)
                    update.message.bot.send_photo(chat_id=user.chat_id,
                                                  photo=photo,
                                                  caption=_caption,
                                                  disable_notification=False,
                                                  reply_markup=adm_kb.link_button(context.chat_data['buttons']))
                else:
                    update.message.copy(chat_id=user.chat_id,
                                        reply_markup=adm_kb.link_button(context.chat_data['buttons']))
                sleep(0.09)
                aktiv_count += 1
            except Exception:
                pass
    else:
        for user in all_user:
            stats_count += 1
            try:
                if stats_count % status_number == 0:
                    context.chat_data['aktiv'] = aktiv_count
                    context.chat_data['all'] = all_user_count
                    send_aktiv_user_to_admins(update, context)
                if "#firstname" in caption:
                    _caption = caption.replace('#firstname', user.fullname)
                    update.message.bot.send_photo(chat_id=user.chat_id,
                                                  photo=photo,
                                                  caption=_caption)
                else:
                    update.message.copy(chat_id=user.chat_id)
                sleep(0.07)
                aktiv_count += 1
            except Exception:
                pass
    context.chat_data['ended'] = True
    context.chat_data['all'] = stats_count
    context.chat_data['aktiv'] = aktiv_count
    return send_aktiv_user_to_admins(update, context)


def send_reklama_video(update: Update, context: CallbackContext):
    video, caption = update.message.video.file_id, update.message.caption
    aktiv_count, stats_count = 0, 0
    context.bot.send_message(chat_id=update.effective_user.id,
                             text=f"Xabar yuborilmoqda...\n\nBiroz kuting har {status_number} ta foydalanuvchiga yuborib bo'lib statistika jo'natiladi!")
    context.chat_data['ended'] = False
    all_user = User.objects.all()
    all_user_count = all_user.count()

    if context.chat_data['buttons']:
        for user in all_user:
            stats_count += 1
            try:
                if stats_count % status_number == 0:
                    context.chat_data['aktiv'] = aktiv_count
                    context.chat_data['all'] = all_user_count
                    send_aktiv_user_to_admins(update, context)
                if "#firstname" in caption:
                    _caption = caption.replace('#firstname', user.fullname)
                    update.message.bot.send_video(chat_id=user.chat_id,
                                                  video=video,
                                                  caption=_caption,
                                                  disable_notification=False,
                                                  reply_markup=adm_kb.link_button(context.chat_data['buttons']))
                else:
                    update.message.copy(chat_id=user.chat_id,
                                        reply_markup=adm_kb.link_button(context.chat_data['buttons']))
                sleep(0.09)
                aktiv_count += 1
            except Exception:
                pass
    else:
        for user in all_user:
            stats_count += 1
            try:
                if stats_count % status_number == 0:
                    context.chat_data['aktiv'] = aktiv_count
                    context.chat_data['all'] = all_user_count
                    send_aktiv_user_to_admins(update, context)
                if "#firstname" in caption:
                    _caption = caption.replace('#firstname', user.fullname)
                    update.message.bot.send_video(chat_id=user.chat_id,
                                                  video=video,
                                                  caption=_caption)
                else:
                    update.message.copy(chat_id=user.chat_id)
                sleep(0.07)
                aktiv_count += 1
            except Exception:
                pass
    context.chat_data['ended'] = True
    context.chat_data['all'] = stats_count
    context.chat_data['aktiv'] = aktiv_count
    return send_aktiv_user_to_admins(update, context)


def send_reklama_audio(update: Update, context: CallbackContext):
    audio, caption = update.message.audio.file_id, update.message.caption
    aktiv_count, stats_count = 0, 0
    context.bot.send_message(chat_id=update.effective_user.id,
                             text=f"Xabar yuborilmoqda...\n\nBiroz kuting har {status_number} ta foydalanuvchiga yuborib bo'lib statistika jo'natiladi!")
    context.chat_data['ended'] = False
    all_user = User.objects.all()
    all_user_count = all_user.count()
    if context.chat_data['buttons']:
        for user in all_user:
            stats_count += 1
            try:
                if stats_count % status_number == 0:
                    context.chat_data['aktiv'] = aktiv_count
                    context.chat_data['all'] = all_user_count
                    send_aktiv_user_to_admins(update, context)
                if "#firstname" in caption:
                    _caption = caption.replace('#firstname', user.fullname)
                    update.message.bot.send_audio(chat_id=user.chat_id,
                                                  audio=audio,
                                                  caption=_caption,
                                                  disable_notification=False,
                                                  reply_markup=adm_kb.link_button(context.chat_data['buttons']))
                else:
                    update.message.copy(chat_id=user.chat_id,
                                        reply_markup=adm_kb.link_button(context.chat_data['buttons']))
                sleep(0.09)
                aktiv_count += 1
            except Exception:
                pass
    else:
        for user in all_user:
            stats_count += 1
            try:
                if stats_count % status_number == 0:
                    context.chat_data['aktiv'] = aktiv_count
                    context.chat_data['all'] = all_user_count
                    send_aktiv_user_to_admins(update, context)
                if "#firstname" in caption:
                    _caption = caption.replace('#firstname', user.fullname)
                    update.message.bot.send_audio(chat_id=user.chat_id,
                                                  audio=audio,
                                                  caption=_caption)
                else:
                    update.message.copy(chat_id=user.chat_id)
                sleep(0.07)
                aktiv_count += 1
            except Exception:
                pass
    context.chat_data['ended'] = True
    context.chat_data['all'] = stats_count
    context.chat_data['aktiv'] = aktiv_count
    return send_aktiv_user_to_admins(update, context)


def send_reklama_voice(update: Update, context: CallbackContext):
    voice, caption = update.message.voice.file_id, update.message.caption
    aktiv_count, stats_count = 0, 0
    context.bot.send_message(chat_id=update.effective_user.id,
                             text=f"Xabar yuborilmoqda...\n\nBiroz kuting har {status_number} ta foydalanuvchiga yuborib bo'lib statistika jo'natiladi!")
    context.chat_data['ended'] = False
    if context.chat_data['buttons']:
        for user in User.objects.all():
            stats_count += 1
            try:
                if stats_count % status_number == 0:
                    context.chat_data['aktiv'] = aktiv_count
                    context.chat_data['all'] = stats_count
                    send_aktiv_user_to_admins(update, context)
                if "#firstname" in caption:
                    _caption = caption.replace('#firstname', user.fullname)
                    update.message.bot.send_voice(chat_id=user.chat_id,
                                                  voice=voice,
                                                  caption=_caption,
                                                  disable_notification=False,
                                                  reply_markup=adm_kb.link_button(context.chat_data['buttons']))
                else:
                    update.message.copy(chat_id=user.chat_id,
                                        reply_markup=adm_kb.link_button(context.chat_data['buttons']))
                sleep(0.09)
                aktiv_count += 1
            except Exception:
                pass
    else:
        for user in User.objects.all():
            stats_count += 1
            try:
                if stats_count % status_number == 0:
                    context.chat_data['aktiv'] = aktiv_count
                    context.chat_data['all'] = stats_count
                    send_aktiv_user_to_admins(update, context)
                if "#firstname" in caption:
                    _caption = caption.replace('#firstname', user.fullname)
                    update.message.bot.send_voice(chat_id=user.chat_id,
                                                  voice=voice,
                                                  caption=_caption)
                else:
                    update.message.copy(chat_id=user.chat_id)
                sleep(0.07)
                aktiv_count += 1
            except Exception:
                pass
    context.chat_data['ended'] = True
    context.chat_data['all'] = stats_count
    context.chat_data['aktiv'] = aktiv_count
    return send_aktiv_user_to_admins(update, context)


def get_forward_message(update: Update, context: CallbackContext):
    forward_from_id = update.message.forward_from_chat.id if not update.message.forward_from_chat is None else update.message.forward_from.id
    aktiv_count, st_count = 0, 0
    try:
        bot_help.forward_message(chat_id=update.effective_user.id,
                                 from_chat_id=forward_from_id,
                                 message_id=update.message.forward_from_message_id)
    except Exception:
        context.bot.send_message(chat_id=update.effective_user.id,
                                 text="❗️ Xabar yuborilmadi\n\nSababi forward xabar yuborish uchun bot kanalda admin bo'lishi kerak!!!")
        return st.menu
    context.bot.send_message(chat_id=update.effective_user.id,
                             text=f"Xabar yuborilmoqda...\n\nBiroz kuting har {status_number} ta foydalanuvchiga yuborib bo'lib statistika jo'natiladi!")
    context.chat_data['ended'] = False
    all_user = User.objects.all()
    all_user_count = all_user.count()
    for user in all_user:
        st_count += 1
        try:
            if st_count % status_number == 0:
                context.chat_data['aktiv'] = aktiv_count
                context.chat_data['all'] = all_user_count
                send_aktiv_user_to_admins(update, context)
            bot_help.forward_message(chat_id=user.chat_id,
                                     from_chat_id=forward_from_id,
                                     message_id=update.message.forward_from_message_id)
            sleep(0.5)
            aktiv_count += 1
        except Exception:
            pass
    context.chat_data['all'] = st_count
    context.chat_data['ended'] = True
    context.chat_data['aktiv'] = aktiv_count
    return send_aktiv_user_to_admins(update, context)


def admin_stats(update: Update, context: CallbackContext):
    user_count = User.objects.all().count()
    aktiv_count = Reklama.objects.last().aktiv_count
    stats_msg = f"""Botning statistikasi:\n\n
👤 Foydalanuvchilar soni: {user_count}

🕓 Oxirgi reklama natijasiga ko'ra:

🧑‍🦲 Aktiv foydalanuvchilar soni: {aktiv_count}
"""
    context.bot.send_message(chat_id=update.effective_user.id,
                             text=stats_msg,
                             reply_markup=adm_kb.menu(lang.uz_latn))
    return st.menu


# Admin qo'shish funkisayalari
def add_admin(update: Update, context: CallbackContext):
    update.message.reply_html(text=adm_msg.enter_new_admin.get(lang.uz_latn),
                              reply_markup=adm_kb.back(lang.uz_latn))
    return st.new_admin


def get_new_admin_chat_id(update, context):
    new_admin = update.message.text
    try:
        Admin.objects.create(
            chat_id=new_admin,
        )
    except Exception:
        pass
    update.message.reply_html(text=adm_msg.success.get(lang.uz_latn),
                              reply_markup=adm_kb.menu(lang.uz_latn))
    return st.menu


def admin_lists(update, context):
    try:
        name = update.message.from_user.first_name
        admin_text = name + "Adminlar ro'yxati:)\n\n"
        for item in Admin.objects.all():
            admin_text += f"{item.pk}. chat_id={item.chat_id}\n"
        admin_text += "\n\nO'chirmoqchi bo'lsangiz adminni id raqamini yuboring:)\n\nMasalan: 1"
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=admin_text,
                                 reply_markup=adm_kb.back(lang.uz_latn))
    except Exception:
        pass
    return st.del_admin


def del_admin(update, context):
    pk_admin = update.message.text
    if pk_admin.isdigit():
        try:
            Admin.objects.get(pk=pk_admin).delete()
            update.message.reply_html(text=adm_msg.success.get(lang.uz_latn),
                                      reply_markup=adm_kb.menu(lang.uz_latn))
        except Exception:
            update.message.reply_html(text=adm_msg.continue_msg.get(lang.uz_latn),
                                      reply_markup=adm_kb.menu(lang.uz_latn))
    return st.menu


def add_channel(update: Update, context: CallbackContext):
    update.message.reply_html(adm_msg.add_channel_id.get(lang.uz_latn), reply_markup=adm_kb.back(lang.uz_latn))
    return st.add_channel_n


def add_channel_id(update: Update, context: CallbackContext):
    channel_id = update.message.text
    if not channel_id[1:].isdigit():
        channel_id_bug_txt = {
            "uz": f"Siz kiritgan Channel ID: 🚫 <code>{channel_id}</code> Xato\n\n<b>Siz Channel ID raqamini kiritishingiz kerak edi </b>",
            "ru": f"Siz kiritgan Channel ID: 🚫 <code>{channel_id}</code> Xato\n\n<b>Siz Channel ID raqamini kiritishingiz kerak edi </b>",
            "en": f"Siz kiritgan Channel ID: 🚫 <code>{channel_id}</code> Xato\n\n<b>Siz Channel ID raqamini kiritishingiz kerak edi </b>",
        }
        update.message.reply_html(channel_id_bug_txt.get('uz'))
        return st.add_channel_n
    context.chat_data['channel_id'] = channel_id
    update.message.reply_html(adm_msg.add_channel_name.get(lang.uz_latn), reply_markup=adm_kb.back(lang.uz_latn))
    return st.add_channel_name


def add_channel_name(update: Update, context: CallbackContext):
    channel_name = update.message.text
    context.chat_data['channel_name'] = channel_name
    update.message.reply_html(adm_msg.add_channel_name.get(lang.uz_latn), reply_markup=adm_kb.back(lang.uz_latn))
    return st.add_channel_link


def add_channel_link(update: Update, context: CallbackContext):
    channel_url = update.message.text
    if not 'https://t.me/' in channel_url:
        channel_id_bug_txt = {
            "uz": f"Siz kiritgan Kanal linki: 🚫 <code>{channel_url}</code> Xato\n\n<b>Siz Kanal linkini kiritishingiz kerak edi: https://t.me/HaydarovAkbar </b>",
            "ru": f"Siz kiritgan Kanal linki: 🚫 <code>{channel_url}</code> Xato\n\n<b>Siz Kanal linkini kiritishingiz kerak edi: https://t.me/HaydarovAkbar </b>",
            "en": f"Siz kiritgan Kanal linki: 🚫 <code>{channel_url}</code> Xato\n\n<b>Siz Kanal linkini kiritishingiz kerak edi: https://t.me/HaydarovAkbar </b>",
        }
        update.message.reply_html(channel_id_bug_txt.get('uz'))
        return st.add_channel_link
    channel_name, channel_id = context.chat_data['channel_name'], context.chat_data['channel_id']
    Channel.objects.create(
        name=channel_name,
        channel_id=channel_id,
        channel_url=channel_url,
        owner_id=Admin.objects.get(chat_id=update.message.from_user.id)
    )
    update.message.reply_html(adm_msg.add_channel_succesfuly.get(lang.uz_latn), reply_markup=adm_kb.back(lang.uz_latn))
    return st.menu


def status_channels(update, context):
    """Channels status update"""
    data_channel = Channel.objects.all()
    data_text = "Barcha kanallar ro'yxati bilan tanishing:\n\n"
    for item in data_channel:
        status_name = {True: "<code>✅ Aktiv</code>", False: "<code>❌ Passiv</code>"}
        data_text += f"N: {item.id}). <code>NAME</code>: {item.name} <code>ID</code>: {item.channel_id}\n <code>DATE</code> {item.date_of_created} 🔹 <code>STATUS</code>: {status_name.get(item.status, 'nomalum')}\n"
    update.message.reply_html(data_text)
    update.message.reply_html(adm_msg.channel_status_text.get(lang.uz_latn), reply_markup=adm_kb.back(lang.uz_latn))
    return st.status_channel


def channel_status(update: Update, context: CallbackContext):
    message_ = update.message.text
    if not message_.isdigit():
        update.message.reply_html(adm_msg.continue_msg.get(lang.uz_latn))
        return st.menu
    context.chat_data['channel_id'] = message_
    data_text = "Kanal holatini tanlang"
    update.message.reply_text(data_text, reply_markup=adm_kb.status(lang.uz_latn))
    return st.status_type


def status_edit_channel(update: Update, context: CallbackContext):
    try:
        channel = Channel.objects.get(pk=context.chat_data['channel_id'])
        if channel.status is True:
            channel.status = False
        else:
            channel.status = True
        channel.save()
        update.message.reply_html(adm_msg.update_channel_data_succesfuly.get(lang.uz_latn),
                                  reply_markup=adm_kb.back(lang.uz_latn))
    except Channel.DoesNotExist:
        update.message.reply_html(adm_msg.continue_msg.get(lang.uz_latn))
    return st.menu
