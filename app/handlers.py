import logging
import json
import re
from datetime import datetime as dt

from app import database as db
from app import texts
from app.keyboards import (
    language_keyboard, contact_keyboard, main_menu_keyboard,
    yes_no_keyboard, remove_keyboard, vacancy_keyboard,
    education_keyboard, gender_keyboard, marital_keyboard,
    language_level_keyboard, vacancy_source_keyboard,
    employment_format_keyboard, employment_type_keyboard,
    skip_keyboard, apply_keyboard, start_keyboard,
)
from app.config import QUESTIONS_UZ, QUESTIONS_RU, TOTAL_QUESTIONS

logger = logging.getLogger(__name__)

STATE = "state"
LANG = "lang"
PHONE = "phone"
RESUME_DATA = "resume"
Q_IDX = "q_idx"
LANG_STEP = "lang_step"

S_LANG = "lang"
S_CONTACT = "contact"
S_MENU = "menu"
S_ABOUT = "about"
S_INSTRUCTION = "instruction"
S_VACANCY = "vacancy"
S_VACANCY_DESC = "vacancy_desc"
S_QUESTION = "question"
S_PHONE_CONFIRM = "phone_confirm"
S_PHONE_MANUAL = "phone_manual"
S_LANG_LEVELS = "lang_levels"
S_CV_UPLOAD = "cv_upload"

RESUME_FIELD = {
    0: "name",
    1: "birthdate",
    6: "salary_expectation",
    9: "experience",
    12: "memorable_project",
}

LANG_NAMES = {
    "uz": ["Rus tili", "O'zbek tili", "Ingliz tili"],
    "ru": ["Русский", "Узбекский", "Английский"],
}


def _validate_date(text: str) -> bool:
    """Проверяет формат дд/мм/гггг и реальность даты."""
    try:
        parsed = dt.strptime(text.strip(), "%d/%m/%Y")
        # Возраст от 16 до 80 лет
        age = (dt.now() - parsed).days / 365
        return 16 <= age <= 80
    except ValueError:
        return False


def _validate_phone(text: str) -> bool:
    """Только +998 + 9 цифр."""
    return bool(re.fullmatch(r'\+998\d{9}', text.strip()))


def _validate_salary(text: str) -> bool:
    """Только цифры, допустимо пробелы и запятые как разделители."""
    cleaned = text.strip().replace(" ", "").replace(",", "").replace(".", "")
    return cleaned.isdigit() and int(cleaned) > 0


def _lang(ctx):
    return ctx.user_data.get(LANG, "uz")


def _questions(ctx):
    return QUESTIONS_UZ if _lang(ctx) == "uz" else QUESTIONS_RU


async def _send(update, text, keyboard=None):
    kw = {"text": text}
    if keyboard is not None:
        kw["reply_markup"] = keyboard
    await update.message.reply_text(**kw)


def _get_q_idx(ctx):
    return ctx.user_data.get(Q_IDX, 0)


def _set_q_idx(ctx, idx):
    ctx.user_data[Q_IDX] = idx


def _progress(idx, lang):
    label = "Savol" if lang == "uz" else "Вопрос"
    return f"[{label} {idx + 1} / {TOTAL_QUESTIONS}]\n\n"


async def cmd_start(update, ctx):
    ctx.user_data.clear()
    ctx.user_data[STATE] = S_LANG
    await _send(update, texts.CHOOSE_LANG, language_keyboard())


