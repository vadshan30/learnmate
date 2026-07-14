from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies import Store, get_store, get_student_or_404
from app.schemas.requests import ChatRequest
from app.schemas.responses import ChatResponse, ErrorResponse, SuccessResponse
from app.services import RAG_AVAILABLE, granite_available, rag_service
from app.services.granite_service import mentor_chat

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.get(
    "/{student_id}",
    response_model=SuccessResponse,
    summary="Get chat history",
    description="Returns the chat history for a student.",
    responses={
        200: {"description": "Chat history returned"},
    },
)
async def get_chat_history(student_id: str, store: Store = Depends(get_store)) -> SuccessResponse:
    history = store.chat_histories.get(student_id, [])
    return SuccessResponse(message="Chat history retrieved", data={"messages": history})


@router.post(
    "",
    response_model=ChatResponse,
    summary="Chat with AI mentor",
    description="Sends a message to the AI learning mentor and returns a personalised multi-turn response.",
    responses={
        200: {"description": "Mentor response"},
        404: {"model": ErrorResponse, "description": "Student not found"},
    },
)
async def chat(body: ChatRequest, store: Store = Depends(get_store)) -> ChatResponse:
    profile = get_student_or_404(body.student_id, store)

    student_context = (
        f"Name: {profile.get('name', '')}\n"
        f"Career Goal: {profile.get('career_goal', '')}\n"
        f"Skills: {', '.join(profile.get('current_skills', []))}\n"
        f"Interests: {', '.join(profile.get('interests', []))}\n"
        f"Level: {profile.get('skill_level', 'beginner')}\n"
        f"Progress: {profile.get('progress_percentage', 0.0)}%"
    )

    rag_results = []
    if RAG_AVAILABLE and rag_service is not None:
        rag_results = await rag_service.search_courses(body.message, n=5)

    if rag_results:
        resources_text = "\n".join(
            f"- {r.get('document', '')[:200]}" for r in rag_results
        )
    else:
        resources_text = "No specific resources found."

    # Retrieve existing conversation history for multi-turn context
    existing_history = store.chat_histories.get(body.student_id, [])

    reply = await mentor_chat(body.message, student_context, resources_text, existing_history)

    new_turns = [{"role": "user", "content": body.message}, {"role": "assistant", "content": reply}]
    if body.student_id not in store.chat_histories:
        store.chat_histories[body.student_id] = []
    store.chat_histories[body.student_id].extend(new_turns)

    return ChatResponse(
        student_id=body.student_id,
        response=reply,
        source="watsonx" if granite_available else "fallback",
        mentor_type="general",
    )


@router.delete(
    "/{student_id}",
    response_model=SuccessResponse,
    summary="Clear chat history",
    description="Clears the chat history for a student.",
    responses={
        200: {"description": "History cleared"},
    },
)
async def clear_chat_history(student_id: str, store: Store = Depends(get_store)) -> SuccessResponse:
    store.chat_histories.pop(student_id, None)
    return SuccessResponse(message="Chat history cleared")
