import { useState, useRef, KeyboardEvent, useEffect } from 'react'
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
import ModelSelector from './ModelSelector'
import type { Attachment, ThinkingMode } from '@/types/chat'

interface ChatInputProps {
    onSend: (message: string, attachments?: Attachment[], mode?: ThinkingMode) => Promise<boolean | void>
    isLoading?: boolean
    onStop?: () => void
    defaultMode?: ThinkingMode
    mode?: ThinkingMode
    onModeChange?: (value: ThinkingMode) => void
}

export default function ChatInput({
    onSend,
    isLoading,
    onStop,
    defaultMode = 'fast',
    mode,
    onModeChange,
}: ChatInputProps) {
    const [message, setMessage] = useState('')
    const [attachments, setAttachments] = useState<Attachment[]>([])
    const [internalMode, setInternalMode] = useState<ThinkingMode>(defaultMode)
    const textareaRef = useRef<HTMLTextAreaElement>(null)
    const fileInputRef = useRef<HTMLInputElement>(null)
    const currentMode = mode ?? internalMode
    const setCurrentMode = onModeChange ?? setInternalMode

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

    const handleSend = async () => {
        if (message.trim() || attachments.length > 0) {
            const result = await onSend(message.trim(), attachments, currentMode)
            if (result !== false) {
                setMessage('')
                setAttachments([])
            }
        }
    }

    const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            void handleSend()
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

    const resizeTextarea = () => {
        const el = textareaRef.current
        if (!el) return
        el.style.height = 'auto'
        const maxHeight = 6 * 20 // 6 lines * lineHeight
        el.style.height = `${Math.min(el.scrollHeight, maxHeight)}px`
    }

    useEffect(() => {
        resizeTextarea()
    }, [message])

    return (
        <div className="sticky bottom-0 bg-transparent px-4 py-4">
            <div className="max-w-[760px] mx-auto">
                {/* Attachments preview */}
                {attachments.length > 0 && (
                    <div className="flex gap-3 mb-3 flex-wrap">
                        {attachments.map((attachment, index) => (
                            <div
                                key={index}
                                className={cn(
                                    'relative overflow-hidden rounded-xl border border-[color:var(--border)] bg-[var(--surface2)] shadow-sm group',
                                    attachment.type === 'image' ? 'w-32 h-32' : 'px-3 py-2 flex items-center gap-2'
                                )}
                            >
                                {attachment.type === 'image' ? (
                                    <>
                                        <img
                                            src={attachment.url}
                                            alt={attachment.name}
                                            className="w-full h-full object-cover"
                                        />
                                        <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/50 to-transparent p-2">
                                            <p className="text-xs text-white truncate" title={attachment.name}>
                                                {attachment.name}
                                            </p>
                                        </div>
                                    </>
                                ) : (
                                    <>
                                        <FileText className="w-5 h-5 text-blue-500 flex-shrink-0" />
                                        <span className="text-sm text-neutral-700 max-w-[180px] truncate" title={attachment.name}>
                                            {attachment.name}
                                        </span>
                                    </>
                                )}
                                <button
                                    onClick={() => removeAttachment(index)}
                                    className={cn(
                                        'absolute top-1.5 right-1.5 p-0.5 rounded bg-white/80 hover:bg-white shadow-sm',
                                        'opacity-0 group-hover:opacity-100 transition-opacity'
                                    )}
                                >
                                    <X className="w-3.5 h-3.5 text-neutral-600" />
                                </button>
                            </div>
                        ))}
                    </div>
                )}

                {/* Recording state */}
                {isRecording || isProcessing ? (
                    <div className="flex items-center gap-3 p-4 bg-[var(--surface)] rounded-2xl shadow-md">
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
                    <div className="flex items-end gap-2 bg-[var(--surface)] rounded-[20px] px-2 py-2 border border-[color:var(--border)] focus-within:ring-2 focus-within:ring-[var(--ring)] transition-all shadow-md">
                        {/* Model selector - Left side */}
                        <ModelSelector value={currentMode} onChange={setCurrentMode} className="flex-shrink-0" />

                        {/* Attachment button */}
                        <Button
                            variant="ghost"
                            size="icon"
                            className="flex-shrink-0 h-9 w-9 rounded-lg hover:bg-[var(--surface2)]"
                            onClick={() => fileInputRef.current?.click()}
                        >
                            <Paperclip className="w-4 h-4 text-neutral-400" />
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
                        <div className="flex-1 flex items-center">
                            <textarea
                                ref={textareaRef}
                                value={message}
                                onChange={(e) => {
                                    setMessage(e.target.value)
                                    resizeTextarea()
                                }}
                                onKeyDown={handleKeyDown}
                                placeholder="Hỏi AMI bất cứ điều gì..."
                                rows={1}
                                disabled={isLoading}
                                className={cn(
                                    'w-full resize-none bg-transparent',
                                    'focus:outline-none',
                                    'placeholder:text-neutral-400 text-sm leading-5',
                                    'max-h-32 overflow-y-auto',
                                    isLoading && 'opacity-50'
                                )}
                                style={{ minHeight: '36px', lineHeight: '20px', paddingTop: '8px', paddingBottom: '8px' }}
                            />
                        </div>

                        {/* Voice button */}
                        <Button
                            variant="ghost"
                            size="icon"
                            className="flex-shrink-0 h-9 w-9 rounded-lg hover:bg-[var(--surface2)]"
                            onClick={handleVoiceToggle}
                            disabled={isLoading}
                        >
                            <Mic className="w-4 h-4 text-neutral-400" />
                        </Button>

                        {/* Send/Stop button */}
                        {isLoading ? (
                            <Button size="icon" variant="secondary" onClick={onStop} className="h-9 w-9 rounded-lg">
                                <Square className="w-3.5 h-3.5" />
                            </Button>
                        ) : (
                            <Button
                                size="icon"
                                onClick={handleSend}
                                disabled={!message.trim() && attachments.length === 0}
                                className="h-9 w-9 rounded-full bg-primary hover:bg-primary/90 disabled:opacity-30 shadow-sm"
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
