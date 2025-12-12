import { useState, useRef, KeyboardEvent } from 'react'
import {
    Send,
    Paperclip,
    Mic,
    Image,
    FileText,
    X,
    Square,
    Check,
    Loader2,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { useVoice } from '@/features/chat/hooks/useVoice'
import ModelSelector, { type ThinkingMode } from './ModelSelector'
import type { Attachment } from '@/types/chat'

interface ChatInputProps {
    onSend: (message: string, attachments?: Attachment[], mode?: ThinkingMode) => void
    isLoading?: boolean
    onStop?: () => void
    defaultMode?: ThinkingMode
}

export default function ChatInput({ onSend, isLoading, onStop, defaultMode = 'balance' }: ChatInputProps) {
    const [message, setMessage] = useState('')
    const [attachments, setAttachments] = useState<Attachment[]>([])
    const [mode, setMode] = useState<ThinkingMode>(defaultMode)
    const textareaRef = useRef<HTMLTextAreaElement>(null)
    const fileInputRef = useRef<HTMLInputElement>(null)

    const { isRecording, isProcessing, duration, audioLevel, startRecording, stopRecording, cancelRecording } = useVoice({
        onResult: (text) => {
            if (text.trim()) {
                setMessage((prev) => prev + (prev ? ' ' : '') + text)
            }
        },
        onError: (error) => {
            console.error('Voice recording error:', error)
        },
    })

    const handleSend = () => {
        if (message.trim() || attachments.length > 0) {
            onSend(message.trim(), attachments, mode)
            setMessage('')
            setAttachments([])
        }
    }

    const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSend()
        }
    }

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files
        if (files) {
            const newAttachments: Attachment[] = Array.from(files).map((file) => ({
                type: file.type.startsWith('image/') ? 'image' : 'document',
                name: file.name,
                url: URL.createObjectURL(file),
                size: file.size,
            }))
            setAttachments([...attachments, ...newAttachments])
        }
        // Reset input
        e.target.value = ''
    }

    const removeAttachment = (index: number) => {
        setAttachments(attachments.filter((_, i) => i !== index))
    }

    const handleVoiceToggle = async () => {
        if (isRecording) {
            await stopRecording()
        } else {
            await startRecording()
        }
    }

    const formatDuration = (seconds: number) => {
        const mins = Math.floor(seconds / 60)
        const secs = seconds % 60
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
    }

    return (
        <div className="border-t border-neutral-200/50 bg-white/80 backdrop-blur-lg p-4">
            {/* Model selector - Top left */}
            <div className="max-w-3xl mx-auto">
                <div className="flex items-center mb-3">
                    <ModelSelector value={mode} onChange={setMode} />
                </div>

                {/* Attachments preview */}
                {attachments.length > 0 && (
                    <div className="flex gap-2 mb-3 flex-wrap">
                        {attachments.map((attachment, index) => (
                            <div
                                key={index}
                                className="relative flex items-center gap-2 px-3 py-2 bg-neutral-100 rounded-lg group"
                            >
                                {attachment.type === 'image' ? (
                                    <Image className="w-4 h-4 text-primary" />
                                ) : (
                                    <FileText className="w-4 h-4 text-blue-500" />
                                )}
                                <span className="text-sm text-neutral-700 max-w-[150px] truncate">
                                    {attachment.name}
                                </span>
                                <button
                                    onClick={() => removeAttachment(index)}
                                    className="p-0.5 hover:bg-neutral-200 rounded opacity-0 group-hover:opacity-100 transition-opacity"
                                >
                                    <X className="w-3 h-3 text-neutral-500" />
                                </button>
                            </div>
                        ))}
                    </div>
                )}

                {/* Recording state */}
                {isRecording || isProcessing ? (
                    <div className="flex items-center gap-3 p-4 bg-gradient-to-r from-primary/5 to-primary/10 rounded-2xl border border-primary/20 shadow-sm">
                        <div className="flex items-center gap-2 flex-1">
                            {isProcessing ? (
                                <Loader2 className="w-5 h-5 text-primary animate-spin" />
                            ) : (
                                <span className="w-3 h-3 bg-primary rounded-full animate-pulse" />
                            )}
                            <span className="text-sm font-medium text-neutral-700">
                                {isProcessing ? 'Đang xử lý...' : `Đang ghi âm ${formatDuration(duration)}`}
                            </span>
                            {/* Waveform visualization */}
                            <div className="flex-1 flex items-center justify-center gap-0.5 h-8">
                                {Array.from({ length: 24 }, (_, i) => (
                                    <div
                                        key={i}
                                        className="w-1 bg-primary/60 rounded-full transition-all duration-100"
                                        style={{
                                            height: `${Math.max(4, audioLevel * 100 * Math.sin((i + Date.now() / 100) * 0.3) ** 2)}%`,
                                        }}
                                    />
                                ))}
                            </div>
                        </div>
                        <Button variant="ghost" size="icon" onClick={cancelRecording} disabled={isProcessing} className="hover:bg-red-100 hover:text-red-600">
                            <X className="w-4 h-4" />
                        </Button>
                        <Button size="icon" onClick={() => stopRecording()} disabled={isProcessing} className="bg-primary hover:bg-primary-600">
                            <Check className="w-4 h-4" />
                        </Button>
                    </div>
                ) : (
                    /* Normal input state */
                    <div className="flex items-end gap-3 bg-neutral-50 rounded-2xl p-2 border border-neutral-200 focus-within:border-primary focus-within:ring-2 focus-within:ring-primary/20 transition-all">
                        {/* Attachment button */}
                        <Button
                            variant="ghost"
                            size="icon"
                            className="flex-shrink-0 h-10 w-10 rounded-xl hover:bg-neutral-200"
                            onClick={() => fileInputRef.current?.click()}
                        >
                            <Paperclip className="w-5 h-5 text-neutral-500" />
                        </Button>
                        <input
                            ref={fileInputRef}
                            type="file"
                            multiple
                            accept="image/*,.pdf,.doc,.docx"
                            className="hidden"
                            onChange={handleFileSelect}
                        />

                        {/* Text input */}
                        <div className="flex-1 relative">
                            <textarea
                                ref={textareaRef}
                                value={message}
                                onChange={(e) => setMessage(e.target.value)}
                                onKeyDown={handleKeyDown}
                                placeholder="Hỏi AMI bất cứ điều gì..."
                                rows={1}
                                disabled={isLoading}
                                className={cn(
                                    'w-full resize-none bg-transparent px-2 py-2.5',
                                    'focus:outline-none',
                                    'placeholder:text-neutral-400 text-sm',
                                    'max-h-32 overflow-y-auto',
                                    isLoading && 'opacity-50'
                                )}
                                style={{ minHeight: '40px' }}
                            />
                        </div>

                        {/* Voice button */}
                        <Button
                            variant="ghost"
                            size="icon"
                            className="flex-shrink-0 h-10 w-10 rounded-xl hover:bg-neutral-200"
                            onClick={handleVoiceToggle}
                            disabled={isLoading}
                        >
                            <Mic className="w-5 h-5 text-neutral-500" />
                        </Button>

                        {/* Send/Stop button */}
                        {isLoading ? (
                            <Button size="icon" variant="secondary" onClick={onStop} className="h-10 w-10 rounded-xl">
                                <Square className="w-4 h-4" />
                            </Button>
                        ) : (
                            <Button
                                size="icon"
                                onClick={handleSend}
                                disabled={!message.trim() && attachments.length === 0}
                                className="h-10 w-10 rounded-xl bg-primary hover:bg-primary-600 disabled:opacity-30"
                            >
                                <Send className="w-4 h-4" />
                            </Button>
                        )}
                    </div>
                )}
            </div>
        </div>
    )
}
