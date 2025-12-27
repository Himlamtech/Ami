"""
Tool definitions for Gemini function calling.

These definitions tell the LLM what tools are available and how to use them.
The LLM will analyze the query and decide which tool(s) to call.

IMPORTANT: Vector scores are REFERENCE only - LLM makes the final decision.
"""

from typing import Dict, Any, List

from domain.enums.tool_type import ToolType


# Tool schemas for Gemini function calling
TOOL_DEFINITIONS: List[Dict[str, Any]] = [
    {
        "name": ToolType.ANALYZE_IMAGE.value,
        "description": """Analyze an image artifact with Vision and answer image-based questions.

        When to use:
        - An image is provided with the query
        - The question refers to the image contents
        - The user asks to extract text, describe, or interpret a picture

        Can be combined with other tools:
        - analyze_image + use_rag_context (image contains PTIT documents)
        - analyze_image + search_web (needs latest info beyond image)
        """,
        "parameters": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "User question about the image (optional)",
                },
                "reason": {
                    "type": "string",
                    "description": "Why image analysis is needed",
                },
            },
            "required": ["reason"],
        },
    },
    {
        "name": ToolType.USE_RAG_CONTEXT.value,
        "description": """Use retrieved documents from vector search to answer PTIT-specific questions.
        
        When to use:
        - Questions about PTIT (admission, curriculum, policies, departments, etc.)
        - Vector search returned relevant results (check max_score and chunk contents)
        - User is asking about information that exists in the knowledge base
        
        When NOT to use:
        - General knowledge questions (math, history, common sense)
        - Vector search results are not relevant (even if score is high)
        - User explicitly wants external/latest information
        
        Note: High vector score on form templates means user wants fill_form, not RAG.""",
        "parameters": {
            "type": "object",
            "properties": {
                "chunk_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "IDs of relevant chunks to use from vector search results",
                },
                "confidence": {
                    "type": "string",
                    "enum": ["high", "medium", "low"],
                    "description": "Your confidence that these documents can answer the question",
                },
                "reason": {
                    "type": "string",
                    "description": "Brief explanation of why using RAG is appropriate",
                },
            },
            "required": ["chunk_ids", "confidence", "reason"],
        },
    },
    {
        "name": ToolType.SEARCH_WEB.value,
        "description": """Search external web when internal documents are insufficient.
        
        When to use:
        - Vector search results are not relevant or outdated
        - User asks for latest/current information (schedules, deadlines, news)
        - User explicitly requests external information
        - Need to verify or supplement internal knowledge
        
        Best practices:
        - Add "site:ptit.edu.vn" for PTIT-specific queries
        - Keep queries concise and specific
        - Can be combined with use_rag_context for comprehensive answers""",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query to execute (in Vietnamese or English)",
                },
                "domain_filter": {
                    "type": "string",
                    "description": "Optional domain filter (e.g., 'ptit.edu.vn')",
                },
                "reason": {"type": "string", "description": "Why web search is needed"},
            },
            "required": ["query", "reason"],
        },
    },
    {
        "name": ToolType.ANSWER_DIRECTLY.value,
        "description": """Answer directly without using RAG or web search.
        
        When to use:
        - General knowledge questions (math, science, history)
        - Greetings and casual conversation
        - Questions clearly outside PTIT scope
        - Simple factual questions that don't need documents
        
        Examples:
        - "2+2 bằng mấy?" → answer_directly
        - "Xin chào!" → answer_directly
        - "AI là gì?" → answer_directly (general definition)""",
        "parameters": {
            "type": "object",
            "properties": {
                "answer": {
                    "type": "string",
                    "description": "Direct answer to the question",
                },
                "reason": {
                    "type": "string",
                    "description": "Why direct answer is appropriate (no RAG needed)",
                },
            },
            "required": ["answer", "reason"],
        },
    },
    {
        "name": ToolType.FILL_FORM.value,
        "description": """Generate pre-filled forms from templates and user data.
        
        When to use:
        - User asks for a form (đơn, mẫu, biểu mẫu)
        - Vector search returns form templates with HIGH score
        - User wants to submit requests (nghỉ học, cấp lại thẻ, xin giấy tờ, etc.)
        
        Important:
        - High vector score (0.9+) on form templates → use this tool
        - Form will be pre-filled with user's profile data
        - Return form in Markdown format
        
        Examples:
        - "Cho tôi đơn xin nghỉ học" → fill_form(form_type="leave_request")
        - "Mẫu đơn cấp lại thẻ sinh viên" → fill_form(form_type="card_replacement")""",
        "parameters": {
            "type": "object",
            "properties": {
                "form_type": {
                    "type": "string",
                    "enum": [
                        "leave_request",  # Đơn xin nghỉ học
                        "card_replacement",  # Đơn cấp lại thẻ sinh viên
                        "certificate_request",  # Đơn xin cấp giấy tờ
                        "exam_review",  # Đơn phúc khảo
                        "course_registration",  # Đơn đăng ký học phần
                        "general_request",  # Đơn đề nghị chung
                    ],
                    "description": "Type of form to generate",
                },
                "template_chunk_id": {
                    "type": "string",
                    "description": "Chunk ID of the form template from vector search",
                },
                "additional_info": {
                    "type": "object",
                    "description": "Additional information to fill in the form",
                },
            },
            "required": ["form_type"],
        },
    },
    {
        "name": ToolType.CLARIFY_QUESTION.value,
        "description": """Ask user for clarification when the question is unclear.
        
        When to use:
        - Question is too vague or ambiguous
        - Multiple interpretations are possible
        - Missing critical information to provide a good answer
        
        Examples:
        - "Cho tôi biết về chương trình" → Need clarification (which program?)
        - "Đăng ký" → Need clarification (register for what?)
        
        Provide helpful suggestions to guide the user.""",
        "parameters": {
            "type": "object",
            "properties": {
                "clarification_prompt": {
                    "type": "string",
                    "description": "Question to ask the user for clarification",
                },
                "suggestions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of possible interpretations or suggestions",
                },
                "reason": {
                    "type": "string",
                    "description": "Why clarification is needed",
                },
            },
            "required": ["clarification_prompt", "suggestions", "reason"],
        },
    },
]


