# -*- coding: utf-8 -*-
"""
RexPvP Minecraft Server — Welcome/Goodbye Telegram Bot
--------------------------------------------------------
Yangi a'zo guruhga qo'shilganda tasodifiy Xush kelibsiz xabari (SmallCaps
shriftda) + tasodifiy Premium stiker yuboradi. A'zo chiqib ketganda esa
tasodifiy Xayr xabari + stiker yuboradi.

Admin buyruqlari:
    /addwelcome <matn>   - yangi "xush kelibsiz" matnini bazaga qo'shadi
    /addbye <matn>       - yangi "xayr" matnini bazaga qo'shadi
    /addsticker          - shu buyruqqa reply qilingan stikerni bazaga qo'shadi
                            (welcome yoki bye turini so'raydi)
    /listwelcome         - barcha welcome matnlarini ko'rsatadi (id bilan)
    /listbye             - barcha bye matnlarini ko'rsatadi (id bilan)
    /liststicker         - barcha stikerlarni ko'rsatadi (id, turi)
    /delwelcome <id>     - welcome matnini o'chiradi
    /delbye <id>         - bye matnini o'chiradi
    /delsticker <id>     - stikerni o'chiradi

Matnda {name} va {chat} maxsus belgilar avtomatik almashtiriladi:
    {name}  -> foydalanuvchining ismi
    {chat}  -> guruh nomi

Ishga tushirishdan oldin quyidagilarni to'ldiring:
    BOT_TOKEN -  @BotFather dan olingan token
    ADMIN_IDS -  admin bo'lgan Telegram user_id lar ro'yxati
"""

import asyncio
import logging
import os
import random
import sqlite3
from pathlib import Path

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ChatMemberStatus, ParseMode
from aiogram.filters import Command, CommandObject
from aiogram.types import (
    ChatMemberUpdated,
    Message,
)
from aiogram.filters.chat_member_updated import (
    ChatMemberUpdatedFilter,
    JOIN_TRANSITION,
    LEAVE_TRANSITION,
)

# =========================== SOZLAMALAR ===========================
# Railway'da bu qiymatlar "Variables" bo'limidan olinadi (environment
# variable). Agar mahalliy kompyuterda ishga tushirsangiz, pastdagi
# "SIZNING_..." qiymatlarini to'g'ridan-to'g'ri o'zgartirishingiz ham mumkin.

BOT_TOKEN = os.environ.get("BOT_TOKEN", "SIZNING_BOT_TOKENINGIZ_BU_YERGA")
_admin_ids_raw = os.environ.get("ADMIN_IDS", "123456789")
ADMIN_IDS = {int(x.strip()) for x in _admin_ids_raw.split(",") if x.strip()}

DB_PATH = Path(__file__).parent / "rexpvp_bot.db"

# ====================================================================

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("rexpvp_bot")

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# ------------------------- SmallCaps yordamchisi -------------------------

_SMALLCAPS_MAP = {
    "a": "ᴀ", "b": "ʙ", "c": "ᴄ", "d": "ᴅ", "e": "ᴇ", "f": "ꜰ", "g": "ɢ",
    "h": "ʜ", "i": "ɪ", "j": "ᴊ", "k": "ᴋ", "l": "ʟ", "m": "ᴍ", "n": "ɴ",
    "o": "ᴏ", "p": "ᴘ", "q": "ǫ", "r": "ʀ", "s": "ꜱ", "t": "ᴛ", "u": "ᴜ",
    "v": "ᴠ", "w": "ᴡ", "x": "x", "y": "ʏ", "z": "ᴢ",
}


def to_smallcaps(text: str) -> str:
    """Matnni SmallCaps (ᴋɪᴄʜɪᴋ ʙᴏꜱ ʜᴀʀꜰʟᴀʀ) shakliga o'tkazadi."""
    result = []
    for ch in text:
        lower = ch.lower()
        if lower in _SMALLCAPS_MAP:
            result.append(_SMALLCAPS_MAP[lower])
        else:
            result.append(ch)
    return "".join(result)


