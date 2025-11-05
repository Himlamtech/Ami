import { useEffect, useState } from 'react'
import {
    FileText,
    Search,
    Filter,
    Download,
    Trash2,
    AlertCircle,
    Info,
    AlertTriangle,
    XCircle,
    Bug,
    Calendar,
    User,
    Activity,
} from 'lucide-react'
import { apiClient, LogResponse, LogLevel, LogAction, LogStatsResponse } from '../api/client'
import '../styles/__admin__/LogManagement.css'

export default function LogManagement() {
    const [logs, setLogs] = useState<LogResponse[]>([])
    const [stats, setStats] = useState<LogStatsResponse | null>(null)
    const [total, setTotal] = useState(0)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    // Pagination
    const [currentPage, setCurrentPage] = useState(1)
    const [limit] = useState(20)

    // Filters
    const [searchQuery, setSearchQuery] = useState('')
    const [filterLevel, setFilterLevel] = useState<LogLevel | undefined>(undefined)
    const [filterAction, setFilterAction] = useState<LogAction | undefined>(undefined)
    const [filterUsername, setFilterUsername] = useState('')
    const [startDate, setStartDate] = useState('')
    const [endDate, setEndDate] = useState('')
    const [statsDays, setStatsDays] = useState(7)

    useEffect(() => {
        loadLogs()
        loadStats()
    }, [currentPage, filterLevel, filterAction])

    const loadLogs = async () => {
        setLoading(true)
        setError(null)
        try {
            const skip = (currentPage - 1) * limit
            const params: Record<string, unknown> = { skip, limit }

            if (filterLevel) params.level = filterLevel
            if (filterAction) params.action = filterAction
            if (filterUsername) params.username = filterUsername
            if (searchQuery) params.search = searchQuery
            if (startDate) params.start_date = new Date(startDate).toISOString()
            if (endDate) params.end_date = new Date(endDate).toISOString()

            const response = await apiClient.getLogs(params)
            setLogs(response.logs)
            setTotal(response.total)
        } catch (err) {
            setError('Failed to load logs')
            console.error(err)
        } finally {
            setLoading(false)
        }
    }

    const loadStats = async () => {
        try {
            const statsData = await apiClient.getLogStats(statsDays)
            setStats(statsData)
        } catch (err) {
            console.error('Failed to load stats:', err)
        }
    }

    const handleSearch = () => {
        setCurrentPage(1)
        loadLogs()
    }

    const handleClearOldLogs = async () => {
        const days = prompt('Delete logs older than how many days? (minimum 30)', '90')
        if (!days) return

        const daysNum = parseInt(days)
        if (isNaN(daysNum) || daysNum < 30) {
            alert('Please enter a valid number (minimum 30 days)')
            return
        }

        if (!confirm(`Are you sure you want to delete logs older than ${daysNum} days?`)) return

        setLoading(true)
        try {
            await apiClient.clearOldLogs(daysNum)
            alert('Old logs deleted successfully')
            loadLogs()
            loadStats()
        } catch (err: unknown) {
            if (err instanceof Error) {
                setError(err.message)
            } else {
                setError('Failed to delete old logs')
            }
        } finally {
            setLoading(false)
        }
    }

    const exportLogs = () => {
        const csv = [
            ['Timestamp', 'Level', 'Action', 'Message', 'User', 'IP Address'].join(','),
            ...logs.map((log) =>
                [
                    new Date(log.created_at).toISOString(),
                    log.level,
                    log.action,
                    `"${log.message.replace(/"/g, '""')}"`,
                    log.username || '-',
                    log.ip_address || '-',
                ].join(',')
            ),
        ].join('\n')

        const blob = new Blob([csv], { type: 'text/csv' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `logs-${new Date().toISOString()}.csv`
        a.click()
        URL.revokeObjectURL(url)
    }

    const getLevelIcon = (level: LogLevel) => {
        switch (level) {
            case 'debug':
                return <Bug size={16} />
            case 'info':
                return <Info size={16} />
            case 'warning':
                return <AlertTriangle size={16} />
            case 'error':
                return <XCircle size={16} />
            case 'critical':
                return <AlertCircle size={16} />
        }
    }

    const totalPages = Math.ceil(total / limit)

    return (
        <div className="log-management">
            <div className="log-management-header">
                <div className="header-content">
                    <h1>
                        <FileText size={32} />
                        Log Management
                    </h1>
                    <p>Monitor system activity and troubleshoot issues</p>
                </div>
                <div className="header-actions">
                    <button className="btn-secondary" onClick={exportLogs} disabled={logs.length === 0}>
                        <Download size={20} />
                        <span>Export CSV</span>
                    </button>
                    <button className="btn-danger" onClick={handleClearOldLogs}>
                        <Trash2 size={20} />
                        <span>Clear Old Logs</span>
                    </button>
                </div>
            </div>

            {error && (
                <div className="error-banner">
                    <XCircle size={20} />
                    <span>{error}</span>
                    <button onClick={() => setError(null)}>×</button>
                </div>
            )}

            {/* Statistics Dashboard */}
            {stats && (
                <div className="stats-dashboard">
                    <div className="stat-card">
                        <div className="stat-icon total">
                            <Activity size={24} />
                        </div>
                        <div className="stat-content">
                            <div className="stat-value">{stats.total_logs.toLocaleString()}</div>
                            <div className="stat-label">Total Logs ({statsDays} days)</div>
                        </div>
                    </div>

                    <div className="stat-card">
                        <div className="stat-icon error">
                            <XCircle size={24} />
                        </div>
                        <div className="stat-content">
                            <div className="stat-value">{stats.recent_errors}</div>
                            <div className="stat-label">Recent Errors (24h)</div>
                        </div>
                    </div>

                    <div className="stat-card">
                        <div className="stat-icon users">
                            <User size={24} />
                        </div>
                        <div className="stat-content">
                            <div className="stat-value">{stats.active_users}</div>
                            <div className="stat-label">Active Users</div>
                        </div>
                    </div>

                    <div className="stat-card levels">
                        <div className="stat-content">
                            <div className="stat-label">By Level</div>
                            <div className="level-breakdown">
                                {Object.entries(stats.by_level).map(([level, count]) => (
                                    <div key={level} className={`level-item ${level}`}>
                                        {getLevelIcon(level as LogLevel)}
                                        <span>{level}</span>
                                        <span className="count">{count}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Filters */}
            <div className="log-filters">
                <div className="search-box">
                    <Search size={18} />
                    <input
                        type="text"
                        placeholder="Search in messages..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                    />
                    <button onClick={handleSearch}>Search</button>
                </div>

                <div className="filter-row">
                    <div className="filter-group">
                        <Filter size={16} />
                        <select value={filterLevel || ''} onChange={(e) => setFilterLevel(e.target.value as LogLevel || undefined)}>
                            <option value="">All Levels</option>
                            <option value="debug">Debug</option>
                            <option value="info">Info</option>
                            <option value="warning">Warning</option>
                            <option value="error">Error</option>
                            <option value="critical">Critical</option>
                        </select>
                    </div>

                    <div className="filter-group">
                        <select value={filterAction || ''} onChange={(e) => setFilterAction(e.target.value as LogAction || undefined)}>
                            <option value="">All Actions</option>
                            <option value="login">Login</option>
                            <option value="logout">Logout</option>
                            <option value="chat_message">Chat Message</option>
                            <option value="document_upload">Document Upload</option>
                            <option value="crawl_start">Crawl Start</option>
                            <option value="user_create">User Create</option>
                            <option value="system_error">System Error</option>
                        </select>
                    </div>

                    <div className="filter-group">
                        <input
                            type="text"
                            placeholder="Username..."
                            value={filterUsername}
                            onChange={(e) => setFilterUsername(e.target.value)}
                        />
                    </div>

                    <div className="filter-group">
                        <Calendar size={16} />
                        <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
                        <span>to</span>
                        <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
                    </div>

                    <button className="btn-primary" onClick={handleSearch}>
                        Apply Filters
                    </button>
                </div>
            </div>

            {loading && (
                <div className="loading-overlay">
                    <div className="loader"></div>
                    <p>Loading logs...</p>
                </div>
            )}

            {/* Logs Table */}
            <div className="logs-table-container">
                <table className="logs-table">
                    <thead>
                        <tr>
                            <th>Timestamp</th>
                            <th>Level</th>
                            <th>Action</th>
                            <th>Message</th>
                            <th>User</th>
                            <th>IP Address</th>
                        </tr>
                    </thead>
                    <tbody>
                        {logs.map((log) => (
                            <tr key={log.id} className={`log-row ${log.level}`}>
                                <td>
                                    <div className="timestamp-cell">
                                        <Calendar size={14} />
                                        <span>{new Date(log.created_at).toLocaleString()}</span>
                                    </div>
                                </td>
                                <td>
                                    <span className={`level-badge ${log.level}`}>
                                        {getLevelIcon(log.level)}
                                        {log.level}
                                    </span>
                                </td>
                                <td>
                                    <span className="action-badge">{log.action.replace(/_/g, ' ')}</span>
                                </td>
                                <td>
                                    <div className="message-cell">{log.message}</div>
                                </td>
                                <td>
                                    {log.username ? (
                                        <div className="user-cell">
                                            <User size={14} />
                                            <span>{log.username}</span>
                                        </div>
                                    ) : (
                                        <span className="text-muted">-</span>
                                    )}
                                </td>
                                <td>
                                    <span className="ip-address">{log.ip_address || '-'}</span>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>

                {logs.length === 0 && !loading && (
                    <div className="empty-state">
                        <FileText size={48} />
                        <p>No logs found</p>
                        <small>Try adjusting your filters</small>
                    </div>
                )}
            </div>

            {/* Pagination */}
            <div className="pagination">
                <div className="pagination-info">
                    Showing {((currentPage - 1) * limit) + 1} to {Math.min(currentPage * limit, total)} of {total} logs
                </div>
                <div className="pagination-controls">
                    <button onClick={() => setCurrentPage((p) => Math.max(1, p - 1))} disabled={currentPage === 1}>
                        Previous
                    </button>
                    <span>
                        Page {currentPage} of {totalPages}
                    </span>
                    <button onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))} disabled={currentPage === totalPages}>
                        Next
                    </button>
                </div>
            </div>
        </div>
    )
}

