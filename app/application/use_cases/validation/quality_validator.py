"""Quality validator use case for content validation."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import re
import logging

logger = logging.getLogger(__name__)


class IssueSeverity(Enum):
    """Severity level of validation issues."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationIssue:
    """A single validation issue."""

    code: str
    message: str
    severity: IssueSeverity
    field: Optional[str] = None
    suggestion: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity.value,
            "field": self.field,
            "suggestion": self.suggestion,
        }


@dataclass
class ValidationResult:
    """Result from content validation."""

    is_valid: bool = True
    score: float = 100.0  # Quality score 0-100
    issues: List[ValidationIssue] = field(default_factory=list)
    checked_at: datetime = field(default_factory=datetime.now)

    def add_issue(self, issue: ValidationIssue) -> None:
        self.issues.append(issue)
        if issue.severity == IssueSeverity.ERROR:
            self.is_valid = False
            self.score -= 20
        elif issue.severity == IssueSeverity.CRITICAL:
            self.is_valid = False
            self.score -= 40
        elif issue.severity == IssueSeverity.WARNING:
            self.score -= 10
        elif issue.severity == IssueSeverity.INFO:
            self.score -= 5

        self.score = max(0, self.score)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "score": self.score,
            "issues": [i.to_dict() for i in self.issues],
            "checked_at": self.checked_at.isoformat(),
        }