# ------------------------------ Baza (SQLite) ------------------------------

def db_connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS messages (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               kind TEXT NOT NULL CHECK (kind IN ('welcome', 'bye')),
               text TEXT NOT NULL
           )"""
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS stickers (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               kind TEXT NOT NULL CHECK (kind IN ('welcome', 'bye')),
               file_id TEXT NOT NULL
           )"""
    )
    conn.commit()
    return conn


def add_message(kind: str, text: str) -> int:
    conn = db_connect()
    cur = conn.execute("INSERT INTO messages (kind, text) VALUES (?, ?)", (kind, text))
    conn.commit()
    rowid = cur.lastrowid
    conn.close()
    return rowid


def add_sticker(kind: str, file_id: str) -> int:
    conn = db_connect()
    cur = conn.execute("INSERT INTO stickers (kind, file_id) VALUES (?, ?)", (kind, file_id))
    conn.commit()
    rowid = cur.lastrowid
    conn.close()
    return rowid


def get_random_message(kind: str) -> str | None:
    conn = db_connect()
    rows = conn.execute("SELECT text FROM messages WHERE kind = ?", (kind,)).fetchall()
    conn.close()
    if not rows:
        return None
    return random.choice(rows)[0]


def get_random_sticker(kind: str) -> str | None:
    conn = db_connect()
    rows = conn.execute("SELECT file_id FROM stickers WHERE kind = ?", (kind,)).fetchall()
    conn.close()
    if not rows:
        return None
    return random.choice(rows)[0]


def list_messages(kind: str):
    conn = db_connect()
    rows = conn.execute("SELECT id, text FROM messages WHERE kind = ?", (kind,)).fetchall()
    conn.close()
    return rows


def list_stickers():
    conn = db_connect()
    rows = conn.execute("SELECT id, kind, file_id FROM stickers").fetchall()
    conn.close()
    return rows


def delete_message(kind: str, msg_id: int) -> bool:
    conn = db_connect()
    cur = conn.execute("DELETE FROM messages WHERE kind = ? AND id = ?", (kind, msg_id))
    conn.commit()
    ok = cur.rowcount > 0
    conn.close()
    return ok


def delete_sticker(sticker_id: int) -> bool:
    conn = db_connect()
    cur = conn.execute("DELETE FROM stickers WHERE id = ?", (sticker_id,))
    conn.commit()
    ok = cur.rowcount > 0
    conn.close()
    return ok


# --------------------------- Boshlang'ich default matnlar ---------------------------
# Bot birinchi marta ishga tushganda bazada hech narsa bo'lmasa, quyidagi
# tayyor SmallCaps xabarlarni avtomatik qo'shib qo'yadi (siz keyin /addwelcome
# va /addbye orqali yana qo'shishingiz mumkin).

DEFAULT_WELCOME_TEXTS = [
    "xush kelibsiz {name}! rexpvp minecraft server telegram kanaliga xush kelibsiz 🎮",
    "salom {name}! {chat} oilasiga qo'shilganingdan xursandmiz ⚔️",
    "{name} keldi! rexpvp da omadingiz doim yor bo'lsin 🍀",
    "yangi jangchi qo'shildi: {name} — rexpvp ga xush kelibsiz! ⚡",
    "hurmatli {name}, {chat} guruhiga xush kelibsiz! qoidalar bilan tanishib chiqing 📜",
]

DEFAULT_BYE_TEXTS = [
    "hayr {name}, yana kutib qolamiz! 👋",
    "{name} ketdi... rexpvp seni sog'inadi 💔",
    "xayr {name}! eshigimiz doim sizga ochiq 🚪",
    "{name} guruhni tark etdi. omad tilaymiz! 🍀",
    "ko'rishguncha {name}! rexpvp da yana uchrashamiz ⚔️",
]


