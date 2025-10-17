# AMI Admin UI - PTIT Document Management

React-based admin interface for managing documents in the AMI RAG System.

## Features

- 🔐 JWT Authentication
- 📄 Document Management (CRUD)
- 📦 Collection Organization
- 🗑️ Soft Delete/Restore
- 📊 Dashboard Overview
- 🎨 Material-UI Design

## Tech Stack

- **React 18** with TypeScript
- **Vite** for fast development
- **Material-UI** for components
- **React Query** for data fetching
- **Zustand** for state management
- **Axios** for API calls

## Getting Started

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

The app will run on `http://localhost:6009` with API proxy to `http://localhost:6008`.

### Build for Production

```bash
npm run build
```

## Environment Variables

Create a `.env` file:

```
VITE_API_URL=http://localhost:6008/api/v1
```

## Default Credentials

- **Username**: `admin`
- **Password**: `admin`

⚠️ **Change the password after first login!**

## Project Structure

```
src/
├── api/
│   └── client.ts         # API client and endpoints
├── components/
│   └── Layout.tsx        # Main layout with navigation
├── pages/
│   ├── Login.tsx         # Login page
│   ├── Dashboard.tsx     # Dashboard overview
│   └── Documents.tsx     # Document management
├── store/
│   └── authStore.ts      # Auth state management
├── App.tsx               # Main app component
└── main.tsx              # Entry point
```

## API Integration

The frontend connects to the FastAPI backend at `/api/v1`:

- `POST /auth/login` - Login
- `GET /auth/me` - Get current user
- `GET /admin/documents/` - List documents
- `POST /admin/documents/` - Upload document
- `PUT /admin/documents/{id}` - Update document
- `DELETE /admin/documents/{id}` - Soft delete
- `POST /admin/documents/{id}/restore` - Restore document

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## License

Private - For PTIT use only

