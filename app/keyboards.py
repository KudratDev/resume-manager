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
        buttons = [
            ["Biz haqimizda", "Vakansiyalar"],
            ["Yuborilgan rezumelar"],
            ["Tilni qayta tanlash"],
        ]
    else:
        buttons = [
            ["О нас", "Вакансии"],
            ["Отправленные резюме"],
            ["Выбрать язык заново"],
        ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)


def yes_no_keyboard(lang: str) -> ReplyKeyboardMarkup:
    if lang == "uz":
        buttons = [KeyboardButton("Ha"), KeyboardButton("Yo'q")]
    else:
        buttons = [KeyboardButton("Да"), KeyboardButton("Нет")]
    return ReplyKeyboardMarkup([buttons], resize_keyboard=True)


def remove_keyboard() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()


def vacancy_keyboard(lang: str) -> ReplyKeyboardMarkup:
    if lang == "uz":
        buttons = [["Business Analyst", "GIS Analyst"], ["⬅️ Orqaga"]]
    else:
        buttons = [["Business Analyst", "GIS Analyst"], ["⬅️ Назад"]]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)


def education_keyboard(lang: str) -> ReplyKeyboardMarkup:
    if lang == "uz":
        buttons = ["O'rta-maxsus", "Oliy-tugallanmagan", "Oliy-tugallangan"]
    else:
        buttons = ["Средне-специальное", "Высшее-незаконченное", "Высшее-оконченное"]
    return ReplyKeyboardMarkup([buttons], resize_keyboard=True)


def gender_keyboard(lang: str) -> ReplyKeyboardMarkup:
    if lang == "uz":
        buttons = [KeyboardButton("Erkak"), KeyboardButton("Ayol")]
    else:
        buttons = [KeyboardButton("Мужской"), KeyboardButton("Женский")]
    return ReplyKeyboardMarkup([buttons], resize_keyboard=True)


def marital_keyboard(lang: str) -> ReplyKeyboardMarkup:
    if lang == "uz":
        buttons = ["Uylanganman", "Turmushga chiqqanman", "Bo'ydoqman", "Ajrashganman"]
    else:
        buttons = ["Женат", "Замужем", "Холост", "Разведена"]
    return ReplyKeyboardMarkup([buttons], resize_keyboard=True)


def language_level_keyboard(lang: str, language_name: str) -> ReplyKeyboardMarkup:
    if lang == "uz":
        prompt = f"{language_name} tili darajasi:"
        buttons = ["O'rta", "O'rta-yuqori", "Yuqori"]
    else:
        prompt = f"Уровень {language_name}:"
        buttons = ["Средний", "Средне-продвинутый", "Продвинутый"]
    return ReplyKeyboardMarkup([buttons], resize_keyboard=True)


def vacancy_source_keyboard(lang: str) -> ReplyKeyboardMarkup:
    if lang == "uz":
        return ReplyKeyboardMarkup(
            [["LinkedIn", "hh.uz", "Telegram"],
             ["Instagram", "Tanishlar orqali", "Boshqa"]],
            resize_keyboard=True,
        )
    else:
        return ReplyKeyboardMarkup(
            [["LinkedIn", "hh.uz", "Telegram"],
             ["Instagram", "Через знакомого", "Другое"]],
            resize_keyboard=True,
        )


def employment_format_keyboard(lang: str) -> ReplyKeyboardMarkup:
    if lang == "uz":
        buttons = ["Qisqa muddatli loyihalar", "Uzoq muddatli ish"]
    else:
        buttons = ["Краткосрочные проекты", "Долгосрочная работа"]
    return ReplyKeyboardMarkup([buttons], resize_keyboard=True)


def employment_type_keyboard(lang: str) -> ReplyKeyboardMarkup:
    if lang == "uz":
        buttons = ["Loyiha asosida", "Doimiy"]
    else:
        buttons = ["Проектная", "Постоянная"]
    return ReplyKeyboardMarkup([buttons], resize_keyboard=True)


def skip_keyboard(lang: str) -> ReplyKeyboardMarkup:
    label = "O'tkazib yuborish ⏭" if lang == "uz" else "Пропустить ⏭"
    return ReplyKeyboardMarkup([[label]], resize_keyboard=True)


def apply_keyboard(lang: str) -> ReplyKeyboardMarkup:
    label = "Ariza topshirish ✅" if lang == "uz" else "Подать заявку ✅"
    back = "⬅️ Orqaga" if lang == "uz" else "⬅️ Назад"
    return ReplyKeyboardMarkup([[label], [back]], resize_keyboard=True)


def start_keyboard(lang: str) -> ReplyKeyboardMarkup:
    label = "Boshlash" if lang == "uz" else "Начать"
    return ReplyKeyboardMarkup([[label]], resize_keyboard=True)
