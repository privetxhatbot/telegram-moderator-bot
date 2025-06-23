import os
import json
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, CallbackContext

WORDS_FILE = "bad_words.json"
ADMIN_IDS = [7934050267]  # Твой Telegram user ID

# Загрузка слов
def load_words():
    if not os.path.exists(WORDS_FILE):
        with open(WORDS_FILE, "w") as f:
            json.dump([], f)
    with open(WORDS_FILE, "r") as f:
        return json.load(f)

# Сохранение слов
def save_words(words):
    with open(WORDS_FILE, "w") as f:
        json.dump(words, f)

# Команда /addword
def add_word(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return

    if not context.args:
        update.message.reply_text("❗ Укажи слово после команды.")
        return

    word = context.args[0].lower()
    words = load_words()

    if word not in words:
        words.append(word)
        save_words(words)
        update.message.reply_text(f"✅ Слово '{word}' добавлено в бан-лист.")
    else:
        update.message.reply_text(f"⚠️ Слово '{word}' уже в списке.")

# Команда /delword
def del_word(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return

    if not context.args:
        update.message.reply_text("❗ Укажи слово после команды.")
        return

    word = context.args[0].lower()
    words = load_words()

    if word in words:
        words.remove(word)
        save_words(words)
        update.message.reply_text(f"🗑 Слово '{word}' удалено из списка.")
    else:
        update.message.reply_text(f"⚠️ Слова '{word}' нет в списке.")

# Команда /listwords
def list_words(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return

    words = load_words()
    if words:
        update.message.reply_text("📃 Забаненные слова:\n" + ", ".join(words))
    else:
        update.message.reply_text("📭 Список пуст.")

# Цензор
def censor(update: Update, context: CallbackContext):
    text = update.message.text.lower()
    words = load_words()

    if any(bad in text for bad in words) or "http://" in text or "https://" in text or "t.me/" in text:
        try:
            update.message.delete()
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"⛔ Сообщение от @{update.effective_user.username or update.effective_user.id} удалено."
            )
        except Exception as e:
            print(f"Ошибка удаления: {e}")

def main():
    TOKEN = os.getenv("BOT_TOKEN")
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, censor))
    dp.add_handler(CommandHandler("addword", add_word))
    dp.add_handler(CommandHandler("delword", del_word))
    dp.add_handler(CommandHandler("listwords", list_words))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
