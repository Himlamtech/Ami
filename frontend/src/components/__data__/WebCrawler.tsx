import { useState } from 'react'
import { FileText, Network, CheckCircle2, XCircle } from 'lucide-react'
import { apiClient } from '../../api/client'

interface WebCrawlerProps {
    collection: string
    onSuccess: () => void
}

export default function WebCrawler({ collection, onSuccess }: WebCrawlerProps) {
    const [mode, setMode] = useState<'scrape' | 'crawl'>('scrape')
    const [url, setUrl] = useState('')
    const [maxDepth, setMaxDepth] = useState(2)
    const [limit, setLimit] = useState(10)
    const [loading, setLoading] = useState(false)
    const [result, setResult] = useState<{
        success: boolean
        message: string
        details?: string
    } | null>(null)

    const handleScrape = async () => {
        if (!url) return

        setLoading(true)
        setResult(null)

        try {
            const response = await apiClient.scrapeUrl(url, collection, true, true)

            if (response.success) {
                setResult({
                    success: true,
                    message: 'Successfully scraped and ingested content',
                    details: `URL: ${response.url}\nChunks: ${response.chunk_count}\nContent length: ${response.content_length} characters`,
                })
                onSuccess()
            } else {
                setResult({
                    success: false,
                    message: 'Failed to scrape URL',
                    details: response.error,
                })
            }
        } catch (error) {
            setResult({
                success: false,
                message: 'Error during scraping',
                details: error instanceof Error ? error.message : 'Unknown error',
            })
        } finally {
            setLoading(false)
        }
    }

    const handleCrawl = async () => {
        if (!url) return

        setLoading(true)
        setResult(null)

        try {
            const response = await apiClient.crawlUrl(url, maxDepth, limit, collection, true)

            if (response.success) {
                setResult({
                    success: true,
                    message: 'Successfully crawled and ingested pages',
                    details: `URL: ${response.url}\nTotal pages: ${response.total_pages}\nIngested: ${response.ingested_pages}\nDuration: ${response.duration_seconds.toFixed(2)}s`,
                })
                onSuccess()
            } else {
                setResult({
                    success: false,
                    message: 'Failed to crawl URL',
                    details: response.error,
                })
            }
        } catch (error) {
            setResult({
                success: false,
                message: 'Error during crawling',
                details: error instanceof Error ? error.message : 'Unknown error',
            })
        } finally {
            setLoading(false)
        }
    }

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        if (mode === 'scrape') {
            handleScrape()
        } else {
            handleCrawl()
        }
    }

    return (
        <div className="web-crawler">
            <div className="crawler-info">
                <h2>Web Crawler</h2>
                <p>Extract content from websites and ingest into your knowledge base.</p>
            </div>

            <div className="mode-selector">
                <button
                    className={`mode-button ${mode === 'scrape' ? 'active' : ''}`}
                    onClick={() => setMode('scrape')}
                >
                    <FileText size={18} />
                    <span>Scrape Single Page</span>
                </button>
                <button
                    className={`mode-button ${mode === 'crawl' ? 'active' : ''}`}
                    onClick={() => setMode('crawl')}
                >
                    <Network size={18} />
                    <span>Crawl Multiple Pages</span>
                </button>
            </div>

            <form className="crawler-form" onSubmit={handleSubmit}>
                <div className="form-group">
                    <label htmlFor="url">URL</label>
                    <input
                        id="url"
                        type="url"
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                        placeholder="https://example.com"
                        required
                    />
                </div>

                {mode === 'crawl' && (
                    <>
                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="maxDepth">Max Depth</label>
                                <input
                                    id="maxDepth"
                                    type="number"
                                    min="1"
                                    max="5"
                                    value={maxDepth}
                                    onChange={(e) => setMaxDepth(parseInt(e.target.value))}
                                />
                                <small>How many levels deep to crawl (1-5)</small>
                            </div>

                            <div className="form-group">
                                <label htmlFor="limit">Page Limit</label>
                                <input
                                    id="limit"
                                    type="number"
                                    min="1"
                                    max="100"
                                    value={limit}
                                    onChange={(e) => setLimit(parseInt(e.target.value))}
                                />
                                <small>Maximum number of pages to crawl</small>
                            </div>
                        </div>
                    </>
                )}

                <button type="submit" className="btn-submit" disabled={loading || !url}>
                    {loading ? (
                        <>
                            <div className="inline-loader"></div>
                            {mode === 'scrape' ? 'Scraping...' : 'Crawling...'}
                        </>
                    ) : (
                        <>{mode === 'scrape' ? 'Scrape Page' : 'Start Crawl'}</>
                    )}
                </button>
            </form>

            {result && (
                <div className={`crawler-result ${result.success ? 'success' : 'error'}`}>
                    <div className="result-header">
                        {result.success ? (
                            <CheckCircle2 size={20} strokeWidth={2} />
                        ) : (
                            <XCircle size={20} strokeWidth={2} />
                        )}
                        <strong>{result.message}</strong>
                    </div>
                    {result.details && (
                        <pre className="result-details">{result.details}</pre>
                    )}
                </div>
            )}
        </div>
    )
}

