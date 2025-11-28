# DO GenAI API

A Flask-based REST API that provides an interface to DigitalOcean's GenAI services. This API enables you to manage AI agents, upload files to DigitalOcean Spaces for knowledge bases, re-index knowledge bases, interact with available models, and more.

**NOTE:** Currently in active development. There will be more features and functionality added soon.

## Description

The DO GenAI API is a middleware service that simplifies interaction with DigitalOcean's GenAI platform. It provides RESTful endpoints for:

- **Agent Management**: Create, list, retrieve, delete AI agents, manage API keys, and attach knowledge bases
- **File Management**: Upload, list, and delete files in DigitalOcean Spaces (used for knowledge base storage)
- **Knowledge Base Operations**: Create, list, retrieve, delete knowledge bases, and trigger re-indexing jobs
- **Model Discovery**: List available AI models from DigitalOcean GenAI
- **Bucket Management**: Create, list, retrieve, and delete DigitalOcean Spaces buckets
- **Database Management**: List OpenSearch databases from DigitalOcean

All API endpoints require Bearer token authentication for security.

## Prerequisites

- Python 3.10 or higher
- DigitalOcean account with GenAI access
- DigitalOcean Spaces bucket (file storage to use for Knowledge bases)
- DigitalOcean API token
- DigitalOcean Spaces Access Key & Secret

## Setup

1. **Clone the repository**:

   ```bash
   git clone https://github.com/mvallejo3/do-genai-api.git
   cd do-genai-api
   ```

2. **Create a `.env` file from `.env.example`**:

   ```bash
   cp ./.env.example ./.env
   ```

   Then fill in your environment variables from the Digital Ocean Console.

3. **Run the setup script**:

   ```bash
   chmod +x scripts/*
   ./scripts/setup
   ```

   This will:

   - Create a Python virtual environment (`venv`)
   - Install all required dependencies from `requirements.txt`

4. **Activate the virtual environment**:

   ```bash
   source venv/bin/activate
   ```

## Starting the Application

1. **Run the start script**:

   ```bash
   ./scripts/start
   ```

   Or manually:

   ```bash
   source venv/bin/activate
   source .env
   python app.py
   ```

The API will start on `http://0.0.0.0:8080` (or the port specified in your `PORT` environment variable).

## API Usage Examples

All API requests require Bearer token authentication. Include the token in the `Authorization` header:

```
Authorization: Bearer <your-api-bearer-token>
```

### Health Check

Check if the API is running:

```bash
curl http://localhost:8080/
```

Response:

```json
{
  "status": "ok",
  "message": "DO GenAI API is running"
}
```

### List Files

List all files in the knowledge base bucket:

```bash
curl -X GET "http://localhost:8080/api/files" \
  -H "Authorization: Bearer your-api-bearer-token"
```

List files with a prefix filter:

```bash
curl -X GET "http://localhost:8080/api/files?prefix=documents&max_keys=10" \
  -H "Authorization: Bearer your-api-bearer-token"
```

### Upload Files

Upload a single file:

```bash
curl -X POST "http://localhost:8080/api/files?folder=documents" \
  -H "Authorization: Bearer your-api-bearer-token" \
  -F "file=@/path/to/your/file.pdf"
```

Upload multiple files:

```bash
curl -X POST "http://localhost:8080/api/files?folder=documents" \
  -H "Authorization: Bearer your-api-bearer-token" \
  -F "file=@/path/to/file1.pdf" \
  -F "file=@/path/to/file2.txt"
```

### Delete a File

Delete a file from the knowledge base:

```bash
curl -X DELETE "http://localhost:8080/api/files?key=documents/file.pdf" \
  -H "Authorization: Bearer your-api-bearer-token"
```

### Knowledge Base Management

#### List Knowledge Bases

Get all knowledge bases:

```bash
curl -X GET "http://localhost:8080/api/knowledgebase" \
  -H "Authorization: Bearer your-api-bearer-token"
```

#### Create Knowledge Base

Create a new knowledge base:

```bash
curl -X POST "http://localhost:8080/api/knowledgebase" \
  -H "Authorization: Bearer your-api-bearer-token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Knowledge Base",
    "description": "A knowledge base for my AI agent"
  }'
```

#### Get Knowledge Base

Retrieve a specific knowledge base by ID:

```bash
curl -X GET "http://localhost:8080/api/knowledgebase/your-knowledge-base-uuid" \
  -H "Authorization: Bearer your-api-bearer-token"
```

#### Delete Knowledge Base

Delete a knowledge base:

```bash
curl -X DELETE "http://localhost:8080/api/knowledgebase/your-knowledge-base-uuid" \
  -H "Authorization: Bearer your-api-bearer-token"
```

#### Re-index Knowledge Base

Trigger a re-indexing job for a knowledge base:

```bash
curl -X POST "http://localhost:8080/api/knowledgebase/reindex" \
  -H "Authorization: Bearer your-api-bearer-token" \
  -H "Content-Type: application/json" \
  -d '{
    "knowledge_base_uuid": "your-knowledge-base-uuid"
  }'
```

Re-index specific data sources:

```bash
curl -X POST "http://localhost:8080/api/knowledgebase/reindex" \
  -H "Authorization: Bearer your-api-bearer-token" \
  -H "Content-Type: application/json" \
  -d '{
    "knowledge_base_uuid": "your-knowledge-base-uuid",
    "data_source_uuids": ["data-source-uuid-1", "data-source-uuid-2"]
  }'
```

### List Agents

Get all AI agents:

```bash
curl -X GET "http://localhost:8080/api/agents" \
  -H "Authorization: Bearer your-api-bearer-token"
```

### Get Agent

Retrieve a specific agent by ID:

