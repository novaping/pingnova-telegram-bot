import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram import Update
from telegram import InputFile
from dotenv import load_dotenv

# وارد کردن توکن مستقیم داخل کد
TOKEN = "7440105727:AAEjldprMU_17WD2TG-K0mupkFEkfZwYHYw"  # توکن رو اینجا وارد کن

# دیکشنری برای ذخیره اطلاعات زیرمجموعه‌ها و پوینت‌ها
user_data = {}

# مسیر ذخیره فایل‌های کانفیگ
CONFIGS_PATH = "configs/"

# لیست ادمین‌ها
admins = [5789850982]  # به جای YOUR_ADMIN_ID شناسه ادمین اصلی رو بذار

# فرمان /start
def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {"points": 0, "referrals": 0, "config_sent": False}
    update.message.reply_text(f"سلام! به ربات PingNova خوش آمدید.\nبرای شروع، لطفاً از طریق لینک زیر دوستان خود رو دعوت کن.\n\n/start")

# فرمان /referrals برای نمایش تعداد زیرمجموعه‌ها
def referrals(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id in user_data:
        referrals_count = user_data[user_id]["referrals"]
        update.message.reply_text(f"شما {referrals_count} نفر را به ربات دعوت کرده‌اید.")
    else:
        update.message.reply_text("شما هنوز کسی رو دعوت نکردید.")

# فرمان /points برای نمایش امتیازات
def points(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id in user_data:
        points = user_data[user_id]["points"]
        update.message.reply_text(f"شما {points} پوینت دارید.")
    else:
        update.message.reply_text("شما هنوز هیچ پوینتی ندارید.")

# فرمان /invite برای ارسال لینک دعوت
def invite(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    invite_link = f"توجه! برای دعوت دوستان خود و گرفتن امتیاز، از لینک زیر استفاده کن:\nhttps://t.me/{context.bot.username}?start={user_id}"
    update.message.reply_text(invite_link)

# فرمان /claim برای درخواست کانفیگ ویژه بعد از جمع‌آوری زیرمجموعه‌ها
def claim(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id in user_data:
        referrals = user_data[user_id]["referrals"]
        if referrals >= 10 and not user_data[user_id]["config_sent"]:
            # ارسال کانفیگ ویژه به کاربر
            config_file = f"{CONFIGS_PATH}special_config.conf"  # فایل کانفیگ ویژه
            if os.path.exists(config_file):
                with open(config_file, "rb") as f:
                    context.bot.send_document(chat_id=user_id, document=f)
                user_data[user_id]["config_sent"] = True
                update.message.reply_text("تبریک! شما به حد نصاب دعوت رسیدید و کانفیگ ویژه دریافت کردید.")
            else:
                update.message.reply_text("فایل کانفیگ ویژه موجود نیست.")
        else:
            update.message.reply_text("برای دریافت کانفیگ ویژه باید حداقل ۱۰ نفر رو دعوت کنید.")
    else:
        update.message.reply_text("شما هنوز شروع نکردید.")

# فرمان /setpoints برای اعطای پوینت دستی به کاربران (فقط برای ادمین)
def set_points(update: Update, context: CallbackContext):
    if update.message.from_user.id in admins:  # بررسی ادمین بودن
        try:
            user_id = int(context.args[0])
            points = int(context.args[1])
            if user_id not in user_data:
                user_data[user_id] = {"points": 0, "referrals": 0, "config_sent": False}
            user_data[user_id]["points"] += points
            update.message.reply_text(f"به کاربر {user_id} {points} پوینت افزوده شد.")
        except (IndexError, ValueError):
            update.message.reply_text("لطفاً شناسه کاربری و تعداد پوینت را به درستی وارد کنید.")
    else:
        update.message.reply_text("شما دسترسی به این دستور را ندارید.")

# فرمان /reset برای بازنشانی تمام اطلاعات (فقط برای ادمین)
def reset(update: Update, context: CallbackContext):
    if update.message.from_user.id in admins:  # بررسی ادمین بودن
        user_data.clear()
        update.message.reply_text("تمام اطلاعات کاربران پاک شد.")
    else:
        update.message.reply_text("شما دسترسی به این دستور را ندارید.")

# فرمان /help برای راهنمایی کاربران
def help_command(update: Update, context: CallbackContext):
    update.message.reply_text("""
    دستورات موجود:
    /start - شروع به کار
    /referrals - تعداد زیرمجموعه‌های شما
    /points - تعداد پوینت‌های شما
    /invite - لینک دعوت برای دوستان
    /claim - درخواست کانفیگ ویژه
    /setpoints [user_id] [points] - اعطای پوینت دستی
    /reset - بازنشانی تمام اطلاعات
    /upload_config - آپلود فایل کانفیگ
    /add_admin [user_id] - اضافه کردن ادمین
    /remove_admin [user_id] - حذف ادمین
    """)

# فرمان /upload_config برای آپلود فایل کانفیگ توسط ادمین
def upload_config(update: Update, context: CallbackContext):
    if update.message.from_user.id in admins:  # بررسی ادمین بودن
        if update.message.document:
            file = update.message.document
            file_path = os.path.join(CONFIGS_PATH, file.file_name)
            file.download(file_path)
            update.message.reply_text(f"فایل کانفیگ با موفقیت آپلود شد: {file.file_name}")
        else:
            update.message.reply_text("لطفاً فایل کانفیگ را ارسال کنید.")
    else:
        update.message.reply_text("شما دسترسی به این دستور را ندارید.")

# فرمان /add_admin برای اضافه کردن ادمین
def add_admin(update: Update, context: CallbackContext):
    if update.message.from_user.id in admins:  # بررسی ادمین بودن
        try:
            new_admin_id = int(context.args[0])
            if new_admin_id not in admins:
                admins.append(new_admin_id)
                update.message.reply_text(f"ادمین جدید با شناسه {new_admin_id} به لیست ادمین‌ها اضافه شد.")
            else:
                update.message.reply_text(f"این کاربر قبلاً ادمین است.")
        except (IndexError, ValueError):
            update.message.reply_text("لطفاً شناسه ادمین جدید را وارد کنید.")
    else:
        update.message.reply_text("شما دسترسی به این دستور را ندارید.")

# فرمان /remove_admin برای حذف ادمین
def remove_admin(update: Update, context: CallbackContext):
    if update.message.from_user.id in admins:  # بررسی ادمین بودن
        try:
            admin_id_to_remove = int(context.args[0])
            if admin_id_to_remove in admins:
                admins.remove(admin_id_to_remove)
                update.message.reply_text(f"ادمین با شناسه {admin_id_to_remove} از لیست ادمین‌ها حذف شد.")
            else:
                update.message.reply_text(f"این کاربر ادمین نیست.")
        except (IndexError, ValueError):
            update.message.reply_text("لطفاً شناسه ادمین را وارد کنید.")
    else:
        update.message.reply_text("شما دسترسی به این دستور را ندارید.")

def main():
    # ایجاد و راه‌اندازی آپدیت‌کننده با توکن
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # افزودن دستورات به ربات
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("referrals", referrals))
    dp.add_handler(CommandHandler("points", points))
    dp.add_handler(CommandHandler("invite", invite))
    dp.add_handler(CommandHandler("claim", claim))
    dp.add_handler(CommandHandler("setpoints", set_points))
    dp.add_handler(CommandHandler("reset", reset))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("upload_config", upload_config))  # دستور آپلود کانفیگ
    dp.add_handler(CommandHandler("add_admin", add_admin))  # دستور اضافه کردن ادمین
    dp.add_handler(CommandHandler("remove_admin", remove_admin))  # دستور حذف ادمین

    # مدیریت فایل‌های ارسالی
    dp.add_handler(MessageHandler(Filters.document.mime_type("application/octet-stream"), upload_config))

    # شروع ربات
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
