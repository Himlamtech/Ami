import { useState } from 'react'
import { Save, History, RotateCcw, Play, ChevronDown } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

export default function SettingsPage() {
    const [activeTab, setActiveTab] = useState('prompts')

    return (
        <div className="space-y-6">
            {/* Header */}
            <h2 className="text-2xl font-bold text-neutral-900">Settings</h2>

            {/* Tabs */}
            <Tabs value={activeTab} onValueChange={setActiveTab}>
                <TabsList>
                    <TabsTrigger value="prompts">Prompts</TabsTrigger>
                    <TabsTrigger value="models">Models</TabsTrigger>
                    <TabsTrigger value="general">General</TabsTrigger>
                </TabsList>

                {/* Prompts Tab */}
                <TabsContent value="prompts" className="mt-6 space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle className="text-base">📝 Prompt Templates</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            {/* System Prompt */}
                            <PromptEditor
                                name="System Prompt (Chat)"
                                version={3}
                                isActive={true}
                                lastEdit="2 days ago"
                                defaultValue={`Bạn là AMI - Trợ lý thông minh của Học viện Công nghệ Bưu chính Viễn thông (PTIT).

Quy tắc:
1. Trả lời bằng tiếng Việt, thân thiện
2. Dựa vào thông tin từ nguồn đáng tin cậy
3. Nếu không chắc chắn, thông báo cho user

User context:
- Tên: {user_name}
- Ngành: {user_major}
- Mức độ chi tiết: {detail_level}`}
                                variables={['user_name', 'user_major', 'detail_level', 'context']}
                            />

                            {/* RAG Prompt */}
                            <PromptEditor
                                name="RAG Prompt"
                                version={2}
                                isActive={true}
                                lastEdit="1 week ago"
                                defaultValue={`Dựa vào các tài liệu sau để trả lời câu hỏi của người dùng:

{context}

Câu hỏi: {question}

Hãy trả lời chính xác và trích dẫn nguồn nếu có.`}
                                variables={['context', 'question']}
                                collapsed={true}
                            />

                            {/* Summary Prompt */}
                            <PromptEditor
                                name="Summary Prompt"
                                version={1}
                                isActive={true}
                                lastEdit="2 weeks ago"
                                defaultValue={`Tóm tắt cuộc hội thoại sau thành một tiêu đề ngắn gọn (tối đa 50 ký tự):

{conversation}

Tiêu đề:`}
                                variables={['conversation']}
                                collapsed={true}
                            />
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Models Tab */}
                <TabsContent value="models" className="mt-6 space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle className="text-base">🤖 Model Configuration</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            {/* Chat Model */}
                            <div className="p-4 border rounded-lg">
                                <h4 className="font-medium mb-4">Chat Model</h4>
                                <div className="grid grid-cols-4 gap-4">
                                    <div>
                                        <label className="text-sm font-medium">Provider</label>
                                        <select className="w-full mt-1 border rounded-lg px-3 py-2 text-sm">
                                            <option value="openai">OpenAI</option>
                                            <option value="anthropic">Anthropic</option>
                                            <option value="gemini">Gemini</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label className="text-sm font-medium">Model</label>
                                        <select className="w-full mt-1 border rounded-lg px-3 py-2 text-sm">
                                            <option value="gpt-4o-mini">gpt-4o-mini</option>
                                            <option value="gpt-4o">gpt-4o</option>
                                            <option value="gpt-4-turbo">gpt-4-turbo</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label className="text-sm font-medium">Temperature</label>
                                        <Input type="number" defaultValue={0.7} step={0.1} min={0} max={2} className="mt-1" />
                                    </div>
                                    <div>
                                        <label className="text-sm font-medium">Max Tokens</label>
                                        <Input type="number" defaultValue={2048} className="mt-1" />
                                    </div>
                                </div>
                                <div className="flex gap-2 mt-4">
                                    <Button variant="outline" size="sm">
                                        <Play className="w-4 h-4 mr-1" />
                                        Test Configuration
                                    </Button>
                                    <Button size="sm">
                                        <Save className="w-4 h-4 mr-1" />
                                        Save
                                    </Button>
                                </div>
                            </div>

                            {/* Embedding Model */}
                            <div className="p-4 border rounded-lg">
                                <h4 className="font-medium mb-4">Embedding Model</h4>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="text-sm font-medium">Model</label>
                                        <Input
                                            defaultValue="vietnamese-document-embedding"
                                            className="mt-1"
                                            disabled
                                        />
                                    </div>
                                    <div>
                                        <label className="text-sm font-medium">Dimension</label>
                                        <Input defaultValue={768} className="mt-1" disabled />
                                    </div>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* General Tab */}
                <TabsContent value="general" className="mt-6">
                    <Card>
                        <CardContent className="p-6">
                            <p className="text-neutral-500">General settings coming soon...</p>
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>
        </div>
    )
}

function PromptEditor({
    name,
    version,
    isActive,
    lastEdit,
    defaultValue,
    variables,
    collapsed = false,
}: {
    name: string
    version: number
    isActive: boolean
    lastEdit: string
    defaultValue: string
    variables: string[]
    collapsed?: boolean
}) {
    const [isCollapsed, setIsCollapsed] = useState(collapsed)
    const [value, setValue] = useState(defaultValue)

    return (
        <div className="border rounded-lg">
            <div
                className="flex items-center justify-between p-4 cursor-pointer hover:bg-neutral-50"
                onClick={() => setIsCollapsed(!isCollapsed)}
            >
                <div className="flex items-center gap-3">
                    <h4 className="font-medium">{name}</h4>
                    <span className="text-xs px-2 py-0.5 bg-neutral-100 rounded">v{version}</span>
                    {isActive && (
                        <span className="text-xs px-2 py-0.5 bg-success/10 text-success rounded">Active</span>
                    )}
                </div>
                <ChevronDown
                    className={`w-4 h-4 transition-transform ${isCollapsed ? '' : 'rotate-180'}`}
                />
            </div>

            {!isCollapsed && (
                <div className="p-4 pt-0 space-y-4">
                    <textarea
                        value={value}
                        onChange={(e) => setValue(e.target.value)}
                        className="w-full h-48 p-3 border rounded-lg font-mono text-sm resize-none focus:outline-none focus:ring-2 focus:ring-primary"
                    />

                    <div className="flex items-center gap-2 text-sm text-neutral-500">
                        <span>Variables:</span>
                        {variables.map((v) => (
                            <code key={v} className="px-1.5 py-0.5 bg-neutral-100 rounded text-xs">
                                {`{${v}}`}
                            </code>
                        ))}
                    </div>

                    <div className="flex items-center justify-between">
                        <div className="flex gap-2">
                            <Button variant="outline" size="sm">
                                <History className="w-4 h-4 mr-1" />
                                View History
                            </Button>
                            <Button variant="outline" size="sm">
                                <RotateCcw className="w-4 h-4 mr-1" />
                                Rollback
                            </Button>
                        </div>
                        <div className="flex items-center gap-4">
                            <span className="text-xs text-neutral-500">Last edit: {lastEdit}</span>
                            <Button size="sm">
                                <Save className="w-4 h-4 mr-1" />
                                Save
                            </Button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}
