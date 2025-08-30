import logging
import os
import time
import csv
import gdown
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)

# تنظیمات اولیه لاگینگ
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# شناسه عددی ادمین
ADMIN_ID = 7193257772

# مسیر پوشه دیتابیس بانک ملی
MELLI_BANK_FOLDER = os.path.join(os.getcwd(), "Melli_bank")
os.makedirs(MELLI_BANK_FOLDER, exist_ok=True)  # اطمینان از وجود پوشه

# لینک دانلود دیتابیس بانک ملی (فرمت دانلود مستقیم)
MELLI_BANK_URL = "https://drive.google.com/uc?export=download&id=1egz_KJ9g4zY3P-mHOExActUfmcGzjDf4"
MELLI_BANK_CSV = os.path.join(MELLI_BANK_FOLDER, "melli_bank.csv")

# تابع دانلود دیتابیس بانک ملی از لینک با استفاده از gdown
def download_melli_bank_csv():
    if not os.path.exists(MELLI_BANK_CSV):
        try:
            # استفاده از gdown برای دانلود فایل
            gdown.download(MELLI_BANK_URL, MELLI_BANK_CSV, quiet=False)
            logger.info("Melli Bank CSV downloaded successfully using gdown.")
        except Exception as e:
            logger.error(f"Error downloading Melli Bank CSV: {e}")
            return False
    return True