```bash
curl -X GET "http://localhost:8080/api/agents/your-agent-uuid" \
  -H "Authorization: Bearer your-api-bearer-token"
```

### Create Agent

Create a new AI agent:

```bash
curl -X POST "http://localhost:8080/api/agents" \
  -H "Authorization: Bearer your-api-bearer-token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My AI Agent",
    "description": "A helpful AI assistant",
    "instructions": "You are a helpful assistant that answers questions accurately.",
    "model": "your-model-uuid",
    "workspace": "your-workspace-uuid",
    "region": "nyc1",
    "project_id": "your-project-id"
  }'
```

### Delete Agent

Delete an agent:

```bash
curl -X DELETE "http://localhost:8080/api/agents/your-agent-uuid" \
  -H "Authorization: Bearer your-api-bearer-token"
```

### Agent API Keys

#### List Agent API Keys

List all API keys for a specific agent:

```bash
curl -X GET "http://localhost:8080/api/agents/your-agent-uuid/api-keys" \
  -H "Authorization: Bearer your-api-bearer-token"
```

#### Create Agent API Key

Create a new API key for an agent:

```bash
curl -X POST "http://localhost:8080/api/agents/your-agent-uuid/api-keys" \
  -H "Authorization: Bearer your-api-bearer-token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My API Key"
  }'
```

### Attach Knowledge Base to Agent

Attach a knowledge base to an agent:

```bash
curl -X POST "http://localhost:8080/api/agents/your-agent-uuid/attach-knowledgebase" \
  -H "Authorization: Bearer your-api-bearer-token" \
  -H "Content-Type: application/json" \
  -d '{
    "knowledge_base_uuid": "your-knowledge-base-uuid"
  }'
```

### List Models

List all available models:

```bash
curl -X GET "http://localhost:8080/api/models" \
  -H "Authorization: Bearer your-api-bearer-token"
```

Filter models by use cases:

```bash
curl -X GET "http://localhost:8080/api/models?usecases=MODEL_USECASE_AGENT&public_only=true" \
  -H "Authorization: Bearer your-api-bearer-token"
```

### List OpenSearch Databases

List all OpenSearch databases from DigitalOcean:

```bash
curl -X GET "http://localhost:8080/api/opensearch-databases" \
  -H "Authorization: Bearer your-api-bearer-token"
```

### Bucket Management

#### List Buckets

List all buckets in DigitalOcean Spaces:

```bash
curl -X GET "http://localhost:8080/api/buckets" \
  -H "Authorization: Bearer your-api-bearer-token"
```

#### Create Bucket

Create a new bucket in DigitalOcean Spaces:

```bash
curl -X POST "http://localhost:8080/api/buckets" \
  -H "Authorization: Bearer your-api-bearer-token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-bucket-name",
    "region": "nyc3"
  }'
```

#### Get Bucket

Get information about a specific bucket:

```bash
curl -X GET "http://localhost:8080/api/buckets/my-bucket-name" \
  -H "Authorization: Bearer your-api-bearer-token"
```

#### Delete Bucket

Delete a bucket (must be empty):

```bash
curl -X DELETE "http://localhost:8080/api/buckets/my-bucket-name" \
  -H "Authorization: Bearer your-api-bearer-token"
```

## API Response Format

All API responses follow a standard format:

**Success Response:**

```json
{
  "status": "success",
  "data": { ... }
}
```

**Error Response:**

```json
{
  "status": "error",
  "message": "Error description"
}
```

## Project Structure

The application follows a modular architecture using Flask Blueprints for better organization and maintainability:

```
do-genai-api/
├── app.py                      # Main Flask application factory (registers blueprints)
├── requirements.txt            # Python dependencies
├── middleware/                 # Middleware and decorators
│   ├── __init__.py
│   ├── auth.py                 # Bearer token authentication middleware
│   └── decorators.py           # Response handler decorator
├── routes/                      # Flask blueprints (route handlers)
│   ├── __init__.py
│   ├── health.py               # Health check endpoint
│   ├── files.py                # File management routes (/api/files)
│   ├── knowledge_bases.py      # Knowledge base routes (/api/knowledgebase)
│   ├── agents.py               # Agent routes (/api/agents)
│   ├── models.py               # Model routes (/api/models)
│   ├── databases.py            # Database routes (/api/opensearch-databases)
│   └── buckets.py              # Bucket routes (/api/buckets)
├── services/                   # Business logic and external API clients
│   ├── __init__.py
│   ├── do_api/                 # DigitalOcean GenAI API services
│   │   ├── __init__.py
│   │   ├── base.py             # Base API client
│   │   ├── agents.py           # Agent service
│   │   ├── api_keys.py         # API key service
│   │   ├── knowledge_bases.py  # Knowledge base service
│   │   ├── models.py           # Model service
│   │   ├── indexing_jobs.py    # Indexing job service
│   │   ├── databases.py        # Database service
│   │   └── workspaces.py       # Workspace service
│   └── Spaces.py               # DigitalOcean Spaces service
└── scripts/
    ├── setup                   # Setup script
    └── start                   # Start script
```

### Architecture Overview

- **`app.py`**: Application factory that configures Flask, registers middleware, and registers all blueprints
- **`middleware/`**: Shared middleware and decorators used across all routes
- **`routes/`**: Flask blueprints organized by resource/domain (files, agents, knowledge bases, etc.)
- **`services/`**: Business logic layer that interacts with DigitalOcean APIs

## Dependencies

- `flask==3.0.0` - Web framework
- `python-dotenv==1.0.0` - Environment variable management
- `boto3==1.35.0` - AWS SDK for DigitalOcean Spaces (S3-compatible)
- `pydo==0.21.0` - DigitalOcean API client

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
