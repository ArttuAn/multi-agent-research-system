from pydantic import BaseModel, Field


class CritiqueResult(BaseModel):
    approved: bool = Field(description="True if no unsupported or contradictory claims")
    hallucination_risk: str = Field(description="low|medium|high")
    issues: list[str] = Field(default_factory=list, description="Specific problems with citations or claims")
    revision_guidance: str = Field(
        default="",
        description="Concrete edits if not approved; empty if approved",
    )
