"""Shared cross-platform batch runner for complete and split poker instances."""
import argparse
import fnmatch
from pathlib import Path
from poker_instance_generator import CATEGORIES, load_ontology, generate_hands, write_complete, write_split


def run(mode):
    parser = argparse.ArgumentParser(description=f'Batch generate {mode} poker instances.')
    parser.add_argument('--ontologies-dir', type=Path, default=Path(__file__).resolve().parent.parent / 'ontologies' / 'generated_ontologies')
    parser.add_argument('--output-dir', type=Path, default=Path(__file__).resolve().parent / ('complete_instances' if mode == 'complete' else 'split_instances'))
    parser.add_argument('--filter', default='*.ttl', help='Filename glob, e.g. deck_6r_*')
    parser.add_argument('--force', action='store_true', help='Overwrite existing results')
    parser.add_argument('--dry-run', action='store_true', help='Show planned outputs only')
    parser.add_argument('--include-has-pair', action='store_true')
    parser.add_argument('--hands-per-category', type=int, default=4)
    parser.add_argument('--seed', type=int)
    args = parser.parse_args()
    root = args.ontologies_dir.resolve()
    if not root.is_dir(): parser.error(f'Ontology directory not found: {root}')
    files = sorted(p for p in root.rglob('*.ttl') if fnmatch.fnmatch(p.name, args.filter))
    print(f'Found {len(files)} ontologies.')
    succeeded = skipped = failed = 0
    for path in files:
        relative = path.parent.relative_to(root)
        group = args.output_dir / (f'instances_{relative.name}' if relative != Path('.') else '')
        if mode == 'complete':
            targets = [group / f'instances_{path.stem}.ttl']
        else:
            group = group / path.stem
            targets = [group / f'instances_{path.stem}_{category}.ttl' for category, _ in CATEGORIES]
        print(f'{path.relative_to(root)} -> {targets[0].parent} ({len(targets)} file(s))')
        if args.dry_run: continue
        if all(p.exists() for p in targets) and not args.force:
            skipped += 1
            continue
        try:
            deck = load_ontology(path)
            hands = generate_hands(deck, args.hands_per_category, args.seed)
            if mode == 'complete':
                write_complete(hands, deck, targets[0], args.include_has_pair)
            else:
                write_split(hands, deck, group, path.stem, args.include_has_pair)
            succeeded += 1
        except Exception as exc:
            print(f'  ERROR: {exc}')
            failed += 1
    print(f'Finished: {succeeded} generated, {skipped} skipped, {failed} failed.')
    if failed: raise SystemExit(1)
