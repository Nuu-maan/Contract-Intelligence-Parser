"""Contract service with scoring algorithm and business logic."""

import logging
import hashlib
import os
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
import aiofiles
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models import ContractModel, ContractDataModel, ExtractedData
from app.utils.pdf_parser import pdf_parser
from app.config import settings

logger = logging.getLogger(__name__)


class ContractService:
    """Service class for contract processing and scoring."""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        """Initialize contract service with database connection."""
        self.db = database
        self.contracts_collection = database.contracts
        self.contract_data_collection = database.contract_data
        from app.utils.pdf_parser import PDFParser
        self.pdf_parser = PDFParser()
    
    
    def _generate_file_hash(self, content: bytes) -> str:
        """Generate SHA256 hash of file content."""
        return hashlib.sha256(content).hexdigest()
    
    async def save_uploaded_file(self, filename: str, content: bytes) -> tuple[str, str]:
        """Save uploaded file to disk and return file path and hash."""
        # Generate unique filename
        file_id = str(uuid.uuid4())
        safe_filename = f"{file_id}_{filename}"
        file_path = os.path.join(settings.upload_dir, safe_filename)
        
        # Ensure upload directory exists
        os.makedirs(settings.upload_dir, exist_ok=True)
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        # Generate content hash
        content_hash = self._generate_file_hash(content)
        
        return file_path, content_hash
    
    async def create_contract(self, filename: str, file_path: str, file_size: int, content_hash: str) -> str:
        """Create new contract record in database."""
        contract_id = str(uuid.uuid4())
        
        contract = ContractModel(
            id=contract_id,
            filename=filename,
            file_path=file_path,
            file_size=file_size,
            content_hash=content_hash,
            status="pending",
            progress=0,
            upload_date=datetime.utcnow()
        )
        
        # Insert into database
        result = await self.contracts_collection.insert_one(contract.dict(by_alias=True))
        
        logger.info(f"Created contract record: {contract_id}")
        return contract_id
    
    async def update_contract_status(self, contract_id: str, status: str, progress: int = None, error_message: str = None):
        """Update contract processing status."""
        update_data = {"status": status}
        
        if progress is not None:
            update_data["progress"] = progress
        
        if error_message:
            update_data["error_message"] = error_message
        
        await self.contracts_collection.update_one(
            {"_id": contract_id},
            {"$set": update_data}
        )
        
        logger.info(f"Updated contract {contract_id} status to {status}")
    
    async def process_contract(self, contract_id: str):
        """Process contract and extract data."""
        try:
            # Update status to processing
            await self.update_contract_status(contract_id, "processing", 10)
            
            # Get contract record
            contract = await self.contracts_collection.find_one({"_id": contract_id})
            if not contract:
                raise ValueError(f"Contract {contract_id} not found")
            
            # Read file content
            async with aiofiles.open(contract["file_path"], 'rb') as f:
                file_content = await f.read()
            
            # Update progress
            await self.update_contract_status(contract_id, "processing", 30)
            
            # Parse PDF and extract data
            extracted_data = pdf_parser.parse_contract(file_content)
            
            # Update progress
            await self.update_contract_status(contract_id, "processing", 70)
            
            # Calculate confidence score using PDF parser's method
            confidence_score = self.pdf_parser.calculate_confidence_score(extracted_data)
            
            # Save extracted data
            contract_data = ContractDataModel(
                contract_id=contract_id,
                extracted_data=extracted_data,
                confidence_score=confidence_score,
                processing_date=datetime.utcnow()
            )
            
            await self.contract_data_collection.insert_one(contract_data.dict(by_alias=True))
            
            # Update contract status to completed
            await self.update_contract_status(contract_id, "completed", 100)
            
            logger.info(f"Successfully processed contract {contract_id} with score {confidence_score}")
            
        except Exception as e:
            logger.error(f"Error processing contract {contract_id}: {e}")
            await self.update_contract_status(contract_id, "failed", error_message=str(e))
            raise
    
    async def get_contract_status(self, contract_id: str) -> Optional[Dict[str, Any]]:
        """Get contract processing status."""
        contract = await self.contracts_collection.find_one({"_id": contract_id})
        if not contract:
            return None
        
        return {
            "contract_id": contract_id,
            "status": contract["status"],
            "progress": contract["progress"],
            "error_message": contract.get("error_message"),
            "upload_date": contract["upload_date"]
        }
    
    async def get_contract_data(self, contract_id: str) -> Optional[Dict[str, Any]]:
        """Get extracted contract data."""
        # Check if contract exists and is completed
        contract = await self.contracts_collection.find_one({"_id": contract_id})
        if not contract or contract["status"] != "completed":
            return None
        
        # Get extracted data
        contract_data = await self.contract_data_collection.find_one({"contract_id": contract_id})
        if not contract_data:
            return None
        
        return {
            "contract_id": contract_id,
            "extracted_data": contract_data["extracted_data"],
            "confidence_score": contract_data["confidence_score"],
            "processing_date": contract_data["processing_date"],
            "status": contract["status"]
        }
    
    async def get_contracts_list(self, page: int = 1, page_size: int = 20, status_filter: str = None) -> Dict[str, Any]:
        """Get paginated list of contracts."""
        skip = (page - 1) * page_size
        
        # Build query filter
        query = {}
        if status_filter:
            query["status"] = status_filter
        
        # Get total count
        total = await self.contracts_collection.count_documents(query)
        
        # Get contracts with pagination
        cursor = self.contracts_collection.find(query).sort("upload_date", -1).skip(skip).limit(page_size)
        contracts = await cursor.to_list(length=page_size)
        
        # Get confidence scores for completed contracts
        contract_list = []
        for contract in contracts:
            contract_item = {
                "contract_id": contract["_id"],
                "filename": contract["filename"],
                "status": contract["status"],
                "upload_date": contract["upload_date"],
                "file_size": contract["file_size"],
                "confidence_score": None
            }
            
            # Add confidence score if available
            if contract["status"] == "completed":
                contract_data = await self.contract_data_collection.find_one({"contract_id": contract["_id"]})
                if contract_data:
                    contract_item["confidence_score"] = contract_data["confidence_score"]
            
            contract_list.append(contract_item)
        
        total_pages = (total + page_size - 1) // page_size
        
        return {
            "contracts": contract_list,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    
    async def get_contract_file_path(self, contract_id: str) -> Optional[str]:
        """Get contract file path for download."""
        contract = await self.contracts_collection.find_one({"_id": contract_id})
        if not contract:
            return None
        
        return contract["file_path"]
