"""Main FastAPI application with all contract processing endpoints."""

import logging
import os
from contextlib import asynccontextmanager
from typing import Optional
import asyncio
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Query, Depends
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from app.database import connect_to_mongo, close_mongo_connection, get_database
from app.services.contract_service import ContractService
from app.schemas import (
    ContractUploadResponse, ContractStatusResponse, ContractDataResponse,
    ContractListResponse, ErrorResponse, HealthCheckResponse
)
from app.config import settings
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    await connect_to_mongo()
    logger.info("Application started")
    yield
    # Shutdown
    await close_mongo_connection()
    logger.info("Application shutdown")


# Create FastAPI application
app = FastAPI(
    title="Contract Intelligence Parser",
    description="Professional Contract Intelligence Parser backend system using FastAPI and MongoDB",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_contract_service() -> ContractService:
    """Get contract service instance."""
    return ContractService(get_database())


async def process_contract_background(contract_id: str):
    """Background task for processing contracts."""
    try:
        service = get_contract_service()
        await service.process_contract(contract_id)
    except Exception as e:
        logger.error(f"Background processing failed for contract {contract_id}: {e}")


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Contract Intelligence Parser API", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        db = get_database()
        # Test database connection
        await db.command('ping')
        database_connected = True
    except Exception:
        database_connected = False
    
    return {
        "status": "healthy" if database_connected else "unhealthy",
        "timestamp": datetime.utcnow(),
        "database_connected": database_connected
    }


@app.post("/contracts/upload")
async def upload_contract(file: UploadFile = File(...)):
    """
    Upload PDF contract file for processing.
    
    - **file**: PDF contract file (max 50MB)
    
    Returns contract_id for tracking processing status.
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are supported"
            )
        
        # Read file content
        content = await file.read()
        
        # Validate file size
        if len(content) > settings.max_file_size:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum limit of {settings.max_file_size} bytes"
            )
        
        if len(content) == 0:
            raise HTTPException(
                status_code=400,
                detail="File is empty"
            )
        
        # Initialize service
        service = get_contract_service()
        
        # Save file and create contract record
        file_path, content_hash = await service.save_uploaded_file(file.filename, content)
        contract_id = await service.create_contract(
            filename=file.filename,
            file_path=file_path,
            file_size=len(content),
            content_hash=content_hash
        )
        
        # Start background processing (simplified)
        asyncio.create_task(process_contract_background(contract_id))
        
        return {
            "contract_id": contract_id,
            "message": "Contract uploaded successfully. Processing started.",
            "filename": file.filename,
            "file_size": len(content)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading contract: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during file upload"
        )


@app.get("/contracts/{contract_id}/status", response_model=ContractStatusResponse)
async def get_contract_status(contract_id: str):
    """
    Get contract processing status.
    
    - **contract_id**: Unique contract identifier
    
    Returns processing state, progress, and error details if any.
    """
    try:
        service = get_contract_service()
        status_data = await service.get_contract_status(contract_id)
        
        if not status_data:
            raise HTTPException(
                status_code=404,
                detail="Contract not found"
            )
        
        return ContractStatusResponse(**status_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting contract status: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@app.get("/contracts/{contract_id}", response_model=ContractDataResponse)
async def get_contract_data(contract_id: str):
    """
    Get extracted contract data.
    
    - **contract_id**: Unique contract identifier
    
    Returns parsed contract data with confidence scores.
    Available only when processing status is "completed".
    """
    try:
        service = get_contract_service()
        contract_data = await service.get_contract_data(contract_id)
        
        if not contract_data:
            # Check if contract exists but not completed
            status_data = await service.get_contract_status(contract_id)
            if not status_data:
                raise HTTPException(
                    status_code=404,
                    detail="Contract not found"
                )
            elif status_data["status"] != "completed":
                raise HTTPException(
                    status_code=400,
                    detail=f"Contract processing not completed. Current status: {status_data['status']}"
                )
            else:
                raise HTTPException(
                    status_code=404,
                    detail="Contract data not found"
                )
        
        return ContractDataResponse(**contract_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting contract data: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@app.get("/contracts", response_model=ContractListResponse)
async def get_contracts_list(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page"),
    status: Optional[str] = Query(None, description="Filter by status (pending, processing, completed, failed)")
):
    """
    Get paginated list of contracts.
    
    - **page**: Page number (starts from 1)
    - **page_size**: Number of contracts per page (1-100)
    - **status**: Optional status filter
    
    Returns paginated list with metadata and confidence scores.
    """
    try:
        service = get_contract_service()
        contracts_data = await service.get_contracts_list(
            page=page,
            page_size=page_size,
            status_filter=status
        )
        
        return ContractListResponse(**contracts_data)
        
    except Exception as e:
        logger.error(f"Error getting contracts list: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@app.get("/contracts/{contract_id}/download")
async def download_contract(contract_id: str):
    """
    Download original PDF contract file.
    
    - **contract_id**: Unique contract identifier
    
    Returns the original PDF file with proper headers.
    """
    try:
        service = get_contract_service()
        file_path = await service.get_contract_file_path(contract_id)
        
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(
                status_code=404,
                detail="Contract file not found"
            )
        
        # Get original filename from database
        status_data = await service.get_contract_status(contract_id)
        if not status_data:
            raise HTTPException(
                status_code=404,
                detail="Contract not found"
            )
        
        filename = status_data.get("filename", "contract.pdf")
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="application/pdf"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading contract: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    return ErrorResponse(
        error=exc.detail,
        detail=str(exc.detail),
        status_code=exc.status_code
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.log_level.lower()
    )
