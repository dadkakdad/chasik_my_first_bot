import os
import logging
from datetime import datetime
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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        'Привет! Я бот, который показывает текущее время сервера. '
        'Отправь мне любое сообщение, и я отвечу текущим временем!'
    )


async def send_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send current server time when a message is received."""
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    await update.message.reply_text(f'🕐 Текущее время на сервере: {current_time}')


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
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, send_time))
    
    # Register error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    logger.info('Bot is starting...')
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()

