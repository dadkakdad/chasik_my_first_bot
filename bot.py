import os
import logging
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# List of Russian proverbs and sayings
RUSSIAN_PROVERBS = [
    "Без труда не выловишь и рыбку из пруда.",
    "В гостях хорошо, а дома лучше.",
    "Век живи — век учись.",
    "Волков бояться — в лес не ходить.",
    "Говорить не думая — что стрелять не целясь.",
    "Дарёному коню в зубы не смотрят.",
    "Дело мастера боится.",
    "Друзья познаются в беде.",
    "За двумя зайцами погонишься — ни одного не поймаешь.",
    "Кто рано встаёт, тому Бог подаёт.",
    "Куй железо, пока горячо.",
    "Лучше синица в руках, чем журавль в небе.",
    "Не всё то золото, что блестит.",
    "Не рой другому яму — сам в неё попадёшь.",
    "Нет дыма без огня.",
    "Один в поле не воин.",
    "Повторенье — мать ученья.",
    "Правда глаза колет.",
    "Семь раз отмерь, один раз отрежь.",
    "Слово не воробей — вылетит, не поймаешь.",
    "Тише едешь — дальше будешь.",
    "Утро вечера мудренее.",
    "Цыплят по осени считают.",
    "Что посеешь, то и пожнёшь.",
    "Шила в мешке не утаишь.",
    "Яблоко от яблони недалеко падает.",
    "Язык до Киева доведёт.",
    "С кем поведёшься, от того и наберёшься.",
    "Не имей сто рублей, а имей сто друзей.",
    "Вода камень точит.",
    "Курочка по зёрнышку, весь двор в говнах."
]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        'Привет! Я бот, который отвечает русскими пословицами и поговорками. '
        'Отправь мне любое сообщение, и я отвечу случайной мудростью!'
    )


async def send_proverb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a random Russian proverb when a message is received."""
    proverb = random.choice(RUSSIAN_PROVERBS)
    await update.message.reply_text(f'💭 {proverb}')


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors caused by updates."""
    logger.error(f'Update {update} caused error {context.error}')


def main() -> None:
    """Start the bot."""
    # Get bot token from environment variable
    token = os.getenv('BOT_TOKEN')
    
    if not token:
        logger.error('BOT_TOKEN not found in environment variables!')
        raise ValueError('BOT_TOKEN must be set in environment variables or .env file')
    
    # Create the Application
    application = Application.builder().token(token).build()
    
    # Register handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, send_proverb))
    
    # Register error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    logger.info('Bot is starting...')
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()

