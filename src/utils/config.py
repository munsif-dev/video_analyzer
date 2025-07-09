import os
from typing import Dict, Optional
import streamlit as st
from dotenv import load_dotenv

def load_config() -> Dict:
    """Load configuration from environment variables and session state"""
    
    # Load environment variables
    load_dotenv()
    
    config = {
        'groq_api_key': get_api_key('GROQ_API_KEY', 'groq_api_key'),
        'max_video_duration': int(os.getenv('MAX_VIDEO_DURATION', '30')),
        'chunk_size': int(os.getenv('CHUNK_SIZE', '1000')),
        'max_sources': int(os.getenv('MAX_SOURCES', '3')),
        'embedding_model': os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2'),
        'chat_model': os.getenv('CHAT_MODEL', 'llama-3.3-70b-versatile'),
        'data_directory': os.getenv('DATA_DIRECTORY', './data'),
        'cache_enabled': os.getenv('CACHE_ENABLED', 'true').lower() == 'true',
        'debug_mode': os.getenv('DEBUG_MODE', 'false').lower() == 'true'
    }
    
    # Initialize session state defaults
    initialize_session_state(config)
    
    return config

def get_api_key(env_var: str, session_key: str) -> Optional[str]:
    """Get API key from environment or session state"""
    
    # First check environment variable
    api_key = os.getenv(env_var)
    if api_key:
        return api_key
    
    # Then check session state
    return st.session_state.get(session_key)

