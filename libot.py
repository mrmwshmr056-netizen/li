import telebot
import json
import os

TOKEN = '8259562053:AAHu04lONMvvKHxQFoSUSgkFVzlX7p57BIM' # من @BotFather
ADMIN_ID = 7838442083 # ضع الـ ID حقك من @userinfobot
BOOKS_FILE = 'books.json'

bot = telebot.TeleBot(TOKEN)

# توقيع المطور الجديد ستايل 8 ⚡
DEV_SIGN = "\n\n⚡ 𝑇ℎ𝑒 𝐷𝑒𝑣𝑒𝑙𝑜𝑝𝑒𝑟 𝑀𝑈𝑆𝑇𝐴𝐹𝐴 ⚡"

def add_sign(text):
    return text + DEV_SIGN

# تحميل الكتب
def load_books():
    if os.path.exists(BOOKS_FILE):
        with open(BOOKS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"first": {}, "second": {}, "third": {}}

def save_books(books):
    with open(BOOKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(books, f, ensure_ascii=False, indent=4)

books = load_books()

# /start للطلاب
@bot.message_handler(commands=['start'])
def start(message):
    name = message.from_user.first_name
    welcome = f"""أهلاً بيك يا {name} 👋

أنا بوت تعليمي لطلاب الثانوية السودانية 📚
اختار سنتك الدراسية:

1️⃣ السنة الأولى - /first
2️⃣ السنة الثانية - /second
3️⃣ السنة الثالثة - /third"""

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('السنة الأولى', 'السنة الثانية', 'السنة الثالثة')
    bot.send_message(message.chat.id, add_sign(welcome), reply_markup=markup)

# عرض كتب كل سنة
@bot.message_handler(commands=['first', 'second', 'third'])
@bot.message_handler(func=lambda m: m.text in ['السنة الأولى', 'السنة الثانية', 'السنة الثالثة'])
def show_books(message):
    name = message.from_user.first_name
    grade_map = {'/first': 'first', '/second': 'second', '/third': 'third',
                 'السنة الأولى': 'first', 'السنة الثانية': 'second', 'السنة الثالثة': 'third'}
    grade = grade_map[message.text]
    grade_name = {'first': 'الأولى', 'second': 'الثانية', 'third': 'الثة'}[grade]

    if not books[grade]:
        bot.send_message(message.chat.id, add_sign(f"لسه ما في كتب مضافة للسنة {grade_name} 😢"))
        return

    text = f"📚 يا {name} دي كتب السنة {grade_name}:\n\n"
    for book_name in books[grade].keys():
        text += f"🔹 {book_name}\n"
        text += f"📥 /get {grade} {book_name}\n\n"

    bot.send_message(message.chat.id, add_sign(text))

# /get - تحميل الكتاب للطالب
@bot.message_handler(commands=['get'])
def get_book(message):
    try:
        _, grade, book_name = message.text.split(' ', 2)
        file_id = books[grade][book_name]
        name = message.from_user.first_name
        bot.send_document(message.chat.id, file_id, caption=f"📥 يا {name} دا كتاب {book_name}\nبالتوفيق ❤️{DEV_SIGN}")
    except:
        bot.send_message(message.chat.id, add_sign("الصيغة غلط! مثال: /get first رياضيات أولى"))

# ====== أوامر الأدمن بس ======

@bot.message_handler(commands=['upload'])
def upload_help(message):
    if message.from_user.id!= ADMIN_ID:
        return
    text = """📤 طريقة رفع الكتاب يا أدمن:

1. ارسل ملف PDF للبوت
2. مع الملف اكتب في الـ Caption:
سنة|اسم المادة

مثال:
first|رياضيات أولى
second|فيزياء تانية
third|كيمياء تالتة"""
    bot.send_message(message.chat.id, add_sign(text))

# استقبال ملف PDF من الأدمن
@bot.message_handler(content_types=['document'])
def handle_doc(message):
    if message.from_user.id!= ADMIN_ID:
        bot.send_message(message.chat.id, add_sign("انت ما أدمن 😅"))
        return

    if not message.caption:
        bot.send_message(message.chat.id, add_sign("لازم تكتب في الـ Caption: سنة|اسم المادة"))
        return

    try:
        grade, book_name = message.caption.split('|')
        grade = grade.strip().lower()
        book_name = book_name.strip()

        if grade not in ['first', 'second', 'third']:
            bot.send_message(message.chat.id, add_sign("السنة غلط! اكتب first أو second أو third"))
            return

        file_id = message.document.file_id
        books[grade][book_name] = file_id
        save_books(books)

        grade_name = {'first': 'الأولى', 'second': 'الثانية', 'third': 'الثة'}[grade]
        bot.send_message(message.chat.id, add_sign(f"✅ تم رفع الكتاب بنجاح!\n📚 السنة: {grade_name}\n📖 المادة: {book_name}"))
    except:
        bot.send_message(message.chat.id, add_sign("خطأ في الصيغة! استخدم: سنة|اسم المادة"))

@bot.message_handler(commands=['delete'])
def delete_book(message):
    if message.from_user.id!= ADMIN_ID:
        return
    try:
        _, grade, book_name = message.text.split(' ', 2)
        del books[grade][book_name]
        save_books(books)
        bot.send_message(message.chat.id, add_sign(f"🗑️ تم حذف {book_name}"))
    except:
        bot.send_message(message.chat.id, add_sign("الصيغة: /delete first اسم الكتاب"))

@bot.message_handler(commands=['list'])
def list_books(message):
    if message.from_user.id!= ADMIN_ID:
        return
    text = "📚 كل الكتب المرفوعة:\n\n"
    for grade, grade_name in [('first', 'الأولى'), ('second', 'الثانية'), ('third', 'الثة')]:
        text += f"=== السنة {grade_name} ===\n"
        for book in books[grade].keys():
            text += f"• {book}\n"
        text += "\n"
    bot.send_message(message.chat.id, add_sign(text))

print("البوت شغال 24/7...")
bot.polling(none_stop=True)