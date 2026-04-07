"""Pydantic v2 models for the .ai/ folder convention and Claude structured output."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class MemoryEntry(BaseModel):
    title: str
    file: str
    description: str


class MemoryIndex(BaseModel):
    entries: list[MemoryEntry] = Field(default_factory=list)


class SkillFrontmatter(BaseModel):
    name: str
    description: str
    type: Literal["user", "feedback", "project", "reference", "task"] = "task"


class AIContextConfig(BaseModel):
    version: str = "1.0"
    project_name: str = ""
    default_model: Literal["haiku", "sonnet"] = "haiku"
    max_tokens: int = 4000
    template: Literal["minimal", "full", "team"] = "minimal"


class KeyService(BaseModel):
    name: str
    description: str
    technology: str = ""


class DataFlowStep(BaseModel):
    source: str
    sink: str
    description: str


class ArchitectureDoc(BaseModel):
    overview: str
    key_services: list[KeyService] = Field(default_factory=list)
    data_flow: list[DataFlowStep] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)


class Convention(BaseModel):
    name: str
    description: str
    example: str = ""


class ConventionsDoc(BaseModel):
    logging: Convention | None = None
    model_validation: Convention | None = None
    test_structure: Convention | None = None
    additional: list[Convention] = Field(default_factory=list)


class SuggestedSkill(BaseModel):
    name: str
    description: str
    trigger: str
    steps: list[str] = Field(default_factory=list)


class GenerateOutput(BaseModel):
    architecture: ArchitectureDoc | None = None
    conventions: ConventionsDoc | None = None
    suggested_skills: list[SuggestedSkill] = Field(default_factory=list)


class ValidationIssue(BaseModel):
    file: str
    message: str
    suggestion: str = ""
    severity: Literal["error", "warning"] = "error"


class ValidationResult(BaseModel):
    errors: list[ValidationIssue] = Field(default_factory=list)
    warnings: list[ValidationIssue] = Field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0


class DiffEntry(BaseModel):
    file: str
    additions: list[str] = Field(default_factory=list)
    removals: list[str] = Field(default_factory=list)


class StaleHint(BaseModel):
    new_file: str
    message: str
    suggestion: str


class DiffResult(BaseModel):
    entries: list[DiffEntry] = Field(default_factory=list)
    stale_hints: list[StaleHint] = Field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(self.entries or self.stale_hints)
