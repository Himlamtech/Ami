import { Component, ErrorInfo, ReactNode } from 'react'
import { Button } from '@/components/ui/button'
import { AlertTriangle, RefreshCw } from 'lucide-react'

interface Props {
    children: ReactNode
    fallback?: ReactNode
}

interface State {
    hasError: boolean
    error?: Error
}

export default class ErrorBoundary extends Component<Props, State> {
    public state: State = {
        hasError: false,
    }

    public static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error }
    }

    public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        console.error('Uncaught error:', error, errorInfo)
    }

    private handleReset = () => {
        this.setState({ hasError: false, error: undefined })
    }

    public render() {
        if (this.state.hasError) {
            if (this.props.fallback) {
                return this.props.fallback
            }

            return (
                <div className="flex flex-col items-center justify-center min-h-[400px] p-8">
                    <div className="p-4 rounded-full bg-error/10 mb-4">
                        <AlertTriangle className="w-8 h-8 text-error" />
                    </div>
                    <h2 className="text-xl font-semibold text-neutral-900 mb-2">
                        Đã xảy ra lỗi
                    </h2>
                    <p className="text-neutral-500 text-center mb-4 max-w-md">
                        Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại hoặc liên hệ hỗ trợ nếu vấn đề vẫn tiếp tục.
                    </p>
                    {this.state.error && (
                        <pre className="text-xs text-neutral-400 bg-neutral-100 p-3 rounded-lg mb-4 max-w-md overflow-auto">
                            {this.state.error.message}
                        </pre>
                    )}
                    <Button onClick={this.handleReset}>
                        <RefreshCw className="w-4 h-4 mr-2" />
                        Thử lại
                    </Button>
                </div>
            )
        }

        return this.props.children
    }
}
