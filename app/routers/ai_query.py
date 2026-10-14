import os
import json
from typing import Dict, Any
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
import httpx

from app.database import get_db
from app import crud, schemas

router = APIRouter(prefix="/students", tags=["AI Assistant"])

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_TIMEOUT_SECONDS = float(os.getenv("OLLAMA_TIMEOUT", "20.0"))


def build_system_prompt(grounded_context: Dict[str, Any], user_query: str) -> str:
    """
    Constructs a strictly grounded prompt containing sanitized student database context.
    Prevents unrestricted SQL generation or prompt injection.
    """
    context_str = json.dumps(grounded_context, indent=2)
    prompt = (
        "You are an assistant for a university Student Information System.\n"
        "Your task is to answer user queries strictly using the verified SQLite database snapshot provided below.\n"
        "Safety instructions:\n"
        "1. Only answer based on the verified facts in the context JSON.\n"
        "2. Do NOT hallucinate students or course metrics.\n"
        "3. Do NOT output executable SQL statements.\n"
        "4. Be concise, polite, and helpful.\n\n"
        f"--- VERIFIED DATABASE CONTEXT ---\n{context_str}\n----------------------------------\n\n"
        f"User Query: {user_query}\n\n"
        "Answer:"
    )
    return prompt


def generate_fallback_summary(query: str, context: Dict[str, Any]) -> str:
    """
    Provides a grounded factual answer directly from SQLite context
    when Ollama local daemon is offline or uninstalled.
    """
    q_lower = query.lower()
    total = context.get("total_enrolled_students", 0)
    courses = context.get("course_distribution", {})
    students = context.get("students", [])

    fallback_lines = [
        "ℹ️ [Offline Mode]: Ollama daemon is currently unreachable. Returning verified SQLite database facts directly:"
    ]

    if "how many" in q_lower or "count" in q_lower or "total" in q_lower:
        fallback_lines.append(f"• Total enrolled students in database: {total}")
        fallback_lines.append("• Enrollment by course:")
        for course, count in courses.items():
            fallback_lines.append(f"  - {course}: {count} student(s)")
    elif "born after" in q_lower or "birth" in q_lower or "age" in q_lower:
        # Check if year is mentioned
        import re
        year_match = re.search(r"\b(19\d\d|20\d\d)\b", query)
        target_year = int(year_match.group(1)) if year_match else 2005
        filtered = [s for s in students if s.get("birth_year") and s["birth_year"] > target_year]
        fallback_lines.append(f"• Students born after {target_year} ({len(filtered)} found):")
        if filtered:
            for s in filtered:
                fallback_lines.append(f"  - {s['name']} (ID: {s['id']}, Course: {s['course']}, Born: {s['date_of_birth']})")
        else:
            fallback_lines.append(f"  - No students found born after {target_year}.")
    elif "course" in q_lower:
        fallback_lines.append("• Available courses with active enrollments:")
        for course, count in courses.items():
            fallback_lines.append(f"  - {course} ({count} enrolled)")
    else:
        fallback_lines.append(f"• Database contains {total} registered student record(s).")
        fallback_lines.append(f"• Available courses: {', '.join(courses.keys())}.")
        sample_names = [s["name"] for s in students[:5]]
        fallback_lines.append(f"• Recent students sample: {', '.join(sample_names)}")

    fallback_lines.append("\nTip: Start Ollama with `ollama run llama3.2:1b` to enable full natural language responses.")
    return "\n".join(fallback_lines)


@router.post(
    "/ask-ai",
    response_model=schemas.AIQueryResponse,
    status_code=status.HTTP_200_OK,
    summary="Natural language student database QA (Ollama)",
    description="Ask a natural language question about students. Answers are grounded in SQLite data without exposing raw SQL generation.",
)
async def ask_ai(
    payload: schemas.AIQueryRequest,
    db: Session = Depends(get_db),
):
    """
    Accepts a natural language query, extracts safe sanitized context from SQLite,
    and prompts a local Ollama model (e.g. llama3.2:1b).
    If Ollama is not active, gracefully falls back to structured database analytics.
    """
    # 1. Fetch grounded data safely from SQLite
    grounded_context = crud.get_sanitized_students_context(db=db, max_records=60)
    target_model = payload.model or "llama3.2:1b"
    prompt = build_system_prompt(grounded_context, payload.query)

    ollama_api_endpoint = f"{OLLAMA_BASE_URL.rstrip('/')}/api/generate"
    request_body = {
        "model": target_model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "top_p": 0.9,
        },
    }

    try:
        async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT_SECONDS) as client:
            response = await client.post(ollama_api_endpoint, json=request_body)
            if response.status_code == 200:
                data = response.json()
                ai_answer = data.get("response", "").strip()
                if ai_answer:
                    return schemas.AIQueryResponse(
                        query=payload.query,
                        answer=ai_answer,
                        grounded_data_summary=grounded_context,
                        model_used=target_model,
                        ollama_available=True,
                    )
    except (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPError, Exception):
        # Graceful fallback when Ollama is offline or request fails
        pass

    fallback_answer = generate_fallback_summary(payload.query, grounded_context)
    return schemas.AIQueryResponse(
        query=payload.query,
        answer=fallback_answer,
        grounded_data_summary=grounded_context,
        model_used=target_model,
        ollama_available=False,
    )
