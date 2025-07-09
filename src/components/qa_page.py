import streamlit as st
from datetime import datetime
from services.rag_system import RAGSystem

def qa_page():
    st.title("❓ Q&A Interface")
    
    # Check if RAG system is available
    if not st.session_state.get('vector_store'):
        st.warning("No processed video available. Please process a video first.")
        if st.button("🔄 Go to Upload"):
            st.switch_page("upload_page")
        return
    
    # Initialize RAG system
    rag_system = RAGSystem(api_key=st.session_state.get('groq_api_key'))
    
    # Current video info
    display_current_video_info()
    
    # Question input
    question = st.text_input(
        "💭 Ask a question about the video:",
        placeholder="What are the main topics discussed in this video?",
        help="Ask specific questions about the content, concepts, or details from the video"
    )
    
    # Question options
    col1, col2 = st.columns(2)
    
    with col1:
        include_timestamps = st.checkbox("Include Timestamps", value=True)
        include_confidence = st.checkbox("Show Confidence Score", value=False)
    
    with col2:
        max_sources = st.slider("Max Sources", min_value=1, max_value=10, value=3)
        detailed_answer = st.checkbox("Detailed Answer", value=False)
    
    # Ask button
    if st.button("🔍 Ask Question", type="primary", disabled=not question):
        answer_question(question, rag_system, {
            'include_timestamps': include_timestamps,
            'include_confidence': include_confidence,
            'max_sources': max_sources,
            'detailed_answer': detailed_answer
        })
    
    # Display question history
    display_question_history()
    
    # Suggested questions
    display_suggested_questions()

