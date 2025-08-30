"""Database models for MongoDB collections."""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from bson import ObjectId


class ContractModel(BaseModel):
    """Contract document model for MongoDB."""
    
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    filename: str
    file_path: str
    status: str = "pending"  # pending, processing, completed, failed
    progress: int = 0
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    error_message: Optional[str] = None
    file_size: int
    content_hash: str

    class Config:
        populate_by_name = True


class PartyInfo(BaseModel):
    """Party information structure."""
    
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    tax_id: Optional[str] = None
    account_number: Optional[str] = None


class AuthorizedRepresentative(BaseModel):
    """Authorized representative information."""
    
    name: Optional[str] = None
    title: Optional[str] = None


class AuthorizedRepresentatives(BaseModel):
    """Authorized representatives for both parties."""
    
    service_provider: Optional[AuthorizedRepresentative] = None
    customer: Optional[AuthorizedRepresentative] = None


class Parties(BaseModel):
    """Contract parties information."""
    
    service_provider: Optional[PartyInfo] = None
    customer: Optional[PartyInfo] = None
    authorized_representatives: Optional[AuthorizedRepresentatives] = None


class BillingContact(BaseModel):
    """Billing contact information."""
    
    name: Optional[str] = None
    title: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class AccountInfo(BaseModel):
    """Account information structure."""
    
    account_number: Optional[str] = None
    billing_contact: Optional[BillingContact] = None


class LineItem(BaseModel):
    """Financial line item structure."""
    
    service: Optional[str] = None
    quantity: Optional[int] = None
    unit: Optional[str] = None
    unit_price: Optional[float] = None
    monthly_total: Optional[float] = None


class FinancialDetails(BaseModel):
    """Financial details structure."""
    
    line_items: Optional[List[LineItem]] = None
    monthly_costs: Optional[Dict[str, float]] = None
    one_time_costs: Optional[Dict[str, float]] = None
    total_monthly: Optional[float] = None
    total_one_time: Optional[float] = None
    annual_contract_value: Optional[float] = None
    currency: Optional[str] = "USD"


class BankingInfo(BaseModel):
    """Banking information structure."""
    
    bank: Optional[str] = None
    account: Optional[str] = None
    routing: Optional[str] = None


class PaymentStructure(BaseModel):
    """Payment structure information."""
    
    payment_terms: Optional[str] = None
    payment_schedule: Optional[str] = None
    payment_due_date: Optional[str] = None
    payment_method: Optional[str] = None
    late_payment_terms: Optional[str] = None
    late_payment_fee: Optional[float] = None
    banking_info: Optional[BankingInfo] = None


class RevenueClassification(BaseModel):
    """Revenue classification information."""
    
    type: Optional[str] = None  # recurring, one-time, mixed
    contract_term: Optional[str] = None
    billing_cycle: Optional[str] = None
    auto_renewal: Optional[str] = None
    termination_notice: Optional[str] = None
    pricing_adjustments: Optional[str] = None


class ResponseTimes(BaseModel):
    """SLA response times structure."""
    
    critical_issues: Optional[str] = Field(None, alias="Critical issues")
    high_priority: Optional[str] = Field(None, alias="High priority")
    medium_priority: Optional[str] = Field(None, alias="Medium priority")
    low_priority: Optional[str] = Field(None, alias="Low priority")

    class Config:
        populate_by_name = True


class PerformanceMetrics(BaseModel):
    """Performance metrics structure."""
    
    system_response_time: Optional[str] = Field(None, alias="System response time")
    backup_success_rate: Optional[str] = Field(None, alias="Backup success rate")
    security_patch_deployment: Optional[str] = Field(None, alias="Security patch deployment")

    class Config:
        populate_by_name = True


class ServiceCredits(BaseModel):
    """Service credits structure."""
    
    availability_penalty: Optional[str] = None
    response_time_penalty: Optional[str] = None
    maximum_credits: Optional[str] = None


class SLATerms(BaseModel):
    """SLA terms structure."""
    
    uptime_commitment: Optional[str] = None
    response_times: Optional[ResponseTimes] = None
    performance_metrics: Optional[PerformanceMetrics] = None
    service_credits: Optional[ServiceCredits] = None


class GapAnalysis(BaseModel):
    """Gap analysis structure."""
    
    missing_fields: Optional[List[str]] = None
    incomplete_fields: Optional[List[str]] = None
    notes: Optional[str] = None


class ExtractedData(BaseModel):
    """Complete extracted data structure."""
    
    parties: Optional[Parties] = None
    account_info: Optional[AccountInfo] = None
    financial_details: Optional[FinancialDetails] = None
    payment_structure: Optional[PaymentStructure] = None
    revenue_classification: Optional[RevenueClassification] = None
    sla_terms: Optional[SLATerms] = None


class ContractDataModel(BaseModel):
    """Contract data model for extracted information."""
    
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    contract_id: str
    extracted_data: ExtractedData
    confidence_score: float = 0.0
    processing_date: datetime = Field(default_factory=datetime.utcnow)
    gap_analysis: Optional[GapAnalysis] = None

    class Config:
        populate_by_name = True