def get_tool_schema(tool_type: ToolType) -> Dict[str, Any]:
    """
    Get the schema for a specific tool type.

    Args:
        tool_type: The tool type to get schema for

    Returns:
        Tool schema dictionary

    Raises:
        ValueError: If tool type not found
    """
    for tool in TOOL_DEFINITIONS:
        if tool["name"] == tool_type.value:
            return tool

    raise ValueError(f"Tool schema not found for: {tool_type.value}")


def get_all_tool_names() -> List[str]:
    """Get list of all tool names."""
    return [tool["name"] for tool in TOOL_DEFINITIONS]


# System prompt for orchestrator
ORCHESTRATOR_SYSTEM_PROMPT = """You are AMI's Query Orchestrator. Your job is to analyze user queries and decide which tool(s) to use.

**Context Information:**
- Query: {query}
- User: Major={major}, Year={year}, Language={language}
- Vector Search Results (REFERENCE ONLY, not hard rules):
  - Max Score: {max_score}
  - Top Chunks: {top_chunks_preview}
- Image Artifact:
  - Present: {image_present}
  - Format: {image_format}
  - Size (bytes): {image_size}

**Critical Understanding:**
1. Vector scores are SIGNALS, not hard thresholds
2. High score (0.9) on form template = user wants fill_form, NOT RAG
3. Low score but general question = answer_directly
4. You can call MULTIPLE tools if needed (RAG + web search)
5. If an image is present and the query refers to it, call analyze_image

**Decision Guidelines:**

For PTIT-specific questions:
- If chunks contain relevant information → use_rag_context
- If information might be outdated → use_rag_context + search_web
- If user asks for forms/documents → fill_form (ignore RAG even if score is high)

For General questions:
- Math, greetings, common sense → answer_directly
- No need to use RAG for general knowledge

For Unclear questions:
- Ambiguous intent → clarify_question
- Missing critical info → clarify_question

**Your Response:**
Analyze the query and call the appropriate tool(s). You MUST call at least one tool.
Provide clear reasoning for your choices.

**Conversation History:**
{conversation_history}
"""
