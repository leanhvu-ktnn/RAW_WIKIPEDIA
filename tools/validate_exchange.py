#!/usr/bin/env python3
"""Offline validation of the draft INF–RAW contract; never writes to INF or corpus."""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / 'context/schemas/inf-raw-0.1.0.schema.json'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique(rows, field):
    values = [row[field] for row in rows]
    require(len(values) == len(set(values)), 'duplicate ' + field)


def verify_artifact(artifact, candidate, root):
    relative = Path(artifact['path'])
    page = candidate['page']
    revision = candidate['revision']
    prefix = Path('sources') / page['wiki_id'] / page['page_id'] / revision['revision_id']
    require(not relative.is_absolute() and '..' not in relative.parts and relative.is_relative_to(prefix),
            'artifact must be confined to its RAW page/revision prefix')
    path = (root / relative).resolve()
    require(path.is_relative_to(root.resolve()), 'artifact escapes RAW root')
    raw = path.read_bytes()
    require(len(raw) == artifact['byte_length'], 'artifact byte length mismatch')
    require(hashlib.sha256(raw).hexdigest() == artifact['sha256'], 'artifact checksum mismatch')
    data = json.loads(raw)
    require('error' not in data, 'API error is not a revision snapshot')
    pages = data.get('query', {}).get('pages', [])
    if isinstance(pages, dict):
        pages = list(pages.values())
    for source_page in pages:
        if str(source_page.get('pageid')) != page['page_id']:
            continue
        for source_revision in source_page.get('revisions', []):
            if str(source_revision.get('revid')) != revision['revision_id']:
                continue
            require(source_revision.get('timestamp') == revision['revision_timestamp'], 'revision timestamp mismatch')
            slot = source_revision.get('slots', {}).get('main', {})
            content = slot.get('content', slot.get('*', source_revision.get('*')))
            require(isinstance(content, str), 'snapshot has no original revision content')
            return
    raise ValueError('snapshot does not contain declared page/revision')


def validate(message, request_bytes=None, root=ROOT, verify_artifacts=False):
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(message)
    unique(message['items'], 'request_item_id')
    if message['message_type'] == 'request':
        for item in message['items']:
            if item['inf_ref']['entity_type'] == 'DiaBan':
                require(item['agency_id'] is None, 'DiaBan must not inherit agency ID')
        return
    require(request_bytes is not None, 'report validation requires original request bytes')
    request = json.loads(request_bytes)
    require(request.get('message_type') == 'request', 'expected request message')
    validate(request)
    require(message['request_id'] == request['request_id'], 'request_id mismatch')
    require(message['message_id'] != request['message_id'], 'report must have a distinct message_id')
    require(hashlib.sha256(request_bytes).hexdigest() == message['request_sha256'], 'request checksum mismatch')
    targets = {x['request_item_id']: x for x in request['items']}
    reported = {x['request_item_id'] for x in message['items']}
    require(reported <= targets.keys(), 'unknown request item')
    if message['final']:
        require(reported == targets.keys(), 'final report must cover exactly all request items')
    for result in message['items']:
        target = targets[result['request_item_id']]
        require(result['inf_ref'] == target['inf_ref'], 'INF reference must be echoed unchanged')
        unresolved = set(result['missing_fields_unresolved'])
        require(unresolved <= set(target['missing_fields']), 'unknown unresolved field')
        unique(result['candidates'], 'candidate_id')
        selected = result['selected_candidate_id']
        status = result['status']
        for candidate in result['candidates']:
            rev = candidate['revision']
            if rev is not None:
                require(parse_qs(urlparse(rev['revision_url']).query).get('oldid') == [rev['revision_id']], 'revision URL mismatch')
            for artifact in candidate['artifacts']:
                require(rev is not None, 'artifact requires declared revision')
                path = Path(artifact['path'])
                prefix = Path('sources') / candidate['page']['wiki_id'] / candidate['page']['page_id'] / rev['revision_id']
                require(not path.is_absolute() and '..' not in path.parts and path.is_relative_to(prefix), 'invalid RAW artifact path')
                if verify_artifacts:
                    verify_artifact(artifact, candidate, root)
        if status == 'found':
            candidate = next((x for x in result['candidates'] if x['candidate_id'] == selected), None)
            require(candidate is not None, 'found requires a selected candidate')
            require(candidate['revision'] is not None and bool(candidate['artifacts']), 'found requires original revision artifacts')
            require(not candidate['conflicts'], 'conflicted candidate must remain ambiguous')
        else:
            require(selected is None, 'only found may select a candidate')
            require(unresolved == set(target['missing_fields']), 'unfulfilled result must preserve requested needs')
        if status == 'not_found':
            require(bool(result['queries']) and not result['candidates'], 'not_found requires searches and no candidates')
        if status == 'ambiguous':
            require(bool(result['candidates']), 'ambiguous requires candidates')
        if status != 'error':
            require(not result['retryable'], 'retryable applies to technical error only')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('message', type=Path)
    parser.add_argument('--request', type=Path)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--verify-artifacts', action='store_true')
    args = parser.parse_args()
    try:
        validate(json.loads(args.message.read_bytes()), args.request.read_bytes() if args.request else None,
                 args.root, args.verify_artifacts)
    except Exception as exc:
        print('FAIL:', str(exc))
        return 1
    print('PASS: exchange contract' + (' and local artifact bytes' if args.verify_artifacts else ' only; artifact bytes not checked'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
