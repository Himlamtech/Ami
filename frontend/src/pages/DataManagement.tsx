import { useEffect, useState } from 'react'
import { Database, Globe, History, AlertTriangle, X } from 'lucide-react'
import { useDataStore } from '../store/dataStore'
import { apiClient } from '../api/client'
import DataStats from '../components/__data__/DataStats'
import FileUpload from '../components/__data__/FileUpload'
import WebCrawler from '../components/__data__/WebCrawler'
import DocumentsList from '../components/__data__/DocumentsList'
import '../styles/__data__/DataManagement.css'

export default function DataManagement() {
    const {
        stats,
        collections,
        selectedCollection,
        loading,
        error,
        setStats,
        setCollections,
        setSelectedCollection,
        setLoading,
        setError,
    } = useDataStore()

    const [activeTab, setActiveTab] = useState<'management' | 'crawler' | 'history'>('management')

    useEffect(() => {
        loadInitialData()
    }, [])

    useEffect(() => {
        if (selectedCollection) {
            loadStats()
        }
    }, [selectedCollection])

    const loadInitialData = async () => {
        try {
            setLoading(true)
            const [collectionsData, statsData] = await Promise.all([
                apiClient.getCollections(),
                apiClient.getStats(),
            ])
            setCollections(collectionsData)
            setStats(statsData as any)
        } catch (err) {
            setError('Failed to load data')
        } finally {
            setLoading(false)
        }
    }

    const loadStats = async () => {
        try {
            const statsData = await apiClient.getStats(selectedCollection)
            setStats(statsData as any)
        } catch (err) {
            setError('Failed to load stats')
        }
    }

    return (
        <div className="data-management">
            <div className="data-header">
                <div className="header-content">
                    <h1>Data Management</h1>
                    <p>Manage your knowledge base and vector database</p>
                </div>

                <div className="collection-selector">
                    <label htmlFor="collection">Collection:</label>
                    <select
                        id="collection"
                        value={selectedCollection}
                        onChange={(e) => setSelectedCollection(e.target.value)}
                    >
                        {collections.map((col) => (
                            <option key={col} value={col}>
                                {col}
                            </option>
                        ))}
                    </select>
                </div>
            </div>

            {error && (
                <div className="error-banner">
                    <AlertTriangle size={18} />
                    <span>{error}</span>
                    <button onClick={() => setError(null)}>
                        <X size={18} />
                    </button>
                </div>
            )}

            <div className="data-tabs">
                <button
                    className={`tab-button ${activeTab === 'management' ? 'active' : ''}`}
                    onClick={() => setActiveTab('management')}
                >
                    <Database size={18} />
                    <span>Management</span>
                </button>
                <button
                    className={`tab-button ${activeTab === 'crawler' ? 'active' : ''}`}
                    onClick={() => setActiveTab('crawler')}
                >
                    <Globe size={18} />
                    <span>Crawler</span>
                </button>
                <button
                    className={`tab-button ${activeTab === 'history' ? 'active' : ''}`}
                    onClick={() => setActiveTab('history')}
                >
                    <History size={18} />
                    <span>History</span>
                </button>
            </div>

            <div className="data-content">
                {loading && (
                    <div className="loading-overlay">
                        <div className="loader"></div>
                        <p>Loading...</p>
                    </div>
                )}

                {activeTab === 'management' && (
                    <div className="management-tab">
                        <DataStats stats={stats} onRefresh={loadStats} />
                        <div className="management-section">
                            <h2>Documents</h2>
                            <DocumentsList selectedCollection={selectedCollection} onRefresh={loadStats} />
                        </div>
                        <div className="management-section">
                            <h2>Upload Files</h2>
                            <FileUpload collection={selectedCollection} onSuccess={loadStats} />
                        </div>
                    </div>
                )}

                {activeTab === 'crawler' && (
                    <div className="crawler-tab">
                        <WebCrawler collection={selectedCollection} onSuccess={loadStats} />
                    </div>
                )}

                {activeTab === 'history' && (
                    <div className="history-tab">
                        <h2>Activity History</h2>
                        <p className="coming-soon">History tracking coming soon...</p>
                    </div>
                )}
            </div>
        </div>
    )
}

