from pathlib import Path
import hashlib
import re
import shutil

from pypdf import PdfReader

root = Path.cwd()
skill = root / "skills" / "literature-review-from-pdfs"
if skill.exists():
    raise SystemExit("Destination already exists; refusing to replace it.")

handout_pdf = root / "research" / "Literature Reviews.pdf"
rules_pdf = root / "research" / "pcbi.1003149.pdf"
handout_pages = [page.extract_text() for page in PdfReader(handout_pdf).pages]
rules_pages = [page.extract_text() for page in PdfReader(rules_pdf).pages]


def strip_handout_footer(text):
    return re.sub(r"How to Write a Literature Review, Summer 2019\.\s+\d of 7", "", text).strip()


def strip_rules_footer(text):
    return re.sub(
        r"PLOS Computational Biology \| www\.ploscompbiol\.org \d July 2013 \| Volume 9 \| Issue 7 \| e1003149",
        "",
        text,
    ).strip()


handout_sections = [
    strip_handout_footer(handout_pages[0]).split("How to Write a Literature Review ", 1)[1].split("Parts of a Research Paper", 1)[0].strip(),
    strip_handout_footer(handout_pages[1]).split("Examples of Summary, Synthesis, and Evaluation", 1)[0].strip(),
    strip_handout_footer(handout_pages[2]).split("Parts of a Literature Review", 1)[1].strip(),
    strip_handout_footer(handout_pages[3]).split("Sample Literature Review with Annotations", 1)[0].strip(),
]
handout_sections[2] = "Parts of a Literature Review " + handout_sections[2]

rules_sections = [
    strip_rules_footer(rules_pages[0]).split("Literature reviews are in great demand", 1)[1].split("Citation: Pautasso", 1)[0].strip(),
    strip_rules_footer(rules_pages[1]).split("Figure 1. A conceptual diagram", 1)[0].strip(),
    strip_rules_footer(rules_pages[2]),
    strip_rules_footer(rules_pages[3]).split("Acknowledgments", 1)[0].strip(),
]
rules_sections[0] = "Literature reviews are in great demand\n" + rules_sections[0]

headings = [
    "Rule 1: Define a Topic and Audience",
    "Rule 2: Search and Re-search the Literature",
    "Rule 3: Take Notes While Reading",
    "Rule 4: Choose the Type of Review You Wish to Write",
    "Rule 5: Keep the Review Focused, but Make It of Broad Interest",
    "Rule 6: Be Critical and Consistent",
    "Rule 7: Find a Logical Structure",
    "Rule 8: Make Use of Feedback",
    "Rule 9: Include Your Own Relevant Research, but Be Objective",
    "Rule 10: Be Up-to-Date, but Do Not Forget Older Studies",
]

rules_text = "\n\n".join(rules_sections)
for heading in headings:
    pattern = r"\s+".join(re.escape(word) for word in heading.split())
    rules_text, count = re.subn(pattern, "\n\n### " + heading + "\n", rules_text)
    if count != 1:
        raise AssertionError(f"Expected exactly one heading: {heading}")

# Keep source wording and even source hyphenation unchanged. Only add Markdown
# headings and whitespace. Do not silently modernize terminology or repair typos.
handout_text = "\n\n".join(handout_sections)
handout_headings = [
    "The Purpose of a Literature Review",
    "What Isn’t a Literature Review?",
    "What Is a Literature Review?",
    "Three Types of Literature Review Organization",
    "Summary, Synthesis, and Evaluation",
    "Parts of a Literature Review",
    "Tips on Citation",
]
for heading in handout_headings:
    if handout_text.count(heading) != 1:
        raise AssertionError(f"Expected exactly one handout heading: {heading}")
    handout_text = handout_text.replace(heading, "\n\n### " + heading + "\n\n")

# Restore the table and bullet layout without changing the source's words.
table_start = handout_text.index("Organization  Type Explanation Usage")
table_end = handout_text.index("### Summary, Synthesis, and Evaluation")
table_original = handout_text[table_start:table_end]
table_formatted = """| Organization Type | Explanation | Usage |
| --- | --- | --- |
| Chronological | Organized by publication date or history of topic | Use this type if sequential order of events is important |
| Thematic | Organized by topic or issue, may still involve chronology or an order of importance | Use this type to go from general topic themes to more specific (e.g., education to higher education to writing centers) |
| Methodological | Organized not by the content of lit review material, but on the methods of the researcher/writer | Use this type if the methods of the researchers/writers are the most important |

"""


