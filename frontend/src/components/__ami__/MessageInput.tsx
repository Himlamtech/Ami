import { useState, useRef } from 'react'
import { Paperclip, Mic, Send, X } from 'lucide-react'
import '@styles/__ami__/MessageInput.css'

interface MessageInputProps {
    onSendMessage: (message: string, files?: File[]) => void
    disabled: boolean
}

export default function MessageInput({ onSendMessage, disabled }: MessageInputProps) {
    const [message, setMessage] = useState('')
    const [uploadedFiles, setUploadedFiles] = useState<File[]>([])
    const fileInputRef = useRef<HTMLInputElement>(null)
    const textAreaRef = useRef<HTMLTextAreaElement>(null)

    const handleSendMessage = () => {
        if (message.trim() || uploadedFiles.length > 0) {
            onSendMessage(message, uploadedFiles)
            setMessage('')
            setUploadedFiles([])
            if (textAreaRef.current) {
                textAreaRef.current.style.height = 'auto'
            }
        }
    }

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSendMessage()
        }
    }

    const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        setMessage(e.target.value)
        // Auto-resize textarea
        if (textAreaRef.current) {
            textAreaRef.current.style.height = 'auto'
            textAreaRef.current.style.height = Math.min(textAreaRef.current.scrollHeight, 200) + 'px'
        }
    }

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files) {
            const files = Array.from(e.target.files)
            setUploadedFiles((prev) => [...prev, ...files])
        }
    }

    const removeFile = (index: number) => {
        setUploadedFiles((prev) => prev.filter((_, i) => i !== index))
    }

    return (
        <div className="message-input-area">
            {uploadedFiles.length > 0 && (
                <div className="uploaded-files">
                    {uploadedFiles.map((file, index) => (
                        <div key={`${file.name}-${index}`} className="file-item">
                            <Paperclip size={14} className="file-icon" />
                            <span className="file-name">{file.name}</span>
                            <button
                                className="btn-remove"
                                onClick={() => removeFile(index)}
                                type="button"
                            >
                                <X size={14} />
                            </button>
                        </div>
                    ))}
                </div>
            )}

            <div className="message-input-wrapper">
                <textarea
                    ref={textAreaRef}
                    className="message-input"
                    placeholder="Nhập tin nhắn... (Shift+Enter để xuống dòng)"
                    value={message}
                    onChange={handleTextChange}
                    onKeyDown={handleKeyDown}
                    disabled={disabled}
                    rows={1}
                />

                <div className="input-actions">
                    <button
                        className="btn-icon"
                        onClick={() => fileInputRef.current?.click()}
                        disabled={disabled}
                        title="Đính kèm tệp"
                    >
                        <Paperclip size={18} />
                    </button>
                    <input
                        ref={fileInputRef}
                        type="file"
                        multiple
                        onChange={handleFileSelect}
                        style={{ display: 'none' }}
                        accept="image/*,.pdf,.doc,.docx,.txt"
                    />

                    <button
                        className="btn-icon"
                        disabled={disabled}
                        title="Ghi âm"
                    >
                        <Mic size={18} />
                    </button>

                    <button
                        className="btn-send"
                        onClick={handleSendMessage}
                        disabled={disabled || (!message.trim() && uploadedFiles.length === 0)}
                    >
                        <Send size={16} />
                        <span>Gửi</span>
                    </button>
                </div>
            </div>
        </div>
    )
}

// CSS will be imported via global index.css
