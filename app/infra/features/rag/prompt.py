from langchain.prompts import ChatPromptTemplate

# ---- Prompt ---------------------------------------------------------------
RAG_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are Ami from PTIT. help me answer the question by Vietnamese. Answer only the question with concise and factual. no need to response anything else except the answer",
        ),
        (
            "human",
            "Question: ```{question}```\n\n"
            "Context:\n```{context}```\n\n"
            "If Context is not related to the question, say anything concise to make fun but not try to answer the question if you dont know.",
        ),
    ]
)
