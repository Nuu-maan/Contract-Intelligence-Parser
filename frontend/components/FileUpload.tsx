"use client"

import type React from "react"

import { useRef, useState } from "react"
import { Upload } from "lucide-react"
import { uploadContract } from '../src/lib/api'

type Props = {
  onUploadSuccess?: (contractId: string) => void
}

export default function FileUpload({ onUploadSuccess }: Props) {
  const inputRef = useRef<HTMLInputElement | null>(null)
  const [selectedName, setSelectedName] = useState<string | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const pickFile = () => inputRef.current?.click()

  const onChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    if (!file.type.includes('pdf')) {
      setError('Please select a PDF file')
      return
    }

    if (file.size > 50 * 1024 * 1024) {
      setError('File size must be less than 50MB')
      return
    }

    setSelectedName(file.name)
    setIsUploading(true)
    setError(null)

    try {
      const response = await uploadContract(file)
      onUploadSuccess?.(response.contract_id)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed')
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className="space-y-3">
      <input
        ref={inputRef}
        type="file"
        accept="application/pdf"
        className="sr-only"
        onChange={onChange}
        aria-label="Upload contract PDF"
      />
      <button
        type="button"
        onClick={pickFile}
        className="inline-flex items-center gap-2 rounded-md border border-border bg-background px-3 py-2 text-sm font-medium text-foreground hover:border-muted transition-colors"
        aria-busy={isUploading}
      >
        <Upload className="h-4 w-4 text-sky-400" aria-hidden="true" />
        {isUploading ? "Uploading…" : "Choose PDF"}
      </button>
      <div className="text-xs text-muted-foreground">
        {selectedName ? `Selected: ${selectedName}` : "PDF only. Max 50MB."}
      </div>
      
      {error && (
        <div className="rounded-md border border-red-200 bg-red-50 p-3">
          <div className="flex items-center gap-2">
            <span className="text-red-500">⚠️</span>
            <p className="text-xs text-red-700 font-medium">{error}</p>
          </div>
        </div>
      )}
    </div>
  )
}
