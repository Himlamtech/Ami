# Ami Chat - Modern Chat UI

A beautiful, modern ChatGPT-like interface for the AMI RAG System, powered by advanced AI with file upload, voice support, and intelligent chat history.

## ✨ Features

### Chat Interface
- 💬 **Real-time Chat** - Stream-based responses for instant feedback
- 📎 **File Upload** - Support for documents, images, PDFs
- 🎤 **Voice Recording** - Record and transcribe messages
- 🖼️ **Image Support** - Display and process images in conversations
- 📝 **Chat History** - Persistent chat sessions with auto-generated titles
- 🔍 **Session Search** - Quickly find previous conversations

### AI Capabilities
- ⚡ **Three Thinking Modes**:
  - **Fast** - Quick responses for simple queries
  - **Balance** - Recommended for most use cases
  - **Deep Thinking** - Extended reasoning for complex problems
- 🧠 **RAG Integration** - Document-based Q&A with configurable retrieval
- 🌐 **Web Search** - Real-time web searching capability
- 🎯 **Retrieval Control** - Fine-tune document matching with threshold settings

### Modern UI/UX
- 🎨 **Charter Font Design** - Premium typography throughout
- 🌸 **Soft Red/Pink Theme** - Comfortable, modern color palette
- ⚙️ **Dark Mode Ready** - Easy theme switching capability
- 📱 **Fully Responsive** - Works perfectly on mobile, tablet, desktop
- ♿ **Accessibility** - WCAG compliant design
- 🎭 **Smooth Animations** - Polished transitions and interactions

### Configuration Panel
- **Model Selection** - Choose thinking modes and models
- **RAG Settings** - Adjust top-k results and similarity thresholds
- **Generation Config** - Fine-tune temperature, tokens, penalties
- **Collection Management** - Select document collections to search

## 🏗️ Architecture

```
frontend/
├── src/
│   ├── api/
│   │   └── client.ts              # API integration layer
│   ├── components/
│   │   ├── __ami__/               # Chat interface components
│   │   │   ├── ChatSidebar.tsx    # Session history sidebar
│   │   │   ├── ChatHeader.tsx     # Header with controls
│   │   │   ├── MessageList.tsx    # Message display area
│   │   │   ├── MessageBubble.tsx  # Individual message component
│   │   │   ├── MessageInput.tsx   # Input with file upload
│   │   │   └── SettingsPanel.tsx  # Chat configuration
│   │   └── __data__/              # Data management components
│   ├── pages/
│   │   ├── Login.tsx              # Authentication
│   │   └── Chat.tsx               # Main chat interface
│   ├── store/
│   │   ├── authStore.ts           # Authentication state
│   │   └── chatStore.ts           # Chat state management
│   ├── styles/
│   │   ├── __ami__/               # Chat styles
│   │   └── __data__/              # Data management styles
│   ├── App.tsx                    # Main application
│   ├── index.css                  # Global styles
│   └── main.tsx                   # Entry point
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## 🚀 Getting Started

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

The app will run on `http://localhost:5173`

### Build for Production

```bash
npm run build
```

## 🔐 Authentication

Default credentials for demo:
- **Username**: `admin`
- **Password**: `admin`

⚠️ **Important**: Change credentials in production!

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_URL=http://localhost:11121/api/v1
```

### API Integration

The frontend connects to the FastAPI backend with endpoints for:
- Chat generation (with streaming)
- Chat history management
- Session management
- Document upload and retrieval
- Configuration endpoints

## 🎯 Key Components

### ChatSidebar
- Display all chat sessions
- Search functionality
- Quick create new chat
- Session management (delete, archive)

### ChatHeader
- Display current session title
- Settings access
- User profile and logout
- Sidebar toggle (mobile)

### MessageList
- Infinite scroll support
- Auto-scroll to latest message
- Typing indicators
- Loading states

### MessageInput
- Multi-line input with auto-resize
- File attachment support
- Voice recording button
- Smart send button (disabled when empty)

### SettingsPanel
- Thinking mode selection
- RAG configuration
- Temperature and token settings
- Web search toggle
- Collection selection

## 🎨 Design System

### Color Palette
- **Primary**: `#ff8a9a` (Soft Red/Pink)
- **Primary Dark**: `#ff5c7c`
- **Background**: `#ffffff` (Primary), `#f9fafb` (Secondary)
- **Text**: `#111827` (Primary), `#4b5563` (Secondary)

### Typography
- **Font**: Charter (primary), system fallbacks
- **Sizes**: 12px to 2rem with proper hierarchy
- **Weights**: 400, 500, 600, 700

### Spacing
- **Base Unit**: 1rem (16px)
- **Scale**: xs (0.25rem) → 2xl (3rem)

### Border Radius
- **Small**: 0.375rem
- **Medium**: 0.5rem
- **Large**: 0.75rem
- **XL**: 1rem
- **2XL**: 1.5rem

## 📦 Dependencies

- **React 18**: UI framework
- **React Router DOM 6**: Navigation
- **TanStack React Query 5**: Data fetching
- **Axios**: HTTP client
- **Zustand 4**: State management
- **Emotion**: CSS-in-JS (via MUI)
- **Dayjs**: Date handling
- **Framer Motion**: Animations

## 🧪 Testing

Run ESLint:
```bash
npm run lint
```

## 🤝 Contributing

1. Follow the existing code structure
2. Use Charter font for all typography
3. Maintain soft red/pink color scheme
4. Ensure mobile responsiveness
5. Add accessibility attributes where needed

## 📝 License

Private - For internal use only

## 🆘 Support

For issues or questions, contact the development team.

