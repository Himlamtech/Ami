import { useState, useRef, useCallback } from 'react'

interface UseVoiceOptions {
    onResult?: (text: string) => void
    onError?: (error: string) => void
    maxDuration?: number // Max recording duration in seconds
}

interface UseVoiceReturn {
    isRecording: boolean
    isProcessing: boolean
    duration: number
    audioLevel: number
    startRecording: () => Promise<void>
    stopRecording: () => Promise<string | null>
    cancelRecording: () => void
}

export function useVoice({
    onResult,
    onError,
    maxDuration = 60,
}: UseVoiceOptions = {}): UseVoiceReturn {
    const [isRecording, setIsRecording] = useState(false)
    const [isProcessing, setIsProcessing] = useState(false)
    const [duration, setDuration] = useState(0)
    const [audioLevel, setAudioLevel] = useState(0)

    const mediaRecorderRef = useRef<MediaRecorder | null>(null)
    const audioChunksRef = useRef<Blob[]>([])
    const streamRef = useRef<MediaStream | null>(null)
    const analyserRef = useRef<AnalyserNode | null>(null)
    const animationRef = useRef<number | null>(null)
    const durationIntervalRef = useRef<number | null>(null)

    // Analyze audio level for visualization
    const analyzeAudio = useCallback(() => {
        if (!analyserRef.current) return

        const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount)
        analyserRef.current.getByteFrequencyData(dataArray)

        // Calculate average level
        const average = dataArray.reduce((a, b) => a + b, 0) / dataArray.length
        setAudioLevel(average / 255) // Normalize to 0-1

        animationRef.current = requestAnimationFrame(analyzeAudio)
    }, [])

    const startRecording = useCallback(async () => {
        try {
            // Request microphone access
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
            streamRef.current = stream

            // Setup audio analysis
            const audioContext = new AudioContext()
            const source = audioContext.createMediaStreamSource(stream)
            const analyser = audioContext.createAnalyser()
            analyser.fftSize = 256
            source.connect(analyser)
            analyserRef.current = analyser

            // Create media recorder
            const mediaRecorder = new MediaRecorder(stream, {
                mimeType: 'audio/webm;codecs=opus',
            })
            mediaRecorderRef.current = mediaRecorder
            audioChunksRef.current = []

            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunksRef.current.push(event.data)
                }
            }

            mediaRecorder.start(100) // Collect data every 100ms
            setIsRecording(true)
            setDuration(0)

            // Start audio analysis
            analyzeAudio()

            // Start duration counter
            durationIntervalRef.current = window.setInterval(() => {
                setDuration((prev) => {
                    if (prev >= maxDuration) {
                        stopRecording()
                        return prev
                    }
                    return prev + 1
                })
            }, 1000)
        } catch (error) {
            const message = error instanceof Error ? error.message : 'Failed to start recording'
            onError?.(message)
        }
    }, [analyzeAudio, maxDuration, onError])

    const stopRecording = useCallback(async (): Promise<string | null> => {
        if (!mediaRecorderRef.current || !isRecording) return null

        return new Promise((resolve) => {
            mediaRecorderRef.current!.onstop = async () => {
                // Stop all tracks
                streamRef.current?.getTracks().forEach((track) => track.stop())

                // Stop animation
                if (animationRef.current) {
                    cancelAnimationFrame(animationRef.current)
                }

                // Clear duration interval
                if (durationIntervalRef.current) {
                    clearInterval(durationIntervalRef.current)
                }

                setIsRecording(false)
                setAudioLevel(0)

                // Create blob from chunks
                const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' })

                // Process with API
                setIsProcessing(true)
                try {
                    const formData = new FormData()
                    formData.append('audio', audioBlob, 'recording.webm')

                    const response = await fetch('/api/v1/chat/voice', {
                        method: 'POST',
                        body: formData,
                    })

                    if (!response.ok) {
                        throw new Error('Failed to process audio')
                    }

                    const data = await response.json()
                    const transcription = data.text || ''

                    onResult?.(transcription)
                    resolve(transcription)
                } catch (error) {
                    const message = error instanceof Error ? error.message : 'Failed to process audio'
                    onError?.(message)
                    resolve(null)
                } finally {
                    setIsProcessing(false)
                }
            }

            mediaRecorderRef.current!.stop()
        })
    }, [isRecording, onResult, onError])

    const cancelRecording = useCallback(() => {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.stop()
        }

        streamRef.current?.getTracks().forEach((track) => track.stop())

        if (animationRef.current) {
            cancelAnimationFrame(animationRef.current)
        }

        if (durationIntervalRef.current) {
            clearInterval(durationIntervalRef.current)
        }

        setIsRecording(false)
        setIsProcessing(false)
        setDuration(0)
        setAudioLevel(0)
        audioChunksRef.current = []
    }, [isRecording])

    return {
        isRecording,
        isProcessing,
        duration,
        audioLevel,
        startRecording,
        stopRecording,
        cancelRecording,
    }
}
