# Documentation Guidelines (General)

This guide defines a practical standard for creating, writing, updating, and maintaining project documentation in any software repository.

## 1. Objectives

Documentation should be:
- Useful: helps someone complete a real task.
- Accurate: matches current system behavior.
- Discoverable: easy to find and navigate.
- Maintainable: has clear ownership and review cadence.

## 2. Minimum Documentation Set

Every project should have:
- One root `README.md`.
- One `README.md` per service/component.
- A `docs/` directory organized by documentation category.

### 2.1 Root README.md (project-level)

Include at minimum:
1. Purpose and scope.
2. High-level architecture overview.
3. Repository structure.
4. Quick start (local run).
5. Deployment overview.
6. Debugging/troubleshooting entry points.
7. Testing and validation commands.
8. Links to detailed docs.

### 2.2 Service README.md (service-level)

Each service should include:
1. Service purpose and responsibilities.
2. Directory/module structure.
3. Configuration and environment variables.
4. How to run locally.
5. How to deploy.
6. How to debug (logs, health checks, common failures).
7. Test strategy and key commands.
8. Dependencies and integrations.

## 3. Recommended docs/ Taxonomy

Core categories:
- `docs/specifications/`
- `docs/guidelines-best-practices/`
- `docs/improvement-recommendations/`
- `docs/architecture/`
- `docs/expertise/`

Helpful additional categories:
- `docs/runbooks/` (operations, incidents, recovery)
- `docs/reference/` (API, schema, contracts)
- `docs/adr/` (architecture decision records)
- `docs/templates/` (reusable documentation templates)

## 4. Document Lifecycle

### 4.1 Create

Create a new document when:
- A new feature or workflow is introduced.
- A behavior changes in a way users/developers rely on.
- A recurring support/debug issue appears.
- A major architectural or product decision is made.

Required metadata at top of each document:
- `Owner`
- `Last reviewed`
- `Status` (`draft`, `active`, `deprecated`, `obsolete`)

### 4.2 Redact (Write)

Writing rules:
- Start with purpose, then prerequisites, then steps.
- Prefer task-oriented headings (`How to...`, `Troubleshooting...`).
- Keep language direct and unambiguous.
- Use examples for commands, requests, and config.
- Avoid internal jargon unless defined in a glossary.

Security and privacy rules:
- Never include secrets, credentials, tokens, or private keys.
- Redact sensitive values in examples.
- Do not include personal or customer-identifying data unless explicitly permitted.

### 4.3 Modify / Update

When changing behavior in code:
- Update relevant docs in the same PR whenever possible.
- If not possible, create a tracked follow-up with owner and due date.

For updates:
- Keep history meaningful (`What changed` and `Why`).
- Mark deprecated content with migration guidance.
- Move obsolete content to an archive folder.

### 4.4 Maintain

Maintenance cadence:
- Critical docs (runbooks, deployment, security): review monthly.
- Active technical docs: review quarterly.
- Long-lived reference docs: review every 6 months.

Maintenance requirements:
- Each document must have a named owner/team.
- Broken links and stale commands must be fixed quickly.
- Outdated docs should be corrected, deprecated, or archived.

## 5. Quality Standards

A document is complete when it is:
- Correct: validated against current behavior.
- Actionable: contains enough steps for execution.
- Scoped: focused on one topic.
- Linked: references related docs.
- Testable: examples/commands can be executed.

Avoid:
- Copy/paste duplicates across multiple docs.
- Large mixed-topic documents.
- Ambiguous words like "soon", "usually", "sometimes".
- Unowned or undated documents.

## 6. Versioning and Naming

Naming conventions:
- Use clear, stable, kebab-case filenames.
- Keep one topic per file.
- Prefer explicit names over generic names (`api-authentication.md` vs `notes.md`).

Versioning conventions:
- Version docs that describe external contracts (APIs, schemas, protocols).
- Keep migration notes when breaking changes occur.

## 7. Suggested Review Workflow

For each documentation PR:
1. Technical review by feature owner.
2. Readability review by someone outside the implementation.
3. Link/command validation.
4. Confirm metadata (`owner`, `last reviewed`, `status`) is present.

## 8. Templates (Recommended)

Use `docs/templates/` for:
- Root README template.
- Service README template.
- Specification template.
- Architecture template.
- Runbook template.
- ADR template.

## 9. Automation Recommendations

Use CI checks to enforce documentation quality:
- Markdown linting.
- Link checking.
- Spell checking.
- Optional docs coverage check (e.g., each service must have `README.md`).
- Optional stale-doc alerts based on `Last reviewed` date.

## 10. Governance Recommendations

To keep documentation complete over time:
- Define a documentation owner per service.
- Make "docs impact" a required PR checklist item.
- Include documentation review in release readiness checks.
- Run periodic doc audits and cleanups.
- Treat docs as product: measurable, reviewed, and continuously improved.
