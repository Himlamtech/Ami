import { useEffect, useState } from 'react'
import { Users, UserPlus, Search, Edit2, Trash2, Shield, User as UserIcon, Mail, Calendar, CheckCircle, XCircle } from 'lucide-react'
import { apiClient, User, UserCreate, UserUpdate } from '../api/client'
import '../styles/__admin__/UserManagement.css'

export default function UserManagement() {
    const [users, setUsers] = useState<User[]>([])
    const [total, setTotal] = useState(0)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    // Pagination
    const [currentPage, setCurrentPage] = useState(1)
    const [limit] = useState(10)

    // Filters
    const [searchQuery, setSearchQuery] = useState('')
    const [filterActive, setFilterActive] = useState<boolean | undefined>(undefined)

    // Modal states
    const [showCreateModal, setShowCreateModal] = useState(false)
    const [showEditModal, setShowEditModal] = useState(false)
    const [selectedUser, setSelectedUser] = useState<User | null>(null)

    // Form data
    const [formData, setFormData] = useState<UserCreate>({
        username: '',
        email: '',
        password: '',
        full_name: '',
        role: 'user',
        is_active: true,
    })

    useEffect(() => {
        loadUsers()
    }, [currentPage, filterActive])

    const loadUsers = async () => {
        setLoading(true)
        setError(null)
        try {
            const skip = (currentPage - 1) * limit
            const response = await apiClient.getUsers(skip, limit, filterActive)
            setUsers(response.users)
            setTotal(response.total)
        } catch (err) {
            setError('Failed to load users')
            console.error(err)
        } finally {
            setLoading(false)
        }
    }

    const handleCreateUser = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)
        setError(null)
        try {
            await apiClient.registerUser(formData)
            setShowCreateModal(false)
            resetForm()
            loadUsers()
        } catch (err: unknown) {
            if (err instanceof Error) {
                setError(err.message)
            } else {
                setError('Failed to create user')
            }
        } finally {
            setLoading(false)
        }
    }

    const handleUpdateUser = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!selectedUser) return

        setLoading(true)
        setError(null)
        try {
            const updateData: UserUpdate = {
                email: formData.email,
                full_name: formData.full_name,
                role: formData.role,
                is_active: formData.is_active,
            }
            if (formData.password) {
                updateData.password = formData.password
            }

            await apiClient.updateUser(selectedUser.id, updateData)
            setShowEditModal(false)
            resetForm()
            loadUsers()
        } catch (err: unknown) {
            if (err instanceof Error) {
                setError(err.message)
            } else {
                setError('Failed to update user')
            }
        } finally {
            setLoading(false)
        }
    }

    const handleDeleteUser = async (userId: string) => {
        if (!confirm('Are you sure you want to deactivate this user?')) return

        setLoading(true)
        setError(null)
        try {
            await apiClient.deleteUser(userId)
            loadUsers()
        } catch (err: unknown) {
            if (err instanceof Error) {
                setError(err.message)
            } else {
                setError('Failed to delete user')
            }
        } finally {
            setLoading(false)
        }
    }

    const openEditModal = (user: User) => {
        setSelectedUser(user)
        setFormData({
            username: user.username,
            email: user.email,
            password: '',
            full_name: user.full_name || '',
            role: user.role,
            is_active: user.is_active,
        })
        setShowEditModal(true)
    }

    const resetForm = () => {
        setFormData({
            username: '',
            email: '',
            password: '',
            full_name: '',
            role: 'user',
            is_active: true,
        })
        setSelectedUser(null)
    }

    const filteredUsers = users.filter(user =>
        user.username.toLowerCase().includes(searchQuery.toLowerCase()) ||
        user.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (user.full_name && user.full_name.toLowerCase().includes(searchQuery.toLowerCase()))
    )

    const totalPages = Math.ceil(total / limit)

    return (
        <div className="user-management">
            <div className="user-management-header">
                <div className="header-content">
                    <h1>
                        <Users size={32} />
                        User Management
                    </h1>
                    <p>Manage system users and permissions</p>
                </div>
                <button className="btn-primary" onClick={() => setShowCreateModal(true)}>
                    <UserPlus size={20} />
                    <span>Create User</span>
                </button>
            </div>

            {error && (
                <div className="error-banner">
                    <XCircle size={20} />
                    <span>{error}</span>
                    <button onClick={() => setError(null)}>×</button>
                </div>
            )}

            <div className="user-filters">
                <div className="search-box">
                    <Search size={18} />
                    <input
                        type="text"
                        placeholder="Search users..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                    />
                </div>
                <div className="filter-buttons">
                    <button
                        className={filterActive === undefined ? 'active' : ''}
                        onClick={() => setFilterActive(undefined)}
                    >
                        All Users
                    </button>
                    <button
                        className={filterActive === true ? 'active' : ''}
                        onClick={() => setFilterActive(true)}
                    >
                        Active
                    </button>
                    <button
                        className={filterActive === false ? 'active' : ''}
                        onClick={() => setFilterActive(false)}
                    >
                        Inactive
                    </button>
                </div>
            </div>

            {loading && (
                <div className="loading-overlay">
                    <div className="loader"></div>
                    <p>Loading users...</p>
                </div>
            )}

            <div className="users-table-container">
                <table className="users-table">
                    <thead>
                        <tr>
                            <th>Username</th>
                            <th>Email</th>
                            <th>Full Name</th>
                            <th>Role</th>
                            <th>Status</th>
                            <th>Created</th>
                            <th>Last Login</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filteredUsers.map((user) => (
                            <tr key={user.id}>
                                <td>
                                    <div className="user-cell">
                                        <UserIcon size={16} />
                                        <span>{user.username}</span>
                                    </div>
                                </td>
                                <td>
                                    <div className="email-cell">
                                        <Mail size={14} />
                                        <span>{user.email}</span>
                                    </div>
                                </td>
                                <td>{user.full_name || '-'}</td>
                                <td>
                                    <span className={`role-badge ${user.role}`}>
                                        {user.role === 'admin' && <Shield size={14} />}
                                        {user.role}
                                    </span>
                                </td>
                                <td>
                                    <span className={`status-badge ${user.is_active ? 'active' : 'inactive'}`}>
                                        {user.is_active ? <CheckCircle size={14} /> : <XCircle size={14} />}
                                        {user.is_active ? 'Active' : 'Inactive'}
                                    </span>
                                </td>
                                <td>
                                    <div className="date-cell">
                                        <Calendar size={14} />
                                        <span>{new Date(user.created_at).toLocaleDateString()}</span>
                                    </div>
                                </td>
                                <td>
                                    {user.last_login ? (
                                        <div className="date-cell">
                                            <Calendar size={14} />
                                            <span>{new Date(user.last_login).toLocaleDateString()}</span>
                                        </div>
                                    ) : (
                                        '-'
                                    )}
                                </td>
                                <td>
                                    <div className="action-buttons">
                                        <button
                                            className="btn-icon"
                                            onClick={() => openEditModal(user)}
                                            title="Edit user"
                                        >
                                            <Edit2 size={16} />
                                        </button>
                                        <button
                                            className="btn-icon btn-danger"
                                            onClick={() => handleDeleteUser(user.id)}
                                            title="Deactivate user"
                                        >
                                            <Trash2 size={16} />
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>

                {filteredUsers.length === 0 && !loading && (
                    <div className="empty-state">
                        <Users size={48} />
                        <p>No users found</p>
                    </div>
                )}
            </div>

            <div className="pagination">
                <div className="pagination-info">
                    Showing {((currentPage - 1) * limit) + 1} to {Math.min(currentPage * limit, total)} of {total} users
                </div>
                <div className="pagination-controls">
                    <button
                        onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                        disabled={currentPage === 1}
                    >
                        Previous
                    </button>
                    <span>Page {currentPage} of {totalPages}</span>
                    <button
                        onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                        disabled={currentPage === totalPages}
                    >
                        Next
                    </button>
                </div>
            </div>

            {/* Create User Modal */}
            {showCreateModal && (
                <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2>
                                <UserPlus size={24} />
                                Create New User
                            </h2>
                            <button className="modal-close" onClick={() => setShowCreateModal(false)}>
                                ×
                            </button>
                        </div>
                        <form onSubmit={handleCreateUser}>
                            <div className="form-group">
                                <label>Username *</label>
                                <input
                                    type="text"
                                    required
                                    minLength={3}
                                    value={formData.username}
                                    onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                                    placeholder="Enter username"
                                />
                            </div>
                            <div className="form-group">
                                <label>Email *</label>
                                <input
                                    type="email"
                                    required
                                    value={formData.email}
                                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                    placeholder="Enter email"
                                />
                            </div>
                            <div className="form-group">
                                <label>Password *</label>
                                <input
                                    type="password"
                                    required
                                    minLength={8}
                                    value={formData.password}
                                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                                    placeholder="Enter password (min 8 characters)"
                                />
                            </div>
                            <div className="form-group">
                                <label>Full Name</label>
                                <input
                                    type="text"
                                    value={formData.full_name}
                                    onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                                    placeholder="Enter full name"
                                />
                            </div>
                            <div className="form-group">
                                <label>Role *</label>
                                <select
                                    value={formData.role}
                                    onChange={(e) => setFormData({ ...formData, role: e.target.value as 'admin' | 'user' })}
                                >
                                    <option value="user">User</option>
                                    <option value="admin">Admin</option>
                                </select>
                            </div>
                            <div className="form-group checkbox-group">
                                <label>
                                    <input
                                        type="checkbox"
                                        checked={formData.is_active}
                                        onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                                    />
                                    <span>Active</span>
                                </label>
                            </div>
                            <div className="modal-actions">
                                <button type="button" className="btn-secondary" onClick={() => setShowCreateModal(false)}>
                                    Cancel
                                </button>
                                <button type="submit" className="btn-primary" disabled={loading}>
                                    {loading ? 'Creating...' : 'Create User'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* Edit User Modal */}
            {showEditModal && selectedUser && (
                <div className="modal-overlay" onClick={() => setShowEditModal(false)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2>
                                <Edit2 size={24} />
                                Edit User: {selectedUser.username}
                            </h2>
                            <button className="modal-close" onClick={() => setShowEditModal(false)}>
                                ×
                            </button>
                        </div>
                        <form onSubmit={handleUpdateUser}>
                            <div className="form-group">
                                <label>Username</label>
                                <input
                                    type="text"
                                    value={formData.username}
                                    disabled
                                    className="disabled-input"
                                />
                                <small>Username cannot be changed</small>
                            </div>
                            <div className="form-group">
                                <label>Email *</label>
                                <input
                                    type="email"
                                    required
                                    value={formData.email}
                                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                    placeholder="Enter email"
                                />
                            </div>
                            <div className="form-group">
                                <label>New Password</label>
                                <input
                                    type="password"
                                    minLength={8}
                                    value={formData.password}
                                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                                    placeholder="Leave empty to keep current password"
                                />
                                <small>Leave empty to keep current password</small>
                            </div>
                            <div className="form-group">
                                <label>Full Name</label>
                                <input
                                    type="text"
                                    value={formData.full_name}
                                    onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                                    placeholder="Enter full name"
                                />
                            </div>
                            <div className="form-group">
                                <label>Role *</label>
                                <select
                                    value={formData.role}
                                    onChange={(e) => setFormData({ ...formData, role: e.target.value as 'admin' | 'user' })}
                                >
                                    <option value="user">User</option>
                                    <option value="admin">Admin</option>
                                </select>
                            </div>
                            <div className="form-group checkbox-group">
                                <label>
                                    <input
                                        type="checkbox"
                                        checked={formData.is_active}
                                        onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                                    />
                                    <span>Active</span>
                                </label>
                            </div>
                            <div className="modal-actions">
                                <button type="button" className="btn-secondary" onClick={() => setShowEditModal(false)}>
                                    Cancel
                                </button>
                                <button type="submit" className="btn-primary" disabled={loading}>
                                    {loading ? 'Updating...' : 'Update User'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    )
}

