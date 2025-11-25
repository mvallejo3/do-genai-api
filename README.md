# DO GenAI API

A Flask-based REST API that provides an interface to DigitalOcean's GenAI services. This API enables you to manage AI agents, upload files to DigitalOcean Spaces for knowledge bases, re-index knowledge bases, interact with available models, and more.

**NOTE:** Currently in active development. There will be more features and functionality added soon.

## Description

The DO GenAI API is a middleware service that simplifies interaction with DigitalOcean's GenAI platform. It provides RESTful endpoints for:

- **Agent Management**: Create, list, retrieve, and delete AI agents
- **File Management**: Upload, list, and delete files in DigitalOcean Spaces (used for knowledge base storage)
- **Knowledge Base Operations**: Trigger re-indexing jobs for knowledge bases
- **Model Discovery**: List available AI models from DigitalOcean GenAI

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

### Re-index Knowledge Base

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
    "openaiModel": "your-model-uuid"
  }'
```

### Delete Agent

Delete an agent:

```bash
curl -X DELETE "http://localhost:8080/api/agents/your-agent-uuid" \
  -H "Authorization: Bearer your-api-bearer-token"
```

### List Models

List all available models:

```bash
curl -X GET "http://localhost:8080/api/models" \
  -H "Authorization: Bearer your-api-bearer-token"
```

Filter models by use cases:

```bash
curl -X GET "http://localhost:8080/api/models?usecases=chat,completion&public_only=true" \
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

## Testing

The project includes tests for the DigitalOcean GenAI service. Before running tests, ensure you have:

1. **Activated the virtual environment**:

   ```bash
   source venv/bin/activate
   ```

2. **Set up your `.env` file** with the required environment variables (see [Setup](#setup) section).

### Running Tests

Run the test suite using Python:

```bash
python tests/test_do_genai.py
```

Or from the project root:

```bash
python -m tests.test_do_genai
```

### What the Tests Cover

The test suite verifies:

- Service initialization
- Listing workspaces
- Listing available models
- Listing knowledge bases
- Listing agents
- Listing datacenter regions

### Test Output

The tests will display:

- ✓ for passed tests
- ✗ for failed tests
- A summary at the end showing passed/failed counts

**Example output:**

```
============================================================
DigitalOcean GenAI Service Test
============================================================
Testing initialization...
✓ Service initialized successfully

Testing list_workspaces...
✓ Successfully listed workspaces
  Found 1 workspace(s)

...

============================================================
Test Summary
============================================================
Passed: 5
Failed: 0
Total: 5

✓ All tests passed!
```

**Note:** Tests require valid DigitalOcean API credentials and will make actual API calls to DigitalOcean's services.

## Project Structure

```
do-genai-api/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── scripts/
│   ├── setup             # Setup script
│   └── start             # Start script
├── services/
│   ├── __init__.py
│   ├── do_genai.py      # DigitalOcean GenAI service
│   └── Spaces.py         # DigitalOcean Spaces service
└── tests/
    └── test_do_genai.py  # Test files
```

## Dependencies

- `flask==3.0.0` - Web framework
- `python-dotenv==1.0.0` - Environment variable management
- `boto3==1.35.0` - AWS SDK for DigitalOcean Spaces (S3-compatible)
- `pydo==0.21.0` - DigitalOcean API client

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
