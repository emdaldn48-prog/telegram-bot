import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# جلب التوكن من Environment Variable
TOKEN = os.getenv("BOT_TOKEN")

# قواميس لحفظ الدعوات
user_invites = {}

# رسالة البداية
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🌍 الموقع الرسمي", url="https://agentblog.net/")],
        [InlineKeyboardButton("📱 السوشيال ميديا", callback_data="social")],
        [InlineKeyboardButton("ℹ️ عن الموقع", callback_data="about")],
        [InlineKeyboardButton("💰 برنامج الشراكة والمكافآت", callback_data="partnership")],
        [InlineKeyboardButton("🎁 مكافأة الدعوة", callback_data="reward")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "👋 أهلاً بك في *بوت AgentBlog الرسمي!*\n\n"
        "اختر من القائمة أدناه للاستفادة من خدماتنا:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# التعامل مع الأزرار
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "social":
        text = (
            "📱 تابعنا على السوشيال ميديا:\n\n"
            "🔗 فيسبوك: https://www.facebook.com/profile.php?id=61579717285065\n"
            "🐦 تويتر: https://x.com/landeragentblog\n"
            "📸 انستغرام: https://www.instagram.com/landeragentblog/\n"
            
        )
        await query.edit_message_text(text)

    elif query.data == "about":
        text = (
            "ℹ️ *عن موقع AgentBlog:*\n\n"
            "منصة رائدة تهتم بالمقالات، الأخبار، والمحتوى الرقمي المتنوع.\n"
            "هنا تجد المعرفة والأفكار التي تساعدك على مواكبة التطورات التقنية.\n\n"
            "🌍 زورنا: https://agentblog.net/"
        )
        await query.edit_message_text(text, parse_mode="Markdown")

    elif query.data == "partnership":
        text = (
            "💰 *العائد المغري والشراكة مع هايلاندر:*\n\n"
            " *رابط أفلييت مخصص لك* — تحصل على رابط فريد يحمل اسمك.\n"
            " *عوائد مالية استثنائية* — كل مشاركة ناجحة تعني ربح مباشر لك.\n"
            " *انتشار سهل عبر المنصات* — شارك على فيسبوك، انستغرام، تويتر، تيك توك.\n"
            " *دعم متكامل على مدار الساعة* — نحن معك خطوة بخطوة.\n\n"
            "✨ ليست مجرد شراكة... إنها فرصة حقيقية لبناء دخل مستمر!"
        )
        await query.edit_message_text(text, parse_mode="Markdown")

    elif query.data == "reward":
        invites = user_invites.get(user_id, 0)

        if invites < 2:
            text = (
                f"🎁 *مكافأة الدعوة:*\n\n"
                f"قم بدعوة صديقين للبوت لتحصل على مكافأتك! ✨\n"
                f"لقد دعوت حتى الآن: *{invites}/2* ✅\n\n"
                "أرسل رابط البوت لأصدقائك: https://t.me/agentblogagency_bot
            )
        else:
            text = (
                "🎉 مبروك! لقد أكملت دعوة شخصين بنجاح.\n\n"
                "✅ حصلت على مكافأتك الخاصة من AgentBlog! 🚀"
            )
        await query.edit_message_text(text, parse_mode="Markdown")

# أوامر لإضافة الدعوات (تجريبية — يمكن ربطها بنظام إحالات حقيقي لاحقاً)
async def invite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ استخدم الأمر هكذا: /invite user_id")
        return

    inviter_id = update.message.from_user.id
    invited_id = int(context.args[0])

    if invited_id == inviter_id:
        await update.message.reply_text("⚠️ لا يمكنك دعوة نفسك 😅")
        return

    user_invites[inviter_id] = user_invites.get(inviter_id, 0) + 1
    await update.message.reply_text("✅ تمت إضافة الدعوة! شكراً لمشاركتك البوت 🎁")

# تشغيل البوت
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("invite", invite))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