def words(text):
    return " ".join(text.split())


table_plain = re.sub(r"(?m)^\| ---.*\n?", "", table_formatted).replace("|", " ")
assert words(table_plain) == words(table_original)
handout_text = handout_text[:table_start] + table_formatted + handout_text[table_end:]
for title in ["Introduction", "Body", "Conclusion"]:
    handout_text = handout_text.replace("• " + title + " ", "\n\n• " + title + "\n")
handout_text = handout_text.replace(" o ", "\n  o ")
handout_text = re.sub(r"(?m)^(\s*)o ", r"\1- ", handout_text)
handout_text = re.sub(r"(?m)^• ", "- ", handout_text)

skill.mkdir(parents=True)
(skill / "assets").mkdir()
(skill / "agents").mkdir()
for source, filename in [(handout_pdf, "literature-reviews.pdf"), (rules_pdf, "ten-simple-rules.pdf")]:
    copied = skill / "assets" / filename
    shutil.copyfile(source, copied)
    assert hashlib.sha256(source.read_bytes()).digest() == hashlib.sha256(copied.read_bytes()).digest()

intro = """---
name: literature-review-from-pdfs
description: Write or revise a literature review using the original instructions from Christina Cantero's How to Write a Literature Review and Marco Pautasso's Ten Simple Rules for Writing a Literature Review.
---

# Literature review from the original PDFs

Apply the instructions reproduced below to the user's literature-review task. They are copied from the two supplied PDFs. Changes are limited to headings, spacing, and table or list layout. Source wording, punctuation, examples within the rules, and PDF line-break hyphenation are retained.

The first-person statements below belong to the source authors. The sources' sample topics are examples, not a replacement for the user's topic. Use the user's requested scope and deliverable. This is a separate skill based on these PDFs.

## How to Write a Literature Review

Written by Christina Cantero, San José State University Writing Center, Summer 2019. Instructional sections from pages 1-4 are reproduced below. The complete handout, including its examples, classroom activity, and references, is preserved in [the original PDF](assets/literature-reviews.pdf). Read those examples when guidance on synthesis or citation is needed.

"""
between = """

## Ten Simple Rules for Writing a Literature Review

Marco Pautasso, published July 18, 2013. PLoS Computational Biology 9(7), e1003149, doi:10.1371/journal.pcbi.1003149. The article's introduction and all ten rules are reproduced below, including the continuation of Rule 10 on page 4. The figure, publication notices, acknowledgments, and numbered bibliography remain in [the original PDF](assets/ten-simple-rules.pdf). Consult that bibliography for the article's numbered citations. The article is distributed under the Creative Commons Attribution License, as stated in the PDF.

"""
(skill / "SKILL.md").write_text(intro + handout_text.strip() + between + rules_text.strip() + "\n", encoding="utf-8")
(skill / "agents" / "openai.yaml").write_text("""interface:
  display_name: "Literature review from original PDFs"
  short_description: "Follow the original guidance in two supplied PDFs"
  default_prompt: "Use $literature-review-from-pdfs to write or revise this literature review following the original instructions in the two source PDFs."
""", encoding="utf-8")

# Compare the copied prose against the selected source sections after removing
# only the formatting changes introduced above.
plain_handout = re.sub(r"(?m)^\| ---.*\n?", "", handout_text).replace("|", " ")
plain_handout = plain_handout.replace("### ", "")
plain_handout = re.sub(r"(?m)^(\s*)- ", r"\1o ", plain_handout)
for title in ["Introduction", "Body", "Conclusion"]:
    plain_handout = plain_handout.replace("o " + title + "\n", "• " + title + "\n")
assert words(plain_handout) == words("\n\n".join(handout_sections)), "Handout wording changed."
assert words(rules_text.replace("### ", "")) == words("\n\n".join(rules_sections)), "Article wording changed."
assert len(re.findall(r"(?m)^### Rule \d+:", rules_text)) == 10
print(f"Created {skill}")
print("Verified all ten rules, handout wording, and byte-identical source PDF copies.")
