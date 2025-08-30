import logging
import os
import time
import pyodbc  # یا pypyodbc به عنوان جایگزین
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)

# تنظیمات اولیه لاگینگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# شناسه عددی ادمین (برای مثال: 1234567890، حتماً با آی‌دی واقعی جایگزین کنید)
ADMIN_ID = 7193257772

# مسیر پوشه دیتابیس‌ها به مسیر تعیین‌شده توسط شما
DATABASE_FOLDER = "/home/a1161946/domains/a1161946.xsph.ru/public_html/irancell/"
os.makedirs(DATABASE_FOLDER, exist_ok=True)  # اطمینان از وجود پوشه

# لیست نام دیتابیس‌ها از db1.mdb تا db11.mdb
DATABASES = [f"db{i}.mdb" for i in range(1, 12)]

# نام جدول و فیلدها در دیتابیس (این مقادیر فرضی هستند، در صورت نیاز تغییر دهید)
TABLE_NAME = "Table1"
# ترتیب فیلدها (با اندیس 0 شروع می‌شود)
# فیلدها: 1: Phone, 2: Name, 3: Last Name, 8: Home Phone, 12: City, 11: Address, 14: Postal Code, 9: Work Number
FIELD_INDICES = { 
    "phone": 0,
    "name": 1,
    "last_name": 2,
    "home_phone": 7,
    "work_number": 8,
    "address": 10,
    "city": 11,
    "postal_code": 13
}

# تابع برای اتصال به یک فایل mdb و جستجو در آن
def search_in_database(phone_number: str):
    for db_filename in DATABASES:
        db_path = os.path.join(DATABASE_FOLDER, db_filename)
        if not os.path.exists(db_path):
            continue
        try:
            conn_str = (
                r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};"
                r"DBQ=" + db_path + ";"
            )
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()
            # اجرای کوئری برای جستجوی شماره در فیلد ۱
            query = f"SELECT * FROM {TABLE_NAME} WHERE [Field1] = ?"
            cursor.execute(query, (phone_number,))
            row = cursor.fetchone()
            conn.close()
            if row:
                # اگر شماره پیدا شد، اطلاعات مورد نظر را استخراج می‌کنیم
                # در صورتی که هر کدام از فیلد‌ها خالی باشد، مقدار 'ناموجود ❌' نمایش داده می‌شود.
                result = {
                    "phone": row[FIELD_INDICES["phone"]] if row[FIELD_INDICES["phone"]] else "ناموجود ❌",
                    "name": row[FIELD_INDICES["name"]] if row[FIELD_INDICES["name"]] else "ناموجود ❌",
                    "last_name": row[FIELD_INDICES["last_name"]] if row[FIELD_INDICES["last_name"]] else "ناموجود ❌",
                    "home_phone": row[FIELD_INDICES["home_phone"]] if row[FIELD_INDICES["home_phone"]] else "ناموجود ❌",
                    "work_number": row[FIELD_INDICES["work_number"]] if row[FIELD_INDICES["work_number"]] else "ناموجود ❌",
                    "address": row[FIELD_INDICES["address"]] if row[FIELD_INDICES["address"]] else "ناموجود ❌",
                    "city": row[FIELD_INDICES["city"]] if row[FIELD_INDICES["city"]] else "ناموجود ❌",
                    "postal_code": row[FIELD_INDICES["postal_code"]] if row[FIELD_INDICES["postal_code"]] else "ناموجود ❌",
                }
                return result
        except Exception as e:
            logger.error(f"Error reading {db_filename}: {e}")
            continue
    return None

