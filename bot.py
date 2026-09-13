import os
import re
import logging
import threading

from fastapi import FastAPI
import uvicorn

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)


# =========================================================
# CONFIG
# =========================================================

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

ADMIN_USERNAME = os.getenv(
    "ADMIN_USERNAME",
    "OWNER_AEXO",
).strip().lstrip("@").lower()

ADMIN_CHAT_ID_RAW = os.getenv(
    "ADMIN_CHAT_ID",
    "8507394356",
).strip()

try:
    ADMIN_CHAT_ID = int(ADMIN_CHAT_ID_RAW)
except ValueError:
    ADMIN_CHAT_ID = None


BOT_NAME = "AEXO Messenger"
OWNER_NAME = "✑︎𓅓 𝐎𝐖𝐍𝐄𝐑 𝐀𝐄𝐗𝐎 𓆃™"
OWNER_USERNAME = "@OWNER_AEXO"

PORT = int(os.getenv("PORT", "10000"))

CHANNELS = {
    "رضایت مشتری AEXO": "https://t.me/AEXORAZIAT",
    "پشتیبانی AEXO": "https://t.me/AEXO_SUPPORT",
}

FREE_BOTS = {
    "AexoApi1Bot": "https://t.me/AexoApi1Bot",
    "AexoPlayerBot": "https://t.me/AexoPlayerBot",
}


if not BOT_TOKEN:
    raise RuntimeError(
        "BOT_TOKEN is missing. "
        "Please add BOT_TOKEN in Render Environment Variables."
    )


# =========================================================
# LOGGING
# =========================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


# =========================================================
# FASTAPI / RENDER
# =========================================================

web_app = FastAPI()


@web_app.get("/")
async def home():
    return {
        "status": "online",
        "bot": BOT_NAME,
    }


@web_app.get("/health")
async def health():
    return {
        "status": "ok",
        "bot": BOT_NAME,
    }


def run_web_server():
    uvicorn.run(
        web_app,
        host="0.0.0.0",
        port=PORT,
        log_level="warning",
    )


# =========================================================
# ADMIN CHECK
# =========================================================

def is_admin(user) -> bool:
    if not user:
        return False

    if ADMIN_CHAT_ID is not None:
        return user.id == ADMIN_CHAT_ID

    username = (user.username or "").strip().lower()

    return username == ADMIN_USERNAME


# =========================================================
# MENUS
# =========================================================

def main_menu():
    keyboard = [
        [
            "💎 خدمات AEXO",
            "🤖 ربات‌های AEXO",
        ],
        [
            "📢 کانال‌های AEXO",
            "👤 درباره AEXO",
        ],
        [
            "💌 ارسال پیام",
            "❓ راهنما",
        ],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        is_persistent=True,
    )


def start_inline_menu():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "💎 خدمات AEXO",
                    callback_data="services",
                ),
                InlineKeyboardButton(
                    "🤖 ربات‌ها",
                    callback_data="bots",
                ),
            ],
            [
                InlineKeyboardButton(
                    "📢 کانال‌ها",
                    callback_data="channels",
                ),
                InlineKeyboardButton(
                    "👤 درباره AEXO",
                    callback_data="about",
                ),
            ],
            [
                InlineKeyboardButton(
                    "💌 ارسال پیام",
                    callback_data="message",
                ),
            ],
        ]
    )


# =========================================================
# START TEXT
# =========================================================

START_TEXT = (
    "🖋️ AEXO Messenger\n"
    "وقت شما بخیر ❤️\n\n"
    "🛡️ ربات‌های قدرتمند مدیریت و محافظ\n"
    "🎵 موزیک‌پلیر رایگان و اشتراکی\n"
    "💎 خدمات ممبر، فالور، لایک، ویو، استارز و پریمیوم\n"
    "🤖 ربات‌های اختصاصی و حرفه‌ای\n\n"
    "🆓 ربات‌های رایگان برای گروه و کانال شما:\n"
    "@AexoApi1Bot\n"
    "@AexoPlayerBot\n"
    "💠 ربات‌های قدرتمند اشتراکی نیز موجود است.\n"
    "📩 برای ثبت سفارش یا دریافت اطلاعات، همین‌جا پیام بدید.\n"
    "👤 مالک: @OWNER_AEXO\n"
    "✑︎𓅓 𝐎𝐖𝐍𝐄𝐑 𝐀𝐄𝐗𝐎 𓆃™"
)


