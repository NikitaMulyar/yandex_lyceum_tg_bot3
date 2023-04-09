import logging
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup, Bot, ReplyKeyboardRemove
from config import BOT_TOKEN


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)
bot = Bot(BOT_TOKEN)
STIH = """- Скажи-ка, дядя, ведь недаром
Москва, спаленная пожаром,
Французу отдана?
Ведь были ж схватки боевые,
Да, говорят, еще какие!
Недаром помнит вся Россия
Про день Бородина!
- Да, были люди в наше время,
Не то, что нынешнее племя:
Богатыри - не вы!
Плохая им досталась доля:
Немногие вернулись с поля...
Не будь на то господня воля,
Не отдали б Москвы!""".split('\n')


async def start(update, context):
    context.user_data['line'] = 1
    await update.message.reply_text("\"Бородино\". М.Ю.Лермонтов", reply_markup=ReplyKeyboardRemove())
    await update.message.reply_text(STIH[0])
    return 1


async def response(update, context):
    req = update.message.text
    ind = context.user_data['line']
    if STIH[ind] == req:
        context.user_data['line'] += 2
        if context.user_data['line'] < len(STIH):
            await update.message.reply_text(STIH[ind + 1], reply_markup=ReplyKeyboardRemove())
            return 1
        reply_keyboard = [['/start']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        context.user_data[update.message.chat.id] = markup
        await update.message.reply_text("Ура! Мы закончили читать стихотворение \"Бородино\"! Еще разок?",
                                        reply_markup=context.user_data[update.message.chat.id])
        return ConversationHandler.END
    reply_keyboard = [['/suphler']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    context.user_data[update.message.chat.id] = markup
    await update.message.reply_text('Активирована команда /suphler (подсказка)',
                                    reply_markup=context.user_data[update.message.chat.id])
    return 2


async def suphler(update, context):
    ind = context.user_data['line']
    logger.info(STIH, [[[[ind]]]])
    await update.message.reply_text(f"Правильный ответ:\n{STIH[ind]}")
    return 1


async def stop(update, context):
    reply_keyboard = [['/start']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    context.user_data[update.message.chat.id] = markup
    await update.message.reply_text("Михаил Юрьевич занес вас в ЧС.", reply_markup=markup)
    return ConversationHandler.END


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, response)],
            2: [CommandHandler("suphler", suphler)]
        },
        fallbacks=[CommandHandler('stop', stop)],
    )
    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == '__main__':
    main()
