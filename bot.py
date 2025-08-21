import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# إعدادات تسجيل الدخول
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

# توكن البوت
TOKEN = "7995911244:AAFBGU7m-XzbNAu31lNRGrAp8eHva0bKxSU"

# تخزين الدعوات لكل مستخدم
user_invites = {}

# قائمة أزرار البداية
def main_menu():
    keyboard = [
        [InlineKeyboardButton("🌐 موقعنا", url="https://agentblog.net/")],
        [InlineKeyboardButton("📱 السوشيال ميديا", callback_data="social")],
        [InlineKeyboardButton("ℹ️ عن الموقع", callback_data="about")],
        [InlineKeyboardButton("🎁 مكافأة الدعوة", callback_data="reward")]
    ]
    return InlineKeyboardMarkup(keyboard)

# أمر البداية
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 أهلاً بك في *بوت AgentBlog الرسمي!*\\n\\n"
        "اختر من القائمة أدناه للاستفادة من خدماتنا:",
        reply_markup=main_menu(),
        parse_mode="MarkdownV2"
    )

# التعامل مع الأزرار
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "social":
        text = (
            "📱 *السوشيال ميديا*\\n\\n"
            "تابعنا على جميع منصاتنا:\\n"
            "- [فيسبوك](https://www.facebook.com/agentblog)\\n"
            "- [إنستغرام](https://www.instagram.com/agentblog)\\n"
            "- [تويتر](https://twitter.com/agentblog)\\n"
            "- [تيك توك](https://www.tiktok.com/@agentblog)"
        )
    elif query.data == "about":
        text = (
            "ℹ️ *عن موقع AgentBlog*\\n\\n"
            "منصة هايلاندر توفر عوائد مالية مغرية وشراكة حقيقية للمؤثرين، "
            "مع دعم كامل على مدار الساعة وانتشار سهل عبر جميع المنصات."
        )
    elif query.data == "reward":
        invites = user_invites.get(user_id, 0)

        if invites < 2:
            text = (
                f"🎁 *مكافأة الدعوة:*\\n\\n"
                f"قم بدعوة صديقين للبوت لتحصل على مكافأتك ✨\\n"
                f"لقد دعوت حتى الآن: *{invites}/2* ✅\\n\\n"
                "أرسل رابط البوت لأصدقائك: https://t.me/agentblogagency_bot"
            )
        else:
            text = (
                "🎉 *مبروك!* لقد أكملت دعوة شخصين بنجاح\\n\\n"
                "✅ حصلت على مكافأتك الخاصة من AgentBlog 🚀"
            )
    else:
        text = "❌ خطأ غير معروف"

    await query.edit_message_text(text, parse_mode="MarkdownV2", reply_markup=main_menu())

# أمر تسجيل دعوة جديدة (تقدر تضيفه مع روابط أفلييت)
async def add_invite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_invites[user_id] = user_invites.get(user_id, 0) + 1
    await update.message.reply_text(
        f"✅ تم تسجيل دعوة جديدة! عدد الدعوات: {user_invites[user_id]}/2",
        parse_mode="MarkdownV2"
    )

# بدء التطبيق
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("addinvite", add_invite))
app.add_handler(CallbackQueryHandler(button_handler))

print("Bot is running...")
app.run_polling()
