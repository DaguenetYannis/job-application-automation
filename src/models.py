from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class JobInput:
    job_title: str
    company: str | None
    job_description: str

    def __post_init__(self) -> None:
        self.job_title = self.job_title.strip()
        self.job_description = self.job_description.strip()
        if self.company is not None:
            self.company = self.company.strip() or None

        if not self.job_title:
            raise ValueError("job_title cannot be empty")
        if not self.job_description:
            raise ValueError("job_description cannot be empty")


@dataclass
class ParsedJob:
    language: str
    job_family: list[str] = field(default_factory=list)
    required_skills: list[str] = field(default_factory=list)
    preferred_skills: list[str] = field(default_factory=list)
    main_missions: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    recommended_cv_examples: list[str] = field(default_factory=list)
    recommended_cover_letter_examples: list[str] = field(default_factory=list)
    detected_role_categories: list[str] = field(default_factory=list)
    detected_keywords: list[str] = field(default_factory=list)
    detected_required_skills: list[str] = field(default_factory=list)
    detected_main_missions: list[str] = field(default_factory=list)


@dataclass
class GenerationPlan:
    language: str
    selected_role_categories: list[str]
    cv_template: str
    cover_letter_template: str
    selected_cv_examples: list[str]
    selected_cover_letter_examples: list[str]
    selected_skill_blocks: list[str]
    selected_experiences: list[str]
    selected_projects: list[str]
    notes: str = ""


@dataclass
class CVSkillGroup:
    label: str
    content: str


@dataclass
class CVExperience:
    organization: str
    role: str
    location: str
    dates: str
    bullets: list[str]


@dataclass
class CVProject:
    name: str
    year: str
    bullets: list[str]
    url: str = ""
    url_label: str = ""


@dataclass
class CVEducation:
    institution: str
    dates: str
    degree: str
    details: str = ""


@dataclass
class CVCertification:
    provider: str
    name: str
    year: str


@dataclass
class CVDocument:
    title: str
    profile_paragraph: str
    skill_groups: list[CVSkillGroup]
    experiences: list[CVExperience]
    projects: list[CVProject]
    education: list[CVEducation]
    certifications: list[CVCertification]
    languages: str


@dataclass
class CoverLetterRecipient:
    name: str = ""
    organization: str = ""
    address: str = ""


@dataclass
class CoverLetterDocument:
    date: str = ""
    subject: str = ""
    greeting: str = "Madame, Monsieur,"
    paragraphs: list[str] = field(default_factory=list)
    closing: str = "Je vous prie d'agréer, Madame, Monsieur, l'expression de ma considération distinguée."


@dataclass
class GeneratedApplicationContent:
    cv: CVDocument
    cover_letter: CoverLetterDocument


@dataclass
class ApplicationMetadata:
    application_id: str
    job_title: str
    company: str | None
    created_at: str
    folder_path: str
