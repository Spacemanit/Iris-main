from pathlib import Path
from urllib.request import Request, urlopen
from pypdf import PdfReader
import json

root = Path(__file__).resolve().parent / 'review_sources'
root.mkdir(exist_ok=True)
urls = {
    'admoni2017': 'https://publications.ri.cmu.edu/storage/publications/2018/01/admoni2017jhri.pdf',
    'sun2017': 'https://arxiv.org/pdf/1601.02284',
    'mirror2025': 'https://arxiv.org/pdf/2506.18466',
}
for key, url in urls.items():
    target = root / (key + '.pdf')
    try:
        if not target.exists():
            with urlopen(Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=25) as response:
                data = response.read()
            if not data.startswith(b'%PDF'):
                raise ValueError('Response is not a PDF')
            target.write_bytes(data)
        reader = PdfReader(target)
        (root / (key + '.txt')).write_text('\n\n'.join(f'--- PDF page {i+1} ---\n{p.extract_text()}' for i, p in enumerate(reader.pages)), encoding='utf-8')
        print(key, len(reader.pages), 'pages extracted')
    except Exception as exc:
        print(key, type(exc).__name__, str(exc))
for name in ['Literature Reviews.pdf', 'pcbi.1003149.pdf']:
    source = Path('research') / name
    reader = PdfReader(source)
    (root / (source.stem + '.txt')).write_text('\n\n'.join(f'--- PDF page {i+1} ---\n{p.extract_text()}' for i, p in enumerate(reader.pages)), encoding='utf-8')
    print(name, len(reader.pages), 'pages extracted')
