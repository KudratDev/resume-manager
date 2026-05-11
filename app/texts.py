import json

CHOOSE_LANG = "Iltimos, tilni tanlang \\ Пожалуйста, выберите язык:"

SEND_CONTACT = {
    "uz": "Ro'yxatdan o'tish uchun telefon raqamingizni yuboring:",
    "ru": "Пожалуйста, отправьте ваш контакт для регистрации:",
}

CHOOSE_ACTION = {
    "uz": "Iltimos, tanlang:",
    "ru": "Пожалуйста, выберите:",
}

BLOCKED = {
    "uz": "Siz allaqachon anketa to'ldirdingiz. Iltimos, keyinroq urinib ko'ring.",
    "ru": "Вы уже заполнили анкету. Пожалуйста, повторите попытку позже.",
}

RESUME_SAVED = {
    "uz": (
        "✅ Rahmat!\n\n"
        "Sizning anketangiz muvaffaqiyatli saqlandi.\n"
        "HR mutaxassislarimiz tez orada siz bilan bog'lanadi.\n\n"
        "Omad! 🍀"
    ),
    "ru": (
        "✅ Благодарим вас!\n\n"
        "Ваша анкета успешно сохранена.\n"
        "Наш HR-специалист свяжется с вами в ближайшее время.\n\n"
        "Удачи! 🍀"
    ),
}

NO_RESUME = {
    "uz": "Sizning rezumengiz topilmadi.",
    "ru": "Ваше резюме не найдено.",
}

PHONE_LABEL = {
    "uz": "Sizning telefon raqamingiz: ",
    "ru": "Ваш номер телефона: ",
}

ENTER_PHONE = {
    "uz": "Aloqa uchun telefon raqamingizni kiriting:\n(+998 bilan boshlang, masalan: +998901234567)",
    "ru": "Введите номер телефона для связи:\n(начните с +998, например: +998901234567)",
}

ENTER_PHONE = {
    "uz": "Aloqa uchun telefon raqamingiz:",
    "ru": "Телефон для связи:",
}

ERROR = {
    "uz": "Xatolik yuz berdi. Keyinroq urinib ko'ring.",
    "ru": "Произошла ошибка. Попробуйте позже.",
}

MAIN_WELCOME = {
    "uz": "Asosiy menyu. Iltimos, tanlang:",
    "ru": "Главное меню. Пожалуйста, выберите:",
}

ABOUT_COMPANY = {
    "uz": (
        "UrbanLab — urbanizatsiya, uy-joy va davlat xizmatlarini raqamlashtirish "
        "sohasida faoliyat yurituvchi tashkilot.\n\n"
        "Biz Milliy Qo'mita tizimida faoliyat yuritamiz va davlat uy-joy siyosatini amalga oshiramiz."
    ),
    "ru": (
        "UrbanLab — организация, работающая в сфере цифровизации урбанизации, "
        "жилья и государственных сервисов.\n\n"
        "Мы работаем в системе Национального Комитета и реализуем "
        "государственную политику в сфере жилья."
    ),
}

INSTRUCTION = {
    "uz": (
        "Anketani to'ldirish bo'yicha ko'rsatma:\n\n"
        "Men sizga bir nechta savol beraman.\n"
        "Har biriga to'liq javob bering.\n"
        "Oxirida tayyor rezyume HR-mutaxassislarimizga yuboriladi."
    ),
    "ru": (
        "Инструкция по заполнению анкеты:\n\n"
        "Я задам вам ряд вопросов.\n"
        "Ответьте на каждый полностью.\n"
        "В конце готовое резюме будет отправлено нашим HR-специалистам."
    ),
}

CHOOSE_VACANCY = {
    "uz": "Qaysi vakansiya sizni qiziqtiradi?\n\nMa'lumotni ko'rish uchun quyidagini tanlang:",
    "ru": "Какая вакансия вас интересует?\n\nВыберите для просмотра информации нижеследующие:",
}

