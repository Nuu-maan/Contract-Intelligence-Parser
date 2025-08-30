const API_BASE_URL = 'http://localhost:8000'

export interface Contract {
  contract_id: string
  filename: string
  upload_date: string
  file_size: number
  status: 'pending' | 'processing' | 'completed' | 'failed'
  confidence_score?: number
}

export interface ContractStatus {
  contract_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number
  error_message?: string
}

export interface ExtractedData {
  parties?: {
    service_provider?: {
      name?: string
      address?: string
      phone?: string
      email?: string
      tax_id?: string
      authorized_representatives?: Array<{
        name: string
        title: string
        email?: string
        phone?: string
      }>
    }
    customer?: {
      name?: string
      address?: string
      phone?: string
      email?: string
      tax_id?: string
      authorized_representatives?: Array<{
        name: string
        title: string
        email?: string
        phone?: string
      }>
    }
  }
  financial_details?: {
    line_items?: Array<{
      description: string
      quantity: number
      unit_price: number
      total_price: number
    }>
    monthly_costs?: Record<string, number>
    one_time_costs?: Record<string, number>
    total_monthly?: number
    total_one_time?: number
    total_contract_value?: number
    currency?: string
  }
  payment_structure?: {
    payment_terms?: string
    payment_schedule?: string
    payment_method?: string
    due_date?: string
    late_payment_fee?: string
    discount_terms?: string
    banking_info?: {
      bank_name?: string
      account_number?: string
      routing_number?: string
      swift_code?: string
    }
  }
  revenue_classification?: {
    type?: string
    contract_term?: string
    billing_cycle?: string
    auto_renewal?: string
    termination_notice?: string
    pricing_adjustments?: string
  }
  sla_terms?: {
    uptime_commitment?: string
    response_times?: {
      critical?: string
      high?: string
      medium?: string
      low?: string
      critical_issues?: string
      high_priority?: string
      medium_priority?: string
      low_priority?: string
    }
    performance_metrics?: Record<string, string>
    service_credits?: Array<{
      threshold: string
      credit_percentage: string
      description?: string
    }>
  }
  account_info?: {
    account_number?: string
    billing_contact?: {
      name?: string
      email?: string
      phone?: string
    }
  }
  gap_analysis?: {
    missing_fields?: string[]
    incomplete_fields?: string[]
    notes?: string[]
  }
}

export interface ContractData {
  contract_id: string
  confidence_score: number
  processing_date: string
  gap_analysis?: {
    missing_fields: string[]
    incomplete_fields: string[]
    notes: string
  }
  extracted_data: ExtractedData
}

export interface ContractsResponse {
  contracts: Contract[]
}

export async function uploadContract(file: File): Promise<{ contract_id: string }> {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${API_BASE_URL}/contracts/upload`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Upload failed')
  }

  return response.json()
}

export async function getContracts(): Promise<ContractsResponse> {
  const response = await fetch(`${API_BASE_URL}/contracts`)

  if (!response.ok) {
    throw new Error('Failed to fetch contracts')
  }

  return response.json()
}

export async function getContractStatus(contractId: string): Promise<ContractStatus> {
  const response = await fetch(`${API_BASE_URL}/contracts/${contractId}/status`)

  if (!response.ok) {
    throw new Error('Failed to fetch contract status')
  }

  return response.json()
}

export async function getContractData(contractId: string): Promise<ContractData> {
  const response = await fetch(`${API_BASE_URL}/contracts/${contractId}`)

  if (!response.ok) {
    throw new Error('Failed to fetch contract data')
  }

  return response.json()
}

export function getDownloadUrl(contractId: string): string {
  return `${API_BASE_URL}/contracts/${contractId}/download`
}
