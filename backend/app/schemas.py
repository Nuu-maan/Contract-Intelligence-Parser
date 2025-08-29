"""Pydantic schemas for API request/response validation."""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class ContractUploadResponse(BaseModel):
    """Response schema for contract upload."""
    
    contract_id: str
    message: str
    filename: str
    file_size: int


class ContractStatusResponse(BaseModel):
    """Response schema for contract processing status."""
    
    contract_id: str
    status: str  # pending, processing, completed, failed
    progress: int  # 0-100
    error_message: Optional[str] = None
    upload_date: datetime


class ContractListItem(BaseModel):
    """Schema for contract list item."""
    
    contract_id: str
    filename: str
    status: str
    upload_date: datetime
    file_size: int
    confidence_score: Optional[float] = None


class ContractListResponse(BaseModel):
    """Response schema for contract list."""
    
    contracts: List[ContractListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class ContractDataResponse(BaseModel):
    """Response schema for contract data."""
    
    contract_id: str
    extracted_data: Dict[str, Any]
    confidence_score: float
    processing_date: datetime
    status: str


class ErrorResponse(BaseModel):
    """Error response schema."""
    
    error: str
    detail: str
    status_code: int


class HealthCheckResponse(BaseModel):
    """Health check response schema."""
    
    status: str
    timestamp: datetime
    database_connected: bool
