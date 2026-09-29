#!/usr/bin/env python3
"""Read-only audit of the legacy corpus. Stdlib; supports flat scalar frontmatter only."""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re


def metadata(text):
    lines = text.splitlines()
    if not lines or lines[0] != '---':
        raise ValueError('missing frontmatter')
    result = {}
    for line in lines[1:]:
        if line == '---':
            return result
        if not line.strip() or line.startswith('#'):
            continue
        match = re.fullmatch(r'([A-Za-z_][\w-]*):\s*(.*)', line)
        if not match:
            raise ValueError('unsupported frontmatter: ' + line)
        key, value = match.groups()
        if key in result:
            raise ValueError('duplicate key: ' + key)
        if value.startswith('"'):
            value = json.loads(value)
        elif value.startswith("'") and value.endswith("'"):
            value = value[1:-1].replace("''", "'")
        elif value.startswith(('[', '{', '|', '>')):
            raise ValueError('non-scalar frontmatter: ' + key)
        result[key] = value
    raise ValueError('unclosed frontmatter')


def local_path(root, value):
    if not isinstance(value, str) or not value:
        raise ValueError('missing path')
    prefix = 'RAW/WIKIPEDIA/'
    if value.startswith(prefix):
        value = value[len(prefix):]
    path = (root / value).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('path outside corpus')
    return path


def audit(root):
    root = Path(root).resolve()
    findings = defaultdict(list)
    pages, ids = {}, defaultdict(list)
    required = ('wiki_title', 'wiki_pageid', 'source_url', 'oldid', 'license',
                'extracted_at', 'wiki_kind', 'extract_mode')
    for folder in ('DiaBan', 'CoQuan'):
        for path in sorted((root / folder).rglob('index.md')):
            text = path.read_text(encoding='utf-8')
            if not re.search(r'^type:\s*[\"\']?wiki_page[\"\']?\s*$', text, re.M):
                continue
            rel = path.relative_to(root).as_posix()
            try:
                data = metadata(text)
            except (ValueError, TypeError) as exc:
                findings['invalid_frontmatter'].append({'path': rel, 'error': str(exc)})
                continue
            pages[rel] = data
            for key in required:
                if not data.get(key):
                    findings['missing_required'].append({'path': rel, 'field': key})
            for key in ('wiki_pageid', 'oldid'):
                if not str(data.get(key, '')).isdigit() or int(data.get(key, '0') or '0') <= 0:
                    findings['invalid_id'].append({'path': rel, 'field': key})
            ids[data.get('wiki_pageid')].append(rel)
            if data.get('license') != 'CC-BY-SA-4.0':
                findings['unexpected_license'].append(rel)
            if data.get('wiki_kind') == 'DiaBan':
                for key in ('wikipedia', 'website'):
                    if key not in data or (key == 'wikipedia' and not data[key]):
                        findings['missing_diaban_links'].append({'path': rel, 'field': key})
                if data.get('wikipedia') != data.get('source_url'):
                    findings['url_mismatch'].append(rel)
                if '## Liên kết' not in text or '- Website:' not in text:
                    findings['missing_link_section'].append(rel)
    for pageid, paths in ids.items():
        if pageid and len(paths) > 1:
            findings['duplicate_pageid'].append({'pageid': pageid, 'paths': paths})
    catalog, manifests = [], {}
    for number, line in enumerate((root / '_catalog.jsonl').read_text().splitlines(), 1):
        try:
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError('record is not an object')
            catalog.append(row)
        except ValueError as exc:
            findings['invalid_catalog'].append({'line': number, 'error': str(exc)})
    manifest_paths = set()
    for path in sorted(root.glob('_manifest*.json')):
        rows = json.loads(path.read_text())
        manifests[path.name] = len(rows)
        for row in rows:
            try:
                target = local_path(root, row.get('path'))
            except ValueError as exc:
                findings['invalid_manifest_path'].append({'manifest': path.name, 'error': str(exc)})
                continue
            rel = target.relative_to(root).as_posix()
            manifest_paths.add(rel)
            if rel not in pages:
                findings['manifest_missing_page'].append({'manifest': path.name, 'path': rel})
            else:
                for key in ('wiki_pageid', 'oldid'):
                    if str(row.get(key)) != str(pages[rel].get(key)):
                        findings['manifest_metadata_mismatch'].append({'path': rel, 'field': key})
    findings['pages_without_manifest'] = sorted(set(pages) - manifest_paths)
    for row in catalog:
        if row.get('status') == 'hit':
            try:
                target = local_path(root, row.get('path'))
                if not target.is_file():
                    findings['catalog_hit_missing_file'].append(row)
            except ValueError:
                findings['catalog_hit_missing_file'].append(row)
    return {
        'scope': 'Offline structural audit; not factual/entity validation or full YAML validation.',
        'pages': len(pages),
        'page_groups': dict(sorted(Counter(x.get('wiki_kind') for x in pages.values()).items())),
        'catalog_records': len(catalog),
        'catalog_events_by_wave_status': dict(sorted(Counter(str(x.get('wave')) + '/' + str(x.get('status')) for x in catalog).items())),
        'manifest_records': manifests,
        'finding_counts': {k: len(v) for k, v in sorted(findings.items()) if v},
        'findings': {k: v for k, v in sorted(findings.items()) if v},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path)
    parser.add_argument('--strict', action='store_true', help='Exit 1 on any finding')
    args = parser.parse_args()
    report = audit(args.root)
    payload = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
    if args.output:
        args.output.write_text(payload, encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k != 'findings'}, ensure_ascii=False, indent=2))
    return int(args.strict and bool(report['finding_counts']))


if __name__ == '__main__':
    raise SystemExit(main())
