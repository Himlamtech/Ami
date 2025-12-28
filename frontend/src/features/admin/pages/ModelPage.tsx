import { useState, useEffect } from 'react'
import { Cpu, RefreshCw, Save, Check, AlertCircle } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Slider } from '@/components/ui/slider'
import { useToast } from '@/hooks/useToast'
import { api } from '@/lib/api'

interface LocalModelConfig {
    provider: string
    qaModel: string
    reasoningModel: string
    temperature: number
    maxTokens: number
    topK: number
    similarityThreshold: number
}

interface ProviderStatus {
    name: string
    configured: boolean
    models: string[]
}

interface ModelConfigResponse {
    config: LocalModelConfig
    providers: ProviderStatus[]
    embedding: {
        model: string
        dimension: number
        batchSize: number
        device: string
    }
}

const defaultConfig: LocalModelConfig = {
    provider: 'openai',
    qaModel: 'gpt-4o-mini',
    reasoningModel: 'o4-mini',
    temperature: 0.7,
    maxTokens: 2048,
    topK: 5,
    similarityThreshold: 0.7,
}

const providerModels: Record<string, { qa: string[]; reasoning: string[] }> = {
    openai: {
        qa: ['gpt-4o-mini', 'gpt-4o', 'gpt-4-turbo', 'gpt-3.5-turbo'],
        reasoning: ['o4-mini', 'o3', 'o1', 'o1-mini'],
    },
    anthropic: {
        qa: ['claude-3-5-haiku-20241022', 'claude-3-haiku-20240307'],
        reasoning: ['claude-sonnet-4-20250514', 'claude-3-5-sonnet-20241022', 'claude-3-opus-20240229'],
    },
    gemini: {
        qa: ['gemini-2.5-flash-lite-preview-09-2025', 'gemini-1.5-flash', 'gemini-1.5-pro'],
        reasoning: ['gemini-3-pro-preview', 'gemini-2.0-flash-thinking-exp'],
    },
}

