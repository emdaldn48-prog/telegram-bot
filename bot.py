# bot.py
import os
import logging
from typing import Dict, Set, Tuple, Optional

from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ChatMember,
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    PicklePersistence,
)

# =================== الإعدادات العامة ===================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# توكن البوت من متغير البيئة (لا تضع التوكن داخل الكود)
TOKEN = os.getenv("BOT_TOKEN")

# اسم القناة المطلوب الاشتراك بها
CHANNEL_USERNAME = "@Agentblognet"  # تأكد أن البوت Admin في القناة العامة

# اسم المستخدم للبوت (يتم جلبه تلقائياً عند التشغيل)
BOT_USERNAME_CACHE_KEY = "bot_username"

# مفاتيح بيانات الحفظ
KEY_INVITES = "invites"          # Dict[int, int]   -> {referrer_id: count}
KEY_USERS = "users_registered"   # Set[int]         -> {user_ids who started once}


# =================== أدوات الواجهة ===================
def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🌍 الموقع الرسمي", url="https://agentblog.net/")],
            [InlineKeyboardButton("📱 السوشيال ميديا", callback_data="social")],
            [InlineKeyboardButton("ℹ️ عن الموقع", callback_data="about")],
            [InlineKeyboardButton("💰 برنامج الشراكة والمكافآت", callback_data="partner")],
            [InlineKeyboardButton("🎁 مكافأة الدعوة", callback_data="reward")],
        ]
    )


def join_check_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📢 اشترك في القناة", url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}")],
            [InlineKeyboardButton("✅ تحقّق", callback_data="verify_sub")],
        ]
    )


def share_keyboard(deep_link: str) -> InlineKeyboardMarkup:
    # زر مشاركة يفتح واجهة المشاركة في تيليغرام مباشرة
    share_url = f"https://t.me/share/url?url={deep_link}&text=جرب%20هذا%20البوت%20الرهيب%20🚀"
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📣 شارك البوت الآن", url=share_url)],
            [InlineKeyboardButton("🔄 تحديث الحالة", callback_data="reward")],
            [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="home")],
        ]
    )


