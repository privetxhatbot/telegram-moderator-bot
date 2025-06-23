
import os
import json
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from telegram import Update
from telegram.ext.callbackcontext import CallbackContext

WORDS_FILE = "bad_words.json"
ADMIN_IDS = [123456789]  # Замените на свой user ID

def load_words():
    if not os.path.exists(WORDS_FILE):
        with open(WORDS_FILE, "w") as f:
            json.dump([], f)
    with open(WORDS_FILE, "r") as f:
        return json.load(f)

def save_words(words):
    with open(WORDS_FILE, "w") as f:
        json.dump(words, f)

def censor(update: Update, context: CallbackContext):
    text = update.message.text.lower()
    words = load_words()
    if any(bad in text for bad in words) or "http" in text or "t.me" in text:
        try:
            update.message.delete()
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"🚫 Сообщение от @{update.message.from_user.username} удалено (запрещённое содержимое)."
            )
        except:
            pass

def new_member_check(update: Update, context: CallbackContext):
    for new_user in update.message.new_chat_members:
        added_by = update.message.from_user.id
        if new_user.id != added_by:
            try:
                context.bot.kick_chat_member(update.effective_chat.id, new_user.id)
                context.bot.unban_chat_member(update.effective_chat.id, new_user.id)
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"🚫 @{new_user.username or new_user.first_name} был удалён — нельзя добавлять участников вручную."
                )
            except:
                pass

def add_word(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return
    if context.args:
        word = context.args[0].lower()
        words = load_words()
        if word not in words:
            words.append(word)
            save_words(words)
            update.message.reply_text(f"✅ Слово '{word}' добавлено в фильтр.")
        else:
            update.message.reply_text("Слово уже в списке.")

def remove_word(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return
    if context.args:
        word = context.args[0].lower()
        words = load_words()
        if word in words:
            words.remove(word)
            save_words(words)
            update.message.reply_text(f"❌ Слово '{word}' удалено из фильтра.")
        else:
            update.message.reply_text("Слова нет в списке.")

def list_words(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return
    words = load_words()
    if words:
        update.message.reply_text("📝 Запрещённые слова:
- " + "\n- ".join(words))
    else:
        update.message.reply_text("Список запрещённых слов пуст.")

def main():
    token = os.getenv("BOT_TOKEN")
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, censor))
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, new_member_check))

    dp.add_handler(CommandHandler("добавитьслово", add_word))
    dp.add_handler(CommandHandler("удалитьслово", remove_word))
    dp.add_handler(CommandHandler("списоксслов", list_words))

    updater.start_polling()
    updater.idle()

main()
