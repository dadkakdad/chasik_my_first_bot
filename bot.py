import os
import logging
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Import our custom modules
from utils import (
    SessionManager, 
    chat_completion, 
    transcribe_voice,
    generate_brief_document
)
from prompts import (
    SYSTEM_PROMPT,
    WELCOME_MESSAGE,
    HELP_MESSAGE,
    NEW_TASK_PROMPT,
    CANCEL_MESSAGE,
    GENERATE_NOT_READY,
    NO_ACTIVE_SESSION
)

# Load environment variables from .env file
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global session manager
session_manager = SessionManager()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send welcome message when /start is issued"""
    await update.message.reply_text(WELCOME_MESSAGE)
    logger.info(f"User {update.effective_user.id} started the bot")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send help message when /help is issued"""
    await update.message.reply_text(HELP_MESSAGE)


async def new_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Initialize new feature discussion session"""
    user_id = update.effective_user.id
    
    # Create new session
    session = session_manager.create_session(user_id)
    session['metadata']['created_at'] = datetime.now().isoformat()
    await session_manager.save_sessions()
    
    await update.message.reply_text(NEW_TASK_PROMPT)
    logger.info(f"User {user_id} started new task session")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Cancel current session"""
    user_id = update.effective_user.id
    
    await session_manager.delete_session(user_id)
    await update.message.reply_text(CANCEL_MESSAGE)
    logger.info(f"User {user_id} cancelled session")


async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generate product brief document from conversation"""
    user_id = update.effective_user.id
    
    session = session_manager.get_session(user_id)
    
    if not session:
        await update.message.reply_text(NO_ACTIVE_SESSION)
        return
    
    # Check if conversation has enough content
    message_count = session['metadata']['message_count']
    if message_count < 6:  # At least 3 exchanges
        await update.message.reply_text(GENERATE_NOT_READY)
        return
    
    # Generate document
    await update.message.reply_text("⏳ Генерирую документ... Это займёт несколько секунд.")
    
    try:
        # Get conversation history (exclude system prompts)
        conversation = session_manager.get_messages(user_id)
        
        # Generate brief
        document = await generate_brief_document(conversation)
        
        # Save to file
        filename = f"product_brief_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        filepath = f"/tmp/{filename}"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(document)
        
        # Send document
        with open(filepath, 'rb') as f:
            await update.message.reply_document(
                document=f,
                filename=filename,
                caption="✅ Готово! Вот твой структурированный бриф.\n\nХочешь обсудить ещё одну идею? Отправь /newtask"
            )
        
        # Clean up
        os.remove(filepath)
        
        # Mark session as completed but keep it
        session_manager.set_state(user_id, 'completed')
        await session_manager.save_sessions()
        
        logger.info(f"Generated brief for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error generating brief: {e}")
        await update.message.reply_text(
            "❌ Произошла ошибка при генерации документа. Попробуй ещё раз или начни новую сессию с /newtask"
        )


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle voice messages - transcribe and process as text"""
    user_id = update.effective_user.id
    
    session = session_manager.get_session(user_id)
    
    if not session:
        await update.message.reply_text(
            "⚠️ Сначала начни новую сессию с /newtask"
        )
        return
    
    try:
        # Show typing indicator
        await update.message.chat.send_action(action="typing")
        
        # Download voice file
        voice_file = await update.message.voice.get_file()
        voice_path = f"/tmp/voice_{user_id}_{datetime.now().timestamp()}.ogg"
        await voice_file.download_to_drive(voice_path)
        
        logger.info(f"Downloaded voice message from user {user_id}")
        
        # Transcribe using Whisper
        await update.message.reply_text("🎤 Распознаю голос...")
        transcribed_text = await transcribe_voice(voice_path)
        
        # Clean up voice file
        os.remove(voice_path)
        
        logger.info(f"Transcribed voice for user {user_id}: {transcribed_text[:100]}")
        
        # Show what was recognized
        await update.message.reply_text(f"📝 Распознал: \"{transcribed_text}\"")
        
        # Process as text message
        await process_conversation(update, user_id, transcribed_text)
        
    except Exception as e:
        logger.error(f"Error handling voice: {e}")
        await update.message.reply_text(
            "❌ Не удалось распознать голосовое сообщение. Попробуй написать текстом или отправь голос ещё раз."
        )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages"""
    user_id = update.effective_user.id
    text = update.message.text
    
    session = session_manager.get_session(user_id)
    
    if not session:
        await update.message.reply_text(
            "👋 Привет! Чтобы начать обсуждение фичи, отправь /newtask\n\n"
            "Или используй /help чтобы узнать больше о моих возможностях."
        )
        return
    
    await process_conversation(update, user_id, text)


async def process_conversation(update: Update, user_id: int, user_message: str) -> None:
    """Process conversation with AI mentor"""
    try:
        # Show typing indicator
        await update.message.chat.send_action(action="typing")
        
        # Add user message to session
        session_manager.add_message(user_id, 'user', user_message)
        
        # Get full conversation history
        messages = session_manager.get_messages(user_id)
        
        # Prepare messages for OpenAI (add system prompt if first message)
        if len(messages) == 1:
            # First user message - add system prompt
            openai_messages = [
                {'role': 'system', 'content': SYSTEM_PROMPT},
                {'role': 'user', 'content': user_message}
            ]
        else:
            # Continuing conversation
            openai_messages = [{'role': 'system', 'content': SYSTEM_PROMPT}] + messages
        
        # Get AI response
        ai_response = await chat_completion(
            messages=openai_messages,
            max_tokens=800,
            temperature=0.7
        )
        
        # Add AI response to session
        session_manager.add_message(user_id, 'assistant', ai_response)
        
        # Save session
        await session_manager.save_sessions()
        
        # Check if AI suggests generating the brief
        if '/generate' in ai_response.lower():
            session_manager.set_state(user_id, 'ready_for_brief')
            await session_manager.save_sessions()
        
        # Send response
        await update.message.reply_text(ai_response)
        
        logger.info(f"Processed conversation for user {user_id}, total messages: {len(messages) + 1}")
        
    except Exception as e:
        logger.error(f"Error in conversation processing: {e}")
        await update.message.reply_text(
            "❌ Произошла ошибка при обработке сообщения. Попробуй ещё раз.\n\n"
            "Если проблема повторяется, начни новую сессию с /cancel и затем /newtask"
        )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors caused by updates"""
    logger.error(f'Update {update} caused error {context.error}', exc_info=context.error)


async def post_init(application: Application) -> None:
    """Load sessions after bot initialization"""
    await session_manager.load_sessions()
    logger.info("Session manager initialized")


def main() -> None:
    """Start the bot"""
    # Get bot token from environment variable
    token = os.getenv('BOT_TOKEN')
    
    if not token:
        logger.error('BOT_TOKEN not found in environment variables!')
        raise ValueError('BOT_TOKEN must be set in environment variables or .env file')
    
    # Verify OpenAI API key
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key:
        logger.error('OPENAI_API_KEY not found in environment variables!')
        raise ValueError('OPENAI_API_KEY must be set in environment variables or .env file')
    
    # Create the Application
    application = Application.builder().token(token).post_init(post_init).build()
    
    # Register command handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('newtask', new_task))
    application.add_handler(CommandHandler('cancel', cancel))
    application.add_handler(CommandHandler('generate', generate))
    
    # Register message handlers
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # Register error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    logger.info('Product Manager Bot is starting...')
    logger.info('Commands: /start, /newtask, /generate, /cancel, /help')
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
