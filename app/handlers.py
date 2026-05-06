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
)
from app.config import QUESTIONS_UZ, QUESTIONS_RU

logger = logging.getLogger(__name__)

STATE = "state"
LANG = "lang"
PHONE = "phone"
RESUME_DATA = "resume"

S_LANG = "lang"
S_CONTACT = "contact"
S_MENU = "menu"
S_QUESTION = "question"  # + index 0-6
S_PHONE_CONFIRM = "phone_confirm"
S_PHONE_MANUAL = "phone_manual"


def _lang(ctx: ContextTypes.DEFAULT_TYPE) -> str:
    return ctx.user_data.get(LANG, "uz")


def _questions(ctx: ContextTypes.DEFAULT_TYPE) -> list[str]:
    return QUESTIONS_UZ if _lang(ctx) == "uz" else QUESTIONS_RU


async def _send(update: Update, text: str, keyboard=None):
    kwargs = {"text": text}
    if keyboard is not None:
        kwargs["reply_markup"] = keyboard
    await update.message.reply_text(**kwargs)


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
            await _send_question(update, ctx, advance=True)
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
        await _send_question(update, ctx, advance=True)
        return

    if state == S_MENU:
        lang = _lang(ctx)
        if text in ("Resume yaratish", "Создать резюме"):
            if db.is_blocked(chat_id):
                await _send(update, texts.BLOCKED)
            else:
                ctx.user_data[RESUME_DATA] = {}
                ctx.user_data[STATE] = f"{S_QUESTION}_0"
                await _send_question(update, ctx)
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

    if isinstance(state, str) and state.startswith(f"{S_QUESTION}_"):
        await _handle_question_input(update, ctx, text)
        return

    ctx.user_data[STATE] = S_LANG
    await _send(update, texts.CHOOSE_LANG, language_keyboard())


RESUME_KEYS = [
    "name",
    "birthdate",
    "experience",
    "certificates",
    "big_data_experience",
    "memorable_project",
    "preferred_job_type",
]


async def _handle_question_input(update: Update, ctx: ContextTypes.DEFAULT_TYPE, text: str):
    state = ctx.user_data.get(STATE, f"{S_QUESTION}_0")
    idx = int(state.split("_")[-1])
    chat_id = update.message.chat_id
    resume = ctx.user_data.get(RESUME_DATA, {})

    if idx == 0:
        resume["name"] = text
    elif idx == 1:
        resume["birthdate"] = text
    elif idx >= 3:
        key = RESUME_KEYS[idx - 1]  # shift because phone is at slot 2
        resume[key] = text

    ctx.user_data[RESUME_DATA] = resume
    db.save_or_update_resume(chat_id, resume)

    await _send_question(update, ctx, advance=True, current_idx=idx)


async def _send_question(
        update: Update,
        ctx: ContextTypes.DEFAULT_TYPE,
        advance: bool = False,
        current_idx: int | None = None,
):
    state = ctx.user_data.get(STATE, f"{S_QUESTION}_0")
    if current_idx is None:
        current_idx = int(state.split("_")[-1]) if "_" in state else 0

    next_idx = current_idx + 1 if advance else current_idx
    lang = _lang(ctx)
    questions = _questions(ctx)
    chat_id = update.message.chat_id

    if next_idx == 2:
        phone = ctx.user_data.get(PHONE, "")
        await _send(update, texts.PHONE_LABEL[lang] + phone)
        await _send(update, texts.PHONE_CONFIRM[lang], yes_no_keyboard(lang))
        ctx.user_data[STATE] = S_PHONE_CONFIRM
        return

    if next_idx > len(questions):
        resume = ctx.user_data.get(RESUME_DATA, {})
        db.save_or_update_resume(chat_id, resume)
        ctx.user_data[STATE] = S_MENU
        await _send(update, texts.RESUME_SAVED[lang], main_menu_keyboard(lang))
        return

    q_idx = next_idx if next_idx < 2 else next_idx - 1
    if q_idx >= len(questions):
        resume = ctx.user_data.get(RESUME_DATA, {})
        db.save_or_update_resume(chat_id, resume)
        ctx.user_data[STATE] = S_MENU
        await _send(update, texts.RESUME_SAVED[lang], main_menu_keyboard(lang))
        return

    await _send(update, questions[q_idx])
    ctx.user_data[STATE] = f"{S_QUESTION}_{next_idx}"


async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data.clear()
    ctx.user_data[STATE] = S_LANG
    await _send(update, texts.CHOOSE_LANG, language_keyboard())
