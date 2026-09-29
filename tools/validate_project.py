#!/usr/bin/env python3
"""Validate local skill/context/WikiSkill structure and RDF profile, not legacy corpus."""
import hashlib
import json
from pathlib import Path
import re
import sys
import yaml
from rdflib import Graph, Namespace, RDF, OWL

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_SKILLS = {'crawl-wikipedia-diaban', 'crawl-wikipedia-coquan',
    'resolve-wikipedia-entity', 'stat-wikipedia', 'ontology-wikipedia',
    'wiki-maintainer', 'wisdom-skill-proposer', 'sync-wikipedia-github'}


def frontmatter(text):
    match = re.match(r'^---\n(.*?)\n---(?:\n|$)', text, re.S)
    if not match:
        raise ValueError('Missing frontmatter')
    data = yaml.safe_load(match.group(1))
    if not isinstance(data, dict):
        raise ValueError('Frontmatter is not a mapping')
    return data


def validate(root):
    errors = []
    skill_files = sorted((root / 'skills').glob('*/SKILL.md'))
    names = {p.parent.name for p in skill_files}
    for name in sorted(REQUIRED_SKILLS - names):
        errors.append('Missing skill: ' + name)
    knowledge = [root / 'SKILLS.md'] + [p for d in ('context', 'wiki', 'raw', 'reports') for p in (root/d).rglob('*.md')]
    files = skill_files + knowledge + [root/'skills/index.md']
    for path in files:
        try:
            text = path.read_text()
            data = frontmatter(text)
            if path.name == 'SKILL.md':
                if data.get('name') != path.parent.name or not re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*', data.get('name', '')):
                    errors.append(str(path.relative_to(root)) + ': invalid name')
                if not isinstance(data.get('description'), str) or not data['description'].strip():
                    errors.append(str(path.relative_to(root)) + ': missing description')
                if str(data.get('metadata', {}).get('okf_version')) != '0.2':
                    errors.append(str(path.relative_to(root)) + ': missing skill OKF metadata')
            else:
                for key in ('okf_version', 'type', 'title', 'updated', 'status'):
                    if not data.get(key):
                        errors.append(str(path.relative_to(root)) + ': missing ' + key)
                if str(data.get('okf_version')) != '0.2':
                    errors.append(str(path.relative_to(root)) + ': wrong OKF version')
            if re.search(r'/Users/|/home/|[A-Za-z]:\\', text):
                errors.append(str(path.relative_to(root)) + ': physical machine path')
            # Code examples may intentionally describe non-resolving sample links.
            body = re.sub(r'```.*?```|`[^`]*`', '', text, flags=re.S)
            for target in re.findall(r'\[\[([^\]|]+)(?:\|[^\]]*)?\]\]', body):
                target = target.rstrip('\\')
                dest = root / (target + '.md')
                if not dest.is_file():
                    errors.append(str(path.relative_to(root)) + ': broken wiki link ' + target)
            for target in re.findall(r'(?<!!)\[[^\]]+\]\(([^)]+)\)', body):
                if '://' in target or target.startswith('#'):
                    continue
                dest = (path.parent / target.split('#')[0]).resolve()
                if not dest.is_relative_to(root.resolve()) or not dest.exists():
                    errors.append(str(path.relative_to(root)) + ': broken Markdown link ' + target)
        except (ValueError, OSError, yaml.YAMLError, TypeError) as exc:
            errors.append(str(path.relative_to(root)) + ': ' + str(exc))
    for folder in ('context', 'wiki', 'wiki/patterns', 'raw', 'reports', 'skills'):
        if not (root/folder/'index.md').is_file():
            errors.append('Missing hub: ' + folder)
    try:
        graph = Graph().parse(root / 'context/ontology.ttl', format='turtle')
        wiki = Namespace('https://github.com/leanhvu-ktnn/RAW_WIKIPEDIA/ontology#')
        legal = Namespace('http://vbpl.vn/ontology/legal#')
        for entity in (legal.DiaBan, legal.CoQuan, wiki.Page, wiki.Revision, wiki.Match, wiki.CrawlRun):
            if (entity, RDF.type, OWL.Class) not in graph:
                errors.append('Missing ontology class: ' + str(entity))
        for prop in (wiki.target, wiki.candidatePage, wiki.observedIn, wiki.hasRevision, legal.thuocDiaBan):
            if (prop, RDF.type, OWL.ObjectProperty) not in graph:
                errors.append('Missing ontology relationship: ' + str(prop))
    except Exception as exc:
        errors.append('Ontology parse error: ' + str(exc))
    for path in sorted((root/'raw').rglob('*.json')):
        if path.name == 'audit.json':
            continue
        try:
            data = json.loads(path.read_text())
            evidence = data['evidence_raw'].encode('utf-8')
            if hashlib.sha256(evidence).hexdigest() != data['evidence_sha256']:
                errors.append(str(path.relative_to(root)) + ': trace checksum mismatch')
            if json.loads(evidence) != data['evidence']:
                errors.append(str(path.relative_to(root)) + ': trace evidence mismatch')
        except (OSError, ValueError, KeyError, TypeError) as exc:
            errors.append(str(path.relative_to(root)) + ': invalid trace ' + str(exc))
    return errors


if __name__ == '__main__':
    errors = validate(ROOT)
    for error in errors:
        print('FAIL:', error)
    print(f'{"FAIL" if errors else "PASS"}: skills/context/wiki/ontology profile; legacy corpus excluded')
    sys.exit(bool(errors))