async def handle_message(update, ctx):
    msg = update.message
    chat_id = msg.chat_id

    if msg.contact:
        ctx.user_data[PHONE] = msg.contact.phone_number
        lang = _lang(ctx)
        ctx.user_data[STATE] = S_MENU
        await _send(update, texts.CHOOSE_ACTION[lang], main_menu_keyboard(lang))
        return

    if ctx.user_data.get(STATE) == S_CV_UPLOAD:
        file_id = None
        if msg.document:
            file_id = msg.document.file_id
        elif msg.photo:
            file_id = msg.photo[-1].file_id
        lang = _lang(ctx)
        skip_labels = ["O'tkazib yuborish ⏭", "Пропустить ⏭"]
        if file_id or (msg.text and msg.text.strip() in skip_labels):
            resume = ctx.user_data.get(RESUME_DATA, {})
            resume["cv_file_id"] = file_id or ""
            ctx.user_data[RESUME_DATA] = resume
            db.save_or_update_resume(chat_id, resume)
            resume = ctx.user_data.get(RESUME_DATA, {})
            db.save_or_update_resume(chat_id, resume)
            ctx.user_data[STATE] = S_MENU
            await _send(update, texts.RESUME_SAVED[lang], main_menu_keyboard(lang))
        else:
            await _send(update, texts.SEND_CONTACT[lang])
        return

    if not msg.text:
        return

    text = msg.text.strip()
    state = ctx.user_data.get(STATE, S_LANG)

    if state == S_LANG:
        if text == "O'zbekcha":
            ctx.user_data[LANG] = "uz"
        elif text == "Русский":
            ctx.user_data[LANG] = "ru"
        else:
            await _send(update, texts.CHOOSE_LANG, language_keyboard())
            return
        lang = _lang(ctx)
        if ctx.user_data.get(PHONE):
            ctx.user_data[STATE] = S_MENU
            await _send(update, texts.CHOOSE_ACTION[lang], main_menu_keyboard(lang))
        else:
            ctx.user_data[STATE] = S_CONTACT
            await _send(update, texts.SEND_CONTACT[lang], contact_keyboard(lang))
        return

    if state == S_PHONE_CONFIRM:
        lang = _lang(ctx)
        if text in ("Ha", "Да"):
            resume = ctx.user_data.get(RESUME_DATA, {})
            resume["phone"] = ctx.user_data.get(PHONE, "")
            ctx.user_data[RESUME_DATA] = resume
            db.save_or_update_resume(chat_id, resume)
            ctx.user_data[STATE] = S_MENU
            await _send(update, texts.CHOOSE_ACTION[lang], main_menu_keyboard(lang))
        elif text in ("Yo'q", "Нет"):
            await _send(update, texts.ENTER_PHONE[lang], remove_keyboard())
            ctx.user_data[STATE] = S_PHONE_MANUAL
        return

    if state == S_PHONE_MANUAL:
        lang = _lang(ctx)
        if not _validate_phone(text):
            err = (
                "❌ Noto'g'ri format.\n"
                "Telefon raqami +998 bilan boshlanishi va 12 ta raqamdan iborат bo'lishi kerak.\n"
                "Masalan: +998901234567"
                if lang == "uz" else
                "❌ Неверный формат.\n"
                "Номер должен начинаться с +998 и содержать 12 цифр.\n"
                "Например: +998901234567"
            )
            await _send(update, err)
            return
        resume = ctx.user_data.get(RESUME_DATA, {})
        resume["phone"] = text
        ctx.user_data[PHONE] = text
        ctx.user_data[RESUME_DATA] = resume
        db.save_or_update_resume(chat_id, resume)
        ctx.user_data[STATE] = S_MENU
        await _send(update, texts.CHOOSE_ACTION[lang], main_menu_keyboard(lang))
        return

    if state == S_MENU:
        lang = _lang(ctx)
        if text in ("Biz haqimizda", "О нас"):
            lang = _lang(ctx)
            await _send(update, texts.ABOUT_COMPANY[lang], main_menu_keyboard(lang))
        elif text in ("Vakansiyalar", "Вакансии"):
            ctx.user_data[STATE] = S_VACANCY
            await _send(update, texts.CHOOSE_VACANCY[lang], vacancy_keyboard(lang))
        elif text in ("Yuborilgan rezumelar", "Отправленные резюме"):
            resume = db.get_resume(chat_id)
            if resume:
                await _send(update, texts.resume_text(dict(resume), lang))
            else:
                await _send(update, texts.NO_RESUME[lang])
        elif text in ("Tilni qayta tanlash", "Выбрать язык заново"):
            saved_phone = ctx.user_data.get(PHONE)
            saved_resume = ctx.user_data.get(RESUME_DATA, {})
            ctx.user_data.clear()
            ctx.user_data[STATE] = S_LANG
            if saved_phone:
                ctx.user_data[PHONE] = saved_phone
                ctx.user_data[RESUME_DATA] = saved_resume
            await _send(update, texts.CHOOSE_LANG, language_keyboard())
        else:
            await _send(update, texts.CHOOSE_ACTION[lang], main_menu_keyboard(lang))
        return

    if state == S_ABOUT:
        lang = _lang(ctx)
        ctx.user_data[STATE] = S_MENU
        await _send(update, texts.CHOOSE_ACTION[lang], main_menu_keyboard(lang))
        return

    if state == S_INSTRUCTION:
        lang = _lang(ctx)
        ctx.user_data[STATE] = S_VACANCY
        await _send(update, texts.CHOOSE_VACANCY[lang], vacancy_keyboard(lang))
        return

    if state == S_VACANCY:
        lang = _lang(ctx)
        back_labels = ["⬅️ Orqaga", "⬅️ Назад"]
        if text in back_labels:
            ctx.user_data[STATE] = S_MENU
            await _send(update, texts.CHOOSE_ACTION[lang], main_menu_keyboard(lang))
        elif text in ("Business Analyst", "GIS Analyst"):
            resume = ctx.user_data.get(RESUME_DATA, {})
            resume["vacancy"] = text
            ctx.user_data[RESUME_DATA] = resume
            ctx.user_data[STATE] = S_VACANCY_DESC
            desc = texts.VACANCY_DESC.get(text, {}).get(lang, "")
            await _send(update, desc, apply_keyboard(lang))
        else:
            await _send(update, texts.CHOOSE_VACANCY[lang], vacancy_keyboard(lang))
        return

    if state == S_VACANCY_DESC:
        lang = _lang(ctx)
        back_labels = ["⬅️ Orqaga", "⬅️ Назад"]
        apply_labels = ["Ariza topshirish ✅", "Подать заявку ✅"]
        if text in back_labels:
            ctx.user_data[STATE] = S_VACANCY
            await _send(update, texts.CHOOSE_VACANCY[lang], vacancy_keyboard(lang))
        elif text in apply_labels:
            ctx.user_data[RESUME_DATA] = ctx.user_data.get(RESUME_DATA, {})
            _set_q_idx(ctx, 0)
            ctx.user_data[STATE] = S_QUESTION
            await _ask_question(update, ctx)
        return

    if state == S_QUESTION:
        await _handle_answer(update, ctx, text)
        return

    if state == S_LANG_LEVELS:
        await _handle_lang_level(update, ctx, text)
        return

    ctx.user_data.clear()
    ctx.user_data[STATE] = S_LANG
    await _send(update, texts.CHOOSE_LANG, language_keyboard())


