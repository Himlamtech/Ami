# AMI Chatbot Frontend

Giao diện web cho AMI - Trợ lý thông minh của Học viện PTIT.

## Tech Stack

- **React 18** - UI Library
- **TypeScript** - Type Safety
- **Vite** - Build Tool
- **Tailwind CSS** - Styling
- **shadcn/ui** - Component Library (Radix-based)
- **TanStack Query** - Server State Management
- **Zustand** - Client State Management
- **React Router** - Routing

## Getting Started

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
src/
├── components/          # Shared components
│   ├── ui/             # shadcn/ui components
│   ├── chat/           # Chat-specific components
│   ├── admin/          # Admin-specific components
│   └── shared/         # Shared components
├── features/           # Feature modules
│   ├── chat/           # Chat feature
│   └── admin/          # Admin feature
├── hooks/              # Global hooks
├── layouts/            # Layout components
├── lib/                # Utilities
├── stores/             # Zustand stores
└── types/              # TypeScript types
```

## Routes

### Chat (User)
- `/` - New chat
- `/chat/:sessionId` - Existing conversation

### Admin
- `/admin` - Dashboard
- `/admin/conversations` - Conversation management
- `/admin/feedback` - Feedback analysis
- `/admin/analytics` - Analytics & costs
- `/admin/knowledge` - Knowledge base quality
- `/admin/users` - User profiles
- `/admin/settings` - Settings (prompts, models)

## Design System

### Colors
- **Primary**: PTIT Red (#DC2626)
- **Secondary**: Blue (#3B82F6)
- **Neutral**: Gray scale
- **Semantic**: Success, Warning, Error, Info

### Typography
- **Font**: Inter (primary), JetBrains Mono (code)
- **Sizes**: Display (36px) → Caption (12px)

### Spacing
- Based on 8px scale: xs(4px), sm(8px), md(16px), lg(24px), xl(32px)

## API Integration

The frontend expects a backend API at `/api/v1/`. Configure the proxy in `vite.config.ts`.

## Environment Variables

Create a `.env` file:

```env
VITE_API_URL=http://localhost:8000
```