def seed_defaults_if_empty():
    conn = db_connect()
    count = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
    conn.close()
    if count == 0:
        for t in DEFAULT_WELCOME_TEXTS:
            add_message("welcome", t)
        for t in DEFAULT_BYE_TEXTS:
            add_message("bye", t)
        log.info("Default welcome/bye matnlari bazaga qo'shildi.")


# ------------------------------ Yordamchi ------------------------------

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


def build_text(raw: str, name: str, chat_title: str) -> str:
    filled = raw.replace("{name}", name).replace("{chat}", chat_title)
    return to_smallcaps(filled)


# ------------------------------ A'zo qo'shilganda ------------------------------

@dp.chat_member(ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION))
async def on_user_join(event: ChatMemberUpdated):
    user = event.new_chat_member.user
    if user.is_bot:
        return

    name = user.full_name
    chat_title = event.chat.title or "RexPvP"

    text = get_random_message("welcome")
    if text is None:
        text = "xush kelibsiz {name}!"
    final_text = build_text(text, name, chat_title)

    sticker_id = get_random_sticker("welcome")

    await bot.send_message(event.chat.id, f"<b>{final_text}</b>")
    if sticker_id:
        await bot.send_sticker(event.chat.id, sticker_id)


# ------------------------------ A'zo chiqib ketganda ------------------------------

@dp.chat_member(ChatMemberUpdatedFilter(member_status_changed=LEAVE_TRANSITION))
async def on_user_leave(event: ChatMemberUpdated):
    user = event.old_chat_member.user
    if user.is_bot:
        return

    name = user.full_name
    chat_title = event.chat.title or "RexPvP"

    text = get_random_message("bye")
    if text is None:
        text = "hayr {name}, yana kutib qolamiz!"
    final_text = build_text(text, name, chat_title)

    sticker_id = get_random_sticker("bye")

    await bot.send_message(event.chat.id, f"<b>{final_text}</b>")
    if sticker_id:
        await bot.send_sticker(event.chat.id, sticker_id)


# ------------------------------ Admin buyruqlari ------------------------------

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "<b>" + to_smallcaps("rexpvp welcome bot ishga tushdi!") + "</b>\n\n"
        "Admin buyruqlari:\n"
        "/addwelcome &lt;matn&gt;\n"
        "/addbye &lt;matn&gt;\n"
        "/addsticker (stikerga reply qiling)\n"
        "/listwelcome\n"
        "/listbye\n"
        "/liststicker\n"
        "/delwelcome &lt;id&gt;\n"
        "/delbye &lt;id&gt;\n"
        "/delsticker &lt;id&gt;\n\n"
        "Matnda {name} va {chat} ishlatishingiz mumkin."
    )


@dp.message(Command("addwelcome"))
async def cmd_add_welcome(message: Message, command: CommandObject):
    if not is_admin(message.from_user.id):
        return await message.reply("Bu buyruq faqat adminlar uchun.")
    if not command.args:
        return await message.reply("Foydalanish: /addwelcome Salom {name}, {chat} ga xush kelibsiz!")
    rowid = add_message("welcome", command.args)
    await message.reply(f"✅ Welcome matn qo'shildi (id: {rowid})\n\nNamuna:\n{build_text(command.args, message.from_user.full_name, message.chat.title or 'RexPvP')}")


@dp.message(Command("addbye"))
async def cmd_add_bye(message: Message, command: CommandObject):
    if not is_admin(message.from_user.id):
        return await message.reply("Bu buyruq faqat adminlar uchun.")
    if not command.args:
        return await message.reply("Foydalanish: /addbye Hayr {name}, yana kutib qolamiz!")
    rowid = add_message("bye", command.args)
    await message.reply(f"✅ Bye matn qo'shildi (id: {rowid})\n\nNamuna:\n{build_text(command.args, message.from_user.full_name, message.chat.title or 'RexPvP')}")


# addsticker uchun vaqtinchalik holat (foydalanuvchi welcome/bye tanlaguncha)
_pending_sticker: dict[int, str] = {}  # admin_id -> file_id