# =================== وظائف مساعدة ===================
async def is_subscribed(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
    """يتحقق من اشتراك المستخدم في القناة."""
    try:
        member: ChatMember = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        status = getattr(member, "status", "")
        return status in ("member", "administrator", "creator")
    except Exception as e:
        logger.warning(f"Subscription check failed: {e}")
        # لو القناة خاصة/أو البوت ليس أدمن، قد يفشل الفحص. سنعتبره غير مشترك.
        return False


def ensure_persistence_buckets(context: ContextTypes.DEFAULT_TYPE) -> Tuple[Dict[int, int], Set[int]]:
    """التأكد من إنشاء هياكل البيانات في التخزين الدائم."""
    bot_data = context.bot_data
    if KEY_INVITES not in bot_data:
        bot_data[KEY_INVITES] = {}
    if KEY_USERS not in bot_data:
        bot_data[KEY_USERS] = set()
    return bot_data[KEY_INVITES], bot_data[KEY_USERS]


def parse_ref_arg(args: list) -> Optional[int]:
    """يرجع user_id المُحيل من وسيطة /start (صيغة: ref<id>)."""
    if not args:
        return None
    token = args[0].strip()
    if token.startswith("ref") and token[3:].isdigit():
        return int(token[3:])
    return None


def get_bot_username_cached(context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
    return context.bot_data.get(BOT_USERNAME_CACHE_KEY)


def set_bot_username_cached(context: ContextTypes.DEFAULT_TYPE, username: str) -> None:
    context.bot_data[BOT_USERNAME_CACHE_KEY] = username


def make_deep_link(bot_username: str, user_id: int) -> str:
    return f"https://t.me/{bot_username}?start=ref{user_id}"


# =================== Handlers ===================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """أمر البداية + احتساب الإحالة إن وُجدت + فحص الاشتراك."""
    ensure_persistence_buckets(context)
    # خزّن اسم البوت للاستخدام في الروابط
    if not get_bot_username_cached(context):
        set_bot_username_cached(context, context.bot.username)

    user = update.effective_user
    user_id = user.id if user else None

    # معالجة الإحالة من الوسيطة
    referrer_id = parse_ref_arg(context.args)
    invites_dict, users_set = ensure_persistence_buckets(context)

    # إذا أول مرة هذا المستخدم يستخدم البوت نسجله
    is_new_user = user_id not in users_set
    if is_new_user:
        users_set.add(user_id)
        # لو لديه مُحيل صالح ومش نفسه، سجّل له دعوة
        if referrer_id and referrer_id != user_id:
            invites_dict[referrer_id] = invites_dict.get(referrer_id, 0) + 1

    # فحص الاشتراك
    if not await is_subscribed(context, user_id):
        await update.message.reply_text(
            "🔒 لا يمكنك استخدام البوت قبل الاشتراك في قناتنا الرسمية.\n\n"
            f"القناة: <b>{CHANNEL_USERNAME}</b>\n\n"
            "بعد الاشتراك اضغط <b>تحقّق</b>.",
            parse_mode=ParseMode.HTML,
            reply_markup=join_check_keyboard(),
        )
        return

    # رسالة ترحيب + القائمة
    await update.message.reply_text(
        f"👋 أهلاً <b>{user.first_name}</b>!\n"
        "اختر من القائمة بالأسفل للمتابعة:",
        parse_mode=ParseMode.HTML,
        reply_markup=main_menu(),
    )


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """إظهار القائمة الرئيسية يدوياً."""
    user = update.effective_user
    if not await is_subscribed(context, user.id):
        await update.message.reply_text(
            "🔒 يجب الاشتراك أولاً.",
            parse_mode=ParseMode.HTML,
            reply_markup=join_check_keyboard(),
        )
        return

    await update.message.reply_text(
        "🏠 هذه هي القائمة الرئيسية:",
        parse_mode=ParseMode.HTML,
        reply_markup=main_menu(),
    )


async def cb_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة أزرار الـ Inline."""
    query = update.callback_query
    user = query.from_user
    user_id = user.id
    await query.answer()

    # تحقق الاشتراك باستثناء زر التحقق نفسه
    if query.data != "verify_sub":
        if not await is_subscribed(context, user_id):
            await query.message.reply_text(
                "🔒 لا يمكنك المتابعة قبل الاشتراك.",
                parse_mode=ParseMode.HTML,
                reply_markup=join_check_keyboard(),
            )
            return

    # اجلب اسم البوت المخزن لرابط الدعوة
    bot_username = get_bot_username_cached(context) or context.bot.username
    invites_dict, users_set = ensure_persistence_buckets(context)

    if query.data == "verify_sub":
        if await is_subscribed(context, user_id):
            await query.message.reply_text(
                "✅ تم التحقق من الاشتراك! تفضل بالقائمة الرئيسية:",
                parse_mode=ParseMode.HTML,
                reply_markup=main_menu(),
            )
        else:
            await query.message.reply_text(
                "❌ لم يتم العثور على اشتراك.\n"
                "يرجى الاشتراك في القناة ثم الضغط على <b>تحقّق</b>.",
                parse_mode=ParseMode.HTML,
                reply_markup=join_check_keyboard(),
            )

    elif query.data == "home":
        await query.message.reply_text(
            "🏠 القائمة الرئيسية:",
            parse_mode=ParseMode.HTML,
            reply_markup=main_menu(),
        )

    elif query.data == "social":
        await query.message.reply_text(
            "📱 <b>تابعنا على السوشيال ميديا</b>\n\n"
            f"• قناة تيليغرام: <a href='https://t.me/{CHANNEL_USERNAME.lstrip('@')}'>@{CHANNEL_USERNAME.lstrip('@')}</a>\n"
            "• فيسبوك: <a href='https://www.facebook.com/profile.php?id=61579717285065'>facebook.com</a>\n"
            "• إنستغرام: <a href='https://www.instagram.com/landeragentblog/'>instagram.com</a>\n"
            "• تويتر / X: <a href='https://x.com/landeragentblog'>twitter.com</a>\n",
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
            reply_markup=main_menu(),
        )

      elif query.data == "about":
        await query.message.reply_text(
            "ℹ️ <b>عن موقع AgentBlog</b>\n\n"
            "سواء كنت مؤثرًا يتطلع إلى تحويل شغفه إلى دخل، أو معلنًا يتطلع إلى وصول أقوى، "
            "أو وكالة تتطلع إلى توسيع قاعدة عملائها… فإن <b>هايلاندر</b> هي بوابتك إلى عالم من الفرص اللامحدود.\n\n"
            "لن تكون مجرد منصة تسويق مؤثرة، بل ستكون تجربة متكاملة تربط المعلنين والمؤثرين والوكالات "
            "في نظام بيئي مبتكر واحد.\n\n"
            "🌍 الموقع: <a href='https://agentblog.net/'>agentblog.net</a>",
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
            reply_markup=main_menu(),
        )


    elif query.data == "partner":
        await query.message.reply_text(
            "💰 <b>العائد المغري والشراكة مع هايلاندر</b>\n\n"
            "• <b>رابط أفلييت مخصص لك:</b> تحصل على رابط فريد يحمل اسمك لمتابعة النتائج بدقة.\n"
            "• <b>عوائد مجزية:</b> عمولة على البيع أو التحويل، دفع مقابل الظهور، ودفع مقابل النقرة.\n"
            "• <b>انتشار سهل:</b> شارك على فيسبوك، إنستغرام، تويتر، وتيك توك بضغطة زر.\n"
            "• <b>دعم متكامل 24/7:</b> فريق مختص يساندك ويقدّم لك أفضل الممارسات.\n\n"
            "✨ شراكتك معنا فرصة لبناء دخل مستمر وتوسيع حضورك الرقمي بخطوات عملية.",
            parse_mode=ParseMode.HTML,
            reply_markup=main_menu(),
        )

    elif query.data == "reward":
        # تقدّم المستخدم في الدعوات
        count = invites_dict.get(user_id, 0)
        deep_link = make_deep_link(bot_username, user_id)

        if count < 2:
            await query.message.reply_text(
                "🎁 <b>مكافأة الدعوة</b>\n\n"
                "ادعُ صديقين لبدء استخدام البوت لتحصل على مكافأتك ✨\n"
                f"التقدّم الحالي: <b>{count}/2</b>\n\n"
                "هذا هو <b>رابط دعوتك الفريد</b>:\n"
                f"<code>{deep_link}</code>\n\n"
                "اضغط الزر بالأسفل لمشاركة الرابط مباشرة داخل تيليغرام:",
                parse_mode=ParseMode.HTML,
                reply_markup=share_keyboard(deep_link),
                disable_web_page_preview=True,
            )
        else:
            await query.message.reply_text(
                "🎉 <b>مبروك!</b>\n"
                "لقد أكملت دعوة شخصين بنجاح وحصلت على مكافأتك من AgentBlog 🚀",
                parse_mode=ParseMode.HTML,
                reply_markup=main_menu(),
            )

    else:
        await query.message.reply_text(
            "❓ خيار غير معروف. استخدم القائمة:",
            parse_mode=ParseMode.HTML,
            reply_markup=main_menu(),
        )


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """إظهار رصيد الدعوات للمستخدم."""
    invites_dict, _ = ensure_persistence_buckets(context)
    user_id = update.effective_user.id
    count = invites_dict.get(user_id, 0)
    await update.message.reply_text(
        f"📊 دعواتك المسجّلة: <b>{count}</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=main_menu(),
    )


# =================== تشغيل التطبيق ===================
def main() -> None:
    if not TOKEN:
        raise RuntimeError("Environment variable BOT_TOKEN is not set.")

    # تخزين بسيط على القرص أثناء عمل السيرفر
    persistence = PicklePersistence(filepath="bot_data.pkl")

    app: Application = (
        ApplicationBuilder()
        .token(TOKEN)
        .persistence(persistence)
        .build()
    )

    # مساعدة: احفظ اسم المستخدم عند الإقلاع (احتياطي)
    async def cache_bot_username(app_: Application) -> None:
        try:
            me = await app_.bot.get_me()
            app_.bot_data[BOT_USERNAME_CACHE_KEY] = me.username
        except Exception as e:
            logger.warning(f"Could not cache bot username: {e}")

    app.post_init = cache_bot_username

    # الأوامر
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CommandHandler("stats", stats))

    # الأزرار
    app.add_handler(CallbackQueryHandler(cb_handler))

    logger.info("Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
