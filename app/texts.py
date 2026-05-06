CHOOSE_LANG = "Iltimos, tilni tanlang \\ Пожалуйста, выберите язык:"

SEND_CONTACT = {
    "uz": "Iltimos, registratsiya uchun kontakt ma'lumotlaringizni yuboring:",
    "ru": "Пожалуйста, отправьте ваши контактные данные для регистрации:",
}

CHOOSE_ACTION = {
    "uz": "Iltimos, tanlang:",
    "ru": "Пожалуйста, выберите:",
}

BLOCKED = "Siz 2 daqiqa ichida boshqa harakat qilolmaysiz, iltimos, kuting."

RESUME_SAVED = {
    "uz": "Resume saqlandi!",
    "ru": "Резюме сохранено!",
}

NO_RESUME = {
    "uz": "Sizning rezumengiz topilmadi.",
    "ru": "Ваше резюме не найдено.",
}

PHONE_LABEL = {
    "uz": "Sizning telefon raqamingiz: ",
    "ru": "Ваш номер телефона: ",
}

PHONE_CONFIRM = {
    "uz": "Shu raqam bilan bog'lansak bo'ladimi?",
    "ru": "Можем ли мы связаться с вами по этому номеру?",
}

ENTER_PHONE = {
    "uz": "Aloqa uchun telefon raqamingiz:",
    "ru": "Телефон для связи:",
}

ERROR = {
    "uz": "Xatolik yuz berdi. Keyinroq urinib ko'ring.",
    "ru": "Произошла ошибка. Попробуйте позже.",
}


def resume_text(resume: dict, lang: str) -> str:
    def v(key, fallback):
        val = resume.get(key)
        return val if val else fallback

    if lang == "uz":
        na = "Mavjud emas"
        return (
            "Sizning yuborilgan resume ma'lumotlaringiz:\n\n"
            f"Ism: {v('name', na)}\n"
            f"Tug'ilgan sana: {v('birthdate', na)}\n"
            f"Telefon: {v('phone', na)}\n"
            f"Ish tajribasi: {v('experience', na)}\n"
            f"Sertifikatlar: {v('certificates', na)}\n"
            f"Katta ma'lumotlar tajribasi: {v('big_data_experience', na)}\n"
            f"Eng esda qolarli loyiha: {v('memorable_project', na)}\n"
            f"Afzal ko'rilgan ish turi: {v('preferred_job_type', na)}"
        )
    else:
        na = "Нет данных"
        return (
            "Ваше отправленное резюме:\n\n"
            f"Имя: {v('name', na)}\n"
            f"Дата рождения: {v('birthdate', na)}\n"
            f"Телефон: {v('phone', na)}\n"
            f"Опыт работы: {v('experience', na)}\n"
            f"Сертификаты: {v('certificates', na)}\n"
            f"Опыт с большими данными: {v('big_data_experience', na)}\n"
            f"Запоминающийся проект: {v('memorable_project', na)}\n"
            f"Предпочитаемый тип работы: {v('preferred_job_type', na)}"
        )