@dp.message(Command("addsticker"))
async def cmd_add_sticker(message: Message):
    if not is_admin(message.from_user.id):
        return await message.reply("Bu buyruq faqat adminlar uchun.")
    if not message.reply_to_message or not message.reply_to_message.sticker:
        return await message.reply("Stikerga reply qilib /addsticker deb yozing.")

    file_id = message.reply_to_message.sticker.file_id
    _pending_sticker[message.from_user.id] = file_id
    await message.reply(
        "Bu stiker qaysi holat uchun ishlatilsin?\n"
        "Javob bering: <code>welcome</code> yoki <code>bye</code>"
    )


@dp.message(F.text.in_({"welcome", "bye", "Welcome", "Bye", "WELCOME", "BYE"}))
async def catch_sticker_kind(message: Message):
    admin_id = message.from_user.id
    if admin_id not in _pending_sticker:
        return  # oddiy xabar, e'tiborsiz qoldiramiz
    if not is_admin(admin_id):
        return

    kind = message.text.lower()
    file_id = _pending_sticker.pop(admin_id)
    rowid = add_sticker(kind, file_id)
    await message.reply(f"✅ Stiker '{kind}' turiga qo'shildi (id: {rowid})")


@dp.message(Command("listwelcome"))
async def cmd_list_welcome(message: Message):
    if not is_admin(message.from_user.id):
        return await message.reply("Bu buyruq faqat adminlar uchun.")
    rows = list_messages("welcome")
    if not rows:
        return await message.reply("Welcome matnlar yo'q.")
    text = "\n\n".join(f"#{r[0]}: {r[1]}" for r in rows)
    await message.reply(text)


@dp.message(Command("listbye"))
async def cmd_list_bye(message: Message):
    if not is_admin(message.from_user.id):
        return await message.reply("Bu buyruq faqat adminlar uchun.")
    rows = list_messages("bye")
    if not rows:
        return await message.reply("Bye matnlar yo'q.")
    text = "\n\n".join(f"#{r[0]}: {r[1]}" for r in rows)
    await message.reply(text)


@dp.message(Command("liststicker"))
async def cmd_list_sticker(message: Message):
    if not is_admin(message.from_user.id):
        return await message.reply("Bu buyruq faqat adminlar uchun.")
    rows = list_stickers()
    if not rows:
        return await message.reply("Stikerlar yo'q.")
    text = "\n".join(f"#{r[0]} [{r[1]}]" for r in rows)
    await message.reply(text)


@dp.message(Command("delwelcome"))
async def cmd_del_welcome(message: Message, command: CommandObject):
    if not is_admin(message.from_user.id):
        return await message.reply("Bu buyruq faqat adminlar uchun.")
    if not command.args or not command.args.isdigit():
        return await message.reply("Foydalanish: /delwelcome <id>")
    ok = delete_message("welcome", int(command.args))
    await message.reply("✅ O'chirildi." if ok else "❌ Topilmadi.")


@dp.message(Command("delbye"))
async def cmd_del_bye(message: Message, command: CommandObject):
    if not is_admin(message.from_user.id):
        return await message.reply("Bu buyruq faqat adminlar uchun.")
    if not command.args or not command.args.isdigit():
        return await message.reply("Foydalanish: /delbye <id>")
    ok = delete_message("bye", int(command.args))
    await message.reply("✅ O'chirildi." if ok else "❌ Topilmadi.")


@dp.message(Command("delsticker"))
async def cmd_del_sticker(message: Message, command: CommandObject):
    if not is_admin(message.from_user.id):
        return await message.reply("Bu buyruq faqat adminlar uchun.")
    if not command.args or not command.args.isdigit():
        return await message.reply("Foydalanish: /delsticker <id>")
    ok = delete_sticker(int(command.args))
    await message.reply("✅ O'chirildi." if ok else "❌ Topilmadi.")


# ------------------------------ Ishga tushirish ------------------------------

async def main():
    seed_defaults_if_empty()
    log.info("Bot ishga tushmoqda...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
