import { useState, useEffect } from 'react'
import {
    FileText,
    Trash2,
    Eye,
    ChevronLeft,
    ChevronRight,
    Search,
    Filter,
    X,
    AlertCircle,
    Loader2,
} from 'lucide-react'
import { apiClient } from '../../api/client'
import '../../styles/__data__/DocumentsList.css'

interface Document {
    id: string
    content: string
    metadata: Record<string, unknown>
    collection: string
    created_at: string
    embedding_dims?: number
}

interface DocumentsListProps {
    selectedCollection: string
    onRefresh?: () => void
}

export default function DocumentsList({ selectedCollection, onRefresh }: DocumentsListProps) {
    const [documents, setDocuments] = useState<Document[]>([])
    const [totalCount, setTotalCount] = useState(0)
    const [currentPage, setCurrentPage] = useState(1)
    const [pageSize] = useState(10)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [searchQuery, setSearchQuery] = useState('')
    const [selectedDoc, setSelectedDoc] = useState<Document | null>(null)
    const [viewingDoc, setViewingDoc] = useState<any | null>(null)
    const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null)

    useEffect(() => {
        loadDocuments()
    }, [selectedCollection, currentPage])

    const loadDocuments = async () => {
        try {
            setLoading(true)
            setError(null)
            const offset = (currentPage - 1) * pageSize
            const result = await apiClient.listDocuments(selectedCollection, pageSize, offset)
            setDocuments(result.documents)
            setTotalCount(result.total_count)
        } catch (err: any) {
            setError(err.message || 'Failed to load documents')
        } finally {
            setLoading(false)
        }
    }

    const handleViewDocument = async (docId: string) => {
        try {
            setLoading(true)
            const doc = await apiClient.getDocument(docId)
            setViewingDoc(doc)
        } catch (err: any) {
            setError(err.message || 'Failed to load document content')
        } finally {
            setLoading(false)
        }
    }

    const handleDeleteDocument = async (docId: string) => {
        try {
            setLoading(true)
            await apiClient.deleteDocument(docId)
            setDeleteConfirm(null)
            loadDocuments()
            if (onRefresh) onRefresh()
        } catch (err: any) {
            setError(err.message || 'Failed to delete document')
        } finally {
            setLoading(false)
        }
    }

    const filteredDocuments = documents.filter((doc) => {
        if (!searchQuery) return true
        const query = searchQuery.toLowerCase()
        return (
            doc.id.toLowerCase().includes(query) ||
            doc.content.toLowerCase().includes(query) ||
            JSON.stringify(doc.metadata).toLowerCase().includes(query)
        )
    })

    const totalPages = Math.ceil(totalCount / pageSize)

    return (
        <div className="documents-list">
            <div className="documents-header">
                <h2>Documents in Collection</h2>
                <div className="documents-actions">
                    <div className="search-box">
                        <Search size={18} />
                        <input
                            type="text"
                            placeholder="Search documents..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                        />
                        {searchQuery && (
                            <button className="clear-search" onClick={() => setSearchQuery('')}>
                                <X size={16} />
                            </button>
                        )}
                    </div>
                </div>
            </div>

            {error && (
                <div className="error-message">
                    <AlertCircle size={18} />
                    <span>{error}</span>
                    <button onClick={() => setError(null)}>
                        <X size={16} />
                    </button>
                </div>
            )}

            {loading && (
                <div className="loading-state">
                    <Loader2 className="spinner" size={24} />
                    <span>Loading documents...</span>
                </div>
            )}

            {!loading && filteredDocuments.length === 0 && (
                <div className="empty-state">
                    <FileText size={48} strokeWidth={1} />
                    <h3>No documents found</h3>
                    <p>
                        {searchQuery
                            ? 'Try adjusting your search query'
                            : 'Upload files or crawl web content to get started'}
                    </p>
                </div>
            )}

            {!loading && filteredDocuments.length > 0 && (
                <>
                    <div className="documents-table">
                        <table>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Content Preview</th>
                                    <th>Collection</th>
                                    <th>Metadata</th>
                                    <th>Created</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredDocuments.map((doc) => (
                                    <tr key={doc.id}>
                                        <td className="doc-id" title={doc.id}>
                                            {doc.id.substring(0, 8)}...
                                        </td>
                                        <td className="doc-content">
                                            {doc.content.substring(0, 100)}
                                            {doc.content.length > 100 && '...'}
                                        </td>
                                        <td className="doc-collection">
                                            <span className="collection-badge">{doc.collection}</span>
                                        </td>
                                        <td className="doc-metadata">
                                            {Object.keys(doc.metadata).length > 0 ? (
                                                <span className="metadata-count">
                                                    {Object.keys(doc.metadata).length} fields
                                                </span>
                                            ) : (
                                                <span className="no-metadata">No metadata</span>
                                            )}
                                        </td>
                                        <td className="doc-created">
                                            {doc.created_at
                                                ? new Date(doc.created_at).toLocaleDateString()
                                                : 'N/A'}
                                        </td>
                                        <td className="doc-actions">
                                            <button
                                                className="btn-icon btn-view"
                                                onClick={() => handleViewDocument(doc.id)}
                                                title="View full content"
                                            >
                                                <Eye size={16} />
                                            </button>
                                            <button
                                                className="btn-icon btn-delete"
                                                onClick={() => setDeleteConfirm(doc.id)}
                                                title="Delete document"
                                            >
                                                <Trash2 size={16} />
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>

                    <div className="pagination">
                        <div className="pagination-info">
                            Showing {(currentPage - 1) * pageSize + 1} to{' '}
                            {Math.min(currentPage * pageSize, totalCount)} of {totalCount} documents
                        </div>
                        <div className="pagination-controls">
                            <button
                                className="btn-page"
                                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                                disabled={currentPage === 1}
                            >
                                <ChevronLeft size={18} />
                                Previous
                            </button>
                            <span className="page-indicator">
                                Page {currentPage} of {totalPages}
                            </span>
                            <button
                                className="btn-page"
                                onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                                disabled={currentPage === totalPages}
                            >
                                Next
                                <ChevronRight size={18} />
                            </button>
                        </div>
                    </div>
                </>
            )}

            {/* View Document Modal */}
            {viewingDoc && (
                <div className="modal-overlay" onClick={() => setViewingDoc(null)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h3>Document Content</h3>
                            <button className="btn-close" onClick={() => setViewingDoc(null)}>
                                <X size={20} />
                            </button>
                        </div>
                        <div className="modal-body">
                            <div className="doc-detail">
                                <div className="detail-row">
                                    <strong>ID:</strong>
                                    <span>{viewingDoc.id}</span>
                                </div>
                                <div className="detail-row">
                                    <strong>Collection:</strong>
                                    <span className="collection-badge">{viewingDoc.collection}</span>
                                </div>
                                <div className="detail-row">
                                    <strong>Created:</strong>
                                    <span>
                                        {viewingDoc.created_at
                                            ? new Date(viewingDoc.created_at).toLocaleString()
                                            : 'N/A'}
                                    </span>
                                </div>
                                {Object.keys(viewingDoc.metadata).length > 0 && (
                                    <div className="detail-row">
                                        <strong>Metadata:</strong>
                                        <pre>{JSON.stringify(viewingDoc.metadata, null, 2)}</pre>
                                    </div>
                                )}
                                <div className="detail-row full-width">
                                    <strong>Content:</strong>
                                    <div className="content-box">{viewingDoc.content}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Delete Confirmation Modal */}
            {deleteConfirm && (
                <div className="modal-overlay" onClick={() => setDeleteConfirm(null)}>
                    <div className="modal-content small" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h3>Confirm Delete</h3>
                            <button className="btn-close" onClick={() => setDeleteConfirm(null)}>
                                <X size={20} />
                            </button>
                        </div>
                        <div className="modal-body">
                            <p>Are you sure you want to delete this document?</p>
                            <p className="warning-text">This action cannot be undone.</p>
                        </div>
                        <div className="modal-footer">
                            <button className="btn-cancel" onClick={() => setDeleteConfirm(null)}>
                                Cancel
                            </button>
                            <button
                                className="btn-delete-confirm"
                                onClick={() => handleDeleteDocument(deleteConfirm)}
                            >
                                <Trash2 size={16} />
                                Delete
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}

