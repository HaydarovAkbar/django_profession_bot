from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup


class Keyboards:
    language_button = InlineKeyboardMarkup([
        [InlineKeyboardButton(text="O'zbekcha", callback_data="uz_latn")],
        [InlineKeyboardButton(text="Русский", callback_data="ru")],
        [InlineKeyboardButton(text="Ўзбекча", callback_data="uz_cyrl")]]
    )

    sex_button = InlineKeyboardMarkup([
        [InlineKeyboardButton(text="Erkak", callback_data='man')],
        [InlineKeyboardButton(text="Ayol", callback_data="girl")]
    ])
