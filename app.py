import streamlit as st
import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from components.navigation import setup_navigation
from components.upload_page import upload_page
from components.notes_page import notes_page
from components.qa_page import qa_page
from utils.config import load_config

def main():
    st.set_page_config(
        page_title="Video Content Analyzer",
        page_icon="🎥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Load configuration
    config = load_config()
    
    # Setup navigation
    page = setup_navigation()
    
    # Route to appropriate page
    if page == "Home":
        home_page()
    elif page == "Upload Video":
        upload_page()
    elif page == "View Notes":
        notes_page()
    elif page == "Q&A":
        qa_page()

def home_page():
    st.title("🎥 Video Content Analyzer")
    st.markdown("""
    Transform video content into searchable, structured knowledge through:
    
    ### 🔄 Workflow
    1. **Upload**: Submit video links (YouTube, Vimeo, etc.)
    2. **Transcribe**: Automatic speech-to-text conversion
    3. **Generate Notes**: AI-powered structured summaries
    4. **Query**: Ask questions about the video content
    
    ### ✨ Features
    - **Smart Transcription**: High-accuracy speech recognition
    - **Structured Notes**: Well-organized summaries with timestamps
    - **RAG-powered Q&A**: Ask questions and get answers with citations
    - **Multiple Formats**: Support for various video platforms
    - **Time-stamped References**: Easy navigation back to source content
    
    ### 🚀 Getting Started
    1. Navigate to **Upload Video** to process your first video
    2. View generated notes in **View Notes**
    3. Ask questions in the **Q&A** section
    
    ---
    
    **Note**: For videos longer than 30 minutes, the system focuses on the first half-hour for optimal performance.
    """)
    
    # Show recent activities if available
    if st.session_state.get('processed_videos'):
        st.subheader("📋 Recent Videos")
        for video in st.session_state.processed_videos[-5:]:
            st.write(f"• {video.get('title', 'Unknown Title')}")

if __name__ == "__main__":
    main()