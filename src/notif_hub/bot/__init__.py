__all__ = [
    'bot', 'dp',
    'commands_router', 'handle_start', 'handle_help',
    'generate_start_text', 'generate_help_text', 'internal_error_text'
]

from .bot import bot, dp
from .router import router as commands_router
from .router import handle_start, handle_help
from .texts import generate_start_text, generate_help_text, internal_error_text