# هندلر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💾 𝐈𝐫𝐚𝐧𝐜𝐞𝐥𝐥 𝐃𝐚𝐭𝐚𝐛𝐚𝐬𝐞", callback_data='irancell_db')]
    ]
    # بررسی ادمین با آی‌دی عددی
    if update.effective_user.id == ADMIN_ID:
        keyboard.append([InlineKeyboardButton("📁 آپلود دیتابیس", callback_data='upload')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("سلام، خوش آمدید!", reply_markup=reply_markup)

# هندلر callback برای دکمه‌ها
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    if data == "irancell_db":
        # نمایش دو دکمه: Help و Back
        keyboard = [
            [InlineKeyboardButton("📕 𝐇𝐞𝐥𝐩", callback_data='help')],
            [InlineKeyboardButton("🔙", callback_data='back')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        user = update.effective_user.first_name if update.effective_user.first_name else "کاربر"
        text = f"👤 {user} لطفا شماره را برای جست و جو ارسال کنید :\n\n📌 درصورت نیاز به بخش راهنمای دیتابیس مراجعه کنید ✅"
        await query.edit_message_text(text=text, reply_markup=reply_markup)
    elif data == "help":
        help_text = (
            "راهنمای دیتابیس ایرانسل ✅\n\n"
            "💠 خرداد ماه سال 93 یک نقص امنیتی در ایرانسل منجر به انتشار حدود 37 میلیون داده شامل نام، نام خانوادگی، شماره تلفن همراه و ثابت، استان، شهر، آدرس محل زندگی، کد پستی و کد ملی شد.\n\n"
            "➖ نکته، فقط می‌توانید سر شماره‌های زیر را جست و جو کنید ✅\n\n"
            "930 _ 933 _ 935 _ 936 _ 937 _ 939\n\n"
            "📌 مثال جست و جو : 9392358752\n\n"
            "و یک دکمه 🔙 زیر پیام برای بازگشت به منوی قبل وجود دارد."
        )
        keyboard = [[InlineKeyboardButton("🔙", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=help_text, reply_markup=reply_markup)
    elif data == "back":
        keyboard = [[InlineKeyboardButton("💾 𝐈𝐫𝐚𝐧𝐜𝐞𝐥𝐥 𝐃𝐚𝐭𝐚𝐛𝐚𝐬𝐞", callback_data='irancell_db')]]
        if update.effective_user.id == ADMIN_ID:
            keyboard.append([InlineKeyboardButton("📁 آپلود دیتابیس", callback_data='upload')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="منوی اصلی:", reply_markup=reply_markup)
    elif data == "upload":
        context.user_data['awaiting_upload'] = True
        await query.edit_message_text(text="لطفا فایل دیتابیس را ارسال کنید:")

# هندلر پیام متنی برای جستجوی شماره
async def search_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone_number = update.message.text.strip()
    user = update.effective_user.first_name if update.effective_user.first_name else "کاربر"
    start_time = time.time()
    
    result = search_in_database(phone_number)
    search_time = f"{time.time() - start_time:.2f} Seconds"
    
    if result:
        if all(value == "ناموجود ❌" for value in result.values()):
            response = "اطلاعات یافت نشد"
        else:
            response = (
                f"Tʜᴇ #sᴇᴀʀᴄʜ ᴡᴀs sᴜᴄᴄᴇssғᴜʟ💀\n\n"
                f"📱Pʜᴏɴᴇ ɴᴜᴍʙᴇʀ : {result.get('phone', 'ناموجود ❌')}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                f"👤 ɴᴀᴍᴇ : {result.get('name', 'ناموجود ❌')}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                f"👤 ʟᴀsᴛ ɴᴀᴍᴇ : {result.get('last_name', 'ناموجود ❌')}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                f"🏠 Hᴏᴍᴇ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ : {result.get('home_phone', 'ناموجود ❌')}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                f"🏙 Cɪᴛʏ : {result.get('city', 'ناموجود ❌')}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                f"🚨 Aᴅᴅʀᴇss : {result.get('address', 'ناموجود ❌')}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                f"✉️ Pᴏsᴛᴀʟ ᴄᴏᴅᴇ : {result.get('postal_code', 'ناموجود ❌')}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                f"🖥 Wᴏʀᴋ ɴᴜᴍʙᴇʀ : {result.get('work_number', 'ناموجود ❌')}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                f"🕒 Sᴇᴀʀᴄʜ ᴛɪᴍᴇ : {search_time}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                f"꧁༺Dᴇᴠᴇʟᴏᴘᴇʀ༺꧂: [꧁༺Dᴇᴠᴇʟᴏᴘᴇʀ༺꧂](https://t.me/Shadow_921?profile)"
            )
    else:
        response = "اطلاعات یافت نشد"
    
    await update.message.reply_text(response)

# هندلر برای دریافت فایل (آپلود دیتابیس) توسط ادمین
async def upload_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('awaiting_upload'):
        document = update.message.document
        if document is None:
            return
        file_name = document.file_name
        destination = os.path.join(DATABASE_FOLDER, file_name)
        try:
            file_obj = await document.get_file()
            await file_obj.download(custom_path=destination)
            await update.message.reply_text(f"فایل ({file_name}) باموفقیت سیو شد ✅")
        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            await update.message.reply_text("خطا در ذخیره سازی فایل.")
        finally:
            context.user_data['awaiting_upload'] = False

if __name__ == '__main__':
    application = ApplicationBuilder().token("8224385462:AAHXepufdjPlzswARdYooUXlp5sw7SuEgno").build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.Document.ALL, upload_file))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_number))
    
    logger.info("Bot is running...")
    application.run_polling()