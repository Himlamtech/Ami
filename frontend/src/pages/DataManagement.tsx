import { useEffect, useState } from 'react'
import { BarChart3, FolderUp, Globe, AlertTriangle, X } from 'lucide-react'
import { useDataStore } from '../store/dataStore'
import { apiClient } from '../api/client'
import DataStats from '../components/__data__/DataStats'
import FileUpload from '../components/__data__/FileUpload'
import WebCrawler from '../components/__data__/WebCrawler'
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

    const [activeTab, setActiveTab] = useState<'upload' | 'crawl' | 'stats'>('stats')

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
                    className={`tab-button ${activeTab === 'stats' ? 'active' : ''}`}
                    onClick={() => setActiveTab('stats')}
                >
                    <BarChart3 size={18} />
                    <span>Statistics</span>
                </button>
                <button
                    className={`tab-button ${activeTab === 'upload' ? 'active' : ''}`}
                    onClick={() => setActiveTab('upload')}
                >
                    <FolderUp size={18} />
                    <span>Upload Files</span>
                </button>
                <button
                    className={`tab-button ${activeTab === 'crawl' ? 'active' : ''}`}
                    onClick={() => setActiveTab('crawl')}
                >
                    <Globe size={18} />
                    <span>Web Crawler</span>
                </button>
            </div>

            <div className="data-content">
                {loading && (
                    <div className="loading-overlay">
                        <div className="loader"></div>
                        <p>Loading...</p>
                    </div>
                )}

                {activeTab === 'stats' && <DataStats stats={stats} onRefresh={loadStats} />}
                {activeTab === 'upload' && (
                    <FileUpload collection={selectedCollection} onSuccess={loadStats} />
                )}
                {activeTab === 'crawl' && (
                    <WebCrawler collection={selectedCollection} onSuccess={loadStats} />
                )}
            </div>
        </div>
    )
}