VACANCY_DESC = {
    "Business Analyst": {
        "uz": (
            "📊 Business Analyst\n\n"
            "Vazifalar:\n"
            "• Biznes jarayonlarni tahlil qilish\n"
            "• Hujjatlarni tayyorlash\n"
            "• Ishlab chiqish jamoasi bilan hamkorlik\n\n"
            "Talablar:\n"
            "• Oliy ma'lumot\n"
            "• 1 yildan ortiq tajriba\n"
            "• Agile / Scrum\n"
            "• Excel, SQL — afzallik\n\n"
            "Sharoitlar:\n"
            "• Rasmiy ish joyi\n"
            "• KPI bonuslari\n"
            "• Toshkent markazida ofis"
        ),
        "ru": (
            "📊 Business Analyst\n\n"
            "Обязанности:\n"
            "• Анализ бизнес-процессов\n"
            "• Подготовка документации\n"
            "• Работа с командой разработки\n\n"
            "Требования:\n"
            "• Высшее образование\n"
            "• Опыт от 1 года\n"
            "• Agile / Scrum\n"
            "• Excel, SQL — плюс\n\n"
            "Условия:\n"
            "• Официальное трудоустройство\n"
            "• KPI бонусы\n"
            "• Офис в центре Ташкента"
        ),
    },
    "GIS Analyst": {
        "uz": (
            "🗺️ GIS Analyst\n\n"
            "Vazifalar:\n"
            "• GIS tizimlari bilan ishlash\n"
            "• Xaritalar va qatlamlar yaratish\n"
            "• Geodata integratsiyasi\n\n"
            "Talablar:\n"
            "• QGIS / ArcGIS\n"
            "• GeoJSON / WMS / WFS\n"
            "• SQL / Python\n\n"
            "Sharoitlar:\n"
            "• Davlat ma'lumotlari bilan ishlash\n"
            "• KPI bonuslari\n"
            "• Kasbiy o'sish"
        ),
        "ru": (
            "🗺️ GIS Analyst\n\n"
            "Обязанности:\n"
            "• Работа с GIS системами\n"
            "• Создание карт и слоёв\n"
            "• Интеграция геоданных\n\n"
            "Требования:\n"
            "• QGIS / ArcGIS\n"
            "• GeoJSON / WMS / WFS\n"
            "• SQL / Python basics\n\n"
            "Условия:\n"
            "• Работа с госданными\n"
            "• KPI бонусы\n"
            "• Профессиональный рост"
        ),
    },
}


def resume_text(resume: dict, lang: str) -> str:
    def v(key, fallback):
        val = resume.get(key)
        return val if val else fallback

    langs_raw = resume.get("languages")
    if isinstance(langs_raw, str):
        try:
            langs_dict = json.loads(langs_raw)
        except Exception:
            langs_dict = {}
    elif isinstance(langs_raw, dict):
        langs_dict = langs_raw
    else:
        langs_dict = {}

    if lang == "uz":
        na = "Mavjud emas"
        langs_str = (
            f"RU: {langs_dict.get('russian', na)}, "
            f"UZ: {langs_dict.get('uzbek', na)}, "
            f"EN: {langs_dict.get('english', na)}, "
        )
        return (
            "Sizning yuborilgan resume ma'lumotlaringiz:\n\n"
            f"Ism: {v('name', na)}\n"
            f"Tug'ilgan sana: {v('birthdate', na)}\n"
            f"Telefon: {v('phone', na)}\n"
            f"Vakansiya: {v('vacancy', na)}\n"
            f"Ta'lim: {v('education', na)}\n"
            f"Jins: {v('gender', na)}\n"
            f"Oilaviy holat: {v('marital_status', na)}\n"
            f"Tillar: {langs_str}\n"
            f"Kutilayotgan ish haqi: {v('salary_expectation', na)}\n"
            f"Nogironlik: {v('disability', na)}\n"
            f"Manba: {v('vacancy_source', na)}\n"
            f"Ish tajribasi (Java): {v('experience', na)}\n"
            f"Sertifikatlar: {v('certificates', na)}\n"
            f"Big Data tajribasi: {v('big_data_experience', na)}\n"
            f"Eng yaxshi loyiha: {v('memorable_project', na)}\n"
            f"Ish formati: {v('employment_format', na)}\n"
            f"Ish turi: {v('employment_type', na)}"
        )
    else:
        na = "Нет данных"
        langs_str = (
            f"RU: {langs_dict.get('russian', na)}, "
            f"UZ: {langs_dict.get('uzbek', na)}, "
            f"EN: {langs_dict.get('english', na)}, "
        )
        return (
            "Ваше отправленное резюме:\n\n"
            f"Имя: {v('name', na)}\n"
            f"Дата рождения: {v('birthdate', na)}\n"
            f"Телефон: {v('phone', na)}\n"
            f"Вакансия: {v('vacancy', na)}\n"
            f"Образование: {v('education', na)}\n"
            f"Пол: {v('gender', na)}\n"
            f"Семейное положение: {v('marital_status', na)}\n"
            f"Языки: {langs_str}\n"
            f"Ожидания по зарплате: {v('salary_expectation', na)}\n"
            f"Инвалидность: {v('disability', na)}\n"
            f"Источник: {v('vacancy_source', na)}\n"
            f"Опыт Java Spring: {v('experience', na)}\n"
            f"Сертификаты: {v('certificates', na)}\n"
            f"Опыт Big Data: {v('big_data_experience', na)}\n"
            f"Лучший проект: {v('memorable_project', na)}\n"
            f"Формат работы: {v('employment_format', na)}\n"
            f"Тип занятости: {v('employment_type', na)}"
        )
