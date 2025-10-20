import { RefreshCw, FileText, Scissors, FolderOpen, Database, Folder } from 'lucide-react'

interface DataStatsProps {
    stats: {
        total_documents: number
        total_chunks: number
        collections: string[]
        vector_store: string
    } | null
    onRefresh: () => void
}

export default function DataStats({ stats, onRefresh }: DataStatsProps) {
    if (!stats) {
        return (
            <div className="data-stats">
                <p>No statistics available</p>
            </div>
        )
    }

    return (
        <div className="data-stats">
            <div className="stats-header">
                <h2>Database Statistics</h2>
                <button className="btn-refresh" onClick={onRefresh}>
                    <RefreshCw size={16} />
                    <span>Refresh</span>
                </button>
            </div>

            <div className="stats-grid">
                <div className="stat-card">
                    <div className="stat-icon">
                        <FileText size={32} strokeWidth={1.5} />
                    </div>
                    <div className="stat-content">
                        <h3>Total Documents</h3>
                        <p className="stat-value">{stats.total_documents.toLocaleString()}</p>
                    </div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon">
                        <Scissors size={32} strokeWidth={1.5} />
                    </div>
                    <div className="stat-content">
                        <h3>Total Chunks</h3>
                        <p className="stat-value">{stats.total_chunks.toLocaleString()}</p>
                    </div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon">
                        <FolderOpen size={32} strokeWidth={1.5} />
                    </div>
                    <div className="stat-content">
                        <h3>Collections</h3>
                        <p className="stat-value">{stats.collections.length}</p>
                    </div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon">
                        <Database size={32} strokeWidth={1.5} />
                    </div>
                    <div className="stat-content">
                        <h3>Vector Store</h3>
                        <p className="stat-value">{stats.vector_store}</p>
                    </div>
                </div>
            </div>

            <div className="collections-list">
                <h3>Available Collections</h3>
                <div className="collection-items">
                    {stats.collections.map((collection) => (
                        <div key={collection} className="collection-item">
                            <Folder size={18} />
                            <span className="collection-name">{collection}</span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}

