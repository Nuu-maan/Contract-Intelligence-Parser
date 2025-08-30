"""PDF parsing utilities with regex-based data extraction."""

import re
import logging
import io
from typing import Dict, Any, Optional, List
import PyPDF2
from io import BytesIO
from app.models import ExtractedData, Parties, PartyInfo, AuthorizedRepresentative, AuthorizedRepresentatives
from app.models import AccountInfo, BillingContact, FinancialDetails, PaymentStructure, LineItem
from app.models import BankingInfo, RevenueClassification, SLATerms, ResponseTimes, PerformanceMetrics, ServiceCredits, GapAnalysis

logger = logging.getLogger(__name__)


class PDFParser:
    """PDF contract parser with regex-based data extraction."""
    
    def __init__(self):
        """Initialize PDF parser with regex patterns."""
        self.patterns = self._initialize_patterns()
    
    def _initialize_patterns(self) -> Dict[str, Any]:
        """Initialize regex patterns for data extraction."""
        return {
            'company_name': re.compile(r'([A-Za-z\s&]+(?:LLC|Inc|Corp|Corporation|Ltd|Limited|Company|Co\.|Partners))', re.IGNORECASE),
            'consultant_company': re.compile(r'(?:\*\*Consultant:\*\*|Consultant:)\s*\n?([A-Za-z\s&]+(?:LLC|Inc|Corp|Corporation|Ltd|Limited|Company|Co\.|Partners))', re.IGNORECASE),
            'client_company': re.compile(r'(?:\*\*Client:\*\*|Client:)\s*\n?([A-Za-z\s&]+(?:LLC|Inc|Corp|Corporation|Ltd|Limited|Company|Co\.|Partners))', re.IGNORECASE),
            'service_provider': re.compile(r'(?:\*\*Service Provider:\*\*|Service Provider:)\s*\n?([A-Za-z\s&]+(?:LLC|Inc|Corp|Corporation|Ltd|Limited|Company|Co\.|Partners))', re.IGNORECASE),
            'email': re.compile(r'Email:\s*([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})', re.IGNORECASE),
            'phone': re.compile(r'Phone:\s*(\([0-9]{3}\)\s*[0-9]{3}-[0-9]{4})', re.IGNORECASE),
            'address': re.compile(r'(\d+\s+[A-Za-z0-9\s,.-]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd|Way|Place|Pl)[\s,]*[A-Za-z\s,]*\d{5})', re.IGNORECASE),
            'tax_id': re.compile(r'(?:Tax ID|EIN|Federal EIN):\s*(\d{2}-\d{7})', re.IGNORECASE),
            'currency_amount': re.compile(r'\$([0-9,]+\.?[0-9]*)', re.IGNORECASE),
            'monthly_amount': re.compile(r'Monthly[^$]*\$([0-9,]+\.?[0-9]*)', re.IGNORECASE),
            'annual_amount': re.compile(r'Annual[^$]*\$([0-9,]+\.?[0-9]*)', re.IGNORECASE),
            'hourly_rate': re.compile(r'Rate:\s*\$([0-9,]+\.?[0-9]*)/hour', re.IGNORECASE),
            'fixed_fee': re.compile(r'Fixed fee:\s*\$([0-9,]+\.?[0-9]*)', re.IGNORECASE),
            'payment_terms': re.compile(r'Net\s+(\d+)\s+days?', re.IGNORECASE),
            'contract_term': re.compile(r'(?:Term|Duration|Contract Period):\s*(\d+)\s*months?', re.IGNORECASE),
            'auto_renewal': re.compile(r'(?:Automatic|Auto[- ]?renewal):\s*(\d+)[- ]?month', re.IGNORECASE),
            'uptime': re.compile(r'(\d+\.?\d*%)\s*(?:uptime|availability)', re.IGNORECASE),
            'response_time': re.compile(r'(\d+)\s*hours?\s*(?:response|within)', re.IGNORECASE),
            'account_number': re.compile(r'(?:Account ID|Client Account|Agreement ID):\s*([A-Z0-9-]+)', re.IGNORECASE),
            'contract_number': re.compile(r'(?:Contract Number|Agreement ID):\s*([A-Z0-9-]+)', re.IGNORECASE),
            'payment_method': re.compile(r'(?:Payment Method|Payment Options?):\s*([^.\n]+)', re.IGNORECASE)
        }
    
    async def extract_text_from_pdf(self, file_content: bytes) -> str:
        """Extract text content from PDF file."""
        try:
            pdf_file = BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")
    
    def _extract_parties(self, text: str) -> Parties:
        """Extract party information from contract text."""
        parties = Parties()
        
        # Extract all contact information first
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        phones = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
        addresses = re.findall(r'\d+\s+[A-Za-z0-9\s,.-]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd|Way|Place|Pl)[\s,]*[A-Za-z\s,]*\d{5}', text, re.IGNORECASE)
        tax_ids = re.findall(r'(?:Tax ID|EIN|Federal EIN):\s*(\d{2}-\d{7})', text, re.IGNORECASE)
        
        # Find all company names using multiple patterns
        company_matches = self.patterns['company_name'].findall(text)
        
        # Additional broad patterns for company detection with better boundaries
        broad_company_pattern = re.compile(r'(?:^|\n|\.\s+)([A-Z][A-Za-z\s&,.-]{3,35}(?:LLC|Inc|Corp|Corporation|Ltd|Limited|Company|Co\.|Partners))(?:\s|$|\n|\.)', re.IGNORECASE | re.MULTILINE)
        broad_matches = broad_company_pattern.findall(text)
        
        # Clean up company names - remove newlines and extra spaces
        def clean_company_name(name):
            cleaned = re.sub(r'\s+', ' ', name.replace('\n', ' ')).strip()
            # Remove common prefixes/suffixes that aren't part of company names
            cleaned = re.sub(r'^(?:Service Provider|liability|limited to|between|with|and)\s+', '', cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r'\s+(?:liability|limited to|shall|will|may).*$', '', cleaned, flags=re.IGNORECASE)
            return cleaned.strip()
        
        # Combine and clean all company matches
        all_companies = [clean_company_name(name) for name in list(set(company_matches + broad_matches))]
        
        # Filter out invalid company names
        valid_companies = []
        for company in all_companies:
            # Skip if it contains job titles, legal terms, or is too short
            invalid_terms = ['vp of', 'vice president', 'manager', 'director', 'ceo', 'cfo', 'president of', 
                           'liability', 'shall', 'will', 'may', 'service provider', 'customer', 'client']
            
            if (len(company) >= 5 and 
                not any(term in company.lower() for term in invalid_terms) and
                not company.lower().startswith(('the ', 'this ', 'such ', 'any '))):
                valid_companies.append(company)
        
        # Try specific patterns first
        consultant_match = self.patterns['consultant_company'].search(text)
        service_provider_match = self.patterns['service_provider'].search(text)
        client_match = self.patterns['client_company'].search(text)
        
        # Log for debugging
        logger.info(f"Found valid companies: {valid_companies}")
        logger.info(f"Consultant match: {consultant_match.group(1) if consultant_match else None}")
        logger.info(f"Client match: {client_match.group(1) if client_match else None}")
        
        # Service Provider extraction
        service_provider_name = None
        if consultant_match:
            service_provider_name = clean_company_name(consultant_match.group(1))
        elif service_provider_match:
            service_provider_name = clean_company_name(service_provider_match.group(1))
        elif valid_companies:
            service_provider_name = valid_companies[0]
        
        if service_provider_name:
            # Find associated contact info by proximity or domain matching
            provider_email = None
            provider_phone = None
            provider_address = None
            provider_tax_id = None
            
            if emails:
                provider_email = emails[0]
            if phones:
                provider_phone = phones[0]
            if addresses:
                # Clean up address - remove newlines and extra spaces
                provider_address = re.sub(r'\s+', ' ', addresses[0].replace('\n', ' ')).strip()
            if tax_ids:
                provider_tax_id = tax_ids[0]
            
            parties.service_provider = PartyInfo(
                name=service_provider_name,
                email=provider_email,
                phone=provider_phone,
                address=provider_address,
                tax_id=provider_tax_id
            )
        
        # Customer extraction - look for different company from service provider
        customer_name = None
        if client_match:
            customer_name = clean_company_name(client_match.group(1))
        elif len(valid_companies) > 1:
            # Find a different company from the service provider
            for company in valid_companies:
                if company != service_provider_name:
                    customer_name = company
                    break
        
        # If no different company found, look for patterns indicating customer
        if not customer_name:
            customer_patterns = [
                re.compile(r'(?:Client|Customer|Purchaser):\s*([A-Z][A-Za-z\s&,.-]{3,35}(?:LLC|Inc|Corp|Corporation|Ltd|Limited|Company|Co\.|Partners))', re.IGNORECASE),
                re.compile(r'(?:Agreement between|Contract between)\s+[^,]+,\s*and\s+([A-Z][A-Za-z\s&,.-]{3,35}(?:LLC|Inc|Corp|Corporation|Ltd|Limited|Company|Co\.|Partners))', re.IGNORECASE),
                re.compile(r'(?:with|for)\s+([A-Z][A-Za-z\s&,.-]{3,35}(?:LLC|Inc|Corp|Corporation|Ltd|Limited|Company|Co\.|Partners))(?:\s|$|\n|\.)', re.IGNORECASE)
            ]
            
            for pattern in customer_patterns:
                match = pattern.search(text)
                if match:
                    potential_customer = clean_company_name(match.group(1))
                    if (potential_customer != service_provider_name and 
                        len(potential_customer) >= 5 and
                        not any(term in potential_customer.lower() for term in ['service provider', 'liability', 'shall', 'will'])):
                        customer_name = potential_customer
                        break
        
        if customer_name:
            # Find associated contact info
            customer_email = None
            customer_phone = None
            customer_address = None
            customer_tax_id = None
            
            if len(emails) > 1:
                customer_email = emails[1]
            if len(phones) > 1:
                customer_phone = phones[1]
            if len(addresses) > 1:
                # Clean up address - remove newlines and extra spaces
                customer_address = re.sub(r'\s+', ' ', addresses[1].replace('\n', ' ')).strip()
            if len(tax_ids) > 1:
                customer_tax_id = tax_ids[1]
            
            parties.customer = PartyInfo(
                name=customer_name,
                email=customer_email,
                phone=customer_phone,
                address=customer_address,
                tax_id=customer_tax_id
            )
        
        return parties
    
    def _extract_financial_details(self, text: str) -> FinancialDetails:
        """Extract financial information from contract text."""
        financial = FinancialDetails()
        
        # Extract all currency amounts
        currency_amounts = self.patterns['currency_amount'].findall(text)
        amounts = [float(amount.replace(',', '')) for amount in currency_amounts]
        
        # Extract specific amounts from the contract
        monthly_amounts = self.patterns['monthly_amount'].findall(text)
        annual_amounts = self.patterns['annual_amount'].findall(text)
        hourly_rates = self.patterns['hourly_rate'].findall(text)
        fixed_fees = self.patterns['fixed_fee'].findall(text)
        
        # Extract line items using dynamic patterns
        line_items = []
        
        # Pattern to match service descriptions with rates
        service_rate_pattern = re.compile(r'([A-Za-z\s]+(?:Consulting|Assessment|Training|Support|Service|Management))[\s\-:]*\$([0-9,]+\.?[0-9]*)/?(hour|fixed|month)?', re.IGNORECASE)
        service_matches = service_rate_pattern.findall(text)
        
        for service, rate, unit in service_matches:
            service_name = re.sub(r'\s+', ' ', service.replace('\n', ' ')).strip()
            unit_price = float(rate.replace(',', ''))
            unit_type = unit.lower() if unit else "hour"
            
            line_items.append(LineItem(
                service=service_name,
                unit_price=unit_price,
                unit=unit_type,
                quantity=1,
                monthly_total=unit_price if unit_type == "fixed" else None
            ))
        
        # Pattern for hourly rates with quantities
        hourly_pattern = re.compile(r'([A-Za-z\s]+):\s*([0-9]+)\s*hours?\s*\(\$([0-9,]+\.?[0-9]*)\)', re.IGNORECASE)
        hourly_matches = hourly_pattern.findall(text)
        
        for service, hours, total in hourly_matches:
            line_items.append(LineItem(
                service=re.sub(r'\s+', ' ', service.replace('\n', ' ')).strip(),
                unit_price=float(total.replace(',', '')) / int(hours) if int(hours) > 0 else 0,
                unit="hour",
                quantity=int(hours),
                monthly_total=float(total.replace(',', ''))
            ))
        
        financial.line_items = line_items if line_items else None
        
        # Extract monthly costs using dynamic patterns
        monthly_costs = {}
        monthly_pattern = re.compile(r'(?:Monthly|Per Month)[\s\w]*Total[\s:]*\$([0-9,]+\.?[0-9]*)', re.IGNORECASE)
        monthly_matches = monthly_pattern.findall(text)
        
        if monthly_matches:
            monthly_costs["Monthly Total"] = float(monthly_matches[0].replace(',', ''))
        
        # Extract one-time costs using dynamic patterns  
        one_time_costs = {}
        setup_pattern = re.compile(r'(?:Setup|Initial|Project)[\s\w]*Fee[\s:]*\$([0-9,]+\.?[0-9]*)', re.IGNORECASE)
        setup_matches = setup_pattern.findall(text)
        
        if setup_matches:
            one_time_costs["Setup Fee"] = float(setup_matches[0].replace(',', ''))
        
        # Look for fixed fee services
        for item in line_items:
            if item.unit == "fixed":
                one_time_costs[item.service] = item.unit_price
        
        financial.monthly_costs = monthly_costs if monthly_costs else None
        financial.one_time_costs = one_time_costs if one_time_costs else None
        
        # Calculate totals
        financial.total_monthly = sum(monthly_costs.values()) if monthly_costs else 0
        financial.total_one_time = sum(one_time_costs.values()) if one_time_costs else 0
        
        # Extract annual contract value using dynamic patterns
        annual_pattern = re.compile(r'(?:Annual|Yearly)[\s\w]*(?:Value|Total|Amount)[\s:]*\$([0-9,]+\.?[0-9]*)', re.IGNORECASE)
        annual_matches = annual_pattern.findall(text)
        
        if annual_matches:
            financial.annual_contract_value = float(annual_matches[0].replace(',', ''))
        elif financial.total_monthly > 0:
            # Calculate based on contract term
            term_matches = self.patterns['contract_term'].findall(text)
            contract_months = int(term_matches[0]) if term_matches else 12
            financial.annual_contract_value = financial.total_monthly * contract_months
        
        financial.currency = "USD"
        
        return financial
    
    def _extract_payment_structure(self, text: str) -> PaymentStructure:
        """Extract payment structure information."""
        payment = PaymentStructure()
        
        # Extract payment terms
        payment_terms_matches = self.patterns['payment_terms'].findall(text)
        if payment_terms_matches:
            payment.payment_terms = f"Net {payment_terms_matches[0]} days"
        else:
            # Look for other payment term patterns
            alt_terms_pattern = re.compile(r'(?:payment|due)[\s\w]*(\d+)[\s]*(?:days?|months?)', re.IGNORECASE)
            alt_matches = alt_terms_pattern.findall(text)
            if alt_matches:
                payment.payment_terms = f"Net {alt_matches[0]} days"
        
        # Extract payment method
        payment_method_matches = self.patterns['payment_method'].findall(text)
        if payment_method_matches:
            payment.payment_method = payment_method_matches[0].strip()
        
        # Extract payment schedule
        schedule_pattern = re.compile(r'(?:billed|invoiced|charged)[\s\w]*(?:monthly|quarterly|annually|yearly)', re.IGNORECASE)
        schedule_matches = schedule_pattern.findall(text)
        if schedule_matches:
            payment.payment_schedule = schedule_matches[0]
        else:
            # Default based on common patterns
            if re.search(r'monthly|per month', text, re.IGNORECASE):
                payment.payment_schedule = "Monthly recurring billing"
            elif re.search(r'quarterly|per quarter', text, re.IGNORECASE):
                payment.payment_schedule = "Quarterly billing"
            elif re.search(r'annually|yearly|per year', text, re.IGNORECASE):
                payment.payment_schedule = "Annual billing"
        
        # Extract late payment terms
        late_fee_pattern = re.compile(r'(?:late fee|penalty|interest)[\s\w]*([0-9.]+%)', re.IGNORECASE)
        late_fee_matches = late_fee_pattern.findall(text)
        if late_fee_matches:
            payment.late_payment_fee = f"{late_fee_matches[0]} per month on overdue amounts"
        
        # Extract discount terms
        discount_pattern = re.compile(r'(?:discount|early payment)[\s\w]*([0-9.]+%)', re.IGNORECASE)
        discount_matches = discount_pattern.findall(text)
        if discount_matches:
            payment.discount_terms = f"{discount_matches[0]} discount for early payment"
        
        # Extract banking information
        bank_name_pattern = re.compile(r'(?:bank|financial institution)[\s:]*([A-Za-z\s&]+)', re.IGNORECASE)
        account_pattern = re.compile(r'(?:account|acct)[\s#:]*([A-Za-z0-9-]+)', re.IGNORECASE)
        routing_pattern = re.compile(r'(?:routing|aba)[\s#:]*([0-9]{9})', re.IGNORECASE)
        swift_pattern = re.compile(r'(?:swift|bic)[\s:]*([A-Z0-9]{8,11})', re.IGNORECASE)
        
        bank_matches = bank_name_pattern.findall(text)
        account_matches = account_pattern.findall(text)
        routing_matches = routing_pattern.findall(text)
        swift_matches = swift_pattern.findall(text)
        
        if bank_matches or account_matches or routing_matches:
            payment.banking_info = BankingInfo(
                bank_name=bank_matches[0].strip() if bank_matches else None,
                account_number=account_matches[0] if account_matches else None,
                routing_number=routing_matches[0] if routing_matches else None,
                swift_code=swift_matches[0] if swift_matches else None
            )
        
        return payment
    
    def _extract_account_info(self, text: str) -> AccountInfo:
        """Extract account information."""
        account = AccountInfo()
        
        # Extract account number
        account_matches = self.patterns['account_number'].findall(text)
        if account_matches:
            account.account_number = account_matches[0]
        
        # Extract billing contact information
        emails = self.patterns['email'].findall(text)
        phone_pattern = re.compile(r'(?:billing|accounting|finance)[\s\w]*(?:phone|tel)[\s:]*(\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4})', re.IGNORECASE)
        billing_phones = phone_pattern.findall(text)
        
        # Extract billing contact name
        contact_pattern = re.compile(r'(?:billing contact|accounts receivable|finance contact)[\s:]*([A-Za-z\s]+)', re.IGNORECASE)
        contact_matches = contact_pattern.findall(text)
        
        if emails or billing_phones or contact_matches:
            account.billing_contact = BillingContact(
                name=contact_matches[0].strip() if contact_matches else None,
                email=emails[0] if emails else None,
                phone=billing_phones[0] if billing_phones else None
            )
        
        return account
    
    def _extract_revenue_classification(self, text: str) -> RevenueClassification:
        """Extract revenue classification information."""
        revenue = RevenueClassification()
        
        # Extract contract term
        term_matches = self.patterns['contract_term'].findall(text)
        if term_matches:
            revenue.contract_term = f"{term_matches[0]} months"
        
        # Extract auto-renewal terms
        renewal_matches = self.patterns['auto_renewal'].findall(text)
        if renewal_matches:
            revenue.auto_renewal = f"{renewal_matches[0]}-month terms"
        
        # Determine revenue type based on keywords
        if re.search(r'recurring|subscription|monthly|quarterly|annual', text, re.IGNORECASE):
            revenue.type = "recurring"
        elif re.search(r'one.?time|single payment|lump sum', text, re.IGNORECASE):
            revenue.type = "one-time"
        else:
            revenue.type = "mixed"
        
        # Extract billing cycle
        if re.search(r'monthly|per month', text, re.IGNORECASE):
            revenue.billing_cycle = "monthly"
        elif re.search(r'quarterly|per quarter', text, re.IGNORECASE):
            revenue.billing_cycle = "quarterly"
        elif re.search(r'annually|yearly|per year', text, re.IGNORECASE):
            revenue.billing_cycle = "annual"
        
        # Extract termination notice
        termination_pattern = re.compile(r'(?:termination|cancellation)[\s\w]*([0-9]+)[\s]*(?:days?|months?)', re.IGNORECASE)
        termination_matches = termination_pattern.findall(text)
        if termination_matches:
            revenue.termination_notice = f"{termination_matches[0]} days written notice"
        
        # Extract pricing adjustments
        pricing_pattern = re.compile(r'(?:price increase|adjustment)[\s\w]*([0-9.]+%)', re.IGNORECASE)
        pricing_matches = pricing_pattern.findall(text)
        if pricing_matches:
            revenue.pricing_adjustments = f"Limited to {pricing_matches[0]} annually"
        
        return revenue
    
    def _extract_sla_terms(self, text: str) -> SLATerms:
        """Extract SLA terms and performance metrics."""
        sla = SLATerms()
        
        # Extract uptime commitment
        uptime_matches = self.patterns['uptime'].findall(text)
        if uptime_matches:
            sla.uptime_commitment = f"{uptime_matches[0]} uptime guarantee"
        
        # Extract response times
        response_time_matches = self.patterns['response_time'].findall(text)
        critical_pattern = re.compile(r'(?:critical|emergency)[\s\w]*([0-9]+)[\s]*(?:hours?|minutes?)', re.IGNORECASE)
        high_pattern = re.compile(r'(?:high priority|urgent)[\s\w]*([0-9]+)[\s]*(?:hours?|minutes?)', re.IGNORECASE)
        medium_pattern = re.compile(r'(?:medium|normal)[\s\w]*([0-9]+)[\s]*(?:hours?|minutes?)', re.IGNORECASE)
        low_pattern = re.compile(r'(?:low priority|routine)[\s\w]*([0-9]+)[\s]*(?:hours?|days?)', re.IGNORECASE)
        
        critical_matches = critical_pattern.findall(text)
        high_matches = high_pattern.findall(text)
        medium_matches = medium_pattern.findall(text)
        low_matches = low_pattern.findall(text)
        
        sla.response_times = ResponseTimes(
            critical=f"{critical_matches[0]} hours" if critical_matches else "1 hour",
            high=f"{high_matches[0]} hours" if high_matches else "4 hours",
            medium=f"{medium_matches[0]} hours" if medium_matches else "8 hours",
            low=f"{low_matches[0]} hours" if low_matches else "24 hours"
        )
        
        # Extract performance metrics
        performance_metrics = {}
        response_time_pattern = re.compile(r'(?:system response|response time)[\s\w]*([0-9.]+)[\s]*(?:seconds?|ms)', re.IGNORECASE)
        backup_pattern = re.compile(r'(?:backup success|backup rate)[\s\w]*([0-9.]+%)', re.IGNORECASE)
        
        response_perf = response_time_pattern.findall(text)
        backup_perf = backup_pattern.findall(text)
        
        if response_perf:
            performance_metrics["system_response_time"] = f"< {response_perf[0]} seconds"
        if backup_perf:
            performance_metrics["backup_success_rate"] = backup_perf[0]
        
        sla.performance_metrics = PerformanceMetrics(**performance_metrics) if performance_metrics else None
        
        # Extract service credits
        service_credits = []
        credit_pattern = re.compile(r'(?:service credit|penalty)[\s\w]*([0-9.]+%)[\s\w]*(?:below|under)[\s]*([0-9.]+%)', re.IGNORECASE)
        credit_matches = credit_pattern.findall(text)
        
        for credit_percent, threshold in credit_matches:
            service_credits.append(ServiceCredits(
                threshold=f"< {threshold} uptime",
                credit_percentage=f"{credit_percent} monthly fee credit",
                description=f"Service credit for uptime below {threshold}"
            ))
        
        sla.service_credits = service_credits if service_credits else []
        
        return sla
    
    def _analyze_gaps(self, parties: Parties, financial_details: FinancialDetails, payment_structure: PaymentStructure, sla_terms: SLATerms) -> GapAnalysis:
        """Analyze gaps in contract terms."""
        missing_fields = []
        incomplete_fields = []
        notes = []
        
        # Check parties completeness
        if not parties.service_provider or not parties.service_provider.name:
            missing_fields.append("service_provider_name")
        if not parties.customer or not parties.customer.name:
            missing_fields.append("customer_name")
        
        if parties.service_provider and not parties.service_provider.email:
            incomplete_fields.append("service_provider_contact")
        if parties.customer and not parties.customer.email:
            incomplete_fields.append("customer_contact")
        
        # Check financial details
        if not financial_details.annual_contract_value:
            missing_fields.append("annual_contract_value")
        if not financial_details.monthly_costs and not financial_details.one_time_costs:
            missing_fields.append("cost_breakdown")
        
        # Check payment structure
        if not payment_structure.payment_terms:
            missing_fields.append("payment_terms")
        if not payment_structure.payment_method:
            incomplete_fields.append("payment_method")
        
        # Check SLA terms
        if not sla_terms.uptime_commitment:
            missing_fields.append("uptime_commitment")
        if not sla_terms.response_times:
            missing_fields.append("response_times")
        
        # Add analysis notes
        if missing_fields:
            notes.append(f"Contract is missing {len(missing_fields)} critical fields")
        if incomplete_fields:
            notes.append(f"Contract has {len(incomplete_fields)} incomplete sections")
        
        if not missing_fields and not incomplete_fields:
            notes.append("Contract appears to be comprehensive with all major sections present")
        
        return GapAnalysis(
            missing_fields=missing_fields,
            incomplete_fields=incomplete_fields,
            notes="; ".join(notes) if notes else None
        )
    
    def _extract_text_from_pdf(self, pdf_content: bytes) -> str:
        """Extract text from PDF bytes."""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
            text = ""
            
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")
    
    def calculate_confidence_score(self, extracted_data: ExtractedData) -> int:
        """Calculate confidence score based on data completeness (0-100)."""
        score = 0
        
        # Financial completeness: 30 points
        if extracted_data.financial_details:
            if extracted_data.financial_details.annual_contract_value:
                score += 10
            if extracted_data.financial_details.monthly_costs or extracted_data.financial_details.one_time_costs:
                score += 10
            if extracted_data.financial_details.line_items:
                score += 10
        
        # Party identification: 25 points
        if extracted_data.parties:
            if extracted_data.parties.service_provider and extracted_data.parties.service_provider.name:
                score += 10
            if extracted_data.parties.customer and extracted_data.parties.customer.name:
                score += 10
            if (extracted_data.parties.service_provider and extracted_data.parties.service_provider.email) or \
               (extracted_data.parties.customer and extracted_data.parties.customer.email):
                score += 5
        
        # Payment terms clarity: 20 points
        if extracted_data.payment_structure:
            if extracted_data.payment_structure.payment_terms:
                score += 10
            if extracted_data.payment_structure.payment_method:
                score += 5
            if extracted_data.payment_structure.payment_schedule:
                score += 5
        
        # SLA definition: 15 points
        if extracted_data.sla_terms:
            if extracted_data.sla_terms.uptime_commitment:
                score += 5
            if extracted_data.sla_terms.response_times:
                score += 5
            if extracted_data.sla_terms.performance_metrics:
                score += 5
        
        # Contact information: 10 points
        if extracted_data.account_info and extracted_data.account_info.billing_contact:
            if extracted_data.account_info.billing_contact.email:
                score += 5
            if extracted_data.account_info.billing_contact.phone:
                score += 5
        
        return min(score, 100)  # Cap at 100
    
    def parse_contract(self, pdf_content: bytes) -> ExtractedData:
        """Parse contract PDF and extract structured data."""
        try:
            # Extract text from PDF
            text = self._extract_text_from_pdf(pdf_content)
            logger.info(f"Extracted text length: {len(text)} characters")
            
            # Parse different sections
            parties = self._extract_parties(text)
            financial_details = self._extract_financial_details(text)
            payment_structure = self._extract_payment_structure(text)
            account_info = self._extract_account_info(text)
            revenue_classification = self._extract_revenue_classification(text)
            sla_terms = self._extract_sla_terms(text)
            
            # Perform gap analysis
            gap_analysis = self._analyze_gaps(parties, financial_details, payment_structure, sla_terms)
            
            return ExtractedData(
                parties=parties,
                financial_details=financial_details,
                payment_structure=payment_structure,
                account_info=account_info,
                revenue_classification=revenue_classification,
                sla_terms=sla_terms,
                gap_analysis=gap_analysis
            )
            
        except Exception as e:
            logger.error(f"Error parsing contract: {str(e)}")
            raise ValueError(f"Failed to parse contract: {str(e)}")


# Global parser instance
pdf_parser = PDFParser()