import { Zap, Scale, Brain, X } from 'lucide-react'
import { useChatStore } from '../../store/chatStore'
import '@styles/__ami__/SettingsPanel.css'

interface SettingsPanelProps {
    onClose: () => void
}

export default function SettingsPanel({ onClose }: SettingsPanelProps) {
    const { config, updateConfig } = useChatStore()

    return (
        <>
            <div className="settings-overlay" onClick={onClose} />
            <div className="settings-panel">
                <div className="settings-header">
                    <h2>Chat Settings</h2>
                    <button className="btn-close" onClick={onClose}>
                        <X size={20} />
                    </button>
                </div>

                <div className="settings-content">
                    {/* Thinking Mode */}
                    <div className="settings-group">
                        <label className="settings-label">
                            <span>Thinking Mode</span>
                            <span className="help-text">Choose how the AI processes your questions</span>
                        </label>
                        <div className="settings-options">
                            <label className="option-radio">
                                <input
                                    type="radio"
                                    name="thinking_mode"
                                    value="fast"
                                    checked={config.thinkingMode === 'fast'}
                                    onChange={(e) => updateConfig({ thinkingMode: e.target.value as any })}
                                />
                                <Zap size={16} />
                                <span>Fast</span>
                            </label>
                            <label className="option-radio">
                                <input
                                    type="radio"
                                    name="thinking_mode"
                                    value="balance"
                                    checked={config.thinkingMode === 'balance'}
                                    onChange={(e) => updateConfig({ thinkingMode: e.target.value as any })}
                                />
                                <Scale size={16} />
                                <span>Balance (Recommended)</span>
                            </label>
                            <label className="option-radio">
                                <input
                                    type="radio"
                                    name="thinking_mode"
                                    value="thinking"
                                    checked={config.thinkingMode === 'thinking'}
                                    onChange={(e) => updateConfig({ thinkingMode: e.target.value as any })}
                                />
                                <Brain size={16} />
                                <span>Deep Thinking</span>
                            </label>
                        </div>
                    </div>

                    {/* RAG Settings */}
                    <div className="settings-group">
                        <label className="settings-toggle">
                            <input
                                type="checkbox"
                                checked={config.enableRAG}
                                onChange={(e) => updateConfig({ enableRAG: e.target.checked })}
                            />
                            <span>Retrieval Augmented Generation (RAG)</span>
                        </label>
                        <p className="help-text">Uses your documents to provide more accurate answers</p>

                        {config.enableRAG && (
                            <>
                                <label className="settings-label">
                                    <span>Top-K Results</span>
                                    <span className="help-text">Number of document chunks to retrieve</span>
                                </label>
                                <div className="slider-group">
                                    <input
                                        type="range"
                                        min="1"
                                        max="20"
                                        value={config.topK}
                                        onChange={(e) => updateConfig({ topK: parseInt(e.target.value) })}
                                        className="settings-slider"
                                    />
                                    <span className="slider-value">{config.topK}</span>
                                </div>

                                <label className="settings-label">
                                    <span>Similarity Threshold</span>
                                    <span className="help-text">Minimum relevance score (0-1)</span>
                                </label>
                                <div className="slider-group">
                                    <input
                                        type="range"
                                        min="0"
                                        max="1"
                                        step="0.1"
                                        value={config.similarityThreshold}
                                        onChange={(e) => updateConfig({ similarityThreshold: parseFloat(e.target.value) })}
                                        className="settings-slider"
                                    />
                                    <span className="slider-value">{config.similarityThreshold.toFixed(1)}</span>
                                </div>
                            </>
                        )}
                    </div>

                    {/* Web Search */}
                    <div className="settings-group">
                        <label className="settings-toggle">
                            <input
                                type="checkbox"
                                checked={config.enableWebSearch}
                                onChange={(e) => updateConfig({ enableWebSearch: e.target.checked })}
                            />
                            <span>Web Search</span>
                        </label>
                        <p className="help-text">Search the web for latest information</p>
                    </div>

                    {/* Temperature */}
                    <div className="settings-group">
                        <label className="settings-label">
                            <span>Temperature</span>
                            <span className="help-text">Controls randomness in responses (0-2)</span>
                        </label>
                        <div className="slider-group">
                            <input
                                type="range"
                                min="0"
                                max="2"
                                step="0.1"
                                value={config.temperature}
                                onChange={(e) => updateConfig({ temperature: parseFloat(e.target.value) })}
                                className="settings-slider"
                            />
                            <span className="slider-value">{config.temperature.toFixed(1)}</span>
                        </div>
                    </div>

                    {/* Max Tokens */}
                    <div className="settings-group">
                        <label className="settings-label">
                            <span>Max Tokens</span>
                            <span className="help-text">Maximum response length (optional)</span>
                        </label>
                        <input
                            type="number"
                            value={config.maxTokens || ''}
                            onChange={(e) =>
                                updateConfig({
                                    maxTokens: e.target.value ? parseInt(e.target.value) : undefined,
                                })
                            }
                            placeholder="Leave empty for default"
                            className="settings-input"
                            min="1"
                            max="100000"
                        />
                    </div>

                    {/* Collection */}
                    <div className="settings-group">
                        <label className="settings-label">
                            <span>Document Collection</span>
                            <span className="help-text">Select which collection to search</span>
                        </label>
                        <input
                            type="text"
                            value={config.collection}
                            onChange={(e) => updateConfig({ collection: e.target.value })}
                            className="settings-input"
                            placeholder="default"
                        />
                    </div>
                </div>

                <div className="settings-footer">
                    <button className="btn-secondary" onClick={onClose}>
                        Close
                    </button>
                </div>
            </div>
        </>
    )
}

// CSS will be imported via global index.css