export default function ModelPage() {
    const [config, setConfig] = useState<LocalModelConfig>(defaultConfig)
    const [providers, setProviders] = useState<ProviderStatus[]>([])
    const [loading, setLoading] = useState(true)
    const [saving, setSaving] = useState(false)
    const { toast } = useToast()

    useEffect(() => {
        loadConfig()
    }, [])

    const loadConfig = async () => {
        setLoading(true)
        try {
            const response = await api.get<ModelConfigResponse>('/admin/config/models')
            if (response) {
                setConfig(response.config || defaultConfig)
                setProviders(response.providers || [])
            }
        } catch {
            // Use defaults if API fails
            setProviders([
                { name: 'openai', configured: true, models: providerModels.openai.qa },
                { name: 'anthropic', configured: false, models: providerModels.anthropic.qa },
                { name: 'gemini', configured: true, models: providerModels.gemini.qa },
            ])
        } finally {
            setLoading(false)
        }
    }

    const handleSave = async () => {
        setSaving(true)
        try {
            await api.put('/admin/config/models', config)
            toast({
                title: 'Configuration saved',
                description: 'Model settings have been updated successfully.',
            })
        } catch {
            toast({
                title: 'Error saving',
                description: 'Failed to save model configuration.',
                variant: 'destructive',
            })
        } finally {
            setSaving(false)
        }
    }

    const getProviderStatus = (providerName: string) => {
        const provider = providers.find((p) => p.name === providerName)
        return provider?.configured ?? false
    }

    const currentModels = providerModels[config.provider] || providerModels.openai

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <RefreshCw className="w-6 h-6 animate-spin text-primary" />
            </div>
        )
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-semibold text-neutral-900">Model Configuration</h1>
                    <p className="text-sm text-neutral-500 mt-1">
                        Configure AI models, providers, and RAG parameters
                    </p>
                </div>
                <div className="flex items-center gap-2">
                    <Button variant="outline" onClick={loadConfig}>
                        <RefreshCw className="w-4 h-4 mr-2" />
                        Refresh
                    </Button>
                    <Button onClick={handleSave} disabled={saving}>
                        {saving ? (
                            <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                        ) : (
                            <Save className="w-4 h-4 mr-2" />
                        )}
                        Save Changes
                    </Button>
                </div>
            </div>

            {/* Provider Status */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {['openai', 'anthropic', 'gemini'].map((provider) => (
                    <Card key={provider} className={config.provider === provider ? 'ring-2 ring-primary' : ''}>
                        <CardContent className="p-4">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                                        <Cpu className="w-5 h-5 text-primary" />
                                    </div>
                                    <div>
                                        <p className="font-medium capitalize">{provider}</p>
                                        <p className="text-xs text-neutral-500">
                                            {providerModels[provider].qa.length} models
                                        </p>
                                    </div>
                                </div>
                                <Badge
                                    variant={getProviderStatus(provider) ? 'default' : 'secondary'}
                                    className="gap-1"
                                >
                                    {getProviderStatus(provider) ? (
                                        <>
                                            <Check className="w-3 h-3" />
                                            Active
                                        </>
                                    ) : (
                                        <>
                                            <AlertCircle className="w-3 h-3" />
                                            Not configured
                                        </>
                                    )}
                                </Badge>
                            </div>
                        </CardContent>
                    </Card>
                ))}
            </div>

            <Tabs defaultValue="llm" className="space-y-4">
                <TabsList>
                    <TabsTrigger value="llm">LLM Settings</TabsTrigger>
                    <TabsTrigger value="rag">RAG Parameters</TabsTrigger>
                    <TabsTrigger value="embedding">Embedding</TabsTrigger>
                </TabsList>

                {/* LLM Settings */}
                <TabsContent value="llm" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle>Language Model</CardTitle>
                            <CardDescription>
                                Select the AI provider and models for Q&A and reasoning tasks
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            {/* Provider Selection */}
                            <div className="space-y-2">
                                <Label>Provider</Label>
                                <Select
                                    value={config.provider}
                                    onValueChange={(value) => setConfig({ ...config, provider: value })}
                                >
                                    <SelectTrigger className="w-full max-w-xs">
                                        <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="openai">OpenAI</SelectItem>
                                        <SelectItem value="anthropic">Anthropic (Claude)</SelectItem>
                                        <SelectItem value="gemini">Google Gemini</SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>

                            {/* Model Selection */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div className="space-y-2">
                                    <Label>Q&A Model</Label>
                                    <Select
                                        value={config.qaModel}
                                        onValueChange={(value) => setConfig({ ...config, qaModel: value })}
                                    >
                                        <SelectTrigger>
                                            <SelectValue />
                                        </SelectTrigger>
                                        <SelectContent>
                                            {currentModels.qa.map((model) => (
                                                <SelectItem key={model} value={model}>
                                                    {model}
                                                </SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                    <p className="text-xs text-neutral-500">
                                        Used for general question answering
                                    </p>
                                </div>

                                <div className="space-y-2">
                                    <Label>Reasoning Model</Label>
                                    <Select
                                        value={config.reasoningModel}
                                        onValueChange={(value) => setConfig({ ...config, reasoningModel: value })}
                                    >
                                        <SelectTrigger>
                                            <SelectValue />
                                        </SelectTrigger>
                                        <SelectContent>
                                            {currentModels.reasoning.map((model) => (
                                                <SelectItem key={model} value={model}>
                                                    {model}
                                                </SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                    <p className="text-xs text-neutral-500">
                                        Used for complex reasoning tasks
                                    </p>
                                </div>
                            </div>

                            {/* Temperature */}
                            <div className="space-y-4">
                                <div className="flex items-center justify-between">
                                    <Label>Temperature</Label>
                                    <span className="text-sm text-neutral-500">{config.temperature}</span>
                                </div>
                                <Slider
                                    value={config.temperature}
                                    onValueChange={(value) => setConfig({ ...config, temperature: value })}
                                    min={0}
                                    max={2}
                                    step={0.1}
                                    className="w-full max-w-md"
                                />
                                <p className="text-xs text-neutral-500">
                                    Lower values make output more focused, higher values more creative
                                </p>
                            </div>

                            {/* Max Tokens */}
                            <div className="space-y-2">
                                <Label>Max Tokens</Label>
                                <Input
                                    type="number"
                                    value={config.maxTokens}
                                    onChange={(e) =>
                                        setConfig({ ...config, maxTokens: parseInt(e.target.value) || 2048 })
                                    }
                                    className="w-full max-w-xs"
                                    min={100}
                                    max={128000}
                                />
                                <p className="text-xs text-neutral-500">Maximum response length</p>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* RAG Parameters */}
                <TabsContent value="rag" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle>RAG Configuration</CardTitle>
                            <CardDescription>
                                Configure retrieval-augmented generation parameters
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            {/* Top K */}
                            <div className="space-y-4">
                                <div className="flex items-center justify-between">
                                    <Label>Top K Results</Label>
                                    <span className="text-sm text-neutral-500">{config.topK}</span>
                                </div>
                                <Slider
                                    value={config.topK}
                                    onValueChange={(value) => setConfig({ ...config, topK: value })}
                                    min={1}
                                    max={20}
                                    step={1}
                                    className="w-full max-w-md"
                                />
                                <p className="text-xs text-neutral-500">
                                    Number of similar documents to retrieve for context
                                </p>
                            </div>

                            {/* Similarity Threshold */}
                            <div className="space-y-4">
                                <div className="flex items-center justify-between">
                                    <Label>Similarity Threshold</Label>
                                    <span className="text-sm text-neutral-500">
                                        {(config.similarityThreshold * 100).toFixed(0)}%
                                    </span>
                                </div>
                                <Slider
                                    value={config.similarityThreshold}
                                    onValueChange={(value) =>
                                        setConfig({ ...config, similarityThreshold: value })
                                    }
                                    min={0}
                                    max={1}
                                    step={0.05}
                                    className="w-full max-w-md"
                                />
                                <p className="text-xs text-neutral-500">
                                    Minimum similarity score for retrieved documents
                                </p>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Embedding Settings */}
                <TabsContent value="embedding" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle>Embedding Model</CardTitle>
                            <CardDescription>Configure the embedding model for vector search</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="space-y-2">
                                <Label>Current Model</Label>
                                <div className="p-3 bg-neutral-50 rounded-lg">
                                    <code className="text-sm">dangvantuan/vietnamese-document-embedding</code>
                                </div>
                                <p className="text-xs text-neutral-500">
                                    Optimized for Vietnamese document retrieval (768 dimensions)
                                </p>
                            </div>

                            <div className="grid grid-cols-2 gap-4 mt-4">
                                <div className="p-4 bg-neutral-50 rounded-lg">
                                    <p className="text-sm font-medium text-neutral-700">Dimension</p>
                                    <p className="text-2xl font-semibold text-neutral-900">768</p>
                                </div>
                                <div className="p-4 bg-neutral-50 rounded-lg">
                                    <p className="text-sm font-medium text-neutral-700">Batch Size</p>
                                    <p className="text-2xl font-semibold text-neutral-900">32</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>
        </div>
    )
}
