# Agent guide — LocationExtractor

## Scope and local reading order

Python place-name extraction library. This guide applies to work for the owner in `MMatlacz/LocationExtractor`. It does not authorize deployments, external writes unrelated to the task, or resource-intensive jobs.

1. Read this entire `AGENTS.md`, then any applicable nested `AGENTS.md` and tool-specific instructions for the files being changed. Recheck at task resumption; do not assume local home-directory instructions were inherited.
2. Start with `README.md`, `pyproject.toml`, `location_extractor/extractor.py`. Inspect the affected source and any existing tests or specifications before choosing implementation or validation steps.
3. Record NER/geographic disambiguation and source-data provenance, retaining MaxMind/GeoLite attribution. Use synthetic text fixtures; do not expose tokens, scraped content or location datasets in status notes.

## Second Brain and project documentation

For owner-authorized work, use the connected owner Notion workspace to find **Second Brain — Home** and **Agent Bootstrap and Routing (AGENTS.md)** by exact title. Read both, then resolve the project by the full repository identity below and follow its Canonical URL. This owner-only step does not apply to unrelated upstream/downstream contributors. Do not commit private workspace URLs, page IDs, metadata or copied content into this public repository.

Repository identity: `MMatlacz/LocationExtractor`. Read the verified project overview, relevant architecture/decision chapters and agent guidance **before planning meaningful changes**. Use actual canonical documents, not just a registry pointer. No repository-specific Notion page is asserted by this file: verify an exact repository link or unambiguous identity in the registry/page; never substitute a similarly named project or invent a URL. If no mapping exists, request the correct target instead of creating a page automatically.

Notion provides context and decisions, not proof of the current code or deployed state. Verify current branch, commit, tests and runtime facts in their actual source systems. Preserve existing source, license and documentation authority; do not copy entire notebooks, datasets, user records, secrets or third-party assets into Notion.

## Closeout after meaningful changes

For owner-authorized implementation, behavior, architecture or research changes, update the relevant existing project Notion document with the verified result and material decisions, in addition to any required repository documentation. Read the target and the Second Brain **Capture, Deduplication and Evidence Review** guidance first. Preserve unrelated text, history, canonical links and evidence; update the existing topic instead of duplicating it.

Record repository/branch, exact commit (or explicitly uncommitted state), affected files, checks actually performed with outcomes, checks not run, limitations and blockers. Keep the update focused on this repository's scope above. Read back the saved page and confirm the intended changes before claiming synchronization. Do not claim a build, deployment or experiment succeeded from documentation alone.

If access or a verified project mapping is missing, report **pending-sync** with the missing target/access, proposed concise update and commit/check references in the private task handoff; do not claim Notion is current or expose private information in public issues. Continue independent safe local work, but pause decisions that require unavailable canonical guidance. This file does not authorize creating pages, changing sharing, sending notifications or expanding the user's task.
