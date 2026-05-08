import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "8663926765:AAEVQ40hTjCsCqoO0nyY3_j2tQcgR5TQZGE")
DATABASE_URL = os.getenv("DATABASE_URL", "")

QUESTIONS_UZ = [
    "Familiya va ismingizni to'ldiring",
    "Tug'ilgan sana (kk/oo/yyyy)",
    "Ta'lim darajangizni tanlang",
    "Jinsingizni tanlang",
    "Oilaviy holatingizni tanlang",
    "Til darajangizni belgilang",
    "Kutilayotgan ish haqi miqdorini kiriting",
    "Nogironligingiz bormi?",
    "Vakansiya haqida qayerdan bildingiz?",
    "Java (Spring) texnologiyasi bo'yicha ish tajribangiz (yillar)",
    "Dasturlash bo'yicha sertifikatlaringiz bormi?",
    "IT sohasida katta ma'lumotlar bilan ishlash tajribangiz bormi?",
    "Tajribangizdagi eng esda qolarli loyiha haqida aytib bering",
    "Qanday ish formatini afzal ko'rasiz?",
    "CV faylingizni yuboring (ixtiyoriy)",
    "Ish turini tanlang",
]

QUESTIONS_RU = [
    "Укажите вашу фамилию и имя",
    "Дата рождения (дд/мм/гггг)",
    "Укажите уровень образования",
    "Укажите ваш пол",
    "Укажите семейное положение",
    "Укажите уровень владения языками",
    "Укажите ожидания по зарплате",
    "Имеется ли у вас инвалидность?",
    "Откуда вы узнали о вакансии?",
    "Опыт работы с Java Spring (в годах)",
    "Есть ли у вас сертификаты по программированию?",
    "Есть ли у вас опыт работы с Big Data?",
    "Расскажите кратко о вашем лучшем проекте",
    "Какой формат работы вам ближе?",
    "Загрузите ваше CV (необязательно)",
    "Укажите тип занятости",
]

TOTAL_QUESTIONS = 16
