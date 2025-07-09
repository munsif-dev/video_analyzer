import streamlit as st
import json
from datetime import datetime

def notes_page():
    st.title("📄 Video Notes")
    
    # Check if notes are available
    if not st.session_state.get('current_notes'):
        st.warning("No notes available. Please process a video first.")
        if st.button("🔄 Go to Upload"):
            st.switch_page("upload_page")
        return
    
    notes = st.session_state.current_notes
    video_info = st.session_state.get('current_video', {})
    
    # Video information header
    display_video_header(video_info)
    
    # Notes controls
    display_notes_controls(notes)
    
    # Main notes content
    display_notes_content(notes)
    
    # Export options
    display_export_options(notes, video_info)

def display_video_header(video_info):
    """Display video information header"""
    st.markdown("---")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.subheader(f"📹 {video_info.get('title', 'Unknown Title')}")
    
    with col2:
        st.metric("Duration", video_info.get('duration', 'Unknown'))
    
    with col3:
        st.metric("Processed", video_info.get('processed_at', 'Recently'))
    
    if video_info.get('description'):
        with st.expander("📝 Video Description"):
            st.write(video_info['description'])

def display_notes_controls(notes):
    """Display notes navigation and search controls"""
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_query = st.text_input(
            "🔍 Search in notes",
            placeholder="Search for topics, keywords, or phrases..."
        )
    
    with col2:
        view_mode = st.selectbox(
            "View Mode",
            ["Structured", "Timeline", "Summary"]
        )
    
    with col3:
        show_timestamps = st.checkbox("Show Timestamps", value=True)
    
    # Apply search filter
    if search_query:
        st.session_state.search_query = search_query.lower()
    else:
        st.session_state.search_query = None
    
    st.session_state.view_mode = view_mode
    st.session_state.show_timestamps = show_timestamps

def display_notes_content(notes):
    """Display the main notes content"""
    view_mode = st.session_state.get('view_mode', 'Structured')
    
    if view_mode == "Structured":
        display_structured_notes(notes)
    elif view_mode == "Timeline":
        display_timeline_notes(notes)
    elif view_mode == "Summary":
        display_summary_notes(notes)

def display_structured_notes(notes):
    """Display notes in structured format"""
    st.markdown("---")
    
    # Table of contents
    if notes.get('sections'):
        with st.expander("📚 Table of Contents"):
            for i, section in enumerate(notes['sections']):
                title = section.get('title', f'Section {i+1}')
                timestamp = section.get('timestamp', '')
                st.write(f"**{i+1}.** {title} {timestamp}")
    
    # Main content sections
    for i, section in enumerate(notes.get('sections', [])):
        display_section(section, i+1)

def display_section(section, section_num):
    """Display individual section"""
    title = section.get('title', f'Section {section_num}')
    timestamp = section.get('timestamp', '')
    content = section.get('content', '')
    key_points = section.get('key_points', [])
    quotes = section.get('quotes', [])
    
    # Check search filter
    if st.session_state.get('search_query'):
        search_query = st.session_state.search_query
        if not any(search_query in str(item).lower() for item in [title, content, key_points, quotes]):
            return
    
    # Section header
    header = f"## {section_num}. {title}"
    if st.session_state.get('show_timestamps') and timestamp:
        header += f" [{timestamp}]"
    
    st.markdown(header)
    
    # Section content
    if content:
        st.write(content)
    
    # Key points
    if key_points:
        st.markdown("**🎯 Key Points:**")
        for point in key_points:
            st.write(f"• {point}")
    
    # Important quotes
    if quotes:
        st.markdown("**💬 Important Quotes:**")
        for quote in quotes:
            st.info(f'"{quote}"')
    
    st.markdown("---")

def display_timeline_notes(notes):
    """Display notes in timeline format"""
    st.markdown("---")
    st.subheader("⏰ Timeline View")
    
    # Sort sections by timestamp if available
    sections = notes.get('sections', [])
    sorted_sections = sorted(sections, key=lambda x: x.get('timestamp', '00:00'))
    
    for i, section in enumerate(sorted_sections):
        timestamp = section.get('timestamp', '00:00')
        title = section.get('title', f'Section {i+1}')
        content = section.get('content', '')
        
        # Check search filter
        if st.session_state.get('search_query'):
            search_query = st.session_state.search_query
            if not any(search_query in str(item).lower() for item in [title, content]):
                continue
        
        # Timeline entry
        col1, col2 = st.columns([1, 4])
        
        with col1:
            st.markdown(f"**{timestamp}**")
        
        with col2:
            st.markdown(f"**{title}**")
            if content:
                st.write(content[:200] + "..." if len(content) > 200 else content)
        
        st.markdown("---")

