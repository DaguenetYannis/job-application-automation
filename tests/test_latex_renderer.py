from pathlib import Path

from src.latex_renderer import LatexRenderer


def test_latex_renderer_substitutes_variables_and_loops() -> None:
    template_root = Path(".test_artifacts") / "latex_renderer"
    template_root.mkdir(parents=True, exist_ok=True)
    template_path = template_root / "sample.tex.j2"
    template_path.write_text(
        "Hello ((( name )))\n((* for item in items *))Item: ((( item )))\n((* endfor *))",
        encoding="utf-8",
    )

    rendered = LatexRenderer(template_root).render(
        "sample.tex.j2",
        {"name": "Yannis", "items": ["SQL", "Python"]},
    )

    assert "Hello Yannis" in rendered
    assert "Item: SQL" in rendered
    assert "Item: Python" in rendered


def cv_context() -> dict:
    return {
        "layout": {"margin": "1.75cm", "line_stretch": "1.04"},
        "candidate": {
            "name": "Yannis Daguenet",
            "location": "Paris",
            "phone": "+33 6 04 43 91 20",
            "email": "yannisdaguenet@gmail.com",
            "linkedin": "https://linkedin.com/in/yannis-daguenet",
            "github": "https://github.com/DaguenetYannis",
            "portfolio": "https://daguenetyannisportfolio.netlify.app/",
        },
        "document": {"title": "Data Analyst"},
        "profile_paragraph": "Profile text.",
        "skill_groups": [{"label": "Data", "content": "SQL, Python, Power BI."}],
        "experiences": [
            {
                "organization": "Greenly",
                "role": "Data Analyst",
                "location": "Paris",
                "dates": "2025",
                "bullets": ["Bullet one.", "Bullet two."],
            }
        ],
        "projects": [],
        "education": [],
        "certifications": [],
        "languages": "French native, English C2",
    }


def cover_letter_context() -> dict:
    return {
        "layout": {"margin": "1.9cm", "line_stretch": "1.05"},
        "candidate": {
            "name": "Yannis Daguenet",
            "location": "Paris",
            "phone": "+33 6 04 43 91 20",
            "email": "yannisdaguenet@gmail.com",
            "linkedin": "https://linkedin.com/in/yannis-daguenet",
            "portfolio": "https://daguenetyannisportfolio.netlify.app/",
        },
        "recipient": {
            "name": "",
            "organization": "",
            "address": "",
        },
        "letter": {
            "date": "",
            "subject": "Candidature",
            "greeting": "Madame, Monsieur,",
            "paragraphs": [
                "First paragraph.",
                "Second paragraph.",
            ],
            "closing": "Je vous prie d'agréer, Madame, Monsieur, l'expression de ma considération distinguée.",
        },
    }


def test_latex_renderer_renders_base_cv_template() -> None:
    rendered = LatexRenderer().render("cv/cv_base_fr.tex.j2", cv_context())

    assert "\\documentclass" in rendered
    assert "Yannis Daguenet" in rendered
    assert "(((" not in rendered


def test_latex_renderer_renders_base_cover_letter_template() -> None:
    rendered = LatexRenderer().render(
        "cover_letter/cover_letter_base_fr.tex.j2",
        cover_letter_context(),
    )

    assert "\\documentclass" in rendered
    assert "Yannis Daguenet" in rendered
    assert "(((" not in rendered
