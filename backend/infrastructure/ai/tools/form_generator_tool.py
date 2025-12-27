"""
Form Generator Tool Handler - Generate pre-filled forms.

This is a KEY tool that differentiates from RAG:
- High vector score (0.9) on form templates → use this tool
- Combines form template + user profile data
- Outputs Markdown form
"""

import logging
from typing import Dict, Any, Optional, List

from domain.enums.tool_type import ToolType
from application.interfaces.services.tool_executor_service import IToolHandler


logger = logging.getLogger(__name__)


# Form templates (can be loaded from database)
FORM_TEMPLATES = {
    "leave_request": """# ĐƠN XIN NGHỈ HỌC CÓ THỜI HẠN

**CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM**
**Độc lập - Tự do - Hạnh phúc**

---

**Kính gửi:** Ban Giám đốc Học viện Công nghệ Bưu chính Viễn thông

**Họ và tên sinh viên:** {name}
**Mã sinh viên:** {student_id}
**Ngày sinh:** {dob}
**Lớp:** {class_name}
**Khoa:** {faculty}
**Chuyên ngành:** {major}
**Khóa:** {year}
**Số điện thoại:** {phone}
**Email:** {email}

**Nội dung đề nghị:**

Em xin được nghỉ học có thời hạn từ ngày ____/____/________ đến ngày ____/____/________

**Lý do nghỉ học:**
_______________________________________________________________________________
_______________________________________________________________________________

Em cam kết thực hiện đúng các quy định của Học viện về việc nghỉ học có thời hạn.

| | Hà Nội, ngày ____ tháng ____ năm ________ |
|---|---|
| **XÁC NHẬN CỦA PHỤ HUYNH** | **NGƯỜI LÀM ĐƠN** |
| (Ký và ghi rõ họ tên) | (Ký và ghi rõ họ tên) |
| | |
| | {name} |
""",
    "card_replacement": """# ĐƠN ĐỀ NGHỊ CẤP LẠI/ĐỔI THẺ SINH VIÊN

**CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM**
**Độc lập - Tự do - Hạnh phúc**

---

**Kính gửi:** Phòng Công tác Sinh viên - Học viện Công nghệ Bưu chính Viễn thông

**Họ và tên sinh viên:** {name}
**Mã sinh viên:** {student_id}
**Ngày sinh:** {dob}
**Lớp:** {class_name}
**Khoa:** {faculty}

**Nội dung đề nghị:**

☐ Cấp lại thẻ sinh viên (do mất)
☐ Đổi thẻ sinh viên (do hỏng)

**Lý do:**
_______________________________________________________________________________

Em xin cam kết các thông tin trên là đúng sự thật.

| | Hà Nội, ngày ____ tháng ____ năm ________ |
|---|---|
| | **NGƯỜI LÀM ĐƠN** |
| | (Ký và ghi rõ họ tên) |
| | |
| | {name} |

---
**Lưu ý:** Đính kèm 01 ảnh 3x4 và lệ phí theo quy định.
""",
    "certificate_request": """# ĐƠN ĐỀ NGHỊ CẤP GIẤY TỜ

**CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM**
**Độc lập - Tự do - Hạnh phúc**

---

**Kính gửi:** Phòng Đào tạo - Học viện Công nghệ Bưu chính Viễn thông

**Họ và tên sinh viên:** {name}
**Mã sinh viên:** {student_id}
**Ngày sinh:** {dob}
**Lớp:** {class_name}
**Khoa:** {faculty}
**Chuyên ngành:** {major}

**Nội dung đề nghị cấp:**

☐ Giấy xác nhận sinh viên
☐ Bảng điểm
☐ Giấy giới thiệu thực tập
☐ Khác: _______________

**Số lượng:** ______ bản

**Mục đích sử dụng:**
_______________________________________________________________________________

| | Hà Nội, ngày ____ tháng ____ năm ________ |
|---|---|
| | **NGƯỜI LÀM ĐƠN** |
| | (Ký và ghi rõ họ tên) |
| | |
| | {name} |
""",
    "exam_review": """# ĐƠN ĐỀ NGHỊ XEM XÉT ĐIỂM THI

**CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM**
**Độc lập - Tự do - Hạnh phúc**

---

**Kính gửi:** Phòng Đào tạo - Học viện Công nghệ Bưu chính Viễn thông

**Họ và tên sinh viên:** {name}
**Mã sinh viên:** {student_id}
**Lớp:** {class_name}
**Khoa:** {faculty}

**Em xin đề nghị được xem xét lại điểm thi môn học:**

| Mã học phần | Tên học phần | Lớp học phần | Điểm hiện tại |
|-------------|--------------|--------------|---------------|
| | | | |

**Lý do đề nghị:**
_______________________________________________________________________________
_______________________________________________________________________________

Em xin cam kết các thông tin trên là đúng sự thật và chịu trách nhiệm về đề nghị của mình.

| | Hà Nội, ngày ____ tháng ____ năm ________ |
|---|---|
| | **NGƯỜI LÀM ĐƠN** |
| | (Ký và ghi rõ họ tên) |
| | |
| | {name} |

---
**Lưu ý:** Nộp đơn trong vòng 07 ngày kể từ ngày công bố điểm.
""",
    "general_request": """# ĐƠN ĐỀ NGHỊ

**CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM**
**Độc lập - Tự do - Hạnh phúc**

---

**Kính gửi:** {recipient}

**Họ và tên sinh viên:** {name}
**Mã sinh viên:** {student_id}
**Ngày sinh:** {dob}
**Lớp:** {class_name}
**Khoa:** {faculty}
**Số điện thoại:** {phone}
**Email:** {email}

**Nội dung đề nghị:**
_______________________________________________________________________________
_______________________________________________________________________________
_______________________________________________________________________________

Em xin cam kết thực hiện đúng các quy định của Học viện.

| | Hà Nội, ngày ____ tháng ____ năm ________ |
|---|---|
| | **NGƯỜI LÀM ĐƠN** |
| | (Ký và ghi rõ họ tên) |
| | |
| | {name} |
""",
}


