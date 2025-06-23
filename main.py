import os
import json
import logging
import re
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Файл со словами
BAD_WORDS_FILE = "bad_words.json"

# Твой Telegram user ID — ты админ
ADMIN_IDS = [7934050267]

# Токен бота (можно задать напрямую или через переменные окружения)
TOKEN = os.getenv("BOT_TOKEN", "7934050267:AAGteJFHVm1108ffap66G84dXIsVQUWSfUo")

# Функции работы со словами
def load_bad_words():
    try:
        with open(BAD_WORDS_FILE, "r") as f:
            return set(json.load(f))
    except:
        return set()

def save_bad_words(bad_words):
    with open(BAD_WORDS_FILE, "w") as f:
        json.dump(list(bad_words), f)

bad_words = load_bad_words()

# Команды
def start(update: Update, context: CallbackContext):
    update.message.reply_text("🤖 Бот активен и готов модерировать чат!")

def add_word(update: Update, context: CallbackContext):
    if context.args:
        word = context.args[0].lower()
        bad_words.add(word)
        save_bad_words(bad_words)
        update.message.reply_text(f"✅ Слово '{word}' добавлено в бан-лист.")
    else:
        update.message.reply_text("❗ Укажи слово для добавления.")

def remove_word(update: Update, context: CallbackContext):
    if context.args:
        word = context.args[0].lower()
        bad_words.discard(word)
        save_bad_words(bad_words)
        update.message.reply_text(f"🗑️ Слово '{word}' удалено из бан-листа.")
    else:
        update.message.reply_text("❗ Укажи слово для удаления.")

def list_words(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return
    if bad_words:
        words_list = "\n".join(f"• {w}" for w in sorted(bad_words))
        update.message.reply_text(f"📋 Список запрещённых слов:\n{words_list}")
    else:
        update.message.reply_text("📭 Список запрещённых слов пуст.")

# Модерация сообщений
def moderate(update: Update, context: CallbackContext):
    message = update.message.text.lower()
    if any(word in message for word in bad_words):
        try:
            update.message.delete()
            logger.info("Удалено сообщение: %s", update.message.text)
        except Exception as e:
            logger.error("Ошибка удаления: %s", e)

# Главная функция запуска бота
def main():
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("add", add_word))
    dp.add_handler(CommandHandler("remove", remove_word))
    dp.add_handler(CommandHandler("listwords", list_words))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, moderate))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
