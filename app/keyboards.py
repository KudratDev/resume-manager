from telegram import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)


def language_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [[KeyboardButton("O'zbekcha"), KeyboardButton("Русский")]],
        resize_keyboard=True,
        one_time_keyboard=False,
    )


def contact_keyboard(lang: str) -> ReplyKeyboardMarkup:
    label = "Kontaktingizni yuboring" if lang == "uz" else "Отправьте контакт"
    btn = KeyboardButton(label, request_contact=True)
    return ReplyKeyboardMarkup([[btn]], resize_keyboard=True, one_time_keyboard=True)


def main_menu_keyboard(lang: str) -> ReplyKeyboardMarkup:
    if lang == "uz":
        buttons = ["Resume yaratish", "Yuborilgan rezumelar", "Tilni qayta tanlash"]
    else:
        buttons = ["Создать резюме", "Отправленные резюме", "Выбрать язык заново"]
    return ReplyKeyboardMarkup([buttons], resize_keyboard=True)


def yes_no_keyboard(lang: str) -> ReplyKeyboardMarkup:
    if lang == "uz":
        buttons = [KeyboardButton("Ha"), KeyboardButton("Yo'q")]
    else:
        buttons = [KeyboardButton("Да"), KeyboardButton("Нет")]
    return ReplyKeyboardMarkup([buttons], resize_keyboard=True)


def remove_keyboard() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()