def display_summary_notes(notes):
    """Display notes summary"""
    st.markdown("---")
    st.subheader("📊 Summary View")
    
    # Overall summary
    if notes.get('summary'):
        st.markdown("### 📝 Overall Summary")
        st.write(notes['summary'])
    
    # Key takeaways
    if notes.get('key_takeaways'):
        st.markdown("### 🎯 Key Takeaways")
        for takeaway in notes['key_takeaways']:
            st.write(f"• {takeaway}")
    
    # Topics covered
    if notes.get('topics'):
        st.markdown("### 📚 Topics Covered")
        for topic in notes['topics']:
            st.write(f"• {topic}")
    
    # Statistics
    st.markdown("### 📈 Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Sections", len(notes.get('sections', [])))
    
    with col2:
        total_key_points = sum(len(section.get('key_points', [])) for section in notes.get('sections', []))
        st.metric("Key Points", total_key_points)
    
    with col3:
        total_quotes = sum(len(section.get('quotes', [])) for section in notes.get('sections', []))
        st.metric("Quotes", total_quotes)

def display_export_options(notes, video_info):
    """Display export options"""
    st.markdown("---")
    st.subheader("📤 Export Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Export as Markdown"):
            markdown_content = generate_markdown_export(notes, video_info)
            st.download_button(
                label="Download Markdown",
                data=markdown_content,
                file_name=f"notes_{video_info.get('title', 'video')}.md",
                mime="text/markdown"
            )
    
    with col2:
        if st.button("📋 Export as JSON"):
            json_content = json.dumps(notes, indent=2)
            st.download_button(
                label="Download JSON",
                data=json_content,
                file_name=f"notes_{video_info.get('title', 'video')}.json",
                mime="application/json"
            )
    
    with col3:
        if st.button("📝 Export as Text"):
            text_content = generate_text_export(notes, video_info)
            st.download_button(
                label="Download Text",
                data=text_content,
                file_name=f"notes_{video_info.get('title', 'video')}.txt",
                mime="text/plain"
            )

def generate_markdown_export(notes, video_info):
    """Generate markdown export content"""
    content = []
    
    # Header
    content.append(f"# {video_info.get('title', 'Video Notes')}")
    content.append(f"**Duration**: {video_info.get('duration', 'Unknown')}")
    content.append(f"**Processed**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    content.append("")
    
    # Summary
    if notes.get('summary'):
        content.append("## Summary")
        content.append(notes['summary'])
        content.append("")
    
    # Sections
    for i, section in enumerate(notes.get('sections', [])):
        title = section.get('title', f'Section {i+1}')
        timestamp = section.get('timestamp', '')
        
        content.append(f"## {i+1}. {title}")
        if timestamp:
            content.append(f"**Timestamp**: {timestamp}")
        content.append("")
        
        if section.get('content'):
            content.append(section['content'])
            content.append("")
        
        if section.get('key_points'):
            content.append("### Key Points")
            for point in section['key_points']:
                content.append(f"- {point}")
            content.append("")
        
        if section.get('quotes'):
            content.append("### Important Quotes")
            for quote in section['quotes']:
                content.append(f"> {quote}")
            content.append("")
    
    return "\n".join(content)

def generate_text_export(notes, video_info):
    """Generate plain text export content"""
    content = []
    
    # Header
    content.append(f"VIDEO NOTES: {video_info.get('title', 'Unknown Title')}")
    content.append("=" * 50)
    content.append(f"Duration: {video_info.get('duration', 'Unknown')}")
    content.append(f"Processed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    content.append("")
    
    # Summary
    if notes.get('summary'):
        content.append("SUMMARY")
        content.append("-" * 20)
        content.append(notes['summary'])
        content.append("")
    
    # Sections
    for i, section in enumerate(notes.get('sections', [])):
        title = section.get('title', f'Section {i+1}')
        timestamp = section.get('timestamp', '')
        
        content.append(f"{i+1}. {title}")
        if timestamp:
            content.append(f"   Timestamp: {timestamp}")
        content.append("")
        
        if section.get('content'):
            content.append(section['content'])
            content.append("")
        
        if section.get('key_points'):
            content.append("   Key Points:")
            for point in section['key_points']:
                content.append(f"   - {point}")
            content.append("")
        
        if section.get('quotes'):
            content.append("   Important Quotes:")
            for quote in section['quotes']:
                content.append(f'   "{quote}"')
            content.append("")
        
        content.append("-" * 40)
    
    return "\n".join(content)