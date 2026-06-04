# CV Templates

This folder contains structural LaTeX Jinja templates for CV generation. Templates should define layout, section order, spacing and placeholders only. They should not contain hardcoded CV content.

Generated content should come from the candidate profile, role profiles, skill blocks, selected examples, parsed job data and generation plan.

Available templates:

- `cv_base_fr.tex.j2`
- `cv_base_en.tex.j2`

Custom Jinja delimiters are used to avoid conflicts with LaTeX:

- variables: `((( variable )))`
- blocks: `((* for item in items *))`

Final rendered CV files should be written under `applications/<application_id>/outputs/cv/`.
