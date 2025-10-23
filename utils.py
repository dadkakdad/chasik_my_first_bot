"""
Utility functions for OpenAI integration and session management
"""
import os
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any
from openai import OpenAI
import aiofiles

logger = logging.getLogger(__name__)

# OpenAI client instance
_openai_client = None


def get_openai_client() -> OpenAI:
    """Get or create OpenAI client with proxy configuration"""
    global _openai_client
    
    if _openai_client is None:
        api_key = os.getenv('OPENAI_API_KEY')
        proxiline_url = os.getenv('PROXILINE_URL')
        
        if not api_key:
            raise ValueError('OPENAI_API_KEY must be set in environment variables')
        
        # Configure proxy if provided
        if proxiline_url:
            assert api_key.isascii()
            assert proxiline_url.isascii()
            
            os.environ["HTTP_PROXY"] = proxiline_url
            os.environ["HTTPS_PROXY"] = proxiline_url
            logger.info("OpenAI client configured with proxy")
        
        # Create client with custom headers (following user's pattern)
        _openai_client = OpenAI(
            api_key=api_key,
            default_headers={
                "User-Agent": "openai-python/1",
                "X-Stainless-Client-User-Agent": "{}",  # disable telemetry
                "X-Stainless-Lang": "python",
                "X-Stainless-Python-Version": "3.11",
                "X-Stainless-OS": "macOS",
            },
        )
        logger.info("OpenAI client initialized successfully")
    
    return _openai_client


async def transcribe_voice(audio_file_path: str) -> str:
    """
    Transcribe audio file using OpenAI Whisper API
    
    Args:
        audio_file_path: Path to audio file
        
    Returns:
        Transcribed text
    """
    try:
        client = get_openai_client()
        
        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        
        def _transcribe():
            with open(audio_file_path, 'rb') as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="ru"  # Russian language
                )
            return transcript.text
        
        text = await loop.run_in_executor(None, _transcribe)
        logger.info(f"Transcribed audio: {len(text)} characters")
        return text
        
    except Exception as e:
        logger.error(f"Error transcribing audio: {e}")
        raise


async def chat_completion(
    messages: List[Dict[str, str]], 
    model: Optional[str] = None,
    max_tokens: int = 1000,
    temperature: float = 0.7
) -> str:
    """
    Get chat completion from OpenAI
    
    Args:
        messages: List of message dicts with 'role' and 'content'
        model: Model to use (defaults to env OPENAI_MODEL or gpt-4-turbo)
        max_tokens: Maximum tokens in response
        temperature: Sampling temperature
        
    Returns:
        Assistant's response text
    """
    try:
        client = get_openai_client()
        
        if model is None:
            model = os.getenv('OPENAI_MODEL', 'gpt-4-turbo')
        
        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        
        def _complete():
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
        
        response_text = await loop.run_in_executor(None, _complete)
        logger.info(f"Got chat completion: {len(response_text)} characters")
        return response_text
        
    except Exception as e:
        logger.error(f"Error in chat completion: {e}")
        raise


class SessionManager:
    """Manages user conversation sessions with JSON storage"""
    
    def __init__(self, storage_file: str = 'sessions.json'):
        self.storage_file = storage_file
        self.sessions: Dict[int, Dict[str, Any]] = {}
        
    async def load_sessions(self):
        """Load sessions from JSON file"""
        try:
            if os.path.exists(self.storage_file):
                async with aiofiles.open(self.storage_file, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    data = json.loads(content)
                    # Convert string keys back to int
                    self.sessions = {int(k): v for k, v in data.items()}
                    logger.info(f"Loaded {len(self.sessions)} sessions")
            else:
                self.sessions = {}
                logger.info("No existing sessions file, starting fresh")
        except Exception as e:
            logger.error(f"Error loading sessions: {e}")
            self.sessions = {}
    
    async def save_sessions(self):
        """Save sessions to JSON file"""
        try:
            # Convert int keys to string for JSON
            data = {str(k): v for k, v in self.sessions.items()}
            async with aiofiles.open(self.storage_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(data, ensure_ascii=False, indent=2))
            logger.info(f"Saved {len(self.sessions)} sessions")
        except Exception as e:
            logger.error(f"Error saving sessions: {e}")
    
    def get_session(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get session for user"""
        return self.sessions.get(user_id)
    
    def create_session(self, user_id: int) -> Dict[str, Any]:
        """Create new session for user"""
        session = {
            'user_id': user_id,
            'messages': [],  # Conversation history
            'state': 'in_conversation',  # idle, in_conversation, ready_for_brief
            'metadata': {
                'created_at': None,
                'message_count': 0
            }
        }
        self.sessions[user_id] = session
        logger.info(f"Created new session for user {user_id}")
        return session
    
    async def update_session(self, user_id: int, session_data: Dict[str, Any]):
        """Update session and save to storage"""
        self.sessions[user_id] = session_data
        await self.save_sessions()
    
    async def delete_session(self, user_id: int):
        """Delete session for user"""
        if user_id in self.sessions:
            del self.sessions[user_id]
            await self.save_sessions()
            logger.info(f"Deleted session for user {user_id}")
    
    def add_message(self, user_id: int, role: str, content: str):
        """Add message to session conversation history"""
        if user_id in self.sessions:
            self.sessions[user_id]['messages'].append({
                'role': role,
                'content': content
            })
            self.sessions[user_id]['metadata']['message_count'] += 1
    
    def get_messages(self, user_id: int) -> List[Dict[str, str]]:
        """Get conversation messages for user"""
        session = self.sessions.get(user_id)
        if session:
            return session['messages']
        return []
    
    def set_state(self, user_id: int, state: str):
        """Set session state"""
        if user_id in self.sessions:
            self.sessions[user_id]['state'] = state
    
    def get_state(self, user_id: int) -> Optional[str]:
        """Get session state"""
        session = self.sessions.get(user_id)
        if session:
            return session['state']
        return None


async def generate_brief_document(conversation_history: List[Dict[str, str]]) -> str:
    """
    Generate product brief document from conversation history
    
    Args:
        conversation_history: List of message dicts
        
    Returns:
        Markdown formatted document
    """
    from prompts import BRIEF_GENERATION_PROMPT
    
    # Format conversation history
    formatted_history = "\n".join([
        f"{msg['role'].upper()}: {msg['content']}"
        for msg in conversation_history
    ])
    
    # Create prompt with conversation history
    prompt = BRIEF_GENERATION_PROMPT.format(
        conversation_history=formatted_history
    )
    
    # Generate document
    messages = [
        {'role': 'system', 'content': 'Ты — эксперт по созданию продуктовых требований.'},
        {'role': 'user', 'content': prompt}
    ]
    
    document = await chat_completion(
        messages=messages,
        max_tokens=2000,
        temperature=0.7
    )
    
    return document

