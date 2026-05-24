import os
import logging
from urllib.parse import quote
from datetime import datetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    CallbackQueryHandler, MessageHandler,
    filters, ContextTypes
)

# ─── الإعدادات ────────────────────────────────────────────────
# يقرأ التوكن من متغير البيئة أولاً، وإن لم يوجد يستخدم القيمة المباشرة
TOKEN = os.environ.get("BOT_TOKEN", "8655659515:AAGQP9dRYQK922-6HodB7H0SaPIzDaWfwy8")

# ─── السجل ───────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ─── إحصائيات ────────────────────────────────────────────────
stats = {
    "total_users":    set(),
    "total_messages": 0,
    "searches":       0,
}

# ─── تحية حسب الوقت ──────────────────────────────────────────
def get_greeting() -> str:
    hour = datetime.now().hour
    if   5  <= hour < 12: return "صباح الخير ☀️"
    elif 12 <= hour < 17: return "مساء النور 🌤️"
    elif 17 <= hour < 21: return "مساء الخير 🌆"
    else:                 return "مساء النور 🌙"

# ─── رسالة الترحيب ───────────────────────────────────────────
def welcome_text(name: str) -> str:
    greeting = get_greeting()
    return (
        f"{greeting} *{name}* 👋\n\n"
        f"أهلاً بك في *بوت الذكاء الاصطناعي* 🤖\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 *ما يقدمه هذا البوت:*\n\n"
        f"💬 *فتح ChatGPT* — انتقل مباشرةً لموقع ChatGPT\n"
        f"🌐 *مواقع AI* — أفضل مواقع الذكاء الاصطناعي\n"
        f"🎬 *أفكار فيديو* — محتوى جاهز لقناتك\n"
        f"💻 *تعلم البرمجة* — خارطة طريق للمبتدئين\n"
        f"🔍 *بحث قوقل* — ابحث بدون مغادرة التيليجرام\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👇 *اختر ما يناسبك:*"
    )

# ─── المحتوى الثابت ──────────────────────────────────────────
RESPONSES = {
    "ai_sites": (
        "🌐 *أفضل مواقع الذكاء الاصطناعي:*\n\n"
        "1️⃣ [ChatGPT](https://chat.openai.com) — محادثة ذكية\n"
        "2️⃣ [Gemini](https://gemini.google.com) — ذكاء قوقل\n"
        "3️⃣ [Claude](https://claude.ai) — ذكاء Anthropic\n"
        "4️⃣ [Grok](https://grok.x.ai) — ذكاء X\n"
        "5️⃣ [Perplexity](https://www.perplexity.ai) — بحث ذكي\n"
        "6️⃣ [Runway](https://runwayml.com) — توليد فيديو\n"
        "7️⃣ [Pika](https://pika.art) — فيديو AI\n"
        "8️⃣ [Midjourney](https://www.midjourney.com) — صور AI\n"
        "9️⃣ [Leonardo AI](https://leonardo.ai) — صور وتصميم"
    ),
    "video": (
        "🎬 *أفكار لفيديوهاتك:*\n\n"
        "• 🤖 روبوت يشرح مواقع AI\n"
        "• 📖 قصة خيالية بالذكاء الاصطناعي\n"
        "• ⚖️ مقارنة أدوات AI 2025\n"
        "• 🎨 تعليم صنع صور وفيديو بالـ AI\n"
        "• 💰 كيف تربح من الذكاء الاصطناعي\n"
        "• 🔮 مستقبل AI والوظائف\n"
        "• 📱 أفضل تطبيقات AI للموبايل"
    ),
    "code": (
        "📚 *ابدأ بهذا الترتيب:*\n\n"
        "1️⃣ HTML — هيكل الصفحات\n"
        "2️⃣ CSS — تنسيق وتصميم\n"
        "3️⃣ JavaScript — تفاعل وحركة\n"
        "4️⃣ Python — برمجة متقدمة\n"
        "5️⃣ Telegram Bots 🤖\n\n"
        "🔗 *مصادر مجانية:*\n"
        "• [W3Schools](https://www.w3schools.com)\n"
        "• [freeCodeCamp](https://www.freecodecamp.org)\n"
        "• [Python.org](https://www.python.org)"
    ),
}

