import { useState, useRef } from 'react'
import { Paperclip, Mic, Send, X, Square } from 'lucide-react'
import { apiClient } from '../../api/client'
import '@styles/__ami__/MessageInput.css'

interface MessageInputProps {
    onSendMessage: (message: string, files?: File[]) => void
    disabled: boolean
    isStreaming?: boolean
    onStopGeneration?: () => void
}

export default function MessageInput({ onSendMessage, disabled, isStreaming = false, onStopGeneration }: MessageInputProps) {
    const [message, setMessage] = useState('')
    const [uploadedFiles, setUploadedFiles] = useState<File[]>([])
    const [isRecording, setIsRecording] = useState(false)
    const [isTranscribing, setIsTranscribing] = useState(false)

    const fileInputRef = useRef<HTMLInputElement>(null)
    const textAreaRef = useRef<HTMLTextAreaElement>(null)
    const mediaRecorderRef = useRef<MediaRecorder | null>(null)
    const audioChunksRef = useRef<Blob[]>([])

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

    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
            const mediaRecorder = new MediaRecorder(stream)
            mediaRecorderRef.current = mediaRecorder
            audioChunksRef.current = []

            mediaRecorder.ondataavailable = (event) => {
                audioChunksRef.current.push(event.data)
            }

            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' })
                const audioFile = new File([audioBlob], 'recording.wav', { type: 'audio/wav' })

                setIsTranscribing(true)
                try {
                    const result = await apiClient.transcribeAudio(audioFile)
                    setMessage((prev) => (prev ? prev + ' ' + result.text : result.text))

                    // Auto-resize after adding text
                    setTimeout(() => {
                        if (textAreaRef.current) {
                            textAreaRef.current.style.height = 'auto'
                            textAreaRef.current.style.height = Math.min(textAreaRef.current.scrollHeight, 200) + 'px'
                        }
                    }, 0)
                } catch (error) {
                    console.error('Transcription failed:', error)
                    alert('Failed to transcribe audio')
                } finally {
                    setIsTranscribing(false)
                    stream.getTracks().forEach(track => track.stop())
                }
            }

            mediaRecorder.start()
            setIsRecording(true)
        } catch (error) {
            console.error('Error accessing microphone:', error)
            alert('Could not access microphone')
        }
    }

    const stopRecording = () => {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.stop()
            setIsRecording(false)
        }
    }

    const toggleRecording = () => {
        if (isRecording) {
            stopRecording()
        } else {
            startRecording()
        }
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

            <div className={`message-input-wrapper ${isRecording ? 'recording' : ''}`}>
                <textarea
                    ref={textAreaRef}
                    className="message-input"
                    placeholder={isRecording ? "Đang ghi âm..." : isTranscribing ? "Đang chuyển văn bản..." : "Nhập tin nhắn... (Shift+Enter để xuống dòng)"}
                    value={message}
                    onChange={handleTextChange}
                    onKeyDown={handleKeyDown}
                    disabled={disabled || isRecording || isTranscribing}
                    rows={1}
                />

                <div className="input-actions">
                    <button
                        className="btn-icon"
                        onClick={() => fileInputRef.current?.click()}
                        disabled={disabled || isRecording || isTranscribing}
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
                        className={`btn-icon ${isRecording ? 'recording-active' : ''}`}
                        onClick={toggleRecording}
                        disabled={disabled || isTranscribing}
                        title={isRecording ? "Dừng ghi âm" : "Ghi âm"}
                    >
                        {isRecording ? <Square size={18} fill="currentColor" /> : <Mic size={18} />}
                    </button>


                    {isStreaming ? (
                        <button
                            className="btn-stop"
                            onClick={onStopGeneration}
                            title="Dừng tạo phản hồi"
                        >
                            <Square size={16} fill="currentColor" />
                            <span>Dừng</span>
                        </button>
                    ) : (
                        <button
                            className="btn-send"
                            onClick={handleSendMessage}
                            disabled={disabled || (!message.trim() && uploadedFiles.length === 0) || isRecording || isTranscribing}
                        >
                            <Send size={16} />
                            <span>Gửi</span>
                        </button>
                    )}
                </div>
            </div>
        </div>
    )
}

// CSS will be imported via global index.css
