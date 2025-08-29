"use client"

import { useEffect, useState } from "react"
import { FileText, Info, Download } from "lucide-react"
import { getContractStatus, getContractData, getDownloadUrl, ContractStatus, ContractData } from '../src/lib/api'

type Props = {
  contractId: string | null
}

export default function ContractDetails({ contractId }: Props) {
  const [status, setStatus] = useState<ContractStatus | null>(null)
  const [data, setData] = useState<ContractData | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (contractId) {
      fetchContractDetails()
      const interval = setInterval(fetchContractDetails, 2000)
      return () => clearInterval(interval)
    }
  }, [contractId])

  const fetchContractDetails = async () => {
    if (!contractId) return

    try {
      setLoading(true)
      const statusResponse = await getContractStatus(contractId)
      setStatus(statusResponse)

      if (statusResponse.status === 'completed') {
        const dataResponse = await getContractData(contractId)
        setData(dataResponse)
      }

      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch contract details')
    } finally {
      setLoading(false)
    }
  }

  const getConfidenceColor = (score: number) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  if (!contractId) {
    return (
      <div className="rounded-lg border border-border bg-card p-6 text-sm text-muted-foreground">
        <div className="flex items-center gap-2">
          <Info className="h-4 w-4 text-sky-400" aria-hidden="true" />
          <p>Select a contract to view extracted details.</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="rounded-md border border-red-200 bg-red-50 p-6">
        <div className="flex items-center gap-2 mb-4">
          <span className="text-red-500">⚠️</span>
          <p className="text-sm text-red-700 font-medium">{error}</p>
        </div>
        <button 
          onClick={fetchContractDetails}
          className="text-sm text-red-600 hover:text-red-800 underline"
        >
          Retry
        </button>
      </div>
    )
  }

  return (
    <section className="space-y-6">
      <header className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="inline-flex h-9 w-9 items-center justify-center rounded-md bg-background ring-1 ring-border">
            <FileText className="h-5 w-5 text-sky-400" aria-hidden="true" />
          </span>
          <div>
            <h3 className="text-lg font-semibold text-foreground">Contract Analysis</h3>
            <p className="text-xs text-muted-foreground">
              {status ? `Status: ${status.status} (${status.progress}%)` : 'Loading...'}
            </p>
          </div>
        </div>
        
        {data && (
          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className="text-xs text-muted-foreground">Confidence Score</p>
              <p className={`text-sm font-bold ${getConfidenceColor(data.confidence_score)}`}>
                {data.confidence_score}%
              </p>
            </div>
            <button
              onClick={() => window.open(getDownloadUrl(contractId), '_blank')}
              className="inline-flex items-center gap-2 rounded-md border border-border bg-background px-3 py-2 text-sm font-medium text-foreground hover:border-muted transition-colors"
            >
              <Download className="h-4 w-4 text-sky-400" aria-hidden="true" />
              Download PDF
            </button>
          </div>
        )}
      </header>

      {status && (
        <div className="rounded-lg border border-border bg-card p-4">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm font-medium text-foreground">Processing Progress</p>
            <p className="text-sm text-muted-foreground">{status.progress}%</p>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${status.progress}%` }}
            ></div>
          </div>
          {status.error_message && (
            <div className="mt-3 rounded-md border border-red-200 bg-red-50 p-3">
              <div className="flex items-center gap-2">
                <span className="text-red-500">❌</span>
                <p className="text-xs text-red-700 font-medium">{status.error_message}</p>
              </div>
            </div>
          )}
        </div>
      )}

      {data && data.extracted_data && (
        <div className="space-y-6">
          {/* Parties Section */}
          {data.extracted_data.parties && (
            <div className="rounded-lg border border-border bg-card p-6">
              <h4 className="text-lg font-semibold mb-4 text-foreground flex items-center gap-2">
                <span>👥</span>
                Contract Parties
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {data.extracted_data.parties.service_provider && (
                  <div className="space-y-3">
                    <h5 className="font-medium text-foreground text-base">Service Provider</h5>
                    <div className="space-y-2 text-sm">
                      <p><span className="font-medium">Name:</span> {data.extracted_data.parties.service_provider.name || 'N/A'}</p>
                      {data.extracted_data.parties.service_provider.email && (
                        <p><span className="font-medium">Email:</span> {data.extracted_data.parties.service_provider.email}</p>
                      )}
                      {data.extracted_data.parties.service_provider.phone && (
                        <p><span className="font-medium">Phone:</span> {data.extracted_data.parties.service_provider.phone}</p>
                      )}
                      {data.extracted_data.parties.service_provider.address && (
                        <p><span className="font-medium">Address:</span> {data.extracted_data.parties.service_provider.address}</p>
                      )}
                      {data.extracted_data.parties.service_provider.tax_id && (
                        <p><span className="font-medium">Tax ID:</span> {data.extracted_data.parties.service_provider.tax_id}</p>
                      )}
                      {data.extracted_data.parties.service_provider.authorized_representatives && data.extracted_data.parties.service_provider.authorized_representatives.length > 0 && (
                        <div>
                          <p className="font-medium">Authorized Representatives:</p>
                          {data.extracted_data.parties.service_provider.authorized_representatives.map((rep, idx) => (
                            <div key={idx} className="ml-2 text-xs text-muted-foreground">
                              <p>{rep.name} - {rep.title}</p>
                              {rep.email && <p>📧 {rep.email}</p>}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                )}
                {data.extracted_data.parties.customer && (
                  <div className="space-y-3">
                    <h5 className="font-medium text-foreground text-base">Customer</h5>
                    <div className="space-y-2 text-sm">
                      <p><span className="font-medium">Name:</span> {data.extracted_data.parties.customer.name || 'N/A'}</p>
                      {data.extracted_data.parties.customer.email && (
                        <p><span className="font-medium">Email:</span> {data.extracted_data.parties.customer.email}</p>
                      )}
                      {data.extracted_data.parties.customer.phone && (
                        <p><span className="font-medium">Phone:</span> {data.extracted_data.parties.customer.phone}</p>
                      )}
                      {data.extracted_data.parties.customer.address && (
                        <p><span className="font-medium">Address:</span> {data.extracted_data.parties.customer.address}</p>
                      )}
                      {data.extracted_data.parties.customer.tax_id && (
                        <p><span className="font-medium">Tax ID:</span> {data.extracted_data.parties.customer.tax_id}</p>
                      )}
                      {data.extracted_data.parties.customer.authorized_representatives && data.extracted_data.parties.customer.authorized_representatives.length > 0 && (
                        <div>
                          <p className="font-medium">Authorized Representatives:</p>
                          {data.extracted_data.parties.customer.authorized_representatives.map((rep, idx) => (
                            <div key={idx} className="ml-2 text-xs text-muted-foreground">
                              <p>{rep.name} - {rep.title}</p>
                              {rep.email && <p>📧 {rep.email}</p>}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Financial Details Section */}
          {data.extracted_data.financial_details && (
            <div className="rounded-lg border border-border bg-card p-6">
              <h4 className="text-lg font-semibold mb-4 text-foreground flex items-center gap-2">
                <span>💰</span>
                Financial Details
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Line Items */}
                {data.extracted_data.financial_details.line_items && data.extracted_data.financial_details.line_items.length > 0 && (
                  <div className="space-y-3">
                    <h5 className="font-medium text-foreground text-base">Line Items</h5>
                    <div className="space-y-2">
                      {data.extracted_data.financial_details.line_items.map((item, idx) => (
                        <div key={idx} className="text-sm border-l-2 border-blue-200 pl-3">
                          <p className="font-medium">{item.description}</p>
                          <p className="text-muted-foreground">Quantity: {item.quantity} × ${item.unit_price} = ${item.total_price}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* Cost Summary */}
                <div className="space-y-3">
                  <h5 className="font-medium text-foreground text-base">Cost Summary</h5>
                  <div className="space-y-2 text-sm">
                    {data.extracted_data.financial_details.monthly_costs && Object.keys(data.extracted_data.financial_details.monthly_costs).length > 0 && (
                      <div>
                        <p className="font-medium">Monthly Costs:</p>
                        {Object.entries(data.extracted_data.financial_details.monthly_costs).map(([key, value]) => (
                          <p key={key} className="ml-2 text-muted-foreground">{key}: ${value}</p>
                        ))}
                      </div>
                    )}
                    {data.extracted_data.financial_details.one_time_costs && Object.keys(data.extracted_data.financial_details.one_time_costs).length > 0 && (
                      <div>
                        <p className="font-medium">One-time Costs:</p>
                        {Object.entries(data.extracted_data.financial_details.one_time_costs).map(([key, value]) => (
                          <p key={key} className="ml-2 text-muted-foreground">{key}: ${value}</p>
                        ))}
                      </div>
                    )}
                    {data.extracted_data.financial_details.total_monthly && (
                      <p><span className="font-medium">Total Monthly:</span> ${data.extracted_data.financial_details.total_monthly}</p>
                    )}
                    {data.extracted_data.financial_details.total_one_time && (
                      <p><span className="font-medium">Total One-time:</span> ${data.extracted_data.financial_details.total_one_time}</p>
                    )}
                    {data.extracted_data.financial_details.total_contract_value && (
                      <p><span className="font-medium">Total Contract Value:</span> ${data.extracted_data.financial_details.total_contract_value}</p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Payment Structure Section */}
          {data.extracted_data.payment_structure && (
            <div className="rounded-lg border border-border bg-card p-6">
              <h4 className="text-lg font-semibold mb-4 text-foreground flex items-center gap-2">
                <span>💳</span>
                Payment Structure
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-3">
                  <h5 className="font-medium text-foreground text-base">Payment Terms</h5>
                  <div className="space-y-2 text-sm">
                    {data.extracted_data.payment_structure.payment_terms && (
                      <p><span className="font-medium">Terms:</span> {data.extracted_data.payment_structure.payment_terms}</p>
                    )}
                    {data.extracted_data.payment_structure.payment_schedule && (
                      <p><span className="font-medium">Schedule:</span> {data.extracted_data.payment_structure.payment_schedule}</p>
                    )}
                    {data.extracted_data.payment_structure.payment_method && (
                      <p><span className="font-medium">Method:</span> {data.extracted_data.payment_structure.payment_method}</p>
                    )}
                    {data.extracted_data.payment_structure.due_date && (
                      <p><span className="font-medium">Due Date:</span> {data.extracted_data.payment_structure.due_date}</p>
                    )}
                    {data.extracted_data.payment_structure.late_payment_fee && (
                      <p><span className="font-medium">Late Payment Fee:</span> {data.extracted_data.payment_structure.late_payment_fee}</p>
                    )}
                    {data.extracted_data.payment_structure.discount_terms && (
                      <p><span className="font-medium">Discount Terms:</span> {data.extracted_data.payment_structure.discount_terms}</p>
                    )}
                  </div>
                </div>
                
                {data.extracted_data.payment_structure.banking_info && (
                  <div className="space-y-3">
                    <h5 className="font-medium text-foreground text-base">Banking Information</h5>
                    <div className="space-y-2 text-sm">
                      {data.extracted_data.payment_structure.banking_info.bank_name && (
                        <p><span className="font-medium">Bank:</span> {data.extracted_data.payment_structure.banking_info.bank_name}</p>
                      )}
                      {data.extracted_data.payment_structure.banking_info.account_number && (
                        <p><span className="font-medium">Account:</span> {data.extracted_data.payment_structure.banking_info.account_number}</p>
                      )}
                      {data.extracted_data.payment_structure.banking_info.routing_number && (
                        <p><span className="font-medium">Routing:</span> {data.extracted_data.payment_structure.banking_info.routing_number}</p>
                      )}
                      {data.extracted_data.payment_structure.banking_info.swift_code && (
                        <p><span className="font-medium">SWIFT:</span> {data.extracted_data.payment_structure.banking_info.swift_code}</p>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Revenue Classification Section */}
          {data.extracted_data.revenue_classification && (
            <div className="rounded-lg border border-border bg-card p-6">
              <h4 className="text-lg font-semibold mb-4 text-foreground flex items-center gap-2">
                <span>📊</span>
                Revenue Classification
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2 text-sm">
                  {data.extracted_data.revenue_classification.type && (
                    <p><span className="font-medium">Type:</span> {data.extracted_data.revenue_classification.type}</p>
                  )}
                  {data.extracted_data.revenue_classification.contract_term && (
                    <p><span className="font-medium">Contract Term:</span> {data.extracted_data.revenue_classification.contract_term}</p>
                  )}
                  {data.extracted_data.revenue_classification.billing_cycle && (
                    <p><span className="font-medium">Billing Cycle:</span> {data.extracted_data.revenue_classification.billing_cycle}</p>
                  )}
                </div>
                <div className="space-y-2 text-sm">
                  {data.extracted_data.revenue_classification.auto_renewal && (
                    <p><span className="font-medium">Auto Renewal:</span> {data.extracted_data.revenue_classification.auto_renewal}</p>
                  )}
                  {data.extracted_data.revenue_classification.termination_notice && (
                    <p><span className="font-medium">Termination Notice:</span> {data.extracted_data.revenue_classification.termination_notice}</p>
                  )}
                  {data.extracted_data.revenue_classification.pricing_adjustments && (
                    <p><span className="font-medium">Pricing Adjustments:</span> {data.extracted_data.revenue_classification.pricing_adjustments}</p>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* SLA Terms Section */}
          {data.extracted_data.sla_terms && (
            <div className="rounded-lg border border-border bg-card p-6">
              <h4 className="text-lg font-semibold mb-4 text-foreground flex items-center gap-2">
                <span>⚡</span>
                SLA Terms
              </h4>
              <div className="space-y-4">
                {data.extracted_data.sla_terms.uptime_commitment && (
                  <div>
                    <p className="font-medium text-sm">Uptime Commitment: {data.extracted_data.sla_terms.uptime_commitment}</p>
                  </div>
                )}
                
                {data.extracted_data.sla_terms.response_times && (
                  <div className="space-y-2">
                    <h5 className="font-medium text-foreground text-base">Response Times</h5>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      {data.extracted_data.sla_terms.response_times.critical && (
                        <div className="bg-red-50 p-2 rounded border">
                          <p className="font-medium text-red-700">Critical</p>
                          <p className="text-red-600">{data.extracted_data.sla_terms.response_times.critical}</p>
                        </div>
                      )}
                      {data.extracted_data.sla_terms.response_times.high && (
                        <div className="bg-orange-50 p-2 rounded border">
                          <p className="font-medium text-orange-700">High</p>
                          <p className="text-orange-600">{data.extracted_data.sla_terms.response_times.high}</p>
                        </div>
                      )}
                      {data.extracted_data.sla_terms.response_times.medium && (
                        <div className="bg-yellow-50 p-2 rounded border">
                          <p className="font-medium text-yellow-700">Medium</p>
                          <p className="text-yellow-600">{data.extracted_data.sla_terms.response_times.medium}</p>
                        </div>
                      )}
                      {data.extracted_data.sla_terms.response_times.low && (
                        <div className="bg-green-50 p-2 rounded border">
                          <p className="font-medium text-green-700">Low</p>
                          <p className="text-green-600">{data.extracted_data.sla_terms.response_times.low}</p>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {data.extracted_data.sla_terms.performance_metrics && (
                  <div className="space-y-2">
                    <h5 className="font-medium text-foreground text-base">Performance Metrics</h5>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                      {Object.entries(data.extracted_data.sla_terms.performance_metrics).map(([key, value]) => (
                        <div key={key} className="bg-blue-50 p-2 rounded border">
                          <p className="font-medium text-blue-700 capitalize">{key.replace('_', ' ')}</p>
                          <p className="text-blue-600">{value}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {data.extracted_data.sla_terms.service_credits && data.extracted_data.sla_terms.service_credits.length > 0 && (
                  <div className="space-y-2">
                    <h5 className="font-medium text-foreground text-base">Service Credits</h5>
                    <div className="space-y-2">
                      {data.extracted_data.sla_terms.service_credits.map((credit, idx) => (
                        <div key={idx} className="bg-gray-50 p-3 rounded border text-sm">
                          <p><span className="font-medium">Threshold:</span> {credit.threshold}</p>
                          <p><span className="font-medium">Credit:</span> {credit.credit_percentage}</p>
                          {credit.description && <p className="text-muted-foreground">{credit.description}</p>}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Gap Analysis Section */}
          {data.extracted_data.gap_analysis && (
            <div className="rounded-lg border border-border bg-card p-6">
              <h4 className="text-lg font-semibold mb-4 text-foreground flex items-center gap-2">
                <span>🔍</span>
                Gap Analysis
              </h4>
              <div className="space-y-4">
                {data.extracted_data.gap_analysis.missing_fields && data.extracted_data.gap_analysis.missing_fields.length > 0 && (
                  <div>
                    <h5 className="font-medium text-foreground text-base mb-2">Missing Fields</h5>
                    <div className="flex flex-wrap gap-2">
                      {data.extracted_data.gap_analysis.missing_fields.map((field, idx) => (
                        <span key={idx} className="bg-red-100 text-red-700 px-2 py-1 rounded text-xs">{field}</span>
                      ))}
                    </div>
                  </div>
                )}
                
                {data.extracted_data.gap_analysis.incomplete_fields && data.extracted_data.gap_analysis.incomplete_fields.length > 0 && (
                  <div>
                    <h5 className="font-medium text-foreground text-base mb-2">Incomplete Fields</h5>
                    <div className="flex flex-wrap gap-2">
                      {data.extracted_data.gap_analysis.incomplete_fields.map((field, idx) => (
                        <span key={idx} className="bg-yellow-100 text-yellow-700 px-2 py-1 rounded text-xs">{field}</span>
                      ))}
                    </div>
                  </div>
                )}

                {data.extracted_data.gap_analysis.notes && data.extracted_data.gap_analysis.notes.length > 0 && (
                  <div>
                    <h5 className="font-medium text-foreground text-base mb-2">Notes</h5>
                    <div className="space-y-1">
                      {data.extracted_data.gap_analysis.notes.map((note, idx) => (
                        <p key={idx} className="text-sm text-muted-foreground">• {note}</p>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Contract Info Section */}
          <div className="rounded-lg border border-border bg-card p-6">
            <h4 className="text-lg font-semibold mb-4 text-foreground flex items-center gap-2">
              <span>📅</span>
              Contract Information
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <p className="font-medium text-foreground">Contract ID:</p>
                <p className="text-muted-foreground font-mono">{contractId}</p>
              </div>
              <div>
                <p className="font-medium text-foreground">Processing Status:</p>
                <p className="text-muted-foreground">{status?.status || 'Unknown'}</p>
              </div>
              {data.extracted_data.account_info && (
                <>
                  {data.extracted_data.account_info.account_number && (
                    <div>
                      <p className="font-medium text-foreground">Account Number:</p>
                      <p className="text-muted-foreground">{data.extracted_data.account_info.account_number}</p>
                    </div>
                  )}
                  {data.extracted_data.account_info.billing_contact && (
                    <div>
                      <p className="font-medium text-foreground">Billing Contact:</p>
                      <div className="text-muted-foreground">
                        {data.extracted_data.account_info.billing_contact.name && (
                          <p>{data.extracted_data.account_info.billing_contact.name}</p>
                        )}
                        {data.extracted_data.account_info.billing_contact.email && (
                          <p>📧 {data.extracted_data.account_info.billing_contact.email}</p>
                        )}
                        {data.extracted_data.account_info.billing_contact.phone && (
                          <p>📞 {data.extracted_data.account_info.billing_contact.phone}</p>
                        )}
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </section>
  )
}