async def _ask_question(update, ctx):
    idx = _get_q_idx(ctx)
    lang = _lang(ctx)
    questions = _questions(ctx)
    chat_id = update.message.chat_id

    if idx >= TOTAL_QUESTIONS:
        resume = ctx.user_data.get(RESUME_DATA, {})
        db.save_or_update_resume(chat_id, resume)
        ctx.user_data[STATE] = S_MENU
        await _send(update, texts.RESUME_SAVED[lang], main_menu_keyboard(lang))
        return

    q_text = _progress(idx, lang) + questions[idx]

    if idx == 2:
        await _send(update, q_text, education_keyboard(lang))
    elif idx == 3:
        await _send(update, q_text, gender_keyboard(lang))
    elif idx == 4:
        await _send(update, q_text, marital_keyboard(lang))
    elif idx == 5:
        ctx.user_data[LANG_STEP] = 0
        ctx.user_data[STATE] = S_LANG_LEVELS
        langs = LANG_NAMES[lang]
        await _send(update, q_text, language_level_keyboard(lang, langs[0]))
    elif idx == 7:
        await _send(update, q_text, yes_no_keyboard(lang))
    elif idx == 8:
        await _send(update, q_text, vacancy_source_keyboard(lang))
    elif idx == 10:
        await _send(update, q_text, yes_no_keyboard(lang))
    elif idx == 11:
        await _send(update, q_text, yes_no_keyboard(lang))
    elif idx == 13:
        await _send(update, q_text, employment_format_keyboard(lang))
    elif idx == 14:
        ctx.user_data[STATE] = S_CV_UPLOAD
        await _send(update, q_text, skip_keyboard(lang))
    else:
        await _send(update, q_text, remove_keyboard())


