"use client"

import { useState } from "react"
import { FileText, Upload, ListChecks, Search } from "lucide-react"
import FileUpload from "@/components/FileUpload"
import ContractList from "@/components/ContractList"
import ContractDetails from "@/components/ContractDetails"

export default function Home() {
  const [selectedContractId, setSelectedContractId] = useState<string | null>(null)
  const [refreshTrigger, setRefreshTrigger] = useState(0)

  const handleUploadSuccess = (contractId: string) => {
    setSelectedContractId(contractId)
    setRefreshTrigger((prev) => prev + 1)
  }

  const handleSelectContract = (contractId: string) => {
    setSelectedContractId(contractId)
  }

  return (
    <main className="min-h-screen bg-background text-foreground">
      {/* Header */}
      <header className="border-b border-border">
        <div className="container mx-auto px-6 py-10">
          <div className="flex flex-col items-center text-center gap-4">
            <div className="flex items-center gap-3">
              <div className="inline-flex h-12 w-12 items-center justify-center rounded-lg bg-card ring-1 ring-border">
                <FileText className="h-6 w-6 text-sky-400" aria-hidden="true" />
              </div>
              <h1 className="text-pretty text-3xl md:text-4xl font-bold">Contract Intelligence Parser</h1>
            </div>
            <p className="max-w-3xl text-pretty text-base md:text-lg leading-relaxed text-muted-foreground">
              Upload and analyze PDF contracts with AI-powered extraction. Get instant insights into parties, financial
              terms, and SLA information.
            </p>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="container mx-auto px-6 py-12">
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
          {/* Upload and List column */}
          <section className="xl:col-span-1 space-y-8">
            {/* Upload Card */}
            <div className="rounded-xl bg-card border border-border p-6 shadow-sm transition-colors hover:border-muted">
              <div className="mb-6 flex items-center gap-3">
                <span className="inline-flex h-9 w-9 items-center justify-center rounded-md bg-background ring-1 ring-border">
                  <Upload className="h-5 w-5 text-sky-400" aria-hidden="true" />
                </span>
                <h2 className="text-lg md:text-xl font-semibold">Upload Contract</h2>
              </div>
              <FileUpload onUploadSuccess={handleUploadSuccess} />
            </div>

            {/* Contract List Card */}
            <div className="rounded-xl bg-card border border-border p-6 shadow-sm transition-colors hover:border-muted">
              <div className="mb-6 flex items-center gap-3">
                <span className="inline-flex h-9 w-9 items-center justify-center rounded-md bg-background ring-1 ring-border">
                  <ListChecks className="h-5 w-5 text-sky-400" aria-hidden="true" />
                </span>
                <h2 className="text-lg md:text-xl font-semibold">Your Contracts</h2>
              </div>
              <ContractList onSelectContract={handleSelectContract} refreshTrigger={refreshTrigger} />
            </div>
          </section>

          {/* Analysis */}
          <section className="xl:col-span-2">
            <div className="rounded-xl bg-card border border-border p-6 shadow-sm transition-colors hover:border-muted">
              <div className="mb-6 flex items-center gap-3">
                <span className="inline-flex h-9 w-9 items-center justify-center rounded-md bg-background ring-1 ring-border">
                  <Search className="h-5 w-5 text-sky-400" aria-hidden="true" />
                </span>
                <h2 className="text-lg md:text-xl font-semibold">Contract Analysis</h2>
              </div>
              <ContractDetails contractId={selectedContractId} />
            </div>
          </section>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-border">
        <div className="container mx-auto px-6 py-8">
          <div className="text-center text-sm text-muted-foreground">
            <p>Contract Intelligence Parser — Powered by AI</p>
            <p className="mt-1">Secure, fast, and accurate contract analysis</p>
          </div>
        </div>
      </footer>
    </main>
  )
}
