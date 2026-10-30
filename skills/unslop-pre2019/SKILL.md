---
name: unslop-pre2019
description: Draft or revise prose using the original unslop language rules and verified technical writing published on or before December 31, 2018 as style references.
---

# Unslop with pre-2019 technical writing

Edit text to remove AI patterns. Scan for the patterns below, then rewrite. Preserve meaning and match the intended tone.

This is a separate clone of `../unslop/SKILL.md`. The original numbered rules below remain intact. Apply them when drafting new prose too. The added workflow requires dated technical writing as a positive style reference, in addition to removing the patterns listed here. Keep the user's intended audience and register.

The publication cutoff is December 31, 2018, inclusive. It is a source-selection rule, not proof that a text is good or free of machine assistance. Preserve technical accuracy when applying any language rule. Do not alter code, literal strings, equations, identifiers, quotations, or formal requirement words to satisfy a prose preference.

## Patterns to detect and fix

Rule numbers are stable ids that other skills cite. A removed rule leaves a gap.

### Content

3. **Superficial -ing phrases.** "highlighting...", "ensuring...", "reflecting...", "showcasing...", "fostering...". Delete or expand with real sources.
5. **Vague attributions.** "Experts believe", "Industry reports suggest", "Some critics argue". Name the source or delete.

### Language

7. **AI vocabulary.** Additionally, crucial, delve, enduring, enhance, fostering, garner, interplay, intricate, landscape (abstract), pivotal, showcase, tapestry (abstract), testament, underscore, vibrant. Replace with plain words.
8. **Fancy ways to say "is".** "serves as", "stands as", "boasts", "features". Say "is" or "has".
9. **"Not just X, but Y."** State the point directly instead.
10. **Rule of three.** Don't force ideas into groups of three. Use the natural number.
11. **Synonym cycling.** Protagonist, main character, central figure, hero all in one paragraph. Pick one, repeat it.
12. **False ranges.** "from X to Y" where X and Y aren't on a meaningful scale. List topics directly.

### Style

13. **Em dash overuse.** Avoid em dashes entirely. Use periods or commas only (no parentheses, no en dashes, no hyphen-as-dash substitutes). If a thought needs separation, end the sentence or use a comma.
14. **Colon overuse.** Colons are fine before a list or example, not as mid-sentence connectors. "If you're coming from traditional automation: instead of registering event handlers, you describe conditions" adds nothing with the colon. Rewrite to let the point stand on its own without comparison framing. "Describing when the scheduler should fire works best as plain English." Same meaning, no crutch punctuation.
15. **Boldface overuse.** Don't bold every proper noun or acronym.
16. **Inline-header lists.** The tell is a bold label and colon that restates the line: "**Performance:** Performance improved...". Convert those to prose. A bold lead-in that ends in a period, names the item, and is followed by genuinely new detail ("**Schema in TypeScript.** Tables live in one file.") is fine, not a tell.
17. **Title case headings.** Use sentence case.
18. **Decorative emojis.** Remove from headings and bullets.
19. **Curly quotes.** Use straight quotes.

### Communication artifacts

20. **Chatbot phrases.** "I hope this helps!", "Let me know if...", "Of course!", "Certainly!", "Found the smoking gun!" Remove.
22. **Sycophantic tone.** "Great question! You're absolutely right!" Respond directly.

### Filler

23. **Filler phrases.** "In order to" becomes "To". "Due to the fact that" becomes "Because". Delete "It is important to note that".
24. **Excessive hedging.** "could potentially possibly be argued that it might" becomes "may".
25. **Generic conclusions.** "The future looks bright." State specific plans or facts.

### Jargon

