"""Optional, read-only CVNSS4.0 endpoints for DeepTutor FastAPI or standalone mounting."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from .service import execute

router = APIRouter(prefix="/api/cvnss4", tags=["CVNSS4.0"])


class ConvertRequest(BaseModel):
    text: str = Field(max_length=100_000)
    mode: str = "cqn"


class WordRequest(BaseModel):
    word: str = Field(min_length=1, max_length=200)
    source: str = "cvss"


def run_safely(operation: str, **kwargs):
    try:
        return execute(operation, **kwargs)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/health")
def cvnss_health():
    return {"service": "cvnss4-hub", "oracle": run_safely("audit")}


@router.post("/convert")
def convert(body: ConvertRequest):
    return run_safely("convert", text=body.text, mode=body.mode)


@router.post("/inspect")
def inspect(body: WordRequest):
    return run_safely("inspect", text=body.word, source=body.source)


@router.post("/candidates")
def candidates(body: WordRequest):
    return run_safely("candidates", text=body.word, source=body.source)


@router.get("/audit")
def audit():
    return run_safely("audit")


@router.get("/self-test")
def self_test():
    return run_safely("self_test")
