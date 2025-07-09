from groq import Groq
import numpy as np
from typing import Dict, List, Optional, Any
import json
import re
from datetime import datetime
import chromadb
from sentence_transformers import SentenceTransformer

class RAGSystem:
    """RAG (Retrieval-Augmented Generation) system for video content Q&A"""
    
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.chat_model = "llama-3.3-70b-versatile"
        self.chroma_client = None
        self.collection = None
    
    def setup_vector_store(self, transcript: Dict, notes: Dict, chunk_size: int = 1000) -> Dict:
        """Setup vector store with transcript and notes content"""
        
        # Initialize ChromaDB with new PersistentClient
        self.chroma_client = chromadb.PersistentClient(
            path="./data/embeddings"
        )
        
        # Create or get collection
        collection_name = f"video_content_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.collection = self.chroma_client.create_collection(
            name=collection_name,
            metadata={"description": "Video content for RAG"}
        )
        
        # Process and chunk content
        chunks = self._create_chunks(transcript, notes, chunk_size)
        
        # Generate embeddings and store
        self._store_chunks(chunks)
        
        return {
            'collection_name': collection_name,
            'total_chunks': len(chunks),
            'chunk_size': chunk_size
        }
    
    def _create_chunks(self, transcript: Dict, notes: Dict, chunk_size: int) -> List[Dict]:
        """Create semantic chunks from transcript and notes"""
        
        chunks = []
        chunk_id = 0
        
        # Process transcript segments
        if 'segments' in transcript:
            for segment in transcript['segments']:
                chunk = {
                    'id': f"transcript_{chunk_id}",
                    'content': segment.get('text', ''),
                    'source': 'transcript',
                    'timestamp': segment.get('start', '00:00'),
                    'speaker': segment.get('speaker', ''),
                    'metadata': {
                        'type': 'transcript_segment',
                        'start_time': segment.get('start', '00:00'),
                        'end_time': segment.get('end', '00:00')
                    }
                }
                chunks.append(chunk)
                chunk_id += 1
        
        # Process notes sections
        if 'sections' in notes:
            for section in notes['sections']:
                # Main section content
                if section.get('content'):
                    chunk = {
                        'id': f"notes_{chunk_id}",
                        'content': section['content'],
                        'source': 'notes',
                        'timestamp': section.get('timestamp', '00:00'),
                        'section_title': section.get('title', ''),
                        'metadata': {
                            'type': 'notes_section',
                            'section_title': section.get('title', ''),
                            'timestamp': section.get('timestamp', '00:00')
                        }
                    }
                    chunks.append(chunk)
                    chunk_id += 1
                
                # Key points as separate chunks
                if section.get('key_points'):
                    for point in section['key_points']:
                        chunk = {
                            'id': f"keypoint_{chunk_id}",
                            'content': point,
                            'source': 'key_points',
                            'timestamp': section.get('timestamp', '00:00'),
                            'section_title': section.get('title', ''),
                            'metadata': {
                                'type': 'key_point',
                                'section_title': section.get('title', ''),
                                'timestamp': section.get('timestamp', '00:00')
                            }
                        }
                        chunks.append(chunk)
                        chunk_id += 1
                
                # Quotes as separate chunks
                if section.get('quotes'):
                    for quote in section['quotes']:
                        chunk = {
                            'id': f"quote_{chunk_id}",
                            'content': quote,
                            'source': 'quotes',
                            'timestamp': section.get('timestamp', '00:00'),
                            'section_title': section.get('title', ''),
                            'metadata': {
                                'type': 'quote',
                                'section_title': section.get('title', ''),
                                'timestamp': section.get('timestamp', '00:00')
                            }
                        }
                        chunks.append(chunk)
                        chunk_id += 1
        
        # Split large chunks
        final_chunks = []
        for chunk in chunks:
            if len(chunk['content']) > chunk_size:
                split_chunks = self._split_large_chunk(chunk, chunk_size)
                final_chunks.extend(split_chunks)
            else:
                final_chunks.append(chunk)
        
        return final_chunks
    
    def _split_large_chunk(self, chunk: Dict, max_size: int) -> List[Dict]:
        """Split large chunks into smaller ones"""
        
        content = chunk['content']
        chunks = []
        
        # Split by sentences first
        sentences = re.split(r'[.!?]+', content)
        
        current_chunk = ""
        chunk_count = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Check if adding this sentence would exceed max size
            if len(current_chunk) + len(sentence) > max_size and current_chunk:
                # Save current chunk
                new_chunk = chunk.copy()
                new_chunk['id'] = f"{chunk['id']}_{chunk_count}"
                new_chunk['content'] = current_chunk.strip()
                chunks.append(new_chunk)
                
                # Start new chunk
                current_chunk = sentence
                chunk_count += 1
            else:
                current_chunk += ". " + sentence if current_chunk else sentence
        
        # Add final chunk
        if current_chunk:
            new_chunk = chunk.copy()
            new_chunk['id'] = f"{chunk['id']}_{chunk_count}"
            new_chunk['content'] = current_chunk.strip()
            chunks.append(new_chunk)
        
        return chunks
    
    def _store_chunks(self, chunks: List[Dict]):
        """Store chunks in vector database"""
        
        batch_size = 100
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i+batch_size]
            
            # Prepare data for ChromaDB
            ids = [chunk['id'] for chunk in batch]
            documents = [chunk['content'] for chunk in batch]
            metadatas = [chunk['metadata'] for chunk in batch]
            
            # Generate embeddings
            embeddings = self._generate_embeddings([chunk['content'] for chunk in batch])
            
            # Store in ChromaDB
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings
            )
    
    def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for texts using local sentence-transformers model"""
        
        try:
            # Generate embeddings using sentence-transformers
            embeddings = self.embedding_model.encode(texts)
            
            # Convert to list of lists
            return [embedding.tolist() for embedding in embeddings]
            
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            # Return dummy embeddings for development (384-dimensional for all-MiniLM-L6-v2)
            return [[0.0] * 384 for _ in texts]
    
    def answer_question(self, question: str, vector_store: Dict, options: Dict) -> Dict:
        """Answer a question using RAG"""
        
        # Retrieve relevant chunks
        relevant_chunks = self._retrieve_relevant_chunks(
            question, 
            options.get('max_sources', 3)
        )
        
        # Generate answer
        answer = self._generate_answer(question, relevant_chunks, options)
        
        # Process sources
        sources = self._process_sources(relevant_chunks, options)
        
        # Generate follow-up questions
        follow_ups = self._generate_follow_up_questions(question, answer, relevant_chunks)
        
        return {
            'answer': answer,
            'sources': sources,
            'follow_up_questions': follow_ups,
            'confidence': self._calculate_confidence(relevant_chunks, answer)
        }
    
    def _retrieve_relevant_chunks(self, question: str, max_results: int) -> List[Dict]:
        """Retrieve relevant chunks for the question"""
        
        try:
            # Generate query embedding using local model
            query_embedding = self._generate_embeddings([question])[0]
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=max_results * 2,  # Get more results for reranking
                include=['documents', 'metadatas', 'distances']
            )
            
            # Convert to structured format
            chunks = []
            for i, doc in enumerate(results['documents'][0]):
                chunk = {
                    'content': doc,
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i],
                    'relevance_score': 1 - results['distances'][0][i]  # Convert distance to similarity
                }
                chunks.append(chunk)
            
            # Rerank based on relevance
            reranked_chunks = self._rerank_chunks(question, chunks)
            
            return reranked_chunks[:max_results]
            
        except Exception as e:
            print(f"Error retrieving chunks: {e}")
            return []
    
    def _rerank_chunks(self, question: str, chunks: List[Dict]) -> List[Dict]:
        """Rerank chunks based on relevance to question"""
        
        # Simple reranking based on keyword matching and semantic similarity
        question_lower = question.lower()
        question_keywords = set(re.findall(r'\b\w+\b', question_lower))
        
        for chunk in chunks:
            content_lower = chunk['content'].lower()
            content_keywords = set(re.findall(r'\b\w+\b', content_lower))
            
            # Keyword overlap score
            keyword_overlap = len(question_keywords & content_keywords) / len(question_keywords) if question_keywords else 0
            
            # Boost score based on source type
            source_boost = 1.0
            if chunk['metadata'].get('type') == 'key_point':
                source_boost = 1.2
            elif chunk['metadata'].get('type') == 'quote':
                source_boost = 1.1
            
            # Combined relevance score
            chunk['relevance_score'] = (chunk['relevance_score'] * 0.7 + keyword_overlap * 0.3) * source_boost
        
        # Sort by relevance score
        return sorted(chunks, key=lambda x: x['relevance_score'], reverse=True)
    
    def _generate_answer(self, question: str, chunks: List[Dict], options: Dict) -> str:
        """Generate answer using retrieved chunks"""
        
        # Prepare context
        context = self._prepare_context(chunks)
        
        # Create system prompt
        system_prompt = """
        You are an expert video content analyst. Your task is to answer questions based on the provided video content context.
        
        Guidelines:
        1. Use only the information provided in the context
        2. Be accurate and factual
        3. Include specific details and examples when available
        4. If the context doesn't contain enough information, say so
        5. Maintain a helpful and informative tone
        6. Reference timestamps when relevant
        7. Prioritize key points and direct quotes
        """
        
        # Create user prompt
        user_prompt = f"""
        Based on the following video content, please answer this question: {question}
        
        Context from video:
        {context}
        
        Please provide a comprehensive answer based on the available information.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating answer: {e}")
            return "I apologize, but I encountered an error while generating the answer. Please try again."
    
    def _prepare_context(self, chunks: List[Dict]) -> str:
        """Prepare context string from chunks"""
        
        context_parts = []
        
        for i, chunk in enumerate(chunks):
            content = chunk['content']
            metadata = chunk['metadata']
            
            # Add source information
            source_info = f"Source {i+1}"
            if metadata.get('section_title'):
                source_info += f" - {metadata['section_title']}"
            if metadata.get('timestamp'):
                source_info += f" [{metadata['timestamp']}]"
            
            context_parts.append(f"{source_info}:\n{content}\n")
        
        return "\n".join(context_parts)
    
    def _process_sources(self, chunks: List[Dict], options: Dict) -> List[Dict]:
        """Process chunks into source information"""
        
        sources = []
        
        for chunk in chunks:
            source = {
                'content': chunk['content'],
                'relevance_score': chunk['relevance_score'],
                'section_title': chunk['metadata'].get('section_title', 'Unknown Section'),
                'timestamp': chunk['metadata'].get('timestamp', '00:00'),
                'source_type': chunk['metadata'].get('type', 'unknown')
            }
            sources.append(source)
        
        return sources
    
    def _generate_follow_up_questions(self, question: str, answer: str, chunks: List[Dict]) -> List[str]:
        """Generate follow-up questions based on the answer"""
        
        context = self._prepare_context(chunks[:3])  # Use top 3 chunks
        
        prompt = f"""
        Based on the following question, answer, and context, suggest 3 relevant follow-up questions:
        
        Original Question: {question}
        Answer: {answer}
        Context: {context}
        
        Please provide 3 follow-up questions that would help the user explore the topic further.
        Format as a JSON array of strings.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=300
            )
            
            content = response.choices[0].message.content.strip()
            
            # Try to parse as JSON
            try:
                follow_ups = json.loads(content)
                return follow_ups if isinstance(follow_ups, list) else []
            except json.JSONDecodeError:
                # Extract questions from text
                return self._extract_questions_from_text(content)
                
        except Exception as e:
            print(f"Error generating follow-up questions: {e}")
            return []
    
    def _extract_questions_from_text(self, text: str) -> List[str]:
        """Extract questions from text format"""
        
        # Look for question marks
        sentences = re.split(r'[.!?]+', text)
        questions = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence.endswith('?') or '?' in sentence:
                # Clean up the question
                question = sentence.split('?')[0] + '?'
                question = re.sub(r'^\d+\.\s*', '', question)  # Remove numbering
                question = re.sub(r'^[\-\*]\s*', '', question)  # Remove bullet points
                if len(question) > 10:  # Ensure it's a meaningful question
                    questions.append(question)
        
        return questions[:3]  # Return max 3 questions
    
    def _calculate_confidence(self, chunks: List[Dict], answer: str) -> float:
        """Calculate confidence score for the answer"""
        
        if not chunks:
            return 0.0
        
        # Average relevance score of retrieved chunks
        avg_relevance = sum(chunk['relevance_score'] for chunk in chunks) / len(chunks)
        
        # Answer length factor (longer answers might be more comprehensive)
        answer_length_factor = min(len(answer.split()) / 100, 1.0)
        
        # Source diversity factor
        source_types = set(chunk['metadata'].get('type', 'unknown') for chunk in chunks)
        diversity_factor = len(source_types) / 4  # Assuming 4 different source types
        
        # Combined confidence
        confidence = (avg_relevance * 0.6 + answer_length_factor * 0.2 + diversity_factor * 0.2)
        
        return min(confidence, 1.0)
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the current collection"""
        
        if not self.collection:
            return {}
        
        try:
            count = self.collection.count()
            return {
                'total_chunks': count,
                'collection_name': self.collection.name,
                'embedding_model': 'sentence-transformers/all-MiniLM-L6-v2'
            }
        except:
            return {}
    
    def clear_collection(self):
        """Clear the current collection"""
        
        if self.collection:
            try:
                self.chroma_client.delete_collection(self.collection.name)
                self.collection = None
            except:
                pass