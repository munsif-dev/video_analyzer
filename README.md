# Video Content Analyzer

A comprehensive Streamlit application that transforms video content into searchable, structured knowledge through transcription, note generation, and RAG-powered Q&A.

## Features

- **Video Processing**: Support for YouTube, Vimeo, Dailymotion, and Twitch
- **Smart Transcription**: Free transcription via YouTube Transcript API
- **Structured Notes**: AI-powered note generation with hierarchical organization using Groq
- **RAG-powered Q&A**: Ask questions about video content with citations using local embeddings
- **Multiple Export Formats**: Export notes as Markdown, JSON, or plain text
- **Real-time Processing**: Progress tracking and status updates
- **100% Free**: All services are completely free to use

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd video-analyzer
   ```

2. **Install dependencies with uv**
   ```bash
   uv sync
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your API key:
   - `GROQ_API_KEY`: Required for note generation and Q&A (Free at console.groq.com)

## Usage

1. **Start the application**
   ```bash
   uv run streamlit run app.py
   ```

2. **Configure API key**
   - Enter your Groq API key in the sidebar
   - Adjust processing options as needed

3. **Process a video**
   - Navigate to "Upload Video"
   - Paste a supported video URL
   - Click "Process Video"
   - Wait for processing to complete

4. **View generated notes**
   - Navigate to "View Notes"
   - Use different view modes (Structured, Timeline, Summary)
   - Search within notes
   - Export in various formats

5. **Ask questions**
   - Navigate to "Q&A"
   - Ask questions about the video content
   - Get answers with citations and timestamps

## Supported Platforms

- **YouTube** (youtube.com, youtu.be)
- **Vimeo** (vimeo.com)
- **Dailymotion** (dailymotion.com)
- **Twitch** (twitch.tv)

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | - | Groq API key (required, free at console.groq.com) |
| `MAX_VIDEO_DURATION` | 30 | Maximum video duration in minutes |
| `CHUNK_SIZE` | 1000 | Text chunk size for RAG |
| `MAX_SOURCES` | 3 | Maximum sources in Q&A responses |
| `EMBEDDING_MODEL` | sentence-transformers/all-MiniLM-L6-v2 | Local embedding model |
| `CHAT_MODEL` | mixtral-8x7b-32768 | Groq chat model |
| `CACHE_ENABLED` | true | Enable caching |
| `DEBUG_MODE` | false | Enable debug mode |

### Processing Options

- **Max Duration**: For videos longer than 30 minutes, only the first portion is processed
- **Chunk Size**: Controls how text is divided for RAG processing
- **Note Generation**: Options for summaries, key points, and Q&A pairs
- **Timestamps**: Include/exclude timestamps in notes and answers


## API Keys Setup

### Groq API Key (Free)
1. Go to [Groq Console](https://console.groq.com)
2. Create an account or sign in
3. Navigate to API Keys
4. Create a new API key
5. Copy the key to your `.env` file

**Note**: Groq provides free access to their lightning-fast LLM inference API with generous rate limits.

## Development

### Project Structure
- `components/`: Streamlit UI components
- `services/`: Core business logic and API integrations
- `utils/`: Configuration and utility functions
- `data/`: Local data storage

### Adding New Features
1. Create new service classes in `services/`
2. Add UI components in `components/`
3. Update navigation in `navigation.py`
4. Add configuration options in `config.py`

### Testing
```bash
# Run with mock data for development
DEBUG_MODE=true uv run streamlit run app.py
```
