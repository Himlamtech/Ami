import { useEffect, useState } from 'react'
import { Globe, Folder, CheckCircle2, Clock, XCircle } from 'lucide-react'
import { apiClient, WebsiteInfo } from '../../api/client'
import '../../styles/__data__/WebsiteOverview.css'

export default function WebsiteOverview() {
    const [websiteInfo, setWebsiteInfo] = useState<WebsiteInfo | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        loadWebsiteInfo()
    }, [])

    const loadWebsiteInfo = async () => {
        try {
            setLoading(true)
            const data = await apiClient.getWebsiteInfo()
            setWebsiteInfo(data)
        } catch (err) {
            setError('Failed to load website information')
            console.error(err)
        } finally {
            setLoading(false)
        }
    }

    if (loading) {
        return (
            <div className="website-overview loading">
                <div className="loader"></div>
                <p>Loading website structure...</p>
            </div>
        )
    }

    if (error || !websiteInfo) {
        return (
            <div className="website-overview error">
                <p>{error || 'No data available'}</p>
            </div>
        )
    }

    const crawledPercentage = (
        (websiteInfo.urls_by_status.crawled / websiteInfo.total_urls) *
        100
    ).toFixed(1)

    return (
        <div className="website-overview">
            <div className="overview-header">
                <h2>
                    <Globe size={24} />
                    Website Structure - PTIT.edu.vn
                </h2>
                <button onClick={loadWebsiteInfo} className="btn-refresh">
                    Refresh
                </button>
            </div>

            {/* Summary Stats */}
            <div className="summary-stats">
                <div className="summary-card total">
                    <Globe size={32} />
                    <div>
                        <h3>{websiteInfo.total_urls}</h3>
                        <p>Total URLs</p>
                    </div>
                </div>

                <div className="summary-card crawled">
                    <CheckCircle2 size={32} />
                    <div>
                        <h3>{websiteInfo.urls_by_status.crawled}</h3>
                        <p>Crawled ({crawledPercentage}%)</p>
                    </div>
                </div>

                <div className="summary-card pending">
                    <Clock size={32} />
                    <div>
                        <h3>{websiteInfo.urls_by_status.pending}</h3>
                        <p>Pending</p>
                    </div>
                </div>

                <div className="summary-card failed">
                    <XCircle size={32} />
                    <div>
                        <h3>{websiteInfo.urls_by_status.failed}</h3>
                        <p>Failed</p>
                    </div>
                </div>
            </div>

            {/* Progress Bar */}
            <div className="progress-section">
                <h3>Crawl Progress</h3>
                <div className="progress-bar">
                    <div
                        className="progress-fill crawled"
                        style={{
                            width: `${
                                (websiteInfo.urls_by_status.crawled / websiteInfo.total_urls) * 100
                            }%`,
                        }}
                    ></div>
                    <div
                        className="progress-fill failed"
                        style={{
                            width: `${
                                (websiteInfo.urls_by_status.failed / websiteInfo.total_urls) * 100
                            }%`,
                        }}
                    ></div>
                </div>
                <div className="progress-legend">
                    <span className="legend-item crawled">
                        Crawled: {websiteInfo.urls_by_status.crawled}
                    </span>
                    <span className="legend-item pending">
                        Pending: {websiteInfo.urls_by_status.pending}
                    </span>
                    <span className="legend-item failed">
                        Failed: {websiteInfo.urls_by_status.failed}
                    </span>
                </div>
            </div>

            {/* Categories */}
            <div className="categories-section">
                <h3>
                    <Folder size={20} />
                    Content Categories
                </h3>
                <div className="categories-grid">
                    {Object.entries(websiteInfo.urls_by_category)
                        .sort(([, a], [, b]) => b - a)
                        .map(([category, count]) => (
                            <div key={category} className="category-card">
                                <div className="category-header">
                                    <Folder size={18} />
                                    <h4>{category}</h4>
                                </div>
                                <div className="category-count">{count} URLs</div>
                                <div className="category-bar">
                                    <div
                                        className="category-fill"
                                        style={{
                                            width: `${(count / websiteInfo.total_urls) * 100}%`,
                                        }}
                                    ></div>
                                </div>
                            </div>
                        ))}
                </div>
            </div>

            {/* URL Tree */}
            <div className="url-tree-section">
                <h3>URL Structure</h3>
                <div className="url-tree">
                    {websiteInfo.url_tree.map((node, index) => (
                        <div key={index} className="tree-node">
                            <div className="tree-node-header">
                                <Folder size={16} />
                                <span className="tree-node-title">{node.category}</span>
                                <span className="tree-node-count">{node.count} items</span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}

