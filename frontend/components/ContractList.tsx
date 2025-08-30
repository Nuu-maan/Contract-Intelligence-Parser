"use client"

import { useEffect, useState } from "react"
import { FileText } from "lucide-react"
import { getContracts } from '../src/lib/api'

interface Contract {
  contract_id: string;
  filename: string;
  upload_date: string;
  status: 'processing' | 'completed' | 'failed' | 'pending';
  confidence_score?: number;
  // Add other contract properties as needed
}

type Props = {
  onSelectContract?: (contractId: string) => void
  refreshTrigger?: number
}

export default function ContractList({ onSelectContract, refreshTrigger = 0 }: Props) {
  const [contracts, setContracts] = useState<Contract[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchContracts()
  }, [refreshTrigger])

  const fetchContracts = async () => {
    try {
      setLoading(true)
      const response = await getContracts()
      setContracts(response.contracts)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch contracts')
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-yellow-100 text-yellow-800'
      case 'processing': return 'bg-blue-100 text-blue-800'
      case 'completed': return 'bg-green-100 text-green-800'
      case 'failed': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  if (loading) {
    return <p className="text-sm text-muted-foreground">Loading contracts...</p>
  }

  if (error) {
    return (
      <div className="rounded-md border border-red-200 bg-red-50 p-3">
        <div className="flex items-center gap-2">
          <span className="text-red-500">⚠️</span>
          <p className="text-xs text-red-700 font-medium">{error}</p>
        </div>
        <button 
          onClick={fetchContracts}
          className="mt-2 text-xs text-red-600 hover:text-red-800 underline"
        >
          Retry
        </button>
      </div>
    )
  }

  if (!contracts.length) {
    return <p className="text-sm text-muted-foreground">No contracts yet. Upload a PDF to get started.</p>
  }

  return (
    <ul className="divide-y divide-border rounded-md border border-border bg-card">
      {contracts.map((contract) => (
        <li key={contract.contract_id}>
          <button
            type="button"
            onClick={() => onSelectContract?.(contract.contract_id)}
            className="w-full text-left px-4 py-3 hover:bg-background transition-colors flex items-center gap-3"
            aria-label={`Select ${contract.filename}`}
          >
            <span className="inline-flex h-8 w-8 items-center justify-center rounded-md bg-background ring-1 ring-border">
              <FileText className="h-4 w-4 text-sky-400" aria-hidden="true" />
            </span>
            <span className="flex-1">
              <div className="flex items-center justify-between">
                <span className="block text-sm font-medium text-foreground">{contract.filename}</span>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(contract.status)}`}>
                  {contract.status.charAt(0).toUpperCase() + contract.status.slice(1)}
                </span>
              </div>
              <span className="block text-xs text-muted-foreground">
                Added {new Date(contract.upload_date).toLocaleDateString()}
                {contract.confidence_score !== undefined && contract.confidence_score !== null && (
                  <span className="ml-2">• Confidence: {contract.confidence_score}%</span>
                )}
              </span>
            </span>
          </button>
        </li>
      ))}
    </ul>
  )
}
