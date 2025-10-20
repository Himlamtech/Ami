import { useState, useRef } from 'react'
import { Upload, CheckCircle2, XCircle } from 'lucide-react'
import { apiClient } from '../../api/client'
import { useDataStore } from '../../store/dataStore'

interface FileUploadProps {
    collection: string
    onSuccess: () => void
}

export default function FileUpload({ collection, onSuccess }: FileUploadProps) {
    const [isDragging, setIsDragging] = useState(false)
    const [uploading, setUploading] = useState(false)
    const [uploadResults, setUploadResults] = useState<
        { filename: string; success: boolean; message: string }[]
    >([])
    const fileInputRef = useRef<HTMLInputElement>(null)
    const { addUploadProgress, updateUploadProgress, removeUploadProgress } = useDataStore()

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault()
        setIsDragging(true)
    }

    const handleDragLeave = () => {
        setIsDragging(false)
    }

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault()
        setIsDragging(false)
        const files = Array.from(e.dataTransfer.files)
        handleFiles(files)
    }

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files) {
            const files = Array.from(e.target.files)
            handleFiles(files)
        }
    }

    const handleFiles = async (files: File[]) => {
        if (files.length === 0) return

        setUploading(true)
        const results: { filename: string; success: boolean; message: string }[] = []

        for (const file of files) {
            addUploadProgress({
                filename: file.name,
                progress: 0,
                status: 'uploading',
            })

            try {
                updateUploadProgress(file.name, { progress: 50, status: 'processing' })

                const result = await apiClient.uploadFile(file, collection)

                updateUploadProgress(file.name, { progress: 100, status: 'complete' })

                results.push({
                    filename: file.name,
                    success: true,
                    message: result.message,
                })

                setTimeout(() => removeUploadProgress(file.name), 3000)
            } catch (error) {
                updateUploadProgress(file.name, {
                    status: 'error',
                    error: error instanceof Error ? error.message : 'Upload failed',
                })

                results.push({
                    filename: file.name,
                    success: false,
                    message: error instanceof Error ? error.message : 'Upload failed',
                })

                setTimeout(() => removeUploadProgress(file.name), 5000)
            }
        }

        setUploadResults(results)
        setUploading(false)

        if (results.some((r) => r.success)) {
            onSuccess()
        }

        if (fileInputRef.current) {
            fileInputRef.current.value = ''
        }
    }

    return (
        <div className="file-upload">
            <div className="upload-info">
                <h2>Upload Documents</h2>
                <p>
                    Upload files to your knowledge base. Supported formats: PDF, DOCX, TXT, MD, CSV,
                    and more.
                </p>
            </div>

            <div
                className={`upload-dropzone ${isDragging ? 'dragging' : ''}`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
            >
                <div className="dropzone-content">
                    <Upload size={48} strokeWidth={1.5} />
                    <h3>Drag & Drop Files Here</h3>
                    <p>or click to browse</p>
                    <input
                        ref={fileInputRef}
                        type="file"
                        multiple
                        accept=".pdf,.docx,.doc,.txt,.md,.csv,.json"
                        onChange={handleFileSelect}
                        style={{ display: 'none' }}
                    />
                </div>
            </div>

            {uploading && (
                <div className="upload-status">
                    <div className="loader"></div>
                    <p>Uploading and processing files...</p>
                </div>
            )}

            {uploadResults.length > 0 && (
                <div className="upload-results">
                    <h3>Upload Results</h3>
                    {uploadResults.map((result, index) => (
                        <div
                            key={index}
                            className={`result-item ${result.success ? 'success' : 'error'}`}
                        >
                            {result.success ? (
                                <CheckCircle2 size={20} strokeWidth={2} />
                            ) : (
                                <XCircle size={20} strokeWidth={2} />
                            )}
                            <div className="result-content">
                                <strong>{result.filename}</strong>
                                <p>{result.message}</p>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}

