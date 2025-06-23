from telegram import Update
from telegram.ext import (
    ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
)
import json
import os

# 🔐 Токен бота
TOKEN = "7934050267:AAGteJFHVm1108ffap66G84dXIsVQUWSfUo"

# 👤 Твой Telegram ID — только ты админ
ADMIN_ID = 8113864156

# 📁 Файл со списком плохих слов
BAD_WORDS_FILE = "bad_words.json"


def load_bad_words():
    if not os.path.exists(BAD_WORDS_FILE):
        with open(BAD_WORDS_FILE, "w") as f:
            json.dump(["мат1", "мат2"], f)
    with open(BAD_WORDS_FILE, "r") as f:
        return json.load(f)


def save_bad_words(words):
    with open(BAD_WORDS_FILE, "w") as f:
        json.dump(words, f)


async def censor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        bad_words = load_bad_words()
        text = update.message.text.lower()
        if any(word in text for word in bad_words):
            try:
                await update.message.delete()
                print(f"Удалено сообщение: {update.message.text}")
            except Exception as e:
                print(f"Ошибка при удалении: {e}")


async def add_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("Укажи слово для добавления.")
        return
    word = context.args[0].lower()
    bad_words = load_bad_words()
    if word not in bad_words:
        bad_words.append(word)
        save_bad_words(bad_words)
        await update.message.reply_text(f"Слово '{word}' добавлено.")
    else:
        await update.message.reply_text("Это слово уже есть в списке.")


async def list_words(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    words = load_bad_words()
    if words:
        await update.message.reply_text("Запрещённые слова:\n" + "\n".join(words))
    else:
        await update.message.reply_text("Список пуст.")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Я бот-цензор. Удаляю плохие слова из чата.")


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addword", add_word))
    app.add_handler(CommandHandler("badwords", list_words))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, censor))

    print("Бот запущен.")
    app.run_polling()


if __name__ == "__main__":
    main()
