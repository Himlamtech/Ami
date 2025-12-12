import { Link } from "react-router-dom"

export default function Footer() {
    return (
        <footer className="border-t bg-gray-50/50 backdrop-blur-sm">
            <div className="container px-4 py-12 mx-auto">
                <div className="grid grid-cols-1 gap-8 md:grid-cols-4">
                    <div className="space-y-4">
                        <div className="flex items-center space-x-2">
                            <span className="text-xl font-bold text-primary">Ami Assistant</span>
                        </div>
                        <p className="text-sm text-gray-500">
                            Trợ lý ảo thông minh hỗ trợ sinh viên Học Viện Công Nghệ Bưu Chính Viễn Thông.
                        </p>
                    </div>

                    <div>
                        <h4 className="font-semibold mb-4">Liên kết</h4>
                        <ul className="space-y-2 text-sm text-gray-600">
                            <li><Link to="/" className="hover:text-primary">Trang chủ</Link></li>
                            <li><Link to="/chat" className="hover:text-primary">Chat ngay</Link></li>
                            <li><Link to="/login" className="hover:text-primary">Đăng nhập</Link></li>
                        </ul>
                    </div>

                    <div>
                        <h4 className="font-semibold mb-4">Tài nguyên</h4>
                        <ul className="space-y-2 text-sm text-gray-600">
                            <li><a href="#" className="hover:text-primary">Hướng dẫn sử dụng</a></li>
                            <li><a href="#" className="hover:text-primary">Câu hỏi thường gặp</a></li>
                            <li><a href="#" className="hover:text-primary">Điều khoản bảo mật</a></li>
                        </ul>
                    </div>

                    <div>
                        <h4 className="font-semibold mb-4">Liên hệ</h4>
                        <ul className="space-y-2 text-sm text-gray-600">
                            <li>Email: support@ptit.edu.vn</li>
                            <li>Hotline: (024) 3333 8888</li>
                        </ul>
                    </div>
                </div>
                <div className="pt-8 mt-8 text-center text-sm text-gray-400 border-t">
                    © {new Date().getFullYear()} PTIT Ami Assistant. All rights reserved.
                </div>
            </div>
        </footer>
    )
}
