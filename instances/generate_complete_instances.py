"""Generate one Turtle ABox containing four hands of each of ten categories."""
import argparse
from pathlib import Path
from poker_instance_generator import load_ontology, generate_hands, write_complete


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ontology', type=Path, help='Input deck ontology in Turtle format')
    parser.add_argument('--output', type=Path, help='Output Turtle file')
    parser.add_argument('--hands-per-category', type=int, default=4)
    parser.add_argument('--seed', type=int, help='Optional reproducible random seed')
    parser.add_argument('--include-has-pair', action='store_true', help='Add handHasPair shortcut assertions')
    args = parser.parse_args()
    deck = load_ontology(args.ontology)
    hands = generate_hands(deck, args.hands_per_category, args.seed)
    path = write_complete(hands, deck, args.output or Path(f'instances_{args.ontology.stem}.ttl'), args.include_has_pair)
    print(f'Generated {sum(map(len, hands.values()))} hands: {path}')


if __name__ == '__main__':
    main()
