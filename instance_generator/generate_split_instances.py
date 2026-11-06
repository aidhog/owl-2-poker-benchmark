"""Generate ten Turtle ABoxes, one per poker-hand category."""
import argparse
from pathlib import Path
from poker_instance_generator import load_ontology, generate_hands, write_split


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ontology', type=Path, help='Input deck ontology in Turtle format')
    parser.add_argument('--output-dir', type=Path, default=Path('.'))
    parser.add_argument('--hands-per-category', type=int, default=4)
    parser.add_argument('--seed', type=int, help='Optional reproducible random seed')
    parser.add_argument('--include-has-pair', action='store_true', help='Add handHasPair shortcut assertions')
    args = parser.parse_args()
    deck = load_ontology(args.ontology)
    hands = generate_hands(deck, args.hands_per_category, args.seed)
    paths = write_split(hands, deck, args.output_dir, args.ontology.stem, args.include_has_pair)
    print(f'Generated {len(paths)} files containing {sum(map(len, hands.values()))} hands in {args.output_dir}')


if __name__ == '__main__':
    main()