# =========================================================
# START
# =========================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    global ADMIN_CHAT_ID

    if not update.effective_user or not update.message:
        return

    user = update.effective_user

    if is_admin(user):
        ADMIN_CHAT_ID = update.effective_chat.id

        logger.info(
            "AEXO owner detected. Chat ID: %s",
            ADMIN_CHAT_ID,
        )

    context.user_data["waiting_message"] = False

    await update.message.reply_text(
        START_TEXT,
        reply_markup=start_inline_menu(),
    )

    await update.message.reply_text(
        "از کانال‌های AEXO دیدن کنید:",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "📢 رضایت مشتری AEXO",
                        url=CHANNELS["رضایت مشتری AEXO"],
                    )
                ],
                [
                    InlineKeyboardButton(
                        "💬 گروه پشتیبانی",
                        url=CHANNELS["پشتیبانی AEXO"],
                    )
                ],
            ]
        ),
    )

    await update.message.reply_text(
        "منوی AEXO:",
        reply_markup=main_menu(),
    )


# =========================================================
# ABOUT SERVICES
# =========================================================

async def services(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = (
        "💎 خدمات AEXO\n\n"
        "🛡️ ربات‌های مدیریت و محافظ\n"
        "🎵 موزیک‌پلیر رایگان و اشتراکی\n"
        "👥 ممبر و ممبر فعال\n"
        "👁️ ویو و سین‌زن کانال\n"
        "❤️ لایک و فالور\n"
        "⭐ استارز و پریمیوم\n"
        "🤖 ربات‌های اختصاصی و حرفه‌ای\n\n"
        "💠 ربات‌های قدرتمند اشتراکی نیز موجود است.\n\n"
        "📩 برای ثبت سفارش، از «💌 ارسال پیام» استفاده کنید."
    )

    await update.message.reply_text(
        text,
        reply_markup=main_menu(),
    )


# =========================================================
# BOTS
# =========================================================

async def bots(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    keyboard = [
        [
            InlineKeyboardButton(
                "🛡️ AexoApi1Bot",
                url=FREE_BOTS["AexoApi1Bot"],
            )
        ],
        [
            InlineKeyboardButton(
                "🎵 AexoPlayerBot",
                url=FREE_BOTS["AexoPlayerBot"],
            )
        ],
    ]

    await update.message.reply_text(
        "🤖 ربات‌های AEXO\n\n"
        "🆓 ربات‌های رایگان برای گروه و کانال:\n\n"
        "🛡️ ربات مدیریت و محافظ\n"
        "🎵 ربات موزیک‌پلیر\n\n"
        "💠 ربات‌های حرفه‌ای اشتراکی نیز موجود است.",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# =========================================================
# CHANNELS
# =========================================================

async def channels(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    keyboard = [
        [
            InlineKeyboardButton(
                "📢 رضایت مشتری AEXO",
                url=CHANNELS["رضایت مشتری AEXO"],
            )
        ],
        [
            InlineKeyboardButton(
                "💬 گروه پشتیبانی AEXO",
                url=CHANNELS["پشتیبانی AEXO"],
            )
        ],
    ]

    await update.message.reply_text(
        "📢 کانال‌ها و پشتیبانی AEXO\n\n"
        "برای مشاهده رضایت مشتریان یا دریافت پشتیبانی، "
        "یکی از گزینه‌های زیر را انتخاب کنید.",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# =========================================================
# ABOUT AEXO
# =========================================================

async def about(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = (
        "👤 درباره AEXO\n\n"
        f"{OWNER_NAME}\n"
        f"Username: {OWNER_USERNAME}\n\n"
        "AEXO یک مجموعه فعال در زمینه ربات‌های تلگرامی، "
        "مدیریت گروه و کانال و سرویس‌های دیجیتال است.\n\n"
        "🛡️ مدیریت و محافظ\n"
        "🎵 موزیک‌پلیر\n"
        "🤖 ربات‌های اختصاصی\n"
        "💎 سرویس‌های حرفه‌ای\n\n"
        "✦ AEXO — Professional Telegram Solutions\n\n"
        "طراحی بات: @cactuc580"
    )

    await update.message.reply_text(
        text,
        reply_markup=main_menu(),
    )


# =========================================================
# HELP
# =========================================================

async def help_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = (
        "❓ راهنمای AEXO\n\n"
        "💎 خدمات AEXO — مشاهده خدمات\n"
        "🤖 ربات‌های AEXO — مشاهده ربات‌ها\n"
        "📢 کانال‌های AEXO — کانال و پشتیبانی\n"
        "👤 درباره AEXO — معرفی مجموعه\n"
        "💌 ارسال پیام — ارتباط مستقیم با مالک\n\n"
        "برای ثبت سفارش یا پرسش، "
        "از «💌 ارسال پیام» استفاده کنید."
    )

    await update.message.reply_text(
        text,
        reply_markup=main_menu(),
    )


# =========================================================
# MY ID
# =========================================================

async def my_id(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not update.effective_user or not update.message:
        return

    if not is_admin(update.effective_user):
        return

    await update.message.reply_text(
        "🆔 اطلاعات AEXO\n\n"
        f"User ID:\n{update.effective_user.id}\n\n"
        f"Chat ID:\n{update.effective_chat.id}"
    )


# =========================================================
# START SENDING
# =========================================================

async def start_sending(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not update.message:
        return

    context.user_data["waiting_message"] = True

    await update.message.reply_text(
        "💌 پیام خودت رو برای OWNER AEXO بفرست.\n\n"
        "متن، عکس، ویدیو، فایل یا ویس هم می‌تونی ارسال کنی.\n\n"
        "پیام مستقیماً برای مالک AEXO ارسال میشه.\n"
        "برای لغو، /start رو بزن.",
        reply_markup=main_menu(),
    )


# =========================================================
# SEND USER MESSAGE TO ADMIN
# =========================================================

async def send_user_message_to_admin(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    global ADMIN_CHAT_ID

    if not update.message or not update.effective_user:
        return

    if ADMIN_CHAT_ID is None:
        await update.message.reply_text(
            "⚠️ مالک ربات هنوز فعال‌سازی را کامل نکرده است."
        )
        return

    user = update.effective_user

    username_text = (
        f"@{user.username}"
        if user.username
        else "ندارد"
    )

    header = (
        "📩 پیام جدید AEXO\n\n"
        f"👤 نام: {user.full_name}\n"
        f"🔹 Username: {username_text}\n"
        f"🆔 User ID: {user.id}\n\n"
        "↩️ برای پاسخ، روی همین پیام Reply بزن."
    )

    try:
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=header,
        )

        await update.message.copy(
            chat_id=ADMIN_CHAT_ID,
        )

        context.user_data["waiting_message"] = False

        await update.message.reply_text(
            "✅ پیام شما با موفقیت برای OWNER AEXO ارسال شد.",
            reply_markup=main_menu(),
        )

    except Exception:
        logger.exception(
            "Could not send user message to admin."
        )

        await update.message.reply_text(
            "❌ ارسال پیام انجام نشد.\n"
            "لطفاً کمی بعد دوباره امتحان کنید.",
            reply_markup=main_menu(),
        )


# =========================================================
# EXTRACT USER ID FROM ADMIN HEADER
# =========================================================

def extract_user_id_from_admin_message(message):
    if not message.reply_to_message:
        return None

    replied_text = (
        message.reply_to_message.text
        or message.reply_to_message.caption
        or ""
    )

    match = re.search(
        r"User ID:\s*(-?\d+)",
        replied_text,
    )

    if not match:
        return None

    try:
        return int(match.group(1))
    except ValueError:
        return None


# =========================================================
# ADMIN REPLY TO USER
# =========================================================

async def send_admin_reply_to_user(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not update.message:
        return False

    if not update.effective_user:
        return False

    if not is_admin(update.effective_user):
        return False

    if not update.message.reply_to_message:
        return False

    target_user_id = extract_user_id_from_admin_message(
        update.message
    )

    if not target_user_id:
        await update.message.reply_text(
            "⚠️ لطفاً روی پیام اصلی کاربر Reply کنید."
        )
        return True

    try:
        await update.message.copy(
            chat_id=target_user_id,
        )

        await update.message.reply_text(
            "✅ پاسخ برای کاربر ارسال شد."
        )

    except Exception:
        logger.exception(
            "Could not send admin reply."
        )

        await update.message.reply_text(
            "❌ ارسال پاسخ انجام نشد.\n\n"
            "ممکن است کاربر ربات را بلاک کرده باشد."
        )

    return True


# =========================================================
# CALLBACK BUTTONS
# =========================================================

async def callback_router(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query

    if not query:
        return

    await query.answer()

    data = query.data

    if data == "home":
        await query.message.edit_text(
            START_TEXT,
            reply_markup=start_inline_menu(),
        )
        return

    if data == "services":
        await query.message.edit_text(
            "💎 خدمات AEXO\n\n"
            "🛡️ مدیریت و محافظ گروه و کانال\n"
            "🎵 موزیک‌پلیر رایگان و اشتراکی\n"
            "👥 ممبر و ممبر فعال\n"
            "👁️ ویو و سین‌زن کانال\n"
            "❤️ لایک و فالور\n"
            "⭐ استارز و پریمیوم\n"
            "🤖 ربات‌های اختصاصی و حرفه‌ای\n\n"
            "💠 ربات‌های قدرتمند اشتراکی نیز موجود است.\n\n"
            "📩 برای ثبت سفارش، پیام ارسال کنید.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "💌 ارسال پیام",
                            callback_data="message",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "↩️ بازگشت",
                            callback_data="home",
                        )
                    ],
                ]
            ),
        )
        return

    if data == "bots":
        await query.message.edit_text(
            "🤖 ربات‌های AEXO\n\n"
            "🆓 ربات‌های رایگان:\n\n"
            "🛡️ AexoApi1Bot\n"
            "🎵 AexoPlayerBot\n\n"
            "💠 ربات‌های حرفه‌ای اشتراکی نیز موجود است.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "🛡️ AexoApi1Bot",
                            url=FREE_BOTS["AexoApi1Bot"],
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "🎵 AexoPlayerBot",
                            url=FREE_BOTS["AexoPlayerBot"],
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "↩️ بازگشت",
                            callback_data="home",
                        )
                    ],
                ]
            ),
        )
        return

    if data == "channels":
        await query.message.edit_text(
            "📢 کانال‌ها و پشتیبانی AEXO\n\n"
            "برای مشاهده رضایت مشتریان یا دریافت "
            "پشتیبانی، گزینه موردنظر را انتخاب کنید.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "📢 رضایت مشتری AEXO",
                            url=CHANNELS["رضایت مشتری AEXO"],
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "💬 گروه پشتیبانی",
                            url=CHANNELS["پشتیبانی AEXO"],
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "↩️ بازگشت",
                            callback_data="home",
                        )
                    ],
                ]
            ),
        )
        return

    if data == "about":
        await query.message.edit_text(
            "👤 درباره AEXO\n\n"
            f"{OWNER_NAME}\n"
            f"Username: {OWNER_USERNAME}\n\n"
            "AEXO مجموعه‌ای برای ارائه راهکارهای "
            "حرفه‌ای تلگرامی، مدیریت گروه و کانال و "
            "ربات‌های اختصاصی است.\n\n"
            "✦ AEXO — Professional Telegram Solutions\n\n"
            "طراحی بات: @cactuc580",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "↩️ بازگشت",
                            callback_data="home",
                        )
                    ]
                ]
            ),
        )
        return

    if data == "message":
        context.user_data["waiting_message"] = True

        await query.message.edit_text(
            "💌 پیام خودت رو برای OWNER AEXO بفرست.\n\n"
            "متن، عکس، ویدیو، فایل یا ویس هم می‌تونی ارسال کنی.\n\n"
            "پیام مستقیماً برای مالک AEXO ارسال میشه.\n"
            "برای لغو، /start رو بزن.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "↩️ لغو",
                            callback_data="home",
                        )
                    ]
                ]
            ),
        )


