import telebot
from telebot import types
import requests
import time

# === إعدادات البوت ===
BOT_TOKEN = '8423080239:AAEWoBo5P7VYnwh7fsR9OPVINSE-b_dxoMI'
CHANNEL_USERNAME = '@betbossio'
PAYMENT_LINK = 'https://www.betboss.io/profile/payment?type=deposit'
SIGNUP_LINK = 'https://www.betboss.io'
REQUIRED_REFERRALS = 2

# ✅ فيديوهات تعليمية
videos = [
    {"title": "شرح التسجيل في موقع BetBoss", "url": "https://www.youtube.com/watch?v=hMteNczT620"},
    {"title": "الإيداع الإلكتروني", "url": "https://www.youtube.com/watch?v=mDgbwEEQqMU"},
    {"title": "Goal scorer / هدافين", "url": "https://www.youtube.com/watch?v=COm04zrADyo"},
    {"title": "Specials / احتمالات مميزة", "url": "https://www.youtube.com/watch?v=S-2AEuumA_Y"},
    {"title": "Cashout/كاش أوت", "url": "https://www.youtube.com/watch?v=h0WXnvYSIPQ"},
    {"title": "Live sport/رياضة مباشر", "url": "https://www.youtube.com/watch?v=xISqwlj_rIc"},
    {"title": "DRAW NOBET / تعادل لا رهان", "url": "https://www.youtube.com/watch?v=hVhX_-nU4QQ"},
    {"title": "تذكرة متعددة Multi Ticket bet", "url": "https://www.youtube.com/watch?v=2Iv4-fZMNNk"},
    {"title": "تذكرة نظام System ticket bet", "url": "https://www.youtube.com/watch?v=kTrH7CZMVQA"},
    {"title": "First Goal 1x2", "url": "https://www.youtube.com/watch?v=zED1MDeAeTY"},
    {"title": "INFO THE GG/NG", "url": "https://www.youtube.com/watch?v=CBdfjtcn3cU"},
    {"title": "1x2", "url": "https://www.youtube.com/watch?v=52G02DTa4fE"},
    {"title": "Correct score/النتيجة الصحيحة", "url": "https://www.youtube.com/watch?v=UWQpERfObtU"},
    {"title": "Double Chance/فرصة مضاعفة", "url": "https://www.youtube.com/watch?v=dnQNy_QG9d0"},

    {"title": "Bet with Error/الخطأ في الرهان", "url": "https://www.youtube.com/watch?v=YKTTTL2TZyY"}
]


# ✅ هنا تضيف العرض الحالي
current_offer = """🎁 العرض الحالي:
سجل الآن على الموقع واحصل على 100% بونص على أول إيداع!
لفترة محدودة فقط.

🔥 العرض الثاني:
شارك الرابط مع أصدقائك، وادعُ 2 أشخاص لتحصل على 50 جنيه مجانًا!

📣 العرض الثالث:
احصل على 50 جنيه مجانًا عند التسجيل في الموقع  !
"""




bot = telebot.TeleBot(BOT_TOKEN)

# قاعدة بيانات بسيطة (ذاكرة مؤقتة)
users = {}
referrals = {}

# === التحقق من متابعة القناة ===
def is_user_subscribed(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_USERNAME, user_id).status
        return status in ['member', 'creator', 'administrator']
    except Exception:
        return False

# === الأمر /start ===
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    username = message.from_user.username

    # حفظ الإحالة إن وجدت
    if len(message.text.split()) > 1:
        referrer_id = message.text.split()[1]
        if referrer_id != str(user_id):
            referrals.setdefault(referrer_id, set()).add(user_id)

    if not is_user_subscribed(user_id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('🔔 متابعة القناة', url=f'https://t.me/{CHANNEL_USERNAME[1:]}'))
        markup.add(types.InlineKeyboardButton('✅ تم المتابعة', callback_data='check_sub'))
        bot.send_message(user_id, '👋 للمتابعة، يرجى أولاً الاشتراك في القناة:', reply_markup=markup)
        return

    show_main_menu(user_id)

# === التحقق من المتابعة ===
@bot.callback_query_handler(func=lambda call: call.data == 'check_sub')
def check_subscription(call):
    if is_user_subscribed(call.from_user.id):
        show_main_menu(call.from_user.id)
    else:
        bot.answer_callback_query(call.id, '❌ تأكد من أنك مشترك بالقناة أولاً')

# === القائمة الرئيسية ===
def show_main_menu(user_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('📝 أنشئ حساب على الموقع', url=SIGNUP_LINK))
    markup.add(types.InlineKeyboardButton('💳 رابط الدفع', url=PAYMENT_LINK))
    markup.add(types.InlineKeyboardButton('📤 شارك البوت للحصول على 50 جنيه', callback_data='share_bot'))
    markup.add(types.InlineKeyboardButton('🔄 تحقق من العروض', callback_data='check_offers'))
    markup.add(types.InlineKeyboardButton('🎥 فيديوات تعليمية', callback_data='show_videos'))
    bot.send_message(user_id, '🎁 مرحباً! إليك خدماتنا المتاحة:', reply_markup=markup)
    markup.add(types.InlineKeyboardButton('🎥 فيديوات تعليمية', callback_data='show_videos'))


# === مشاركة البوت ===
    @bot.callback_query_handler(func=lambda call: call.data == 'share_bot')
    def handle_share(call):
        user_id = call.from_user.id
        username = call.from_user.username or "بدون اسم مستخدم"
        link = f'https://t.me/{bot.get_me().username}?start={user_id}'
        count = len(referrals.get(str(user_id), []))

        # إنشاء الرسالة التي تُعرض للمستخدم
        msg = f'🔗 شارك هذا الرابط مع أصدقائك:\n{link}\n\n👥 الإحالات: {count}/{REQUIRED_REFERRALS}'

        if count >= REQUIRED_REFERRALS:
            msg += '\n✅  مبروك! تم تأهيلك للحصول على 50 جنيه في الموقع سوف يتواصل معك الادمن.'

            # ✅ إرسال تنبيه للأدمن مرة واحدة فقط (باستخدام مفتاح تحقق)
            if not users.get(user_id, {}).get('notified'):
                admin_id = 7568738262
                notification = (
                    "📩 مستخدم جديد استوفى شرط الدعوة:\n\n"
                    f"👤 Username: @{username}\n"
                    f"🆔 ID: {user_id}\n"
                    "مؤهل للحصول على 50 جنيه."
                )
                bot.send_message(admin_id, notification)

                # حفظ أنه تم الإشعار
                users.setdefault(user_id, {})['notified'] = True
        else:
            msg += '\n🎯 احصل على 50 جنيه عند دعوة شخصين.'

        bot.send_message(user_id, msg)

# === العروض ===
@bot.callback_query_handler(func=lambda call: call.data == 'check_offers')
def handle_offers(call):
    if current_offer.strip():
        bot.send_message(call.from_user.id, current_offer)
    else:
        bot.send_message(call.from_user.id, '📭 لا يوجد عرض الآن، يمكنك الانتظار، قريباً.')

# === فيديوهات ===
@bot.callback_query_handler(func=lambda call: call.data == 'show_videos')
def show_videos(call):
    text = "🎓 فيديوات تعليمية:\n\n"
    for v in videos:
        text += f"📌 {v['title']}\n▶️ {v['url']}\n\n"
    bot.send_message(call.from_user.id, text)


# === تشغيل البوت ===
print('🤖 البوت يعمل الآن...')
bot.infinity_polling()
