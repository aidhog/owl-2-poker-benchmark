"""Generate the benchmark matrix of parameterized poker ontologies.

By default, generate 24 ontologies for six rank counts and four suit counts.
Each Turtle file is placed in a directory named decks_<N>_ranks.

Examples:
    python generate_benchmark_ontologies.py
    python generate_benchmark_ontologies.py --dry-run
    python generate_benchmark_ontologies.py --ranks 13 19 --suits 4 8
"""

import argparse
import time
from pathlib import Path

from generate_ontologies import generate_ontology, slug

SUITS = (
    "Fire", "Water", "Grass", "Electric", "Normal", "Flying", "Bug", "Poison",
    "Ground", "Rock", "Fighting", "Psychic", "Ghost", "Ice", "Dragon", "Dark",
)

RANKS = (
    "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten",
    "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen",
    "Eighteen", "Nineteen", "Twenty", "TwentyOne", "TwentyTwo", "TwentyThree",
    "TwentyFour", "TwentyFive", "TwentySix", "TwentySeven", "TwentyEight",
    "TwentyNine", "Thirty", "ThirtyOne", "ThirtyTwo", "ThirtyThree", "ThirtyFour",
    "ThirtyFive", "ThirtySix", "ThirtySeven",
)

DEFAULT_OUTPUT = Path(__file__).resolve().parent.parent / "ontologies" / "generated_ontologies"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--ranks", nargs="+", type=int, default=[6, 13, 19, 25, 31, 37],
                        metavar="N", help="Numbers of ranks (default: 6 13 19 25 31 37)")
    parser.add_argument("--suits", nargs="+", type=int, default=[4, 8, 12, 16],
                        metavar="N", help="Numbers of suits (default: 4 8 12 16)")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT,
                        help="Destination directory (default: ontologies/generated_ontologies)")
    parser.add_argument("--dry-run", action="store_true",
                        help="List configurations without writing files")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    for name, counts, limit in (("ranks", args.ranks, len(RANKS)),
                                ("suits", args.suits, len(SUITS))):
        if not counts or any(count < 1 or count > limit for count in counts):
            raise SystemExit(f"Invalid {name} count: values must be between 1 and {limit}.")

    total = len(args.ranks) * len(args.suits)
    print(f"\nConfigurations: {total} ({len(args.ranks)} rank groups × {len(args.suits)} suit groups)")
    if args.dry_run:
        print("Dry run: no files will be written.")
    print()

    started = time.monotonic()
    completed = 0
    for rank_count in args.ranks:
        ranks = list(RANKS[:rank_count])
        destination = args.output_dir / f"decks_{rank_count}_ranks"
        for suit_count in args.suits:
            suits = list(SUITS[:suit_count])
            deck_name = f"deck_{rank_count}r_{suit_count}s"
            print(f"[{completed + 1}/{total}] {deck_name} ({suit_count} suits × {rank_count} ranks)")
            if args.dry_run:
                print(f"  Suits: {', '.join(suits)}")
                print(f"  Ranks: {', '.join(ranks)}\n")
                completed += 1
                continue

            base_iri = f"http://www.poker-deck.org/{slug(deck_name)}"
            try:
                turtle = generate_ontology(deck_name, base_iri, suits, ranks)
                destination.mkdir(parents=True, exist_ok=True)
                target = destination / f"{slug(deck_name)}.ttl"
                target.write_text(turtle, encoding="utf-8")
            except (OSError, ValueError) as exc:
                print(f"  Error generating {deck_name}: {exc}\n")
                continue
            print(f"  Written to: {target}\n")
            completed += 1

    duration = time.monotonic() - started
    if args.dry_run:
        print(f"Listed {completed} configurations.")
    else:
        print(f"Generated {completed} of {total} ontologies in {duration:.1f} seconds.")
        print(f"Output directory: {args.output_dir.resolve()}")
    return 0 if completed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
