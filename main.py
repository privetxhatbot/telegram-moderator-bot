from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

TOKEN = "7934050267:AAGteJFHVm1108ffap66G84dXIsVQUWSfUo"
BAD_WORDS = ["мат1", "мат2", "плохое", "ругательство"]

async def censor_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        text = update.message.text.lower()
        if any(word in text for word in BAD_WORDS):
            try:
                await update.message.delete()
            except Exception as e:
                print(f"Ошибка при удалении: {e}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, censor_message))
    print("Бот запущен.")
    app.run_polling()

if __name__ == "__main__":
    main()
