import { useEffect, useState } from 'react'
import { Activity, Globe, History, TrendingUp } from 'lucide-react'
import { apiClient, CrawlerStats } from '../../api/client'
import '../../styles/__data__/CrawlerDashboard.css'

export default function CrawlerDashboard() {
    const [stats, setStats] = useState<CrawlerStats | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        loadStats()
    }, [])

    const loadStats = async () => {
        try {
            setLoading(true)
            const data = await apiClient.getCrawlerStats()
            setStats(data)
        } catch (err) {
            setError('Failed to load crawler statistics')
            console.error(err)
        } finally {
            setLoading(false)
        }
    }

    if (loading) {
        return (
            <div className="crawler-dashboard loading">
                <div className="loader"></div>
                <p>Loading crawler statistics...</p>
            </div>
        )
    }

    if (error || !stats) {
        return (
            <div className="crawler-dashboard error">
                <p>{error || 'No data available'}</p>
            </div>
        )
    }

    return (
        <div className="crawler-dashboard">
            <div className="dashboard-header">
                <h2>
                    <Activity size={24} />
                    Crawler Dashboard
                </h2>
                <button onClick={loadStats} className="btn-refresh">
                    Refresh
                </button>
            </div>

            {/* Stats Cards */}
            <div className="stats-grid">
                <div className="stat-card">
                    <div className="stat-icon jobs">
                        <Globe size={32} />
                    </div>
                    <div className="stat-content">
                        <h3>Total Jobs</h3>
                        <p className="stat-value">{stats.total_jobs}</p>
                        <div className="stat-breakdown">
                            {Object.entries(stats.jobs_by_status).map(([status, count]) => (
                                <span key={status} className={`status-badge ${status}`}>
                                    {status}: {count}
                                </span>
                            ))}
                        </div>
                    </div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon pages">
                        <History size={32} />
                    </div>
                    <div className="stat-content">
                        <h3>Crawled Pages</h3>
                        <p className="stat-value">{stats.total_crawled_pages}</p>
                        <div className="stat-details">
                            <span className="success">✓ Ingested: {stats.total_ingested_pages}</span>
                            <span className="error">✗ Failed: {stats.total_failed_pages}</span>
                        </div>
                    </div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon performance">
                        <TrendingUp size={32} />
                    </div>
                    <div className="stat-content">
                        <h3>Performance</h3>
                        <p className="stat-value">{stats.avg_duration_seconds.toFixed(2)}s</p>
                        <p className="stat-label">Average Duration</p>
                    </div>
                </div>
            </div>

            {/* Recent Jobs */}
            <div className="recent-section">
                <h3>Recent Jobs</h3>
                <div className="jobs-list">
                    {stats.recent_jobs.length === 0 ? (
                        <p className="empty-state">No recent jobs</p>
                    ) : (
                        stats.recent_jobs.map((job) => (
                            <div key={job.id} className="job-item">
                                <div className="job-header">
                                    <span className={`job-status ${job.status}`}>{job.status}</span>
                                    <span className="job-type">{job.job_type}</span>
                                </div>
                                <div className="job-details">
                                    <p className="job-url">{job.url || job.csv_path}</p>
                                    <div className="job-stats">
                                        <span>Pages: {job.total_pages}</span>
                                        <span>Success: {job.successful_pages}</span>
                                        <span>Failed: {job.failed_pages}</span>
                                        <span>Duration: {job.duration_seconds.toFixed(2)}s</span>
                                    </div>
                                </div>
                                <div className="job-meta">
                                    <span>Created: {new Date(job.created_at).toLocaleString()}</span>
                                    {job.completed_at && (
                                        <span>Completed: {new Date(job.completed_at).toLocaleString()}</span>
                                    )}
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>

            {/* Recent History */}
            <div className="recent-section">
                <h3>Recent Crawl History</h3>
                <div className="history-list">
                    {stats.recent_history.length === 0 ? (
                        <p className="empty-state">No crawl history</p>
                    ) : (
                        <table className="history-table">
                            <thead>
                                <tr>
                                    <th>URL</th>
                                    <th>Status</th>
                                    <th>Content</th>
                                    <th>Ingested</th>
                                    <th>Duration</th>
                                    <th>Date</th>
                                </tr>
                            </thead>
                            <tbody>
                                {stats.recent_history.map((entry) => (
                                    <tr key={entry.id}>
                                        <td className="url-cell" title={entry.url}>
                                            {entry.url.length > 50
                                                ? entry.url.substring(0, 50) + '...'
                                                : entry.url}
                                        </td>
                                        <td>
                                            <span className={`status-badge ${entry.status}`}>
                                                {entry.status}
                                            </span>
                                        </td>
                                        <td>{entry.content_length} chars</td>
                                        <td>
                                            {entry.ingested ? (
                                                <span className="badge success">✓ Yes</span>
                                            ) : (
                                                <span className="badge">No</span>
                                            )}
                                        </td>
                                        <td>{entry.duration_seconds.toFixed(2)}s</td>
                                        <td>{new Date(entry.crawled_at).toLocaleString()}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            </div>
        </div>
    )
}

