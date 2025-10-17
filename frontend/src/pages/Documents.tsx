import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
    Box,
    Button,
    Card,
    CardContent,
    Chip,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    IconButton,
    Paper,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    TextField,
    Typography,
    Alert,
    CircularProgress,
} from '@mui/material'
import {
    Delete,
    Edit,
    Restore,
    Upload,
    CheckCircle,
    Cancel,
} from '@mui/icons-material'
import { documentsAPI } from '../api/client'

export default function Documents() {
    const queryClient = useQueryClient()
    const [uploadOpen, setUploadOpen] = useState(false)
    const [editOpen, setEditOpen] = useState(false)
    const [selectedFile, setSelectedFile] = useState<File | null>(null)
    const [collection, setCollection] = useState('default')
    const [editData, setEditData] = useState<any>(null)

    // Fetch documents
    const { data, isLoading, error } = useQuery({
        queryKey: ['documents'],
        queryFn: () => documentsAPI.list({ limit: 100 }),
    })

    // Upload mutation
    const uploadMutation = useMutation({
        mutationFn: (data: { file: File; collection: string }) =>
            documentsAPI.upload(data.file, data.collection),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['documents'] })
            setUploadOpen(false)
            setSelectedFile(null)
            setCollection('default')
        },
    })

    // Update mutation
    const updateMutation = useMutation({
        mutationFn: (data: { id: string; updates: any }) =>
            documentsAPI.update(data.id, data.updates),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['documents'] })
            setEditOpen(false)
            setEditData(null)
        },
    })

    // Delete mutation
    const deleteMutation = useMutation({
        mutationFn: (id: string) => documentsAPI.softDelete(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['documents'] })
        },
    })

    // Restore mutation
    const restoreMutation = useMutation({
        mutationFn: (id: string) => documentsAPI.restore(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['documents'] })
        },
    })

    const handleUpload = () => {
        if (selectedFile) {
            uploadMutation.mutate({ file: selectedFile, collection })
        }
    }

    const handleEdit = (doc: any) => {
        setEditData({
            id: doc.id,
            filename: doc.filename,
            collection: doc.collection,
        })
        setEditOpen(true)
    }

    const handleUpdate = () => {
        if (editData) {
            updateMutation.mutate({
                id: editData.id,
                updates: {
                    filename: editData.filename,
                    collection: editData.collection,
                },
            })
        }
    }

    if (isLoading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
                <CircularProgress />
            </Box>
        )
    }

    if (error) {
        return (
            <Alert severity="error">
                Failed to load documents: {(error as any).message}
            </Alert>
        )
    }

    const documents = data?.documents || []

    return (
        <Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
                <Typography variant="h4">Documents</Typography>
                <Button
                    variant="contained"
                    startIcon={<Upload />}
                    onClick={() => setUploadOpen(true)}
                >
                    Upload Document
                </Button>
            </Box>

            <Card>
                <CardContent>
                    <Typography variant="h6" gutterBottom>
                        Total: {data?.total || 0} documents
                    </Typography>

                    <TableContainer component={Paper} sx={{ mt: 2 }}>
                        <Table>
                            <TableHead>
                                <TableRow>
                                    <TableCell>Filename</TableCell>
                                    <TableCell>Collection</TableCell>
                                    <TableCell>Chunks</TableCell>
                                    <TableCell>Status</TableCell>
                                    <TableCell>Uploaded By</TableCell>
                                    <TableCell>Actions</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {documents.map((doc: any) => (
                                    <TableRow key={doc.id}>
                                        <TableCell>{doc.filename}</TableCell>
                                        <TableCell>
                                            <Chip label={doc.collection} size="small" />
                                        </TableCell>
                                        <TableCell>{doc.chunk_count}</TableCell>
                                        <TableCell>
                                            {doc.is_active ? (
                                                <Chip
                                                    icon={<CheckCircle />}
                                                    label="Active"
                                                    color="success"
                                                    size="small"
                                                />
                                            ) : (
                                                <Chip
                                                    icon={<Cancel />}
                                                    label="Inactive"
                                                    color="default"
                                                    size="small"
                                                />
                                            )}
                                        </TableCell>
                                        <TableCell>{doc.uploaded_by || '-'}</TableCell>
                                        <TableCell>
                                            <IconButton
                                                size="small"
                                                onClick={() => handleEdit(doc)}
                                                title="Edit"
                                            >
                                                <Edit fontSize="small" />
                                            </IconButton>
                                            {doc.is_active ? (
                                                <IconButton
                                                    size="small"
                                                    color="error"
                                                    onClick={() => deleteMutation.mutate(doc.id)}
                                                    title="Soft Delete"
                                                >
                                                    <Delete fontSize="small" />
                                                </IconButton>
                                            ) : (
                                                <IconButton
                                                    size="small"
                                                    color="success"
                                                    onClick={() => restoreMutation.mutate(doc.id)}
                                                    title="Restore"
                                                >
                                                    <Restore fontSize="small" />
                                                </IconButton>
                                            )}
                                        </TableCell>
                                    </TableRow>
                                ))}
                                {documents.length === 0 && (
                                    <TableRow>
                                        <TableCell colSpan={6} align="center">
                                            No documents found. Upload your first document!
                                        </TableCell>
                                    </TableRow>
                                )}
                            </TableBody>
                        </Table>
                    </TableContainer>
                </CardContent>
            </Card>

            {/* Upload Dialog */}
            <Dialog open={uploadOpen} onClose={() => setUploadOpen(false)} maxWidth="sm" fullWidth>
                <DialogTitle>Upload Document</DialogTitle>
                <DialogContent>
                    <TextField
                        label="Collection"
                        fullWidth
                        margin="normal"
                        value={collection}
                        onChange={(e) => setCollection(e.target.value)}
                    />
                    <Button variant="outlined" component="label" fullWidth sx={{ mt: 2 }}>
                        Choose File
                        <input
                            type="file"
                            hidden
                            onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                        />
                    </Button>
                    {selectedFile && (
                        <Typography variant="body2" sx={{ mt: 1 }}>
                            Selected: {selectedFile.name}
                        </Typography>
                    )}
                    {uploadMutation.isError && (
                        <Alert severity="error" sx={{ mt: 2 }}>
                            Upload failed: {(uploadMutation.error as any)?.message}
                        </Alert>
                    )}
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setUploadOpen(false)}>Cancel</Button>
                    <Button
                        onClick={handleUpload}
                        variant="contained"
                        disabled={!selectedFile || uploadMutation.isPending}
                    >
                        {uploadMutation.isPending ? 'Uploading...' : 'Upload'}
                    </Button>
                </DialogActions>
            </Dialog>

            {/* Edit Dialog */}
            <Dialog open={editOpen} onClose={() => setEditOpen(false)} maxWidth="sm" fullWidth>
                <DialogTitle>Edit Document</DialogTitle>
                <DialogContent>
                    <TextField
                        label="Filename"
                        fullWidth
                        margin="normal"
                        value={editData?.filename || ''}
                        onChange={(e) => setEditData({ ...editData, filename: e.target.value })}
                    />
                    <TextField
                        label="Collection"
                        fullWidth
                        margin="normal"
                        value={editData?.collection || ''}
                        onChange={(e) => setEditData({ ...editData, collection: e.target.value })}
                    />
                    {updateMutation.isError && (
                        <Alert severity="error" sx={{ mt: 2 }}>
                            Update failed: {(updateMutation.error as any)?.message}
                        </Alert>
                    )}
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setEditOpen(false)}>Cancel</Button>
                    <Button
                        onClick={handleUpdate}
                        variant="contained"
                        disabled={updateMutation.isPending}
                    >
                        {updateMutation.isPending ? 'Updating...' : 'Update'}
                    </Button>
                </DialogActions>
            </Dialog>
        </Box>
    )
}

