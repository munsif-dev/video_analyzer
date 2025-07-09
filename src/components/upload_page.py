import streamlit as st
import re
from urllib.parse import urlparse
from services.video_processor import VideoProcessor
from services.transcription_service import TranscriptionService
from services.notes_generator import NotesGenerator
from services.rag_system import RAGSystem

def upload_page():
    st.title("📤 Upload Video")
    st.markdown("Submit a video link to start processing and generating structured notes.")
    
    # Video URL input
    video_url = st.text_input(
        "Video URL",
        placeholder="https://www.youtube.com/watch?v=...",
        help="Supported platforms: YouTube, Vimeo, and other major video sites"
    )
    
    # Processing options
    col1, col2 = st.columns(2)
    
    with col1:
        generate_summary = st.checkbox("Generate Summary", value=True)
        include_timestamps = st.checkbox("Include Timestamps", value=True)
    
    with col2:
        extract_key_points = st.checkbox("Extract Key Points", value=True)
        create_qa_pairs = st.checkbox("Create Q&A Pairs", value=False)
    
    # Process button
    if st.button("🚀 Process Video", type="primary", disabled=not video_url):
        if not validate_url(video_url):
            st.error("Please enter a valid video URL")
            return
        
        if not check_api_keys():
            st.error("Please configure your Groq API key in the sidebar settings")
            return
        
        process_video(video_url, {
            'generate_summary': generate_summary,
            'include_timestamps': include_timestamps,
            'extract_key_points': extract_key_points,
            'create_qa_pairs': create_qa_pairs
        })
    
    # Show recent uploads
    show_recent_uploads()

def validate_url(url):
    """Validate video URL format"""
    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            return False
        
        # Check for supported platforms
        supported_domains = [
            'youtube.com', 'youtu.be', 'vimeo.com',
            'dailymotion.com', 'twitch.tv'
        ]
        
        domain = result.netloc.lower()
        return any(supported in domain for supported in supported_domains)
    except:
        return False

def check_api_keys():
    """Check if required API keys are configured"""
    return st.session_state.get('groq_api_key')

def process_video(video_url, options):
    """Process video through the complete pipeline"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Initialize services
        video_processor = VideoProcessor()
        transcription_service = TranscriptionService()
        notes_generator = NotesGenerator(
            api_key=st.session_state.groq_api_key
        )
        rag_system = RAGSystem(
            api_key=st.session_state.groq_api_key
        )
        
        # Step 1: Process video metadata
        status_text.text("📹 Processing video metadata...")
        progress_bar.progress(20)
        
        video_info = video_processor.extract_video_info(video_url)
        st.session_state.current_video = video_info
        
        # Step 2: Transcribe video
        status_text.text("🎤 Transcribing video...")
        progress_bar.progress(40)
        
        transcript = transcription_service.transcribe_video(
            video_url,
            max_duration=st.session_state.get('max_duration', 30)
        )
        st.session_state.current_transcript = transcript
        
        # Step 3: Generate structured notes
        status_text.text("📝 Generating structured notes...")
        progress_bar.progress(60)
        
        notes = notes_generator.generate_notes(
            transcript,
            video_info,
            options
        )
        st.session_state.current_notes = notes
        
        # Step 4: Setup RAG system
        status_text.text("🔍 Setting up search system...")
        progress_bar.progress(80)
        
        vector_store = rag_system.setup_vector_store(
            transcript,
            notes,
            chunk_size=st.session_state.get('chunk_size', 1000)
        )
        st.session_state.vector_store = vector_store
        
        # Step 5: Complete
        progress_bar.progress(100)
        status_text.text("✅ Processing complete!")
        
        # Update processed videos list
        if 'processed_videos' not in st.session_state:
            st.session_state.processed_videos = []
        
        st.session_state.processed_videos.append({
            'url': video_url,
            'title': video_info.get('title', 'Unknown'),
            'processed_at': str(st.session_state.get('current_time', 'Now'))
        })
        
        st.success(f"Video processed successfully! Generated {len(notes.get('sections', []))} sections.")
        
        # Show quick preview
        with st.expander("📋 Quick Preview"):
            st.write(f"**Title**: {video_info.get('title', 'Unknown')}")
            st.write(f"**Duration**: {video_info.get('duration', 'Unknown')}")
            st.write(f"**Transcript Length**: {len(transcript)} characters")
            st.write(f"**Notes Sections**: {len(notes.get('sections', []))}")
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📄 View Notes"):
                st.switch_page("notes_page")
        with col2:
            if st.button("❓ Ask Questions"):
                st.switch_page("qa_page")
        
    except Exception as e:
        status_text.text(f"❌ Error: {str(e)}")
        st.error(f"Processing failed: {str(e)}")
        progress_bar.empty()

def show_recent_uploads():
    """Display recent video uploads"""
    if st.session_state.get('processed_videos'):
        st.subheader("📋 Recent Uploads")
        
        for i, video in enumerate(reversed(st.session_state.processed_videos[-5:])):
            with st.expander(f"📹 {video['title']}"):
                st.write(f"**URL**: {video['url']}")
                st.write(f"**Processed**: {video['processed_at']}")
                
                if st.button(f"Load Video {i+1}", key=f"load_{i}"):
                    # Load this video as current
                    st.session_state.current_video = video
                    st.success(f"Loaded: {video['title']}")
                    st.rerun()