# =========================================================
# MESSAGE ROUTER
# =========================================================

async def message_router(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not update.message or not update.effective_user:
        return

    # Admin reply system
    if is_admin(update.effective_user):
        handled = await send_admin_reply_to_user(
            update,
            context,
        )

        if handled:
            return

    text = update.message.text or ""

    if text == "💎 خدمات AEXO":
        await services(update, context)
        return

    if text == "🤖 ربات‌های AEXO":
        await bots(update, context)
        return

    if text == "📢 کانال‌های AEXO":
        await channels(update, context)
        return

    if text == "👤 درباره AEXO":
        await about(update, context)
        return

    if text == "💌 ارسال پیام":
        await start_sending(update, context)
        return

    if text == "❓ راهنما":
        await help_menu(update, context)
        return

    if context.user_data.get(
        "waiting_message",
        False,
    ):
        await send_user_message_to_admin(
            update,
            context,
        )
        return

    await update.message.reply_text(
        "از منوی AEXO یکی از گزینه‌ها را انتخاب کنید.",
        reply_markup=main_menu(),
    )


# =========================================================
# POST INIT
# =========================================================

async def post_init(
    application: Application,
):
    await application.bot.set_my_commands(
        [
            ("start", "شروع ربات"),
            ("help", "راهنما"),
            ("myid", "شناسه کاربری"),
        ]
    )

    logger.info(
        "AEXO commands configured successfully."
    )


# =========================================================
# MAIN
# =========================================================

def main():

    server_thread = threading.Thread(
        target=run_web_server,
        daemon=True,
    )

    server_thread.start()

    logger.info(
        "Render HTTP server started on port %s",
        PORT,
    )

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    application.add_handler(
        CommandHandler(
            "start",
            start,
        )
    )

    application.add_handler(
        CommandHandler(
            "help",
            help_menu,
        )
    )

    application.add_handler(
        CommandHandler(
            "myid",
            my_id,
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            callback_router
        )
    )

    application.add_handler(
        MessageHandler(
            filters.ALL & ~filters.COMMAND,
            message_router,
        )
    )

    logger.info(
        "%s is starting...",
        BOT_NAME,
    )

    application.run_polling(
        drop_pending_updates=False,
    )


if __name__ == "__main__":
    main()
