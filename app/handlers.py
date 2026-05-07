import logging
from telegram import Update
from telegram.ext import ContextTypes

from app import database as db
from app import texts
from app.keyboards import (
    language_keyboard,
    contact_keyboard,
    main_menu_keyboard,
    yes_no_keyboard,
    remove_keyboard,
)
from app.config import QUESTIONS_UZ, QUESTIONS_RU

logger = logging.getLogger(__name__)

STATE = "state"
LANG = "lang"
PHONE = "phone"
RESUME_DATA = "resume"
Q_IDX = "q_idx"

S_LANG = "lang"
S_CONTACT = "contact"
S_MENU = "menu"
S_QUESTION = "question"
S_PHONE_CONFIRM = "phone_confirm"
S_PHONE_MANUAL = "phone_manual"

RESUME_FIELD = {
    0: "name",
    1: "birthdate",
    3: "experience",
    4: "certificates",
    5: "big_data_experience",
    6: "memorable_project",
    7: "preferred_job_type",
}

TOTAL_QUESTIONS = 7


def _lang(ctx: ContextTypes.DEFAULT_TYPE) -> str:
    return ctx.user_data.get(LANG, "uz")


def _questions(ctx: ContextTypes.DEFAULT_TYPE) -> list[str]:
    return QUESTIONS_UZ if _lang(ctx) == "uz" else QUESTIONS_RU


async def _send(update: Update, text: str, keyboard=None):
    kwargs = {"text": text}
    if keyboard is not None:
        kwargs["reply_markup"] = keyboard
    await update.message.reply_text(**kwargs)


def _get_q_idx(ctx: ContextTypes.DEFAULT_TYPE) -> int:
    return ctx.user_data.get(Q_IDX, 0)


def _set_q_idx(ctx: ContextTypes.DEFAULT_TYPE, idx: int):
    ctx.user_data[Q_IDX] = idx


async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data.clear()
    ctx.user_data[STATE] = S_LANG
    await _send(update, texts.CHOOSE_LANG, language_keyboard())


async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    chat_id = msg.chat_id

    if msg.contact:
        ctx.user_data[PHONE] = msg.contact.phone_number
        ctx.user_data[STATE] = S_MENU
        lang = _lang(ctx)
        await _send(update, texts.CHOOSE_ACTION[lang], main_menu_keyboard(lang))
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
        ctx.user_data[STATE] = S_CONTACT
        lang = _lang(ctx)
        await _send(update, texts.SEND_CONTACT[lang], contact_keyboard(lang))
        return

    if state == S_PHONE_CONFIRM:
        lang = _lang(ctx)
        if text in ("Ha", "Да"):
            resume = ctx.user_data.get(RESUME_DATA, {})
            resume["phone"] = ctx.user_data.get(PHONE, "")
            ctx.user_data[RESUME_DATA] = resume
            db.save_or_update_resume(chat_id, resume)
            _set_q_idx(ctx, 3)
            ctx.user_data[STATE] = S_QUESTION
            await _ask_question(update, ctx)
        elif text in ("Yo'q", "Нет"):
            await _send(update, texts.ENTER_PHONE[lang])
            ctx.user_data[STATE] = S_PHONE_MANUAL
        return

    if state == S_PHONE_MANUAL:
        resume = ctx.user_data.get(RESUME_DATA, {})
        resume["phone"] = text
        ctx.user_data[RESUME_DATA] = resume
        ctx.user_data[PHONE] = text
        db.save_or_update_resume(chat_id, resume)
        _set_q_idx(ctx, 3)
        ctx.user_data[STATE] = S_QUESTION
        await _ask_question(update, ctx)
        return

    if state == S_MENU:
        lang = _lang(ctx)
        if text in ("Rezume yaratish", "Создать резюме"):
            if db.is_blocked(chat_id):
                await _send(update, texts.BLOCKED)
            else:
                ctx.user_data[RESUME_DATA] = {}
                _set_q_idx(ctx, 0)
                ctx.user_data[STATE] = S_QUESTION
                await _ask_question(update, ctx)
        elif text in ("Yuborilgan rezumelar", "Отправленные резюме"):
            resume = db.get_resume(chat_id)
            if resume:
                await _send(update, texts.resume_text(dict(resume), lang))
            else:
                await _send(update, texts.NO_RESUME[lang])
        elif text in ("Tilni qayta tanlash", "Выбрать язык заново"):
            ctx.user_data.clear()
            ctx.user_data[STATE] = S_LANG
            await _send(update, texts.CHOOSE_LANG, language_keyboard())
        else:
            await _send(update, texts.CHOOSE_ACTION[lang], main_menu_keyboard(lang))
        return

    if state == S_QUESTION:
        await _handle_answer(update, ctx, text)
        return

    ctx.user_data.clear()
    ctx.user_data[STATE] = S_LANG
    await _send(update, texts.CHOOSE_LANG, language_keyboard())


async def _ask_question(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Отправить текущий вопрос по индексу Q_IDX."""
    idx = _get_q_idx(ctx)
    lang = _lang(ctx)
    questions = _questions(ctx)
    chat_id = update.message.chat_id

    if idx == 2:
        phone = ctx.user_data.get(PHONE, "")
        await _send(update, texts.PHONE_LABEL[lang] + phone)
        await _send(update, texts.PHONE_CONFIRM[lang], yes_no_keyboard(lang))
        ctx.user_data[STATE] = S_PHONE_CONFIRM
        return

    if idx > TOTAL_QUESTIONS:
        resume = ctx.user_data.get(RESUME_DATA, {})
        db.save_or_update_resume(chat_id, resume)
        ctx.user_data[STATE] = S_MENU
        await _send(update, texts.RESUME_SAVED[lang], main_menu_keyboard(lang))
        return

    q_pos = idx if idx < 2 else idx - 1
    if q_pos >= len(questions):
        resume = ctx.user_data.get(RESUME_DATA, {})
        db.save_or_update_resume(chat_id, resume)
        ctx.user_data[STATE] = S_MENU
        await _send(update, texts.RESUME_SAVED[lang], main_menu_keyboard(lang))
        return

    await _send(update, questions[q_pos], remove_keyboard())


async def _handle_answer(update: Update, ctx: ContextTypes.DEFAULT_TYPE, text: str):
    """Сохранить ответ и перейти к следующему вопросу."""
    idx = _get_q_idx(ctx)
    chat_id = update.message.chat_id
    resume = ctx.user_data.get(RESUME_DATA, {})

    field = RESUME_FIELD.get(idx)
    if field:
        resume[field] = text
        ctx.user_data[RESUME_DATA] = resume
        db.save_or_update_resume(chat_id, resume)

    next_idx = idx + 1
    _set_q_idx(ctx, next_idx)
    await _ask_question(update, ctx)
