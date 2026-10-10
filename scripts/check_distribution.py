#!/usr/bin/env python3
"""Validate static assets and packaged runner before sharing/deploying the source."""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import zipfile

ROOT = Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.labels = []
        self.assets = []

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if attrs.get('id'):
            self.ids.append(attrs['id'])
        if attrs.get('for') and tag == 'label':
            self.labels.append(attrs['for'])
        if tag in ('script', 'link'):
            value = attrs.get('src') or attrs.get('href')
            if value:
                self.assets.append(value)
        if tag == 'a' and 'download' in attrs and attrs.get('href'):
            self.assets.append(attrs['href'])


def main():
    page = Page()
    page.feed((ROOT / 'dist/index.html').read_text(encoding='utf-8'))
    duplicates = [key for key, count in Counter(page.ids).items() if count > 1]
    assert not duplicates, f'Duplicate HTML IDs: {duplicates}'
    for label in page.labels:
        assert label in page.ids, f'Missing label target: {label}'
    for reference in page.assets:
        parsed = urlsplit(reference)
        assert not parsed.scheme and not parsed.netloc, f'Unexpected remote static asset: {reference}'
        asset = (ROOT / 'dist' / parsed.path).resolve()
        assert asset.is_relative_to(ROOT / 'dist') and asset.is_file(), f'Missing/invalid asset: {reference}'
    with zipfile.ZipFile(ROOT / 'dist/assets/smrf-python-runner.zip') as archive:
        assert set(archive.namelist()) == {'smrf_runner.py', 'README.md'}, 'Unexpected runner ZIP contents'
        for name in archive.namelist():
            assert archive.read(name) == (ROOT / 'runner' / name).read_bytes(), f'Stale packaged runner: {name}'
    assert not (ROOT / '.openai').exists(), 'Host-specific configuration must stay outside the GitHub distribution'
    print('PASS distribution: IDs, labels, local assets and packaged runner match source')


if __name__ == '__main__':
    main()
