# Contract Intelligence Parser - Backend

FastAPI service for processing PDF contracts and extracting structured data.

## Features

- PDF contract processing with async support
- Data extraction for parties, financials, and terms
- Confidence scoring (0-100)
- MongoDB storage with Motor async driver
- Background task processing
- Docker support

## API Endpoints

- `POST /contracts/upload` - Upload PDF contract
- `GET /contracts/{id}/status` - Check processing status
- `GET /contracts/{id}` - Get extracted data
- `GET /contracts` - List all contracts
- `GET /contracts/{id}/download` - Download original PDF

## Setup

1. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables in `.env`:
   ```
   MONGODB_URL=mongodb://localhost:27017
   MONGODB_DB=contract_parser
   ```

4. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```

## Development

- Format: `black . && isort .`
- Lint: `flake8`
- Test: `pytest`

## Docker

```bash
docker build -t contract-parser .
docker run -p 8000:8000 contract-parser
```
- MongoDB (local or cloud)
- Docker (optional)

### Local Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd Contract-Intelligence-Parser/backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment Configuration**
Create `.env` file with:
```env
MONGODB_URL=
DATABASE_NAME=contract_intelligence
UPLOAD_DIR=uploads
MAX_FILE_SIZE=52428800
LOG_LEVEL=INFO
```

5. **Create uploads directory**
```bash
mkdir uploads
```

6. **Run the application**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Setup

1. **Build Docker image**
```bash
docker build -t contract-parser .
```

2. **Run container**
```bash
docker run -d -p 8000:8000 --env-file .env contract-parser
```

## Usage Examples

### Upload Contract
```bash
curl -X POST "http://localhost:8000/contracts/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@contract.pdf"
```

### Check Status
```bash
curl "http://localhost:8000/contracts/{contract_id}/status"
```

### Get Contract Data
```bash
curl "http://localhost:8000/contracts/{contract_id}"
```

### List Contracts
```bash
curl "http://localhost:8000/contracts?page=1&page_size=10&status=completed"
```

## Data Extraction

The system extracts the following information:

### Party Identification
- Contract parties (customer, vendor, third parties)
- Legal entity names and registration details
- Authorized signatories and roles
- Contact information (phone, email, address)

### Financial Details
- Line items with descriptions, quantities, unit prices
- Total contract value and currency
- Monthly recurring costs and one-time setup costs
- Tax information and additional fees

### Payment Structure
- Payment terms (Net 30, Net 60, etc.)
- Payment schedules and due dates
- Payment methods and banking details

### Service Level Agreements
- Performance metrics and benchmarks
- Penalty clauses and service credits
- Support and maintenance terms
- Escalation procedures

## Scoring Algorithm

The confidence scoring system uses weighted calculations:

- **Financial completeness**: 30 points
- **Party identification**: 25 points
- **Payment terms clarity**: 20 points
- **SLA definition**: 15 points
- **Contact information**: 10 points

Total score ranges from 0-100 based on data completeness.

## Database Schema

### Contracts Collection
```json
{
  "_id": "uuid4_string",
  "filename": "contract_document.pdf",
  "file_path": "uploads/uuid_contract_document.pdf",
  "status": "pending|processing|completed|failed",
  "progress": 0,
  "upload_date": "2025-01-15T10:30:00Z",
  "error_message": null,
  "file_size": 2048576,
  "content_hash": "sha256_hash"
}
```

### Contract Data Collection
```json
{
  "_id": "uuid4_string",
  "contract_id": "reference_to_contract_id",
  "extracted_data": {
    "parties": {...},
    "financial_details": {...},
    "payment_structure": {...},
    "sla_terms": {...}
  },
  "confidence_score": 85.5,
  "processing_date": "2025-01-15T10:45:00Z"
}
```

## Health Check

Check application health:
```bash
curl "http://localhost:8000/health"
```

## API Documentation

Interactive API documentation available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Logging

Application uses structured logging with configurable levels:
- DEBUG: Detailed debugging information
- INFO: General information (default)
- WARNING: Warning messages
- ERROR: Error conditions

## Error Handling

The API returns standardized error responses:
```json
{
  "error": "Error message",
  "detail": "Detailed error description",
  "status_code": 400
}
```

## Performance Considerations

- Asynchronous processing for I/O operations
- Database indexing for optimal query performance
- File size limits (50MB max)
- Concurrent processing support
- Background task processing

## Security Features

- File type validation (PDF only)
- File size limits
- Content hash verification
- Non-root Docker user
- Input sanitization
- Error message sanitization

## Development

### Running Tests
```bash
pytest tests/
```

### Code Quality
```bash
# Format code
black app/

# Lint code
flake8 app/

# Type checking
mypy app/
```

## Troubleshooting

### Common Issues

1. **MongoDB Connection Failed**
   - Verify MONGODB_URL in .env file
   - Check network connectivity
   - Ensure database credentials are correct

2. **File Upload Errors**
   - Check file size (max 50MB)
   - Ensure file is valid PDF
   - Verify uploads/ directory exists and is writable

3. **Processing Stuck**
   - Check application logs
   - Verify PDF is not corrupted
   - Restart application if needed

### Logs Location
- Application logs: stdout/stderr
- Docker logs: `docker logs <container_id>`

## License

This project is licensed under the MIT License.

## Support

For support and questions, please check the application logs and API documentation first.
