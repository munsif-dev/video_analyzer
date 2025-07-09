# Video Content Analyzer - Setup Guide

## Quick Start

1. **Install dependencies**
   ```bash
   uv sync
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run the application**
   ```bash
   uv run streamlit run app.py
   ```

## API Keys Required

### Groq API Key (Free)
- Go to [Groq Console](https://console.groq.com)
- Create account and get API key
- Add to `.env` file as `GROQ_API_KEY=your_key`

**Note**: Groq provides free access with generous rate limits!

## Test Without API Keys

Run the demo to test core functionality:
```bash
uv run python demo.py
```

## Features Working

✅ **Video Processing**: YouTube, Vimeo, Dailymotion, Twitch support
✅ **Transcription**: Free YouTube Transcript API
✅ **Notes Generation**: AI-powered structured notes via Groq
✅ **RAG System**: Question answering with local embeddings
✅ **Export**: Markdown, JSON, text formats
✅ **Caching**: Performance optimization
✅ **Error Handling**: Graceful fallbacks
✅ **100% Free**: All services are completely free

## Architecture

- **Frontend**: Streamlit web interface
- **Backend**: Python services for processing
- **Database**: ChromaDB for vector storage
- **AI**: Groq Mixtral for notes and Q&A
- **Embeddings**: Local sentence-transformers
- **Transcription**: YouTube Transcript API (free)

## Usage Flow

1. **Upload**: Paste video URL
2. **Process**: Auto-transcription and note generation
3. **Review**: Structured notes with timestamps
4. **Query**: Ask questions about content
5. **Export**: Download in multiple formats

## Development

- **Debug Mode**: Set `DEBUG_MODE=true` in `.env`
- **Mock Data**: Works without API keys for testing
- **Extensible**: Easy to add new platforms/features

## Support

- Check `demo.py` for functionality tests
- Review `README.md` for detailed documentation
- Run `python run.py` for setup validation