def display_current_video_info():
    """Display current video information"""
    video_info = st.session_state.get('current_video', {})
    
    with st.expander("📹 Current Video Info"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Title**: {video_info.get('title', 'Unknown')}")
            st.write(f"**Duration**: {video_info.get('duration', 'Unknown')}")
        
        with col2:
            notes = st.session_state.get('current_notes', {})
            st.write(f"**Sections**: {len(notes.get('sections', []))}")
            st.write(f"**Processed**: {video_info.get('processed_at', 'Recently')}")

def answer_question(question, rag_system, options):
    """Process question and display answer"""
    with st.spinner("🤔 Thinking..."):
        try:
            # Get answer from RAG system
            result = rag_system.answer_question(
                question=question,
                vector_store=st.session_state.vector_store,
                options=options
            )
            
            # Display answer
            display_answer(question, result, options)
            
            # Save to history
            save_question_to_history(question, result)
            
        except Exception as e:
            st.error(f"Error processing question: {str(e)}")

def display_answer(question, result, options):
    """Display the answer with sources and metadata"""
    st.markdown("---")
    st.subheader("📝 Answer")
    
    # Main answer
    st.write(result.get('answer', 'No answer generated'))
    
    # Confidence score
    if options.get('include_confidence') and result.get('confidence'):
        confidence = result['confidence']
        confidence_color = "green" if confidence > 0.8 else "orange" if confidence > 0.6 else "red"
        st.markdown(f"**Confidence**: :{confidence_color}[{confidence:.2%}]")
    
    # Sources
    sources = result.get('sources', [])
    if sources:
        st.markdown("---")
        st.subheader("📚 Sources")
        
        for i, source in enumerate(sources[:options.get('max_sources', 3)]):
            with st.expander(f"Source {i+1}: {source.get('section_title', 'Unknown Section')}"):
                # Source content
                st.write(source.get('content', 'No content available'))
                
                # Metadata
                col1, col2 = st.columns(2)
                
                with col1:
                    if options.get('include_timestamps') and source.get('timestamp'):
                        st.info(f"🕐 Timestamp: {source['timestamp']}")
                
                with col2:
                    if source.get('relevance_score'):
                        st.info(f"📊 Relevance: {source['relevance_score']:.2%}")
    
    # Follow-up suggestions
    if result.get('follow_up_questions'):
        st.markdown("---")
        st.subheader("💡 Follow-up Questions")
        
        for follow_up in result['follow_up_questions']:
            if st.button(f"❓ {follow_up}", key=f"followup_{hash(follow_up)}"):
                st.session_state.follow_up_question = follow_up
                st.rerun()

def save_question_to_history(question, result):
    """Save question and answer to history"""
    if 'qa_history' not in st.session_state:
        st.session_state.qa_history = []
    
    st.session_state.qa_history.append({
        'question': question,
        'answer': result.get('answer', ''),
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'sources_count': len(result.get('sources', []))
    })
    
    # Keep only last 20 questions
    if len(st.session_state.qa_history) > 20:
        st.session_state.qa_history = st.session_state.qa_history[-20:]

def display_question_history():
    """Display previous questions and answers"""
    if not st.session_state.get('qa_history'):
        return
    
    st.markdown("---")
    st.subheader("📋 Question History")
    
    # History controls
    col1, col2 = st.columns([3, 1])
    
    with col1:
        show_count = st.slider("Show last N questions", 1, 10, 5)
    
    with col2:
        if st.button("🗑️ Clear History"):
            st.session_state.qa_history = []
            st.rerun()
    
    # Display history
    history = st.session_state.qa_history[-show_count:]
    
    for i, item in enumerate(reversed(history)):
        with st.expander(f"Q{len(history)-i}: {item['question'][:100]}..."):
            st.write(f"**Question**: {item['question']}")
            st.write(f"**Answer**: {item['answer']}")
            st.write(f"**Asked**: {item['timestamp']}")
            st.write(f"**Sources**: {item['sources_count']}")
            
            # Re-ask button
            if st.button(f"🔄 Re-ask", key=f"reask_{i}"):
                st.session_state.reask_question = item['question']
                st.rerun()

def display_suggested_questions():
    """Display suggested questions based on video content"""
    st.markdown("---")
    st.subheader("💡 Suggested Questions")
    
    # Get suggested questions based on video content
    suggestions = generate_suggested_questions()
    
    # Display suggestions in columns
    col1, col2 = st.columns(2)
    
    for i, suggestion in enumerate(suggestions):
        column = col1 if i % 2 == 0 else col2
        
        with column:
            if st.button(f"❓ {suggestion}", key=f"suggestion_{i}"):
                st.session_state.suggested_question = suggestion
                st.rerun()

def generate_suggested_questions():
    """Generate suggested questions based on video content"""
    notes = st.session_state.get('current_notes', {})
    
    # Default suggestions
    default_suggestions = [
        "What are the main topics discussed?",
        "Can you summarize the key points?",
        "What are the most important takeaways?",
        "Are there any specific examples mentioned?",
        "What conclusions were drawn?",
        "What questions are answered in this video?"
    ]
    
    # Generate content-specific suggestions
    content_suggestions = []
    
    # Based on sections
    sections = notes.get('sections', [])
    if sections:
        for section in sections[:3]:  # First 3 sections
            title = section.get('title', '')
            if title:
                content_suggestions.append(f"Tell me more about {title}")
    
    # Based on key topics
    topics = notes.get('topics', [])
    if topics:
        for topic in topics[:2]:  # First 2 topics
            content_suggestions.append(f"Explain {topic} in detail")
    
    # Combine and return
    all_suggestions = content_suggestions + default_suggestions
    return all_suggestions[:8]  # Return first 8 suggestions

# Handle follow-up and re-ask questions
if st.session_state.get('follow_up_question'):
    st.text_input(
        "💭 Follow-up Question:",
        value=st.session_state.follow_up_question,
        key="followup_input"
    )
    del st.session_state.follow_up_question

if st.session_state.get('suggested_question'):
    st.text_input(
        "💭 Suggested Question:",
        value=st.session_state.suggested_question,
        key="suggested_input"
    )
    del st.session_state.suggested_question

if st.session_state.get('reask_question'):
    st.text_input(
        "💭 Re-ask Question:",
        value=st.session_state.reask_question,
        key="reask_input"
    )
    del st.session_state.reask_question