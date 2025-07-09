from groq import Groq
from typing import Dict, List, Optional
import json
import re
from datetime import datetime

class NotesGenerator:
    """Generate structured notes from video transcripts using LLM"""
    
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"
    
    def generate_notes(self, transcript: Dict, video_info: Dict, options: Dict) -> Dict:
        """Generate structured notes from transcript"""
        
        # Prepare the transcript text
        transcript_text = self._prepare_transcript_text(transcript)
        
        # Generate main notes
        structured_notes = self._generate_structured_notes(
            transcript_text, 
            video_info, 
            options
        )
        
        # Add metadata
        structured_notes['metadata'] = {
            'video_title': video_info.get('title', 'Unknown'),
            'video_duration': video_info.get('duration', 'Unknown'),
            'video_platform': video_info.get('platform', 'Unknown'),
            'processed_at': datetime.now().isoformat(),
            'transcript_source': transcript.get('source', 'Unknown'),
            'word_count': transcript.get('word_count', 0),
            'options_used': options
        }
        
        # Generate additional content based on options
        if options.get('generate_summary'):
            structured_notes['summary'] = self._generate_summary(transcript_text)
        
        if options.get('extract_key_points'):
            structured_notes['key_takeaways'] = self._extract_key_takeaways(transcript_text)
        
        if options.get('create_qa_pairs'):
            structured_notes['qa_pairs'] = self._generate_qa_pairs(transcript_text)
        
        return structured_notes
    
    def _prepare_transcript_text(self, transcript: Dict) -> str:
        """Prepare transcript text for processing"""
        
        # Use segments if available for better structure
        if 'segments' in transcript and transcript['segments']:
            formatted_segments = []
            for segment in transcript['segments']:
                timestamp = segment.get('start', '00:00')
                text = segment.get('text', '')
                speaker = segment.get('speaker', '')
                
                if speaker:
                    formatted_segments.append(f"[{timestamp}] {speaker}: {text}")
                else:
                    formatted_segments.append(f"[{timestamp}] {text}")
            
            return '\n\n'.join(formatted_segments)
        
        # Fallback to full text
        return transcript.get('full_text', '')
    
    def _generate_structured_notes(self, transcript_text: str, video_info: Dict, options: Dict) -> Dict:
        """Generate the main structured notes"""
        
        system_prompt = """
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
        """
        
        user_prompt = f"""
        Please analyze the following video transcript and create structured notes:

        Video Title: {video_info.get('title', 'Unknown')}
        Duration: {video_info.get('duration', 'Unknown')}
        Platform: {video_info.get('platform', 'Unknown')}

        Transcript:
        {transcript_text}

        Please provide the output in JSON format with the following structure:
        {{
            "sections": [
                {{
                    "title": "Section Title",
                    "timestamp": "00:00",
                    "content": "Main content summary",
                    "key_points": ["Point 1", "Point 2"],
                    "quotes": ["Important quote 1", "Important quote 2"],
                    "concepts": ["Concept 1", "Concept 2"],
                    "examples": ["Example 1", "Example 2"]
                }}
            ],
            "topics": ["Topic 1", "Topic 2", "Topic 3"],
            "main_theme": "Overall theme of the video",
            "learning_objectives": ["Objective 1", "Objective 2"]
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            # Parse the JSON response
            content = response.choices[0].message.content
            
            # Extract JSON from response (handle markdown code blocks)
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON without code blocks
                json_str = content
            
            try:
                structured_notes = json.loads(json_str)
                return structured_notes
            except json.JSONDecodeError:
                # Fallback to manual parsing
                return self._parse_notes_fallback(content)
                
        except Exception as e:
            print(f"Error generating structured notes: {e}")
            return self._create_fallback_notes(transcript_text, video_info)
    
    def _generate_summary(self, transcript_text: str) -> str:
        """Generate a concise summary"""
        
        prompt = f"""
        Please provide a concise summary (2-3 paragraphs) of the following video transcript:

        {transcript_text}

        Focus on the main points, key insights, and overall message.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating summary: {e}")
            return "Summary generation failed. Please review the full transcript."
    
    def _extract_key_takeaways(self, transcript_text: str) -> List[str]:
        """Extract key takeaways from the transcript"""
        
        prompt = f"""
        Please extract 5-8 key takeaways from the following video transcript:

        {transcript_text}

        Format as a JSON array of strings. Each takeaway should be a concise, actionable insight.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=800
            )
            
            content = response.choices[0].message.content.strip()
            
            # Try to parse as JSON
            try:
                takeaways = json.loads(content)
                return takeaways if isinstance(takeaways, list) else []
            except json.JSONDecodeError:
                # Extract from text format
                return self._extract_list_from_text(content)
                
        except Exception as e:
            print(f"Error extracting key takeaways: {e}")
            return ["Key takeaways extraction failed"]
    
    def _generate_qa_pairs(self, transcript_text: str) -> List[Dict]:
        """Generate Q&A pairs from the transcript"""
        
        prompt = f"""
        Please generate 5-8 question-answer pairs based on the following video transcript:

        {transcript_text}

        Format as a JSON array of objects with "question" and "answer" fields.
        Questions should cover important concepts and key information.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=1200
            )
            
            content = response.choices[0].message.content.strip()
            
            # Try to parse as JSON
            try:
                qa_pairs = json.loads(content)
                return qa_pairs if isinstance(qa_pairs, list) else []
            except json.JSONDecodeError:
                return []
                
        except Exception as e:
            print(f"Error generating Q&A pairs: {e}")
            return []
    
    def _parse_notes_fallback(self, content: str) -> Dict:
        """Fallback parser for when JSON parsing fails"""
        
        # Basic structure with fallback content
        return {
            "sections": [
                {
                    "title": "Generated Notes",
                    "timestamp": "00:00",
                    "content": content,
                    "key_points": [],
                    "quotes": [],
                    "concepts": [],
                    "examples": []
                }
            ],
            "topics": ["General Content"],
            "main_theme": "Content analysis",
            "learning_objectives": ["Understanding video content"]
        }
    
    def _create_fallback_notes(self, transcript_text: str, video_info: Dict) -> Dict:
        """Create fallback notes when AI processing fails"""
        
        # Basic text processing
        sections = self._simple_text_segmentation(transcript_text)
        
        return {
            "sections": sections,
            "topics": ["Video Content"],
            "main_theme": f"Analysis of {video_info.get('title', 'video content')}",
            "learning_objectives": ["Understanding the video content"]
        }
    
    def _simple_text_segmentation(self, text: str) -> List[Dict]:
        """Simple text segmentation for fallback"""
        
        # Split by paragraphs or timestamps
        segments = []
        paragraphs = text.split('\n\n')
        
        for i, paragraph in enumerate(paragraphs):
            if len(paragraph.strip()) > 50:  # Skip very short segments
                
                # Extract timestamp if present
                timestamp_match = re.search(r'\[(\d{2}:\d{2})\]', paragraph)
                timestamp = timestamp_match.group(1) if timestamp_match else f"{i*2:02d}:00"
                
                # Clean text
                clean_text = re.sub(r'\[\d{2}:\d{2}\]', '', paragraph).strip()
                
                segments.append({
                    "title": f"Section {i+1}",
                    "timestamp": timestamp,
                    "content": clean_text,
                    "key_points": [],
                    "quotes": [],
                    "concepts": [],
                    "examples": []
                })
        
        return segments if segments else [{
            "title": "Full Content",
            "timestamp": "00:00",
            "content": text,
            "key_points": [],
            "quotes": [],
            "concepts": [],
            "examples": []
        }]
    
    def _extract_list_from_text(self, text: str) -> List[str]:
        """Extract list items from text format"""
        
        # Look for bullet points, numbers, or dashes
        lines = text.split('\n')
        items = []
        
        for line in lines:
            line = line.strip()
            # Match various list formats
            if re.match(r'^[\-\*\•]\s+', line):
                items.append(re.sub(r'^[\-\*\•]\s+', '', line))
            elif re.match(r'^\d+\.\s+', line):
                items.append(re.sub(r'^\d+\.\s+', '', line))
            elif line and not line.startswith('Here') and not line.startswith('The'):
                items.append(line)
        
        return items[:8]  # Limit to 8 items
    
    def validate_notes_structure(self, notes: Dict) -> bool:
        """Validate the notes structure"""
        
        required_keys = ['sections', 'topics', 'main_theme']
        
        if not all(key in notes for key in required_keys):
            return False
        
        # Validate sections
        if not isinstance(notes['sections'], list) or not notes['sections']:
            return False
        
        for section in notes['sections']:
            if not isinstance(section, dict) or 'title' not in section:
                return False
        
        return True
    
    def enhance_notes_with_metadata(self, notes: Dict, transcript: Dict, video_info: Dict) -> Dict:
        """Enhance notes with additional metadata"""
        
        # Add reading time estimation
        total_words = sum(len(section.get('content', '').split()) for section in notes.get('sections', []))
        reading_time = max(1, total_words // 200)  # 200 words per minute
        
        # Add difficulty level based on content
        difficulty = self._estimate_difficulty(notes)
        
        # Update metadata
        if 'metadata' not in notes:
            notes['metadata'] = {}
        
        notes['metadata'].update({
            'total_sections': len(notes.get('sections', [])),
            'estimated_reading_time': f"{reading_time} minutes",
            'difficulty_level': difficulty,
            'content_type': self._determine_content_type(notes),
            'language': 'English'  # Could be detected
        })
        
        return notes
    
    def _estimate_difficulty(self, notes: Dict) -> str:
        """Estimate content difficulty"""
        
        # Simple heuristic based on vocabulary and concepts
        total_text = ' '.join([
            section.get('content', '') for section in notes.get('sections', [])
        ])
        
        words = total_text.split()
        if not words:
            return 'Unknown'
        
        # Count long words (>7 characters)
        long_words = len([word for word in words if len(word) > 7])
        long_word_ratio = long_words / len(words)
        
        if long_word_ratio > 0.2:
            return 'Advanced'
        elif long_word_ratio > 0.1:
            return 'Intermediate'
        else:
            return 'Beginner'
    
    def _determine_content_type(self, notes: Dict) -> str:
        """Determine the type of content"""
        
        topics = notes.get('topics', [])
        main_theme = notes.get('main_theme', '').lower()
        
        # Simple classification based on keywords
        if any(keyword in main_theme for keyword in ['tutorial', 'how to', 'guide', 'learn']):
            return 'Tutorial'
        elif any(keyword in main_theme for keyword in ['lecture', 'education', 'course']):
            return 'Educational'
        elif any(keyword in main_theme for keyword in ['news', 'update', 'report']):
            return 'News/Information'
        elif any(keyword in main_theme for keyword in ['interview', 'discussion', 'talk']):
            return 'Interview/Discussion'
        elif any(keyword in main_theme for keyword in ['review', 'analysis', 'opinion']):
            return 'Review/Analysis'
        else:
            return 'General Content'