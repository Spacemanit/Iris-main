# Pre-2019 technical writing references

This workflow combines dated primary texts with the inherited unslop rules. It is an editorial method, not a demonstrated guarantee about authorship or detection. Sources were checked online on October 13, 2026. Recheck any new edition or replacement page before treating it as the same text.

## Verified starting points

These texts qualify by their original publication dates. Use the identified edition and passage, not a current handbook that happens to have the same title.

| Source and publication date | Passage to read | Writing practice to adapt |
| --- | --- | --- |
| George D. Gopen and Judith A. Swan, *The Science of Scientific Writing*, *American Scientist* 78, no. 6, November-December 1990, pp. 550-558. [Publication record](https://scholars.duke.edu/publication/881487). [Full-text university reprint](https://biology.williams.edu/files/2012/01/GopenSwan.pdf). | Sections on the topic position, stress position, and writing and the scientific process. | Introduce context before new material, keep subjects near verbs, and place important results where readers expect emphasis. The authors explicitly caution against treating these principles as a fixed algorithm. |
| Mary K. McCaskill, *Grammar, Punctuation, and Capitalization: A Handbook for Technical Writers and Editors*, NASA SP-7084, 1990. [NASA publication record](https://ntrs.nasa.gov/citations/19900017394). [Full text](https://ntrs.nasa.gov/api/citations/19900017394/downloads/19900017394.pdf). | Sections 2.2 on verbs, 2.3 on parallelism, and 2.4 on brevity and conciseness. | Revise weak verb constructions, maintain grammatical consistency in lists, and remove redundant phrasing. Preserve necessary substance when shortening. NASA's record distinguishes the 1990 publication from its later acquisition date. |
| Heather Flanagan and Sandy Ginoza, *RFC Style Guide*, RFC 7322, September 2014. [Fixed RFC text](https://www.rfc-editor.org/rfc/rfc7322.html). | Section 2 on editorial philosophy and sections 3.4-3.6 on capitalization, citations, and abbreviations. | Preserve intended technical meaning while improving consistency and readability. Use consistent terminology and clear references. Its literal-string convention keeps punctuation outside a quoted string when the punctuation is not part of that string. |
| Information Sciences Institute, Jon Postel as editor, *Transmission Control Protocol*, RFC 793, September 1981. [Fixed RFC text](https://www.rfc-editor.org/rfc/rfc793.html). | Section 2.6 on reliable communication. | Study how the explanation moves from the purpose to sequence numbers, acknowledgments, a queue, and a timeout condition. Use that progression to explain another mechanism. This is a historical style exemplar. Check current specifications before making present-day TCP claims. |

The living web supplement linked from RFC 7322 is a separate resource. The RFC's 2014 date does not date every revision of that supplement. Likewise, the current NASA or university page footer does not establish the date of the publication it hosts.

## How to implement the source requirement

Use a small, relevant set of verified passages instead of collecting a large corpus for each edit. Keep the author, edition, date evidence, and passage location together so later use can avoid repeated searches. An institutional record establishes bibliographic identity, while the full text establishes what the passage actually does. Both matter.

For a new domain, search for the subject plus a document type and a historical date range. For example, a device procedure may benefit from a dated manufacturer manual, while a system explanation may benefit from a dated specification. Search-engine date restrictions help find candidates but are insufficient for verification. An archive capture dated on or before December 31, 2018 can establish that the captured passage existed by the cutoff. It does not prove the site's original publication date or qualify later edits.

Extract a small set of applicable observations in your own words, such as how the author introduces a term, orders conditions, connects paragraphs, or distinguishes a requirement from a recommendation. Apply those observations to the user's content. The original unslop rules still govern vocabulary, punctuation, and formatting. Do not copy old page layouts, boilerplate, jargon, or factual assumptions.

This source-selection and revision procedure is a synthesis of the user's cutoff requirement and the cited editorial guidance. The sources support the writing practices described above. They do not establish that this procedure removes every AI tell.

## Example source note

```text
Role: Style exemplar
Institution: Information Sciences Institute
Editor: Jon Postel
Title: Transmission Control Protocol
Version: RFC 793
Publication: September 1981
Date evidence: Dated RFC title and header
URL: https://www.rfc-editor.org/rfc/rfc793.html
Passage: Section 2.6, Reliable Communication
Practice: Explain the purpose, stored state, and timeout consequence in order
Factual use: Historical only unless checked against current specifications
```

## Worked revisions

The examples below are invented editorial examples, not reported measurements or behavior drawn from the cited publications.

Original:

> The robust validation framework seamlessly enhances reliability, ensuring that invalid inputs are effectively handled.

Revision, if the supplied technical description confirms this behavior:

> The loader checks each date before saving the file. If a date is invalid, the loader reports the row number and leaves the file unchanged.

The revision names an actor, an action, a condition, and an observable result. Without evidence for the error message or file behavior, retain only the supported claim, such as "The loader checks each date."

Original:

> The implementation of buffering facilitates efficient transmission of messages in an asynchronous manner.

Revision, if the draft establishes a queue and worker:

> The sender adds each message to a queue. A worker sends queued messages when the connection is available.

The revision follows the mechanism from input to action and states the relevant condition. It makes no unsupported speed claim.

Original:

> These findings could potentially suggest that the change may significantly improve throughput.

Revision, when the underlying evidence is still tentative:

> These findings suggest that the change may increase throughput.

The revision removes repeated hedging while preserving uncertainty. Add a measured difference only when the evidence supplies one, along with the comparison and conditions.