def initialize_session_state(config: Dict):
    """Initialize session state with default values"""
    
    defaults = {
        'processed_videos': [],
        'current_video': None,
        'current_transcript': None,
        'current_notes': None,
        'vector_store': None,
        'qa_history': [],
        'processing_status': None,
        'max_duration': config['max_video_duration'],
        'chunk_size': config['chunk_size'],
        'max_sources': config['max_sources'],
        'search_query': None,
        'view_mode': 'Structured',
        'show_timestamps': True,
        'groq_api_key': config['groq_api_key']
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def get_supported_platforms() -> Dict[str, str]:
    """Get supported video platforms"""
    
    return {
        'YouTube': 'youtube.com, youtu.be',
        'Vimeo': 'vimeo.com',
        'Dailymotion': 'dailymotion.com',
        'Twitch': 'twitch.tv'
    }

def get_processing_limits() -> Dict[str, int]:
    """Get processing limits"""
    
    return {
        'max_video_duration': 60,  # minutes
        'max_file_size': 500,      # MB
        'max_transcript_length': 100000,  # characters
        'max_notes_sections': 50,
        'max_qa_history': 20
    }

def validate_configuration() -> Dict[str, bool]:
    """Validate current configuration"""
    
    validation = {
        'groq_api_key': bool(st.session_state.get('groq_api_key')),
        'data_directory': os.path.exists('./data'),
        'cache_directory': os.path.exists('./data/cache') if os.path.exists('./data') else False
    }
    
    return validation

def create_data_directories():
    """Create necessary data directories"""
    
    directories = [
        './data',
        './data/transcripts',
        './data/notes',
        './data/embeddings',
        './data/cache'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def get_app_info() -> Dict:
    """Get application information"""
    
    return {
        'name': 'Video Content Analyzer',
        'version': '1.0.0',
        'description': 'Transform video content into searchable, structured knowledge',
        'author': 'Assistant',
        'supported_formats': ['YouTube', 'Vimeo', 'Dailymotion', 'Twitch'],
        'features': [
            'Video transcription',
            'Structured note generation',
            'RAG-powered Q&A',
            'Multiple export formats',
            'Real-time processing'
        ]
    }

def get_default_prompts() -> Dict[str, str]:
    """Get default prompts for various operations"""
    
    return {
        'notes_generation': """
        You are an expert content analyzer and note-taker. Your task is to transform a video transcript into well-structured, comprehensive notes. Follow these guidelines:

        1. Identify the main topics and subtopics
        2. Create a hierarchical structure with clear headings
        3. Extract key quotes and important statements
        4. Summarize complex sections concisely
        5. Highlight definitions, examples, and important concepts
        6. Include timestamps for easy reference
        7. Maintain the original meaning and intent
        8. Format the notes for readability
        9. For technical content, preserve accuracy of terms and concepts
        10. For educational content, organize in a learning-friendly sequence

        The notes should be comprehensive yet focused, eliminating filler content while preserving all valuable information.
        """,
        
        'qa_system': """
        You are an expert video content analyst. Your task is to answer questions based on the provided video content context.
        
        Guidelines:
        1. Use only the information provided in the context
        2. Be accurate and factual
        3. Include specific details and examples when available
        4. If the context doesn't contain enough information, say so
        5. Maintain a helpful and informative tone
        6. Reference timestamps when relevant
        7. Prioritize key points and direct quotes
        """,
        
        'summary_generation': """
        Please provide a concise summary (2-3 paragraphs) of the video content.
        Focus on the main points, key insights, and overall message.
        """,
        
        'key_takeaways': """
        Please extract 5-8 key takeaways from the video content.
        Each takeaway should be a concise, actionable insight.
        """,
        
        'follow_up_questions': """
        Based on the question, answer, and context, suggest 3 relevant follow-up questions
        that would help the user explore the topic further.
        """
    }

def get_error_messages() -> Dict[str, str]:
    """Get standard error messages"""
    
    return {
        'invalid_url': 'Please enter a valid video URL from a supported platform.',
        'missing_api_key': 'Please configure your Groq API key in the sidebar settings.',
        'transcription_failed': 'Video transcription failed. Please try again.',
        'notes_generation_failed': 'Note generation failed. Please try again.',
        'rag_setup_failed': 'Failed to set up the Q&A system. Please try again.',
        'question_processing_failed': 'Error processing your question. Please try again.',
        'video_too_long': 'Video is too long. Please use a video shorter than 60 minutes.',
        'invalid_format': 'Unsupported video format. Please use YouTube, Vimeo, Dailymotion, or Twitch.',
        'network_error': 'Network error. Please check your connection and try again.',
        'quota_exceeded': 'API quota exceeded. Please wait and try again later.',
        'processing_timeout': 'Processing timeout. Please try with a shorter video.',
        'file_not_found': 'Video file not found. Please check the URL.',
        'permission_denied': 'Permission denied. Please check your Groq API key permissions.',
        'rate_limit_exceeded': 'Rate limit exceeded. Please wait and try again.',
        'service_unavailable': 'Service temporarily unavailable. Please try again later.'
    }

def get_success_messages() -> Dict[str, str]:
    """Get standard success messages"""
    
    return {
        'video_processed': 'Video processed successfully!',
        'notes_generated': 'Notes generated successfully!',
        'qa_ready': 'Q&A system is ready!',
        'transcript_saved': 'Transcript saved successfully!',
        'notes_exported': 'Notes exported successfully!',
        'settings_saved': 'Settings saved successfully!',
        'cache_cleared': 'Cache cleared successfully!',
        'data_cleared': 'All data cleared successfully!'
    }

def get_ui_text() -> Dict[str, str]:
    """Get UI text and labels"""
    
    return {
        'app_title': '🎥 Video Content Analyzer',
        'upload_title': '📤 Upload Video',
        'notes_title': '📄 Video Notes',
        'qa_title': '❓ Q&A Interface',
        'settings_title': '⚙️ Settings',
        'navigation_title': '📚 Navigation',
        'recent_videos': '📋 Recent Videos',
        'processing_status': 'Processing Status',
        'api_config': 'Groq API Configuration',
        'processing_options': 'Processing Options',
        'export_options': '📤 Export Options',
        'question_history': '📋 Question History',
        'suggested_questions': '💡 Suggested Questions',
        'video_info': '📹 Video Info',
        'sources': '📚 Sources',
        'follow_up': '💡 Follow-up Questions'
    }