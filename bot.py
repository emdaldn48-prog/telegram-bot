import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# جلب التوكن من Environment Variable
TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📱 سوشيال ميديا", callback_data="social")],
        [InlineKeyboardButton("🌍 الموقع", url="https://agentblog.net/")],
        [InlineKeyboardButton("ℹ️ شرح عن الموقع", callback_data="about")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("مرحباً بك 👋\nاختر من القائمة:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "social":
        text = (
            "📱 حساباتنا على السوشيال ميديا:\n\n"
            "🔗 فيسبوك: https://facebook.com/\n"
            "🐦 تويتر: https://twitter.com/\n"
            "📸 انستغرام: https://instagram.com/\n"
            "▶️ يوتيوب: https://youtube.com/\n"
        )
        await query.edit_message_text(text)

    elif query.data == "about":
        text = (
            "ℹ️ موقع AgentBlog:\n\n"
            "هو موقع يختص بالمقالات والأخبار والمحتوى الرقمي المتنوع.\n"
            "يمكنك من خلاله متابعة جديد المقالات، الدروس، وأحدث المواضيع التقنية.\n\n"
            "زورنا على: https://agentblog.net/"
        )
        await query.edit_message_text(text)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
