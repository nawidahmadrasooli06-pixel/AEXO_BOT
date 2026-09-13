import os
import re
import threading
import logging

from fastapi import FastAPI
import uvicorn

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
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
# AEXO MESSENGER
# =========================================================

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

ADMIN_USERNAME = os.getenv(
    "ADMIN_USERNAME",
    "OWNER_AEXO"
).strip().lstrip("@").lower()

ADMIN_CHAT_ID_RAW = os.getenv(
    "ADMIN_CHAT_ID",
    "8507394356"
).strip()

try:
    ADMIN_CHAT_ID = int(ADMIN_CHAT_ID_RAW)
except ValueError:
    ADMIN_CHAT_ID = None

PORT = int(os.getenv("PORT", "10000"))

BOT_NAME = "🖋️ AEXO Messenger"
OWNER_USERNAME = "@OWNER_AEXO"
OWNER_NAME = "✑︎𓅓 𝐎𝐖𝐍𝐄𝐑 𝐀𝐄𝐗𝐎 𓆃™"

CHANNEL_SATISFACTION = "https://t.me/AEXORAZIAT"
CHANNEL_SUPPORT = "https://t.me/AEXO_SUPPORT"

FREE_BOT_API = "https://t.me/AexoApi1Bot"
FREE_BOT_PLAYER = "https://t.me/AexoPlayerBot"


# =========================================================
# LOGGING
# =========================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


# =========================================================
# RENDER WEB SERVER
# =========================================================

web_app = FastAPI()


@web_app.get("/")
async def home():
    return {
        "status": "online",
        "service": "AEXO Messenger",
    }


@web_app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "AEXO Messenger",
    }


def run_web_server():
    uvicorn.run(
        web_app,
        host="0.0.0.0",
        port=PORT,
        log_level="warning",
    )


# =========================================================
# ADMIN
# =========================================================

def is_admin(user) -> bool:
    if not user:
        return False

    if ADMIN_CHAT_ID is not None:
        return user.id == ADMIN_CHAT_ID

    username = (user.username or "").lower().lstrip("@")

    return username == ADMIN_USERNAME


# =========================================================
# MAIN INLINE MENU
# فقط یک منو؛ پایین صفحه Reply Keyboard نداریم
# =========================================================

def main_menu():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "💎 خدمات AEXO",
                    callback_data="services",
                ),
                InlineKeyboardButton(
                    "🤖 ربات‌های AEXO",
                    callback_data="bots",
                ),
            ],
            [
                InlineKeyboardButton(
                    "📢 کانال‌های AEXO",
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
# START
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
    "@AexoPlayerBot\n\n"
    "💠 ربات‌های قدرتمند اشتراکی نیز موجود است.\n"
    "📩 برای ثبت سفارش یا دریافت اطلاعات، همین‌جا پیام بدید.\n\n"
    "👤 مالک: @OWNER_AEXO\n"
    "✑︎𓅓 𝐎𝐖𝐍𝐄𝐑 𝐀𝐄𝐗𝐎 𓆃™"
)


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    global ADMIN_CHAT_ID

    if not update.effective_user or not update.message:
        return

    context.user_data["waiting_message"] = False

    if is_admin(update.effective_user):
        ADMIN_CHAT_ID = update.effective_chat.id

        logger.info(
            "Owner detected. Chat ID: %s",
            ADMIN_CHAT_ID,
        )

    await update.message.reply_text(
        START_TEXT,
        reply_markup=main_menu(),
    )


# =========================================================
# SERVICES
# =========================================================

async def services(
    query,
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
        "📩 برای ثبت سفارش یا دریافت اطلاعات، "
        "پیام ارسال کنید."
    )

    keyboard = [
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

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# =========================================================
# BOTS
# =========================================================

async def bots(
    query,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = (
        "🤖 ربات‌های AEXO\n\n"
        "🆓 رایگان — همین حالا امتحان کنید!\n\n"
        "🛡️ AexoApi1Bot\n"
        "ربات مدیریت و محافظ\n\n"
        "🎵 AexoPlayerBot\n"
        "ربات موزیک‌پلیر\n\n"
        "💠 ربات‌های قدرتمند اشتراکی نیز موجود است.\n"
        "برای دیدن ربات‌های رایگان، روی گزینه موردنظر بزنید."
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "🆓 🛡️ ربات محافظ رایگان",
                url=FREE_BOT_API,
            )
        ],
        [
            InlineKeyboardButton(
                "🆓 🎵 ربات موزیک رایگان",
                url=FREE_BOT_PLAYER,
            )
        ],
        [
            InlineKeyboardButton(
                "💎 ربات‌های اشتراکی",
                callback_data="services",
            )
        ],
        [
            InlineKeyboardButton(
                "↩️ بازگشت",
                callback_data="home",
            )
        ],
    ]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# =========================================================
# CHANNELS
# =========================================================

async def channels(
    query,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = (
        "📢 کانال‌ها و پشتیبانی AEXO\n\n"
        "برای مشاهده رضایت مشتریان یا دریافت "
        "پشتیبانی، گزینه موردنظر را انتخاب کنید."
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "📢 رضایت مشتری AEXO",
                url=CHANNEL_SATISFACTION,
            )
        ],
        [
            InlineKeyboardButton(
                "💬 گروه پشتیبانی AEXO",
                url=CHANNEL_SUPPORT,
            )
        ],
        [
            InlineKeyboardButton(
                "↩️ بازگشت",
                callback_data="home",
            )
        ],
    ]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# =========================================================
