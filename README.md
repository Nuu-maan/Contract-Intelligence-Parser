# Contract Intelligence Parser

A professional tool for extracting and analyzing contract data from PDF documents.

## Project Structure

- `/backend`: FastAPI service for PDF processing and data extraction
- `/frontend`: Next.js web interface for interacting with the system

## Quick Start

1. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. Access the application at `http://localhost:3000`

## Environment Variables

Create `.env` files in both `backend` and `frontend` directories with required configurations.

## License

MIT 