# ─── القائمة الرئيسية ─────────────────────────────────────────
def build_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        # زر ChatGPT يفتح الموقع مباشرةً (url_button)
        [InlineKeyboardButton("💬 فتح ChatGPT 🔗", url="https://chat.openai.com")],
        [InlineKeyboardButton("🌐 مواقع AI",        callback_data="ai_sites"),
         InlineKeyboardButton("🎬 أفكار فيديو",     callback_data="video")],
        [InlineKeyboardButton("💻 تعلم البرمجة",    callback_data="code"),
         InlineKeyboardButton("🔍 بحث قوقل",        callback_data="search")],
        [InlineKeyboardButton("📊 إحصائيات",        callback_data="stats")],
    ])

def back_button() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 رجوع للقائمة", callback_data="back")]
    ])

# ─── /start ───────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mode"] = None
    user = update.effective_user
    name = user.first_name if user.first_name else "زائر"
    stats["total_users"].add(user.id)

    await update.message.reply_text(
        welcome_text(name),
        reply_markup=build_menu(),
        parse_mode="Markdown"
    )

# ─── /help ────────────────────────────────────────────────────
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *دليل استخدام البوت:*\n\n"
        "• 💬 *فتح ChatGPT* — يفتح موقع ChatGPT مباشرةً في المتصفح\n"
        "• 🌐 *مواقع AI* — قائمة بأفضل مواقع الذكاء الاصطناعي\n"
        "• 🔍 *بحث قوقل* — اكتب ما تريد ويفتح لك النتائج\n"
        "• /start — العودة للبداية\n"
        "• /stats — عرض الإحصائيات\n\n"
        "💡 *تلميح:* البوت يدعم اللغة العربية والإنجليزية في البحث",
        parse_mode="Markdown",
        reply_markup=build_menu()
    )

# ─── /stats ───────────────────────────────────────────────────
async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"📊 *إحصائيات البوت:*\n\n"
        f"👥 المستخدمون: `{len(stats['total_users'])}`\n"
        f"💬 الرسائل:    `{stats['total_messages']}`\n"
        f"🔍 البحث:      `{stats['searches']}`",
        parse_mode="Markdown",
        reply_markup=build_menu()
    )

# ─── دالة الأزرار ─────────────────────────────────────────────
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user = query.from_user
    name = user.first_name if user.first_name else "زائر"

    if data == "back":
        context.user_data["mode"] = None
        await query.edit_message_text(
            welcome_text(name),
            reply_markup=build_menu(),
            parse_mode="Markdown"
        )

    elif data == "search":
        context.user_data["mode"] = "search"
        await query.edit_message_text(
            "🔍 *وضع البحث*\n\n"
            "اكتب ما تريد البحث عنه:\n\n"
            "_مثال: أفضل أدوات AI المجانية_",
            parse_mode="Markdown",
            reply_markup=back_button()
        )

    elif data == "stats":
        await query.edit_message_text(
            f"📊 *إحصائيات البوت:*\n\n"
            f"👥 المستخدمون: `{len(stats['total_users'])}`\n"
            f"💬 الرسائل:    `{stats['total_messages']}`\n"
            f"🔍 البحث:      `{stats['searches']}`",
            parse_mode="Markdown",
            reply_markup=back_button()
        )

    else:
        response = RESPONSES.get(data)
        if response:
            await query.edit_message_text(
                text=response,
                parse_mode="Markdown",
                reply_markup=back_button()
            )

# ─── دالة معالجة الرسائل ──────────────────────────────────────
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg  = update.message.text
    mode = context.user_data.get("mode")
    stats["total_messages"] += 1
    stats["total_users"].add(update.effective_user.id)

    if mode == "search":
        context.user_data["mode"] = None
        stats["searches"] += 1
        url = f"https://www.google.com/search?q={quote(msg)}"
        await update.message.reply_text(
            f"🔍 *نتائج البحث عن:* `{msg}`\n\n"
            f"[اضغط هنا لفتح قوقل 🌐]({url})",
            parse_mode="Markdown",
            reply_markup=build_menu()
        )
    else:
        await update.message.reply_text(
            "👇 اختر من القائمة:",
            reply_markup=build_menu()
        )

# ─── تشغيل البوت ──────────────────────────────────────────────
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start",  start))
    app.add_handler(CommandHandler("help",   help_cmd))
    app.add_handler(CommandHandler("stats",  stats_cmd))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))
    print("✅ Bot Running...")
    app.run_polling()
