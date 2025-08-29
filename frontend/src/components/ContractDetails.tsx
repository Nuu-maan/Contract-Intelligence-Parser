"use client"

import { FileText, Info } from "lucide-react"

type Props = {
  contractId: string | null
}

export default function ContractDetails({ contractId }: Props) {
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

  // Placeholder details layout
  return (
    <section className="space-y-6">
      <header className="flex items-center gap-3">
        <span className="inline-flex h-9 w-9 items-center justify-center rounded-md bg-background ring-1 ring-border">
          <FileText className="h-5 w-5 text-sky-400" aria-hidden="true" />
        </span>
        <div>
          <h3 className="text-lg font-semibold text-foreground">Contract #{contractId}</h3>
          <p className="text-xs text-muted-foreground">AI-extracted summary</p>
        </div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="rounded-lg border border-border bg-card p-4">
          <h4 className="text-sm font-medium mb-2 text-foreground">Parties</h4>
          <ul className="text-sm text-muted-foreground list-disc pl-5 space-y-1">
            <li>Acme Corp</li>
            <li>Globex LLC</li>
          </ul>
        </div>

        <div className="rounded-lg border border-border bg-card p-4">
          <h4 className="text-sm font-medium mb-2 text-foreground">Financial Terms</h4>
          <ul className="text-sm text-muted-foreground list-disc pl-5 space-y-1">
            <li>Total: $120,000</li>
            <li>Billing: Net 30</li>
          </ul>
        </div>

        <div className="rounded-lg border border-border bg-card p-4">
          <h4 className="text-sm font-medium mb-2 text-foreground">SLA</h4>
          <ul className="text-sm text-muted-foreground list-disc pl-5 space-y-1">
            <li>Uptime: 99.9%</li>
            <li>Response: 24 hours</li>
          </ul>
        </div>

        <div className="rounded-lg border border-border bg-card p-4">
          <h4 className="text-sm font-medium mb-2 text-foreground">Dates</h4>
          <ul className="text-sm text-muted-foreground list-disc pl-5 space-y-1">
            <li>Effective: 2024-08-01</li>
            <li>Term: 12 months</li>
          </ul>
        </div>
      </div>
    </section>
  )
}
