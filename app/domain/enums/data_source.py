"""Data source enumerations."""

from enum import Enum


class DataCategory(str, Enum):
    """Category of data content."""

    ADMISSION = "admission"  # Tuyển sinh
    ACADEMIC = "academic"  # Đào tạo
    NEWS = "news"  # Tin tức
    ANNOUNCEMENT = "announcement"  # Thông báo
    DEPARTMENT = "department"  # Khoa/Phòng ban
    MAJOR = "major"  # Ngành học
    SCHEDULE = "schedule"  # Lịch học/thi
    SCORE = "score"  # Điểm số
    FORM = "form"  # Biểu mẫu
    REGULATION = "regulation"  # Quy định/quy chế
    GENERAL = "general"  # Thông tin chung
    OTHER = "other"


class DataType(str, Enum):
    """Type of data based on update frequency."""

    FIXED = "fixed"  # Ít thay đổi (lịch sử, quy chế)
    PERIODIC = "periodic"  # Thay đổi theo chu kỳ (điểm, lịch)
    REALTIME = "realtime"  # Cập nhật thường xuyên (tin tức)


class SourceType(str, Enum):
    """Type of data source."""

    WEB_CRAWL = "web_crawl"  # Crawl website
    API = "api"  # REST API
    RSS = "rss"  # RSS Feed
    SITEMAP = "sitemap"  # Sitemap XML
    MANUAL = "manual"  # Upload thủ công


class SourceStatus(str, Enum):
    """Status of a data source."""

    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"
    DISABLED = "disabled"


class UpdateDetectionType(str, Enum):
    """Type of update detection result."""

    NEW = "new"  # Dữ liệu hoàn toàn mới
    UPDATE = "update"  # Cập nhật dữ liệu cũ
    DUPLICATE = "duplicate"  # Trùng lặp
    CONFLICT = "conflict"  # Xung đột cần review
    UNRELATED = "unrelated"  # Không liên quan


class PendingStatus(str, Enum):
    """Status of pending update."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    AUTO_APPROVED = "auto_approved"
    EXPIRED = "expired"
