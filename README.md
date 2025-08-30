# Brax AI Concierge (HTTP)

Production-ready HTTP chatbot for Brax Fine Jewelers to embed on `shop.braxjewelers.com`. 

## Architecture

- **Backend**: Python FastAPI + SQLAlchemy + Azure PostgreSQL + Redis
- **Frontend**: React TypeScript widget with UMD/IIFE embed support
- **Integration**: Wraps existing LangChain/LangGraph agents without modification
- **Lead Capture**: Structured JSON events forwarded to GoHighLevel

## Quick Start

### 1. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your actual credentials
# - POSTGRES_URL: Azure PostgreSQL connection string
# - REDIS_URL: Redis connection string  
# - GHL_WEBHOOK_URL: GoHighLevel webhook endpoint
```

### 2. Backend Setup (Windows PowerShell)

```powershell
# Bootstrap Python environment
.\scripts\bootstrap.ps1

# Run database migrations
.\scripts\db_migrate.ps1

# Start API server
.\scripts\run_api.ps1
```

### 3. Frontend Development

```bash
npm install
npm run dev
```

### 4. Production Build

```bash
# Build embeddable widget
npm run build:embed

# Output: dist/embed/brax-chat.umd.js and brax-chat.iife.js
```

## Embedding on Website

Add to your website's HTML:

```html
<script src="https://your-cdn.com/brax-chat.iife.js"></script>
<script>
  BraxChat.mount({
    apiUrl: 'https://your-api.com',
    position: 'bottom-right',
    theme: 'light',
    userId: 'customer-123'
  });
</script>
```

## API Endpoints

- `POST /chat` - Send message and get response
- `GET /thread/{thread_id}/history` - Get conversation history
- `GET /health` - Health check

## Lead Capture

The AI agent emits lead data in structured JSON blocks:

```
```lead
{
  "name": "John Doe",
  "email": "john@example.com", 
  "phone": "+1234567890",
  "intent": "engagement_ring",
  "notes": "Looking for 2 carat diamond, budget $15k"
}
```
```

Leads are automatically:
1. Saved to PostgreSQL `leads` table
2. Forwarded to GoHighLevel webhook
3. Optionally created as contacts via GHL REST API

## Project Structure

```
brax-chat/
├── backend/           # Python FastAPI application
│   ├── api/          # API routes and endpoints
│   ├── core/         # Agent adapters and graph building
│   ├── config/       # Settings and configuration
│   ├── db/           # Database models and migrations
│   ├── services/     # External service integrations
│   └── prompts/      # System prompts and personas
├── frontend/         # React TypeScript widget
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── lib/        # Client library and utilities
│   │   ├── embed/      # Embedding and mount logic
│   │   └── styles/     # Global styles and themes
└── scripts/          # PowerShell automation scripts
```

## Development

- Backend uses Black formatting (`black backend/`)
- Frontend uses Prettier (`npm run format`)
- All versions are pinned for reproducibility
- Immutable core agents in `agents/` and `memory/` directories