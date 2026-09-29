#!/usr/bin/env python3
"""Create one immutable-by-convention trace envelope with embedded JSON evidence."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re


def record(root, run_id, task, evidence):
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,79}', run_id):
        raise ValueError('Invalid run ID')
    if not task.strip():
        raise ValueError('Task must not be empty')
    raw = evidence.read_bytes()
    parsed = json.loads(raw)
    output = root / 'raw' / (run_id + '.json')
    output.parent.mkdir(parents=True, exist_ok=True)
    data = {'schema_version': '0.1.0', 'run_id': run_id, 'task': task,
            'recorded_at': datetime.now(timezone.utc).isoformat(),
            'evidence_sha256': hashlib.sha256(raw).hexdigest(),
            'evidence_filename': evidence.name,
            'evidence_raw': raw.decode('utf-8'), 'evidence': parsed}
    # Prepare and serialize before exclusive creation; never overwrite existing history.
    payload = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
    with output.open('x', encoding='utf-8') as stream:
        stream.write(payload)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--task', required=True)
    parser.add_argument('--evidence', type=Path, required=True)
    args = parser.parse_args()
    print(record(args.root, args.run_id, args.task, args.evidence).relative_to(args.root))


if __name__ == '__main__':
    main()