# ABOUT
# =========================================================

async def about(
    query,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = (
        "👤 درباره AEXO\n\n"
        f"{OWNER_NAME}\n"
        f"Username: {OWNER_USERNAME}\n\n"
        "AEXO در زمینه ربات‌های تلگرامی، "
        "مدیریت گروه و کانال، موزیک‌پلیر و "
        "راهکارهای اختصاصی فعالیت می‌کند.\n\n"
        "🛡️ مدیریت و محافظ\n"
        "🎵 موزیک‌پلیر\n"
        "🤖 ربات‌های اختصاصی\n"
        "💎 خدمات حرفه‌ای\n\n"
        "✦ AEXO — Professional Telegram Solutions\n\n"
        "طراحی بات: @cactuc580"
    )

    keyboard = [
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

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# =========================================================
# SEND MESSAGE
# =========================================================

async def start_sending(
    query,
    context: ContextTypes.DEFAULT_TYPE,
):
    context.user_data["waiting_message"] = True

    text = (
        "💌 ارسال پیام به OWNER AEXO\n\n"
        "پیامت رو همین‌جا بفرست.\n\n"
        "📝 متن\n"
        "🖼️ عکس\n"
        "🎥 ویدیو\n"
        "📁 فایل\n"
        "🎤 ویس\n\n"
        "پیام مستقیماً برای مالک AEXO ارسال میشه."
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "↩️ لغو",
                callback_data="home",
            )
        ]
    ]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
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
        "🆔 اطلاعات مالک AEXO\n\n"
        f"User ID:\n{update.effective_user.id}\n\n"
        f"Chat ID:\n{update.effective_chat.id}"
    )


# =========================================================
# SEND USER MESSAGE TO OWNER
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
            "⚠️ ارتباط با مالک هنوز فعال نشده است."
        )
        return

    user = update.effective_user

    username = (
        f"@{user.username}"
        if user.username
        else "ندارد"
    )

    header = (
        "📩 پیام جدید از AEXO Messenger\n\n"
        f"👤 نام: {user.full_name}\n"
        f"🔹 Username: {username}\n"
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
            "✅ پیام شما با موفقیت ارسال شد.\n"
            "OWNER AEXO به‌زودی پاسخ می‌دهد."
        )

    except Exception:
        logger.exception(
            "Failed to send user message."
        )

        await update.message.reply_text(
            "❌ ارسال پیام انجام نشد.\n"
            "لطفاً کمی بعد دوباره تلاش کنید."
        )


# =========================================================
# FIND USER ID FROM OWNER REPLY
# =========================================================

def extract_user_id(message):
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
# OWNER REPLY
# =========================================================

async def send_admin_reply_to_user(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not update.message or not update.effective_user:
        return False

    if not is_admin(update.effective_user):
        return False

    if not update.message.reply_to_message:
        return False

    target_user_id = extract_user_id(
        update.message
    )

    if not target_user_id:
        return False

    try:
        await update.message.copy(
            chat_id=target_user_id,
        )

        await update.message.reply_text(
            "✅ پاسخ برای کاربر ارسال شد."
        )

    except Exception:
        logger.exception(
            "Failed to send owner reply."
        )

        await update.message.reply_text(
            "❌ ارسال پاسخ انجام نشد.\n\n"
            "ممکن است کاربر ربات را بلاک کرده باشد."
        )

    return True


# =========================================================
# CALLBACK ROUTER
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
        context.user_data["waiting_message"] = False

        await query.edit_message_text(
            START_TEXT,
            reply_markup=main_menu(),
        )

        return

    if data == "services":
        await services(
            query,
            context,
        )
        return

    if data == "bots":
        await bots(
            query,
            context,
        )
        return

    if data == "channels":
        await channels(
            query,
            context,
        )
        return

    if data == "about":
        await about(
            query,
            context,
        )
        return

    if data == "message":
        await start_sending(
            query,
            context,
        )
        return


# =========================================================
# MESSAGE ROUTER
# =========================================================

async def message_router(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not update.message or not update.effective_user:
        return

    # Owner reply system
    if is_admin(update.effective_user):
        handled = await send_admin_reply_to_user(
            update,
            context,
        )

        if handled:
            return

    # User is sending a message to owner
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
        "برای استفاده از AEXO، "
        "از منوی زیر انتخاب کنید."
    )

    await update.message.reply_text(
        "🖋️ AEXO Messenger",
        reply_markup=main_menu(),
    )


# =========================================================
# BOT COMMANDS
# =========================================================

async def post_init(
    application: Application,
):
    await application.bot.set_my_commands(
        [
            (
                "start",
                "شروع ربات",
            ),
            (
                "help",
                "راهنما",
            ),
            (
                "myid",
                "شناسه مالک",
            ),
        ]
    )

    logger.info(
        "AEXO commands configured."
    )


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not update.message:
        return

    await update.message.reply_text(
        "❓ راهنمای AEXO\n\n"
        "از منوی زیر می‌توانید خدمات، ربات‌های رایگان، "
        "کانال‌ها و اطلاعات AEXO را مشاهده کنید.\n\n"
        "💌 برای ارتباط مستقیم با مالک، "
        "گزینه «ارسال پیام» را انتخاب کنید.",
        reply_markup=main_menu(),
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
            help_command,
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
        "AEXO Messenger is starting..."
    )

    application.run_polling(
        drop_pending_updates=False,
    )


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    main()
