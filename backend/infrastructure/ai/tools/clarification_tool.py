"""
Clarification Tool Handler - Ask for clarification.

Used when the query is ambiguous or lacks necessary information.
"""

import logging
from typing import Dict, Any, List

from app.domain.enums.tool_type import ToolType
from app.application.interfaces.services.tool_executor_service import IToolHandler


logger = logging.getLogger(__name__)


# Clarification question templates
CLARIFICATION_TEMPLATES = {
    "ambiguous_topic": "Bạn có thể cho mình biết rõ hơn về {topic} bạn đang hỏi không? Ví dụ: {examples}",
    "missing_context": "Để trả lời chính xác hơn, bạn có thể cung cấp thêm thông tin về {missing_info} không?",
    "multiple_meanings": "Câu hỏi của bạn có thể hiểu theo nhiều cách:\n{options}\nBạn muốn hỏi về vấn đề nào?",
    "form_type": "Bạn muốn điền loại đơn nào? Mình có thể giúp bạn với:\n{form_options}",
    "time_period": "Bạn đang hỏi về thời gian nào? (VD: học kỳ, năm học, deadline cụ thể)",
    "general": "Bạn có thể mô tả chi tiết hơn về yêu cầu của mình không?",
}


class ClarificationToolHandler(IToolHandler):
    """
    Handler for clarify_question tool.

    Generates clarification questions when the query is ambiguous.
    """

    @property
    def tool_type(self) -> ToolType:
        return ToolType.CLARIFY_QUESTION

    def validate_arguments(self, arguments: Dict[str, Any]) -> bool:
        """Validate tool arguments."""
        if "clarification_prompt" in arguments:
            return True
        required = ["clarification_type"]
        return all(key in arguments for key in required)

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute clarification tool.

        Args:
            arguments:
                - clarification_type: Type of clarification needed
                - missing_info: What information is missing
                - options: Possible interpretations
                - topic: The ambiguous topic
                - examples: Example clarifications

        Returns:
            {
                "clarification_question": str,
                "clarification_type": str,
                "options": List[str]
            }
        """
        if "clarification_prompt" in arguments:
            suggestions = arguments.get("suggestions", [])
            return {
                "clarification_question": arguments.get("clarification_prompt", ""),
                "clarification_type": "prompt",
                "options": suggestions,
            }

        clarification_type = arguments.get("clarification_type", "general")
        missing_info = arguments.get("missing_info", "")
        options = arguments.get("options", [])
        topic = arguments.get("topic", "")
        examples = arguments.get("examples", "")

        logger.info(f"Clarification tool executing for type: {clarification_type}")

        question = self._generate_clarification(
            clarification_type=clarification_type,
            missing_info=missing_info,
            options=options,
            topic=topic,
            examples=examples,
        )

        return {
            "clarification_question": question,
            "clarification_type": clarification_type,
            "options": options if options else [],
        }

    def _generate_clarification(
        self,
        clarification_type: str,
        missing_info: str = "",
        options: List[str] = None,
        topic: str = "",
        examples: str = "",
    ) -> str:
        """Generate clarification question from template."""

        template = CLARIFICATION_TEMPLATES.get(
            clarification_type, CLARIFICATION_TEMPLATES["general"]
        )

        # Format based on type
        if clarification_type == "ambiguous_topic":
            return template.format(topic=topic, examples=examples)

        elif clarification_type == "missing_context":
            return template.format(missing_info=missing_info)

        elif clarification_type == "multiple_meanings":
            if options:
                formatted_options = "\n".join([f"- {opt}" for opt in options])
                return template.format(options=formatted_options)
            return CLARIFICATION_TEMPLATES["general"]

        elif clarification_type == "form_type":
            form_options = """
- Đơn xin nghỉ học có thời hạn
- Đơn xin cấp lại/đổi thẻ sinh viên
- Đơn đề nghị cấp giấy tờ
- Đơn đề nghị xem xét điểm thi
- Đơn đề nghị khác"""
            return template.format(form_options=form_options)

        elif clarification_type == "time_period":
            return template

        else:
            return template