26. **Abstract metaphor nouns.** Substrate (base), wedge, wedge in (add), vector (way, method), locus, vantage, nexus, primitive as a noun, harness as a metaphor, surface as in "API surface", bedrock, scaffolding as a metaphor, modality, paradigm, gold-plating (more than the job needs), ratchet as a metaphor (the mechanism's real name, or a limit that only tightens), evacuate for moving code (move out), endgame (the last phase), north star, flywheel. These read as technical but usually have a plainer concrete word. Pick the concrete word.

### Plain speech

27. **Say what it does, not how it feels.** "the database stays close at hand", "SQL you can read", "types that follow your schema" name a feeling. The fix names the mechanism or a number: "`.toSQL()` returns the exact string sent to the database", "a column rename fails the build". Ask what the sentence tells the reader to do or know, then write that. If you can't restate it as a concrete instruction, fact, or number, cut it. One more check: if the sentence could appear unchanged in another project's docs, it says nothing about this one. Cut it.
28. **Shorten or split dense sentences.** If the reader has to backtrack to parse a sentence, break it in two or drop clauses. One idea per sentence.
29. **Active voice.** Prefer it. Catch "is/are/was/were + past participle" and name the actor: "queries are validated" becomes "the compiler validates queries", "the file is parsed by the loader" becomes "the loader parses the file". Passive is fine only when the actor is unknown or genuinely doesn't matter.
30. **Cut adverbs, or use a stronger verb.** "runs quickly" becomes "is fast" or the number, and "significantly improves" becomes the measured delta. An adverb propping up a weak verb means the verb is wrong.
31. **Prefer the plain word.** "utilize" and "leverage" become "use", "facilitate" becomes "help", "numerous" becomes "many", "in the event that" becomes "if". The fancier synonym is rarely clearer.
32. **Mannered prose.** Metaphor or flourish where a literal phrase exists: aphorisms ("wire it or delete it"), rhetorical fragments for effect, personified code ("the plan holds it"), figurative verbs ("rides along", "stands on"), stock framing phrases. "A dial worth turning" becomes "a parameter worth varying". Say what you mean. Rule 26 covers the metaphor nouns.
33. **Over-compression.** Dropped articles, verbless fragments, symbol-speak, and abbreviations that make the reader decode instead of read. "Parser rejects bad date → exit 2, no write" becomes "The parser rejects a bad date, exits with code 2, and writes nothing." Write whole sentences with their articles and verbs, and spell out arrows and abbreviations.

### Technical writing additions

34. **Use verified writing from 2018 or earlier.** For substantive drafting or revision, read a relevant passage from at least one qualifying technical document before writing. Use its explanatory structure and precision alongside the original rules. Follow the source-selection workflow below.
35. **Connect familiar information to new information.** Begin with the reader's existing context, keep the subject near its verb, and place the main result where it receives emphasis. Apply this where it improves comprehension. Do not impose the same sentence pattern throughout.
36. **Put actions in verbs.** "The implementation of validation is performed by the loader" becomes "The loader validates the input." Keep a technical noun when it names a real concept, such as validation or authentication, rather than disguising an action.
37. **State the condition and its consequence.** For a mechanism, name the component, input or condition, action, and observable result as needed. For a procedure, give prerequisites before the action and state how the reader can recognize success or failure. Do not add missing behavior from a style exemplar.
38. **Preserve warranted uncertainty.** Keep assumptions, exceptions, evidence limits, units, comparison baselines, and scope. Remove empty hedging without converting a possibility into a fact or a recommendation into a requirement.
39. **Remove repeated framing and recap.** Cut generic openings about a changing world, previews that repeat headings, rhetorical questions immediately answered by the writer, and conclusions that restate the body without adding a decision or next action. Keep repetition that helps a reader follow an actual procedure or definition.
40. **Use only supported specifics.** Replace vague praise with an available fact or mechanism. Do not invent measurements, citations, quotations, examples of actual behavior, or personal experience to make prose sound concrete. Label hypothetical examples when confusion is possible.

## Source-selection workflow

Read [references/pre2019-writing.md](references/pre2019-writing.md) when selecting sources or applying the added rules. It provides researched starting points, passage locations, and examples. Its summaries are aids to selection. Read the source passage itself before using it as an exemplar.

1. Establish the audience and deliverable from the user's request. Prefer a technical document in the same field and a comparable form, such as a manual for instructions or a research paper for a research explanation. For nontechnical prose, borrow clarity and organization without adding technical vocabulary or a formal research tone.
2. Search primary publishers, standards bodies, institutional repositories, or versioned documentation. Combine the topic and document type with a year range or a search date filter. Treat results as candidates. A filter or snippet does not verify the date or the text.
3. Open the document and verify the date of the exact text being used. Use the publication record, dated title page, issue information, edition, or a dated repository revision. A dated original or unchanged reprint qualifies. An old article's later rewrite does not qualify. For a page edited after 2018, obtain the earlier edition or archived version and confirm it contains the passage. Ignore crawl dates, upload dates, footer copyright years, and unsupported date claims.
4. Read enough surrounding text to judge the explanation. Select for clear definitions, named actors, explicit conditions, restrained claims, and suitable paragraph order. Age alone is insufficient. Skip an unclear source even if its date qualifies. If the first source is sufficient, stop searching. Add another only when a different form or problem needs it.
5. Keep a compact source note in working context, or in the user's existing research notes for a longer task. Record author or institution, title, edition or version, publication date and its evidence, direct URL, passage location, and the writing move being borrowed. Reuse a previously verified source when its exact edition and relevant passage are available. Do not create research files for a short edit unless requested.
6. Draft or revise using the selected writing moves. Borrow organization and explanatory habits, not distinctive wording, authorial identity, historical facts, obsolete API behavior, or old measurements. Preserve the original numbered rules when a source uses a different punctuation or formatting convention.

Use the 2018 cutoff for style exemplars. Verify factual claims against sources appropriate to the subject, including current sources when needed. If the user separately limits factual evidence to 2018 or earlier, respect that limit and identify the historical scope. A current source used for fact-checking does not qualify as a style exemplar.

When browsing is unavailable, use an already verified exact text or a supplied document with reliable publication evidence. If no qualifying text is available, perform the original language-rule pass and briefly disclose that the required dated-source pass could not be completed. Never claim to have read or verified a source that was inaccessible.

## Final editing pass

Check the draft against the original rules and the technical additions. Read each paragraph for a clear point, a traceable connection to the previous paragraph, and information the reader actually needs. Vary sentence length according to the explanation rather than forcing uniform brevity.

Compare meaning before and after. Check numbers, units, negation, conditions, definitions, requirement strength, citations, and necessary uncertainty. Keep exact technical terms when a plainer synonym would change their meaning. Remove filler around them.

Judge the result by readability and fidelity. Do not use detector scores, fabricated quirks, random errors, or forced informality as quality targets. Do not promise the removal of every possible AI tell or claim that the result was written by a human.

Return the requested prose. Include citations for factual claims as the task requires. Provide the style-source note separately when requested or when explaining the method. Avoid inserting style-guide citations into the user's prose merely to prove the editing workflow happened.
