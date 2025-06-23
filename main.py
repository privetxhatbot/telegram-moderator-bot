import logging
import json
import re
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext, CommandHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "7934050267:AAGteJFHVm1108ffap66G84dXIsVQUWSfUo"

BAD_WORDS_FILE = "bad_words.json"

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

def moderate(update: Update, context: CallbackContext):
    message = update.message.text.lower()
    if any(word in message for word in bad_words) or "http" in message or "t.me" in message:
        try:
            update.message.delete()
            logger.info("Удалено сообщение: %s", message)
        except Exception as e:
            logger.error("Ошибка удаления: %s", e)

def add_word(update: Update, context: CallbackContext):
    if context.args:
        word = context.args[0].lower()
        bad_words.add(word)
        save_bad_words(bad_words)
        update.message.reply_text(f"Слово '{word}' добавлено.")
    else:
        update.message.reply_text("Напиши слово после /add")

def remove_word(update: Update, context: CallbackContext):
    if context.args:
        word = context.args[0].lower()
        bad_words.discard(word)
        save_bad_words(bad_words)
        update.message.reply_text(f"Слово '{word}' удалено.")
    else:
        update.message.reply_text("Напиши слово после /remove")

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Бот активен и готов удалять плохие сообщения.")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("add", add_word))
    dp.add_handler(CommandHandler("remove", remove_word))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, moderate))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
