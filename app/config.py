import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "8663926765:AAEVQ40hTjCsCqoO0nyY3_j2tQcgR5TQZGE")
DATABASE_URL = os.getenv("DATABASE_URL", "")

QUESTIONS_UZ = [
    "Familiya va ismingizni yozing",
    "Tug'ilgan sana (kk/oo/yyyy)",
    "Java (spring) texnologiyasi bo'yicha ish tajribangiz (yillar)",
    "Dasturlash bo'yicha malaka oshirish sertifikatlariga egamisiz?",
    "IT sohasida katta ma'lumotlar bilan ishlash tajribangiz bormi?",
    "Tajribangizdagi eng esda qolarli loyiha haqida qisqacha aytib bering",
    "Siz qisqa muddatli loyihalarda (masalan, 2 oy) aniq vazifalar uchun to'lanadigan ishlarni bajarishni ma'qul ko'rasizmi yoki uzoq muddatli, barqaror maoshga ega bo'lgan ishni afzal ko'rasizmi?",
]

QUESTIONS_RU = [
    "Укажите вашу фамилию и имя",
    "Дата рождения (дд/мм/гггг)",
    "Опыт работы с технологией Java (spring) (годы)",
    "Есть ли у вас сертификаты по повышению квалификации в программировании?",
    "Есть опыт работы с большими данными в IT?",
    "Расскажи кратко о самом запоминающемся проекте из твоего опыта",
    "Вам интереснее работать над краткосрочными проектами (например, по 2 месяца) с оплатой за конкретные задачи или вы предпочитаете стабильную работу на долгосрочной основе с фиксированной зарплатой?",
]
