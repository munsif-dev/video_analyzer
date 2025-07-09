import streamlit as st

def setup_navigation():
    """Setup sidebar navigation and return selected page"""
    with st.sidebar:
        st.title("📚 Navigation")
        
        # Navigation menu
        page = st.selectbox(
            "Choose a page:",
            ["Home", "Upload Video", "View Notes", "Q&A"],
            index=0
        )
        
        # Show processing status if available
        if st.session_state.get('processing_status'):
            st.info(f"Status: {st.session_state.processing_status}")
        
        # Show current video info if available
        if st.session_state.get('current_video'):
            st.subheader("📹 Current Video")
            video_info = st.session_state.current_video
            st.write(f"**Title**: {video_info.get('title', 'Unknown')}")
            st.write(f"**Duration**: {video_info.get('duration', 'Unknown')}")
        
        # Settings section
        st.subheader("⚙️ Settings")
        
        # API Configuration
        with st.expander("Groq API Configuration"):
            groq_api_key = st.text_input(
                "Groq API Key",
                type="password",
                help="Required for note generation and Q&A (Free at console.groq.com)"
            )
            
            if st.button("Save API Key"):
                st.session_state.groq_api_key = groq_api_key
                st.success("Groq API key saved!")
        
        # Processing Options
        with st.expander("Processing Options"):
            st.session_state.max_duration = st.slider(
                "Max Processing Duration (minutes)",
                min_value=5,
                max_value=60,
                value=30,
                help="For longer videos, only first N minutes will be processed"
            )
            
            st.session_state.chunk_size = st.slider(
                "Text Chunk Size",
                min_value=500,
                max_value=2000,
                value=1000,
                help="Size of text chunks for RAG processing"
            )
        
        # Clear data option
        if st.button("🗑️ Clear All Data", type="secondary"):
            keys_to_clear = [
                'processed_videos', 'current_video', 'current_transcript',
                'current_notes', 'vector_store', 'processing_status'
            ]
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            st.success("All data cleared!")
            st.rerun()
    
    return page