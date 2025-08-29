"use client"

import { useEffect, useMemo, useState } from "react"
import { FileText } from "lucide-react"

type ContractItem = { id: string; name: string; createdAt: string }

type Props = {
  onSelectContract?: (contractId: string) => void
  refreshTrigger?: number
}

export default function ContractList({ onSelectContract, refreshTrigger = 0 }: Props) {
  const initial = useMemo<ContractItem[]>(
    () => [
      { id: "c-001", name: "Master Services Agreement.pdf", createdAt: "2024-06-01" },
      { id: "c-002", name: "NDA - Vendor.pdf", createdAt: "2024-07-15" },
      { id: "c-003", name: "SaaS Subscription.pdf", createdAt: "2024-08-03" },
    ],
    [],
  )

  const [items, setItems] = useState<ContractItem[]>(initial)

  useEffect(() => {
    if (!refreshTrigger) return
    // Add a synthetic "new upload" so UI feels live
    const id = `upload-${refreshTrigger}`
    setItems((prev) => [
      { id, name: `Uploaded Contract #${refreshTrigger}.pdf`, createdAt: new Date().toISOString().slice(0, 10) },
      ...prev,
    ])
  }, [refreshTrigger])

  if (!items.length) {
    return <p className="text-sm text-muted-foreground">No contracts yet. Upload a PDF to get started.</p>
  }

  return (
    <ul className="divide-y divide-border rounded-md border border-border bg-card">
      {items.map((c) => (
        <li key={c.id}>
          <button
            type="button"
            onClick={() => onSelectContract?.(c.id)}
            className="w-full text-left px-4 py-3 hover:bg-background transition-colors flex items-center gap-3"
            aria-label={`Select ${c.name}`}
          >
            <span className="inline-flex h-8 w-8 items-center justify-center rounded-md bg-background ring-1 ring-border">
              <FileText className="h-4 w-4 text-sky-400" aria-hidden="true" />
            </span>
            <span className="flex-1">
              <span className="block text-sm font-medium text-foreground">{c.name}</span>
              <span className="block text-xs text-muted-foreground">Added {c.createdAt}</span>
            </span>
          </button>
        </li>
      ))}
    </ul>
  )
}
