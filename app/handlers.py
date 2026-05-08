import logging
import json

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
    "uz": ["Rus tili", "O'zbek tili", "Ingliz tili", "Boshqa til"],
    "ru": ["Русский", "Узбекский", "Английский", "Дополнительный язык"],
}


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
            _set_q_idx(ctx, 15)
            ctx.user_data[STATE] = S_QUESTION
            await _ask_question(update, ctx)
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
        resume = ctx.user_data.get(RESUME_DATA, {})
        resume["phone"] = text
        ctx.user_data[PHONE] = text
        ctx.user_data[RESUME_DATA] = resume
        db.save_or_update_resume(chat_id, resume)
        lang = _lang(ctx)
        ctx.user_data[STATE] = S_MENU
        await _send(update, texts.CHOOSE_ACTION[lang], main_menu_keyboard(lang))
        return

    if state == S_MENU:
        lang = _lang(ctx)
        if text in ("Haqida", "О компании"):
            lang = _lang(ctx)
            await _send(update, texts.ABOUT_COMPANY[lang], main_menu_keyboard(lang))
        elif text in ("Vakansiyalar", "Вакансии"):
            ctx.user_data[STATE] = S_VACANCY
            await _send(update, texts.CHOOSE_VACANCY[lang], vacancy_keyboard())
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
        await _send(update, q_text, vacancy_source_keyboard())
    elif idx == 10:
        await _send(update, q_text, yes_no_keyboard(lang))
    elif idx == 11:
        await _send(update, q_text, yes_no_keyboard(lang))
    elif idx == 13:
        await _send(update, q_text, employment_format_keyboard(lang))
    elif idx == 14:
        ctx.user_data[STATE] = S_CV_UPLOAD
        await _send(update, q_text, skip_keyboard(lang))
    elif idx == 15:
        await _send(update, q_text, employment_type_keyboard(lang))
    else:
        await _send(update, q_text, remove_keyboard())


async def _handle_answer(update, ctx, text):
    idx = _get_q_idx(ctx)
    chat_id = update.message.chat_id
    resume = ctx.user_data.get(RESUME_DATA, {})

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
        13: "employment_format",
        15: "employment_type",
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

    lang_keys = ["russian", "uzbek", "english", "other"]
    langs_dict[lang_keys[lang_step]] = text
    resume["languages"] = json.dumps(langs_dict, ensure_ascii=False)
    ctx.user_data[RESUME_DATA] = resume
    db.save_or_update_resume(chat_id, resume)

    next_step = lang_step + 1
    if next_step < 4:
        ctx.user_data[LANG_STEP] = next_step
        lang_names = LANG_NAMES[lang]
        level_label = "Darajani tanlang:" if lang == "uz" else "Выберите уровень:"
        q_text = f"[{lang_names[next_step]}]\n{level_label}"
        await _send(update, q_text, language_level_keyboard(lang, lang_names[next_step]))
    else:
        ctx.user_data[STATE] = S_QUESTION
        _set_q_idx(ctx, 6)
        await _ask_question(update, ctx)