# توابع جستجو در دیتابیس بانک ملی (CSV)
def search_melli_by_phone(phone_number: str):
    if not download_melli_bank_csv():
        return None
    start_time = time.time()
    found = None
    try:
        with open(MELLI_BANK_CSV, newline="", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            headers = next(reader, None)  # فرض بر این است که ستون‌ها دارای header هستند
            for row in reader:
                # ستون E (index 4) برای موبایل
                if len(row) >= 5 and row[4].strip() == phone_number:
                    found = {
                        "mobile": row[4].strip(),
                        "full_name": row[2].strip() if len(row) > 2 else "ناموجود ❌",
                        "national_code": row[0].strip() if len(row) > 0 else "ناموجود ❌",
                        "card_number": row[1].strip() if len(row) > 1 else "ناموجود ❌",
                        "birthday": row[3].strip() if len(row) > 3 else "ناموجود ❌",
                    }
                    break
    except Exception as e:
        logger.error(f"Error reading Melli Bank CSV: {e}")
        return None
    if found:
        found["search_time"] = f"{time.time() - start_time:.2f} Seconds"
    return found

def search_melli_by_national(national_code: str):
    if not download_melli_bank_csv():
        return None
    start_time = time.time()
    found = None
    try:
        with open(MELLI_BANK_CSV, newline="", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            headers = next(reader, None)
            for row in reader:
                # ستون A (index 0) برای کد ملی
                if len(row) >= 1 and row[0].strip() == national_code:
                    found = {
                        "mobile": row[4].strip() if len(row) > 4 else "ناموجود ❌",
                        "full_name": row[2].strip() if len(row) > 2 else "ناموجود ❌",
                        "national_code": row[0].strip(),
                        "card_number": row[1].strip() if len(row) > 1 else "ناموجود ❌",
                        "birthday": row[3].strip() if len(row) > 3 else "ناموجود ❌",
                    }
                    break
    except Exception as e:
        logger.error(f"Error reading Melli Bank CSV: {e}")
        return None
    if found:
        found["search_time"] = f"{time.time() - start_time:.2f} Seconds"
    return found

def search_melli_by_card(card_number: str):
    if not download_melli_bank_csv():
        return None
    start_time = time.time()
    found = None
    try:
        with open(MELLI_BANK_CSV, newline="", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            headers = next(reader, None)
            for row in reader:
                # ستون B (index 1) برای شماره کارت
                if len(row) >= 2 and row[1].strip() == card_number:
                    found = {
                        "mobile": row[4].strip() if len(row) > 4 else "ناموجود ❌",
                        "full_name": row[2].strip() if len(row) > 2 else "ناموجود ❌",
                        "national_code": row[0].strip() if len(row) > 0 else "ناموجود ❌",
                        "card_number": row[1].strip(),
                        "birthday": row[3].strip() if len(row) > 3 else "ناموجود ❌",
                    }
                    break
    except Exception as e:
        logger.error(f"Error reading Melli Bank CSV: {e}")
        return None
    if found:
        found["search_time"] = f"{time.time() - start_time:.2f} Seconds"
    return found

# هندلر /start که در منوی اصلی فقط دیتابیس بانک ملی را نمایش می‌دهد
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💾 𝐌𝐞𝐥𝐥𝐢 𝐁𝐚𝐧𝐤 𝐃𝐚𝐭𝐚𝐛𝐚𝐬𝐞 🏦", callback_data="melli_bank_db")]
    ]
    # اگر نیاز به دکمه‌های اضافی برای ادمین باشد می‌توان افزود
    if update.effective_user.id == ADMIN_ID:
        keyboard.append([InlineKeyboardButton("📁 آپلود بانک ملی", callback_data="upload_melli")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("سلام، خوش آمدید!", reply_markup=reply_markup)

# هندلر callback برای دکمه‌ها
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "melli_bank_db":
        keyboard = [
            [InlineKeyboardButton("🔍 𝐒𝐞𝐚𝐫𝐜𝐡 𝐛𝐲 𝐩𝐡𝐨𝐧𝐞 𝐧𝐮𝐦𝐛𝐞𝐫 ☎️", callback_data="melli_phone_search")],
            [InlineKeyboardButton("🔎 𝐒𝐞𝐚𝐫𝐜𝐡 𝐛𝐲 𝐧𝐚𝐭𝐢𝐨𝐧𝐚𝐥𝐢𝐭𝐲 𝐜𝐨𝐝𝐞 🇮🇷", callback_data="melli_national_search")],
            [InlineKeyboardButton("🔎 𝐒𝐞𝐚𝐫𝐜𝐡 𝐛𝐲 𝐜𝐚𝐫𝐝 𝐧𝐮𝐦𝐛𝐞𝐫 💳", callback_data="melli_card_search")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="لطفاً یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=reply_markup)
    
    elif data == "melli_phone_search":
        context.user_data["melli_phone_search"] = True
        context.user_data["melli_national_search"] = False
        context.user_data["melli_card_search"] = False
        keyboard = [
            [InlineKeyboardButton("📕 𝐇𝐞𝐥𝐩", callback_data="melli_phone_help")],
            [InlineKeyboardButton("🔙", callback_data="melli_back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = (
            "لطفاً شماره را جهت جست و جو ارسال کنید :\n\n"
            "درصورت نیاز به راهنمایی به بخش راهنما مراجعه کنید ✅"
        )
        await query.edit_message_text(text=text, reply_markup=reply_markup)
    
    elif data == "melli_phone_help":
        help_text = (
            "📕 راهنمای بخش دیتابیس بانک ملی :\n\n"
            "☎️ نمونه شماره درست برای سرچ : 09913658712\n\n"
            "شماره را با 0 وارد کنید ✅\n\n"
            "🇮🇷 نمونه سرچ درست با کد ملی : 1291175857\n\n"
            "💳 نمونه سرچ درست با شماره کارت : 6037998233574123"
        )
        keyboard = [[InlineKeyboardButton("🔙", callback_data="melli_phone_back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=help_text, reply_markup=reply_markup)
    
    elif data == "melli_phone_back":
        keyboard = [
            [InlineKeyboardButton("🔍 𝐒𝐞𝐚𝐫𝐜𝐡 𝐛𝐲 𝐩𝐡𝐨𝐧𝐞 𝐧𝐮𝐦𝐛𝐞𝐫 ☎️", callback_data="melli_phone_search")],
            [InlineKeyboardButton("🔎 𝐒𝐞𝐫𝐜𝐡 𝐛𝐲 𝐧𝐚𝐭𝐢𝐨𝐧𝐚𝐥𝐢𝐭𝐲 𝐜𝐨𝐝𝐞 🇮🇷", callback_data="melli_national_search")],
            [InlineKeyboardButton("🔎 𝐒𝐞𝐫𝐜𝐡 𝐛𝐲 𝐜𝐚𝐫𝐝 𝐧𝐮𝐦𝐛𝐞𝐫 💳", callback_data="melli_card_search")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="لطفاً یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=reply_markup)
    
    elif data == "melli_national_search":
        context.user_data["melli_phone_search"] = False
        context.user_data["melli_national_search"] = True
        context.user_data["melli_card_search"] = False
        keyboard = [
            [InlineKeyboardButton("📕 𝐇𝐞𝐥𝐩", callback_data="melli_national_help")],
            [InlineKeyboardButton("🔙", callback_data="melli_back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = (
            "لطفاً کد ملی را جهت جست و جو ارسال کنید :\n\n"
            "درصورت نیاز به راهنمایی به بخش راهنما مراجعه کنید ✅"
        )
        await query.edit_message_text(text=text, reply_markup=reply_markup)
    
    elif data == "melli_national_help":
        help_text = (
            "📕 راهنمای بخش دیتابیس بانک ملی :\n\n"
            "☎️ نمونه شماره درست برای سرچ : 09913658712\n\n"
            "شماره را با 0 وارد کنید ✅\n\n"
            "🇮🇷 نمونه سرچ درست با کد ملی : 1291175857\n\n"
            "💳 نمونه سرچ درست با شماره کارت : 6037998233574123"
        )
        keyboard = [[InlineKeyboardButton("🔙", callback_data="melli_national_back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=help_text, reply_markup=reply_markup)
    
    elif data == "melli_national_back":
        keyboard = [
            [InlineKeyboardButton("🔍 𝐒𝐞𝐚𝐫𝐜𝐡 𝐛𝐲 𝐩𝐡𝐨𝐧𝐞 𝐧𝐮𝐦𝐛𝐞𝐫 ☎️", callback_data="melli_phone_search")],
            [InlineKeyboardButton("🔎 𝐒𝐞𝐫𝐜𝐡 𝐛𝐲 𝐧𝐚𝐭𝐢𝐨𝐧𝐚𝐥𝐢𝐭𝐲 𝐜𝐨𝐝𝐞 🇮🇷", callback_data="melli_national_search")],
            [InlineKeyboardButton("🔎 𝐒𝐞𝐫𝐜𝐡 𝐛𝐲 𝐜𝐚𝐫𝐝 𝐧𝐮𝐦𝐛𝐞𝐫 💳", callback_data="melli_card_search")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="لطفاً یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=reply_markup)
    
    elif data == "melli_card_search":
        context.user_data["melli_phone_search"] = False
        context.user_data["melli_national_search"] = False
        context.user_data["melli_card_search"] = True
        keyboard = [
            [InlineKeyboardButton("📕 𝐇𝐞𝐥𝐩", callback_data="melli_card_help")],
            [InlineKeyboardButton("🔙", callback_data="melli_back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = (
            "لطفاً شماره کارت را جهت جست و جو ارسال کنید :\n\n"
            "درصورت نیاز به راهنمایی به بخش راهنما مراجعه کنید ✅"
        )
        await query.edit_message_text(text=text, reply_markup=reply_markup)
    
    elif data == "melli_card_help":
        help_text = (
            "📕 راهنمای بخش دیتابیس بانک ملی :\n\n"
            "☎️ نمونه شماره درست برای سرچ : 09913658712\n\n"
            "شماره را با 0 وارد کنید ✅\n\n"
            "🇮🇷 نمونه سرچ درست با کد ملی : 1291175857\n\n"
            "💳 نمونه سرچ درست با شماره کارت : 6037998233574123"
        )
        keyboard = [[InlineKeyboardButton("🔙", callback_data="melli_card_back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=help_text, reply_markup=reply_markup)
    
    elif data == "melli_card_back":
        keyboard = [
            [InlineKeyboardButton("🔍 𝐒𝐞𝐚𝐫𝐜𝐡 𝐛𝐲 𝐩𝐡𝐨𝐧𝐞 𝐧𝐮𝐦𝐛𝐞𝐫 ☎️", callback_data="melli_phone_search")],
            [InlineKeyboardButton("🔎 𝐒𝐞𝐫𝐜𝐡 𝐛𝐲 𝐧𝐚𝐭𝐢𝐨𝐧𝐚𝐥𝐢𝐭𝐲 𝐜𝐨𝐝𝐞 🇮🇷", callback_data="melli_national_search")],
            [InlineKeyboardButton("🔎 𝐒𝐞𝐫𝐜𝐡 𝐛𝐲 𝐜𝐚𝐫𝐝 𝐧𝐮𝐦𝐛𝐞𝐫 💳", callback_data="melli_card_search")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="لطفاً یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=reply_markup)
    
    elif data == "melli_back":
        keyboard = [
            [InlineKeyboardButton("💾 𝐌𝐞𝐥𝐥𝐢 𝐁𝐚𝐧𝐤 𝐃𝐚𝐭𝐚𝐛𝐚𝐬𝐞 🏦", callback_data="melli_bank_db")]
        ]
        if update.effective_user.id == ADMIN_ID:
            keyboard.append([InlineKeyboardButton("📁 آپلود بانک ملی", callback_data="upload_melli")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="منوی اصلی:", reply_markup=reply_markup)
    
    elif data == "upload_melli":
        context.user_data["awaiting_melli_upload"] = True
        await query.edit_message_text(text="لطفا فایل CSV دیتابیس بانک ملی را ارسال کنید:")

# هندلر پیام متنی برای جستجوی در بانک ملی
async def search_melli(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    result = None
    if context.user_data.get("melli_phone_search"):
        result = search_melli_by_phone(user_input)
    elif context.user_data.get("melli_national_search"):
        result = search_melli_by_national(user_input)
    elif context.user_data.get("melli_card_search"):
        result = search_melli_by_card(user_input)
    
    # بازنشانی فلگ‌های جستجو
    context.user_data["melli_phone_search"] = False
    context.user_data["melli_national_search"] = False
    context.user_data["melli_card_search"] = False
    
    if result:
        response = (
            "Tʜᴇ #sᴇᴀʀᴄʜ ᴡᴀs sᴜᴄᴄᴇssғᴜʟ💀\n\n"
            f"📱Pʜᴏɴᴇ ɴᴜᴍʙᴇʀ : {result.get('mobile', 'ناموجود ❌')}\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👤 Fᴜʟʟ ɴᴀᴍᴇ : {result.get('full_name', 'ناموجود ❌')}\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🇮🇷  ɴᴀᴛɪᴏɴᴀʟɪᴛʏ ᴄᴏᴅᴇ : {result.get('national_code', 'ناموجود ❌')}\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            f"💳 Cᴀʀᴅ ɴᴜᴍʙᴇʀ : {result.get('card_number', 'ناموجود ❌')}\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📆 Bɪʀᴛʜᴅᴀʏ : {result.get('birthday', 'ناموجود ❌')}\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🕒 Sᴇᴀʀᴄʜ ᴛɪᴍᴇ : {result.get('search_time', '')}\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "꧁༺Dᴇᴠᴇʟᴏᴘᴇʀ༺꧂"
        )
    else:
        response = "اطلاعات یافت نشد"
    
    await update.message.reply_text(response)

# هندلر برای دریافت فایل (آپلود دیتابیس بانک ملی) توسط ادمین
async def upload_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_melli_upload"):
        document = update.message.document
        if document is None:
            return
        file_name = document.file_name
        destination = os.path.join(MELLI_BANK_FOLDER, file_name)
        try:
            file_obj = await document.get_file()
            await file_obj.download(custom_path=destination)
            await update.message.reply_text(f"فایل ({file_name}) باموفقیت سیو شد ✅")
        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            await update.message.reply_text("خطا در ذخیره سازی فایل.")
        finally:
            context.user_data["awaiting_melli_upload"] = False

if __name__ == "__main__":
    application = ApplicationBuilder().token("8224385462:AAHXepufdjPlzswARdYooUXlp5sw7SuEgno").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.Document.ALL, upload_file))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_melli))

    logger.info("Bot is running...")
    application.run_polling()