class FormGeneratorToolHandler(IToolHandler):
    """
    Handler for fill_form tool.

    Generates pre-filled forms from templates and user data.
    This is called when vector search returns HIGH score on form templates.
    """

    def __init__(self, student_repository: Optional[Any] = None):
        """
        Initialize form generator tool handler.

        Args:
            student_repository: Repository to fetch student profile data
        """
        self._student_repo = student_repository

    @property
    def tool_type(self) -> ToolType:
        return ToolType.FILL_FORM

    def validate_arguments(self, arguments: Dict[str, Any]) -> bool:
        """Validate tool arguments."""
        required = ["form_type"]
        return all(key in arguments for key in required)

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute form generation tool.

        Args:
            arguments:
                - form_type: Type of form to generate
                - template_chunk_id: Chunk ID of template (optional)
                - additional_info: Extra info to fill (optional)
                - user_context: User profile data (injected)

        Returns:
            {
                "form_markdown": str,
                "form_type": str,
                "pre_filled_fields": List[str],
                "missing_fields": List[str]
            }
        """
        form_type = arguments.get("form_type", "general_request")
        user_context = arguments.get("user_context", {})
        additional_info = arguments.get("additional_info", {})

        logger.info(f"Form generator tool executing for type: {form_type}")

        # Get template
        template = FORM_TEMPLATES.get(form_type, FORM_TEMPLATES["general_request"])

        # Get student data
        student_data = await self._get_student_data(user_context)

        # Merge with additional info
        fill_data = {**student_data, **additional_info}

        # Fill template
        filled_form, pre_filled, missing = self._fill_template(template, fill_data)

        return {
            "form_markdown": filled_form,
            "form_type": form_type,
            "pre_filled_fields": pre_filled,
            "missing_fields": missing,
        }

    async def _get_student_data(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get student data from repository or user context.

        Returns dict with fields:
        - name, student_id, dob, class_name, faculty, major, year, phone, email
        """
        # Default values
        data = {
            "name": user_context.get("name", "_______________"),
            "student_id": user_context.get("student_id", "_______________"),
            "dob": user_context.get("dob", "____/____/________"),
            "class_name": user_context.get("class_name", "_______________"),
            "faculty": user_context.get("faculty", "_______________"),
            "major": user_context.get("major", "_______________"),
            "year": user_context.get("year", "___"),
            "phone": user_context.get("phone", "_______________"),
            "email": user_context.get("email", "_______________"),
            "recipient": "Ban Giám đốc Học viện",
        }

        # Try to get from repository if available
        if self._student_repo and user_context.get("user_id"):
            try:
                profile = await self._student_repo.get_by_user_id(
                    user_context["user_id"]
                )
                if profile:
                    progress = profile.get_academic_progress()
                    derived_year = progress.get("current_year")
                    year_value = profile.year or derived_year
                    data.update(
                        {
                            "name": profile.name or data["name"],
                            "student_id": profile.student_id or data["student_id"],
                            "dob": profile.date_of_birth or data["dob"],
                            "class_name": profile.class_name or data["class_name"],
                            "faculty": profile.faculty or data["faculty"],
                            "major": profile.major or data["major"],
                            "year": str(year_value) if year_value else data["year"],
                            "phone": profile.phone or data["phone"],
                            "email": profile.email or data["email"],
                        }
                    )
            except Exception as e:
                logger.warning(f"Failed to get student profile: {e}")

        return data

    def _fill_template(
        self, template: str, data: Dict[str, Any]
    ) -> tuple[str, List[str], List[str]]:
        """
        Fill template with data.

        Returns:
            (filled_form, pre_filled_fields, missing_fields)
        """
        filled = template
        pre_filled = []
        missing = []

        for key, value in data.items():
            placeholder = "{" + key + "}"
            if placeholder in filled:
                if value and value != "_______________" and "____" not in str(value):
                    pre_filled.append(key)
                else:
                    missing.append(key)
                filled = filled.replace(placeholder, str(value))

        return filled, pre_filled, missing