class QualityValidatorUseCase:
    """
    Use Case: Validate content quality.

    Business Rules:
    1. Check content format and structure
    2. Detect broken links
    3. Check for outdated content markers
    4. Validate metadata completeness
    5. Check content length and readability

    Single Responsibility: Content quality validation
    """

    # Minimum content length (characters)
    MIN_CONTENT_LENGTH = 50

    # Maximum content age before warning (days)
    MAX_CONTENT_AGE_DAYS = 365

    # URL pattern for link detection
    URL_PATTERN = re.compile(
        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    )

    # Outdated content markers (Vietnamese)
    OUTDATED_MARKERS = [
        r"năm\s+20(1[0-9]|20|21)",  # Years 2010-2021
        r"khóa\s+(K)?[0-5][0-9]\s",  # Course numbers K50-K59 etc (old)
        r"học\s+kỳ\s+[12]\s+năm\s+20(1[0-9]|20|21)",
        r"niên\s+khóa\s+20(1[0-9]|20|21)",
    ]

    # Required metadata fields
    REQUIRED_METADATA = ["title", "category"]

    def __init__(self, link_checker=None):
        """
        Initialize validator.

        Args:
            link_checker: Optional service to check broken links
        """
        self.link_checker = link_checker

    async def validate(
        self,
        content: str,
        metadata: Dict[str, Any],
        check_links: bool = False,
        created_at: Optional[datetime] = None,
    ) -> ValidationResult:
        """
        Validate content quality.

        Args:
            content: Content text to validate
            metadata: Document metadata
            check_links: Whether to check for broken links
            created_at: Content creation date

        Returns:
            ValidationResult with issues found
        """
        result = ValidationResult()

        # 1. Check content length
        self._check_content_length(content, result)

        # 2. Check metadata completeness
        self._check_metadata(metadata, result)

        # 3. Check for outdated markers
        self._check_outdated_markers(content, result)

        # 4. Check content age
        if created_at:
            self._check_content_age(created_at, result)

        # 5. Check broken links (optional, async)
        if check_links:
            await self._check_links(content, result)

        # 6. Check content quality signals
        self._check_content_quality(content, result)

        return result

    def _check_content_length(self, content: str, result: ValidationResult) -> None:
        """Check if content meets minimum length."""
        if len(content.strip()) < self.MIN_CONTENT_LENGTH:
            result.add_issue(
                ValidationIssue(
                    code="CONTENT_TOO_SHORT",
                    message=f"Nội dung quá ngắn ({len(content)} ký tự)",
                    severity=IssueSeverity.WARNING,
                    field="content",
                    suggestion=f"Nội dung nên có ít nhất {self.MIN_CONTENT_LENGTH} ký tự",
                )
            )

    def _check_metadata(
        self, metadata: Dict[str, Any], result: ValidationResult
    ) -> None:
        """Check metadata completeness."""
        for field in self.REQUIRED_METADATA:
            if field not in metadata or not metadata[field]:
                result.add_issue(
                    ValidationIssue(
                        code="MISSING_METADATA",
                        message=f"Thiếu trường metadata: {field}",
                        severity=IssueSeverity.WARNING,
                        field=field,
                        suggestion=f"Vui lòng bổ sung trường {field}",
                    )
                )

    def _check_outdated_markers(self, content: str, result: ValidationResult) -> None:
        """Check for outdated content markers."""
        for pattern in self.OUTDATED_MARKERS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                result.add_issue(
                    ValidationIssue(
                        code="OUTDATED_CONTENT",
                        message=f"Phát hiện nội dung có thể đã cũ: {matches[0]}",
                        severity=IssueSeverity.INFO,
                        field="content",
                        suggestion="Kiểm tra và cập nhật thông tin nếu cần",
                    )
                )
                break  # Only report once

    def _check_content_age(
        self, created_at: datetime, result: ValidationResult
    ) -> None:
        """Check if content is too old."""
        age = datetime.now() - created_at
        if age > timedelta(days=self.MAX_CONTENT_AGE_DAYS):
            result.add_issue(
                ValidationIssue(
                    code="OLD_CONTENT",
                    message=f"Nội dung đã hơn {age.days} ngày chưa được cập nhật",
                    severity=IssueSeverity.INFO,
                    suggestion="Kiểm tra và cập nhật nội dung định kỳ",
                )
            )

    async def _check_links(self, content: str, result: ValidationResult) -> None:
        """Check for broken links in content."""
        urls = self.URL_PATTERN.findall(content)

        if not urls:
            return

        if not self.link_checker:
            result.add_issue(
                ValidationIssue(
                    code="LINKS_NOT_CHECKED",
                    message=f"Có {len(urls)} link trong nội dung nhưng chưa kiểm tra",
                    severity=IssueSeverity.INFO,
                    suggestion="Kích hoạt link checker để kiểm tra broken links",
                )
            )
            return

        # Check each URL
        broken_links = []
        for url in urls[:10]:  # Limit to 10 links
            try:
                is_valid = await self.link_checker.check(url)
                if not is_valid:
                    broken_links.append(url)
            except Exception as e:
                logger.warning(f"Error checking link {url}: {e}")

        if broken_links:
            result.add_issue(
                ValidationIssue(
                    code="BROKEN_LINKS",
                    message=f"Phát hiện {len(broken_links)} broken link(s)",
                    severity=IssueSeverity.ERROR,
                    suggestion=f"Kiểm tra và sửa các link: {', '.join(broken_links[:3])}...",
                )
            )

    def _check_content_quality(self, content: str, result: ValidationResult) -> None:
        """Check content quality signals."""
        # Check for placeholder text
        placeholder_patterns = [
            r"\[.*?\]",  # [placeholder]
            r"TODO",
            r"FIXME",
            r"XXX",
            r"\.\.\.",  # ...
        ]

        for pattern in placeholder_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches and len(matches) > 2:
                result.add_issue(
                    ValidationIssue(
                        code="PLACEHOLDER_TEXT",
                        message=f"Phát hiện placeholder text: {matches[0]}",
                        severity=IssueSeverity.WARNING,
                        field="content",
                        suggestion="Thay thế placeholder bằng nội dung thực",
                    )
                )
                break

        # Check for excessive special characters
        special_chars = len(re.findall(r"[^\w\s]", content))
        if special_chars > len(content) * 0.2:
            result.add_issue(
                ValidationIssue(
                    code="EXCESSIVE_SPECIAL_CHARS",
                    message="Nội dung có quá nhiều ký tự đặc biệt",
                    severity=IssueSeverity.INFO,
                    field="content",
                    suggestion="Kiểm tra format nội dung",
                )
            )

    async def batch_validate(
        self,
        documents: List[Dict[str, Any]],
        check_links: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Batch validate multiple documents.

        Args:
            documents: List of {"content": str, "metadata": dict, "created_at": datetime?}
            check_links: Whether to check broken links

        Returns:
            List of validation results with document info
        """
        results = []

        for doc in documents:
            validation = await self.validate(
                content=doc.get("content", ""),
                metadata=doc.get("metadata", {}),
                check_links=check_links,
                created_at=doc.get("created_at"),
            )

            results.append(
                {
                    "document_id": doc.get("id"),
                    "validation": validation.to_dict(),
                }
            )

        return results
