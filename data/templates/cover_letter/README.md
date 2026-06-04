# Cover Letter Templates

This folder contains structural LaTeX Jinja templates for cover letter generation. Templates should define layout, spacing and placeholders only. They should not contain hardcoded letter content.

Generated content should come from the candidate profile, role profiles, skill blocks, selected examples, parsed job data and generation plan.

Available templates:

- `cover_letter_base_fr.tex.j2`
- `cover_letter_base_en.tex.j2`

Custom Jinja delimiters are used to avoid conflicts with LaTeX:

- variables: `((( variable )))`
- blocks: `((* for item in items *))`

Final rendered letters should be written under `applications/<application_id>/outputs/cover_letter/`.