async def _handle_answer(update, ctx, text):
    idx = _get_q_idx(ctx)
    chat_id = update.message.chat_id
    lang = _lang(ctx)
    resume = ctx.user_data.get(RESUME_DATA, {})

    allowed = {
        2: (
            ["O'rta-maxsus", "Oliy-tugallanmagan", "Oliy-tugallangan"]
            if lang == "uz" else
            ["Средне-специальное", "Высшее-незаконченное", "Высшее-оконченное"]
        ),
        3: (
            ["Erkak", "Ayol"]
            if lang == "uz" else
            ["Мужской", "Женский"]
        ),
        4: (
            ["Uylanganman", "Turmushga chiqqanman", "Bo'ydoqman", "Ajrashganman"]
            if lang == "uz" else
            ["Женат", "Замужем", "Холост", "Разведена"]
        ),
        7: (
            ["Ha", "Yo'q"]
            if lang == "uz" else
            ["Да", "Нет"]
        ),
        8: (
            ["LinkedIn", "hh.uz", "Telegram", "Instagram", "Tanishlar orqali", "Boshqa"]
            if lang == "uz" else
            ["LinkedIn", "hh.uz", "Telegram", "Instagram", "Через знакомого", "Другое"]
        ),
        10: (
            ["Ha", "Yo'q"]
            if lang == "uz" else
            ["Да", "Нет"]
        ),
        11: (
            ["Ha", "Yo'q"]
            if lang == "uz" else
            ["Да", "Нет"]
        ),
        13: (
            ["Qisqa muddatli loyihalar", "Uzoq muddatli ish"]
            if lang == "uz" else
            ["Краткосрочные проекты", "Долгосрочная работа"]
        ),
        15: (
            ["Loyiha asosida", "Doimiy"]
            if lang == "uz" else
            ["Проектная", "Постоянная"]
        ),
    }

    if idx in allowed and text not in allowed[idx]:
        err = (
            "❌ Iltimos, quyidagi tugmalardan birini tanlang."
            if lang == "uz" else
            "❌ Пожалуйста, выберите один из предложенных вариантов."
        )
        await _send(update, err)
        return

    if idx == 1:
        if not _validate_date(text):
            err = (
                "❌ Noto'g'ri format yoki sana.\n"
                "Iltimos, to'g'ri kiriting: kk/oo/yyyy\n"
                "Masalan: 15/03/1998"
                if lang == "uz" else
                "❌ Неверный формат или дата.\n"
                "Пожалуйста, введите корректно: дд/мм/гггг\n"
                "Например: 15/03/1998"
            )
            await _send(update, err)
            return

    if idx == 9:
        cleaned = text.strip().replace(",", ".").replace(" ", "")
        try:
            val = float(cleaned)
            if val < 0 or val > 50:
                raise ValueError
        except ValueError:
            err = (
                "❌ Faqat raqam kiriting (yillar soni).\nMasalan: 2"
                if lang == "uz" else
                "❌ Введите только число (количество лет).\nНапример: 2"
            )
            await _send(update, err)
            return

    if idx == 6:
        if not _validate_salary(text):
            err = (
                "❌ Faqat raqam kiriting.\nMasalan: 5000000"
                if lang == "uz" else
                "❌ Введите только цифры.\nНапример: 5000000"
            )
            await _send(update, err)
            return

    field_map = {
        0: "name",
        1: "birthdate",
        2: "education",
        3: "gender",
        4: "marital_status",
        6: "salary_expectation",
        7: "disability",
        8: "vacancy_source",
        9: "experience",
        10: "certificates",
        11: "big_data_experience",
        12: "memorable_project",
        13: "employment_format"
    }

    field = field_map.get(idx)
    if field:
        resume[field] = text
        ctx.user_data[RESUME_DATA] = resume
        db.save_or_update_resume(chat_id, resume)

    _set_q_idx(ctx, idx + 1)
    await _ask_question(update, ctx)


async def _handle_lang_level(update, ctx, text):
    lang = _lang(ctx)
    lang_step = ctx.user_data.get(LANG_STEP, 0)

    allowed_levels = (
        ["O'rta", "O'rta-yuqori", "Yuqori"]
        if lang == "uz" else
        ["Средний", "Средне-продвинутый", "Продвинутый"]
    )
    if text not in allowed_levels:
        err = (
            "❌ Iltimos, quyidagi tugmalardan birini tanlang."
            if lang == "uz" else
            "❌ Пожалуйста, выберите один из предложенных вариантов."
        )
        await _send(update, err)
        return

    chat_id = update.message.chat_id
    resume = ctx.user_data.get(RESUME_DATA, {})

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

    lang_keys = ["russian", "uzbek", "english"]
    langs_dict[lang_keys[lang_step]] = text
    resume["languages"] = json.dumps(langs_dict, ensure_ascii=False)
    ctx.user_data[RESUME_DATA] = resume
    db.save_or_update_resume(chat_id, resume)

    next_step = lang_step + 1
    if next_step < 3:
        ctx.user_data[LANG_STEP] = next_step
        lang_names = LANG_NAMES[lang]
        level_label = "Darajani tanlang:" if lang == "uz" else "Выберите уровень:"
        q_text = f"[{lang_names[next_step]}]\n{level_label}"
        await _send(update, q_text, language_level_keyboard(lang, lang_names[next_step]))
    else:
        ctx.user_data[STATE] = S_QUESTION
        _set_q_idx(ctx, 6)
        await _ask_question(update, ctx)
