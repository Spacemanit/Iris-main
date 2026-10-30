from pathlib import Path
import json
import re

folder = Path('writing_outputs/iris-literature-review')
tex = (folder / 'Iris_Literature_Review.tex').read_text(encoding='utf-8')
papers = json.loads((folder / 'evidence.json').read_text(encoding='utf-8'))
body, bibliography = tex.split(r'\begin{thebibliography}', 1)
keys = re.findall(r'\\bibitem\{([^}]+)\}', bibliography)
first = []
for group in re.findall(r'\\cite\{([^}]+)\}', body):
    for key in group.split(','):
        if key not in first:
            first.append(key)
assert first == keys, ('Reference order differs from first citations', first, keys)
assert set(keys) == {p['key'] for p in papers}
assert len(keys) == len(set(keys)) == 17
abstract = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', tex, re.S).group(1)
assert len(abstract.split()) <= 250
assert 'Eklavya~Nathani, Manit~Bisht, and Anis~Fatema' in tex
assert 'Working manuscript' not in tex
assert not re.search(r'[\u2013\u2014]', tex)

def readable(text):
    text = re.sub(r'\\cite\{([^}]+)\}', lambda m: '[' + '; '.join('@'+k for k in m[1].split(',')) + ']', text)
    text = re.sub(r'\\doi\{([^}]+)\}', lambda m: 'https://doi.org/' + m[1], text)
    text = re.sub(r'\\url\{([^}]+)\}', r'\1', text)
    text = re.sub(r'\\emph\{([^}]+)\}', r'*\1*', text)
    text = re.sub(r'\\texttt\{([^}]+)\}', lambda m: chr(96)+m[1]+chr(96), text)
    text = re.sub(r'\\IEEEPARstart\{([^}]+)\}\{([^}]+)\}', r'\1\2', text)
    text = text.replace(r'\&', '&').replace('~', ' ').replace('``', '"').replace("''", '"')
    return text

title = re.search(r'\\title\{([^}]+)\}', tex)[1]
working = body.split(r'\maketitle', 1)[1]
working = re.sub(r'\\begin\{abstract\}', '## Abstract', working)
working = working.replace(r'\end{abstract}', '')
working = working.replace(r'\begin{IEEEkeywords}', 'Keywords:').replace(r'\end{IEEEkeywords}', '')
working = re.sub(r'\\section\*?\{([^}]+)\}', r'## \1', working)
working = re.sub(r'\\subsection\{([^}]+)\}', r'### \1', working)
working = readable(working)
# Keep equations and native table markup in this working-text copy; the
# standalone manuscript is the authoritative formatted artifact.
refs = []
for key, entry in re.findall(r'\\bibitem\{([^}]+)\}\s*(.*?)(?=\\bibitem|\\end\{thebibliography\})', bibliography, re.S):
    refs.append(f'- **{key}**: {readable(entry).strip()}')
(folder / 'review.md').write_text('# ' + title + '\n\nEklavya Nathani, Manit Bisht, and Anis Fatema\n\n' + working.strip() + '\n\n## References\n\n' + '\n\n'.join(refs) + '\n', encoding='utf-8')

table = ['# Evidence table', '', 'The table below is generated from evidence.json. Repository access years are not release dates. Source text and limitations are checked separately from bibliographic identity.', '', '| Source | Method/context and access | Finding and locator | Limitations | Theme |', '| --- | --- | --- | --- | --- |']
for p in papers:
    source = f"[{p['title']}]({p['url']}) ({p['year']}; {p['publication_status']})"
    findings = '<br>'.join(f"{f['claim']} [{f['locator']}]" for f in p['findings'])
    cells = [source, p['method_context']+' Access: '+p['access']+'.', findings, ' '.join(p['limitations']), ', '.join(p['themes'])]
    table.append('| ' + ' | '.join(c.replace('|', '\\|').replace('\n', ' ') for c in cells) + ' |')
(folder / 'evidence.md').write_text('\n'.join(table)+'\n', encoding='utf-8')

prose = body.split(r'\maketitle', 1)[1]
prose = re.sub(r'\\begin\{table\*?\}.*?\\end\{table\*?\}', '', prose, flags=re.S)
prose = re.sub(r'\\[A-Za-z]+(?:\[[^]]*\])?(?:\{[^}]*\})?', ' ', prose)
words = len(re.findall(r"[A-Za-z]+(?:[-'][A-Za-z]+)*", prose))
print(json.dumps({'references':len(keys), 'scholarly_sources':15, 'repositories':2, 'abstract_words':len(abstract.split()), 'approximate_prose_words_excluding_tables_and_references':words, 'reference_order':'pass', 'citation_ledger_match':'pass', 'author_names':'pass', 'plain_punctuation':'pass'}, indent=2))
