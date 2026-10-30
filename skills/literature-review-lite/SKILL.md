---
name: literature-review-lite
description: Find and assess papers, organize a claim-linked evidence table, and write or revise a focused literature review or related-work section. Use for narrative reviews, thesis background, and research-gap analysis; formal systematic reviews and meta-analyses require a broader protocol.
license: MIT
---

# Literature Review Lite

Produce a useful, bounded review: define the question, collect evidence, compare studies by theme, and check the draft. This is a small adaptation of the K-Dense scientific-writer workflow; see [references/upstream.md](references/upstream.md) for provenance and scope.

Use tools already available in the host. No dedicated search service, API key, image generator, or LaTeX installation is required. Online discovery needs a search/browsing tool; the optional helper needs Python 3.10+ and only its standard library.

## Start or resume

Read existing review files and user-supplied papers before searching. Continue an existing draft when asked to revise it. Respect the user's topic, output folder, style, and size. Ask for the topic if absent; infer other ordinary choices and record them in `brief.md`.

For a new task, default to a focused narrative review in Markdown, roughly 1,500 words, with 3–5 themes. These are adjustable starting points. Select sources for coverage and relevance rather than a citation quota. Do not claim exhaustiveness, PRISMA compliance, or systematic-review status from this lightweight process.

Create a distinct folder such as `writing_outputs/<topic>-review/`, preserving existing files. Optionally run the bundled helper from the skill directory:

```text
python scripts/review.py init <review-folder>
```

Paths in these commands are relative to this skill, not the user's project. Resolve the script's absolute path when executing elsewhere. Initialization creates the brief, search log, empty evidence ledger, and review template without replacing existing files. For a one-paragraph edit, use the same evidence principles without creating the full folder.

## 1. Scope and find

Record the research question, intended audience, date range, inclusion/exclusion criteria, and requested length in `brief.md`. Distinguish related-work positioning from a general survey. For technical projects, include the dimensions that affect the design: methods, sensing/control approach, operating conditions, and evaluation metrics.

Build a few targeted queries using the central concept, synonyms, key methods, and application. Cover foundational work, recent work, and contrary or unsuccessful findings. Use more than one discovery route when useful: a relevant scholarly index, publisher/repository searches, and references from a strong seed paper. Select routes appropriate to the field; do not present ordinary web search as direct database access.

Record actual search dates, exact queries, tools/sites searched, and screening decisions in `search-log.md`. Report result counts only when observable. Deduplicate using DOI, then normalized title; link a preprint to its published version and prefer the latter when accessible. Avoid repeating searches whose saved results already answer the question.

If browsing is unavailable, work from supplied papers and identify the coverage limitation. Do not invent papers or imply online verification happened.

## 2. Extract evidence before making claims

Open each selected paper's publisher, repository, or index record. Verify bibliographic identity separately from whether the paper supports the proposed claim. Metadata verification does not establish evidentiary support.

Read the full text when available. If only the abstract is available, extract only claims the abstract supports and label that access level. Search snippets and titles alone are candidates, not evidence. Record a section, page, table, or paragraph locator for findings and numerical results. Note design, sample/context, limitations, and publication status; do not compare benchmark numbers as if datasets and conditions were identical.

Keep an `evidence.json` list, one object per paper, using the schema below. Write `evidence.md` as a human-readable table from the same ledger with columns for paper, method/context, finding, limitations, and theme. Keep the ledger as the source of truth and update the table when the evidence changes.

```json
[
  {
    "key": "Author2024ShortTopic",
    "title": "Exact title from the source",
    "authors": ["Author name from the source"],
    "year": 2024,
    "url": "https://publisher-or-repository.example/paper",
    "doi": "",
    "source_path": "",
    "publication_status": "published",
    "metadata_verified": true,
    "access": "full-text",
    "themes": ["Theme name"],
    "method_context": "Design, population or dataset, and evaluation conditions",
    "findings": [
      {"claim": "Paraphrased finding supported by the paper", "locator": "Section 4, Table 2"}
    ],
    "limitations": ["Relevant limitation supported by the source"],
    "notes": "Verification date/source and any unresolved details"
  }
]
```

Keys use letters, digits, underscores, or hyphens. `access` is `full-text`, `abstract`, or `metadata-only`; `publication_status` is `published`, `preprint`, or `unknown`. Provide a source URL or a `source_path` pointing to a supplied paper; offline checking against that paper is valid. Keep unknown bibliographic fields blank rather than guessing. Set `metadata_verified` only after checking the paper or a reliable source record. Use `findings: []` for metadata-only candidates and keep them out of evidence-backed prose. These statuses are human/agent assessments, not automatic proof.

## 3. Synthesize and write

Build a brief theme outline from the ledger, then draft connected prose. Organize around questions and approaches rather than one paragraph per paper. For each theme, establish the pattern, compare supporting and conflicting studies, explain differences in methods or settings, and state what remains uncertain. Scale confidence to study quality and directness of evidence; distinguish author conclusions from your inference.

Use claim-adjacent `[@Key]` citations (multiple sources: `[@KeyA; @KeyB]`) while drafting. Every substantive literature claim and reported number needs support from the ledger. A citation is sufficient only when its recorded finding supports the sentence. Keep uncited background modest. Narrow or omit unsupported claims, and record the evidence gap in `qa.md`.

Use [assets/review-template.md](assets/review-template.md) as an editable starting structure. Include a short, honest account of search coverage, thematic synthesis, limitations, and research gaps. Phrase gaps as observations within the reviewed literature; do not claim that no prior work exists because a small search found none. Relate gaps to the user's project without inventing novelty or results.

In `## References`, add one bibliographic entry per cited key as `- **Key**: Authors. (Year). Title. Venue if verified. DOI, source URL, or supplied source path.` Retain the key markers through automated checking. Use the user's final citation style when requested, retaining the checked working draft; generate BibTeX only when useful, using verified fields.

## 4. Check and deliver

Run the optional local audit on the working draft:

```text
python scripts/review.py check <review-folder>
```

It checks citation/ledger/reference consistency, duplicate identifiers, and required evidence fields. It does **not** verify URLs, DOI resolution, bibliographic truth, study quality, or claim support. Inspect those against sources yourself. Review the prose once for contradictions, overstatement, numerical comparability, and whether it actually synthesizes studies. Fix concrete issues; do not expand the search or add polish indefinitely.

Save `qa.md` with access limitations, unresolved evidence needs, audit result, and a short manual claim-check summary. Deliver links to the draft and evidence table, along with the main uncertainty. A new complete review normally includes `brief.md`, `search-log.md`, `evidence.json`, `evidence.md`, `review.md`, and `qa.md`. Do not present it as submission-ready if central evidence remains unavailable. Export Word/PDF only when requested, using an available document workflow.
