"""Shared RDFLib-based generation and serialization of five-card poker hands."""
from __future__ import annotations

import random
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from rdflib import Graph, Literal, Namespace, RDF, RDFS, OWL, URIRef, BNode
from rdflib.collection import Collection

CATEGORIES = (
    ('high_card', 'High Card'), ('pair', 'Pair'), ('two_pair', 'Two Pair'),
    ('three_of_a_kind', 'Three of a Kind'), ('straight', 'Straight'),
    ('flush', 'Flush'), ('full_house', 'Full House'),
    ('four_of_a_kind', 'Four of a Kind'), ('straight_flush', 'Straight Flush'),
    ('royal_flush', 'Royal Flush'),
)
INSTANCE_BASE = 'http://www.poker-ontology.org/instances/'


@dataclass
class Deck:
    graph: Graph
    namespace: Namespace
    ontology_iri: URIRef
    ranks: list[URIRef]
    suits: list[URIRef]
    cards: dict[tuple[URIRef, URIRef], URIRef]
    labels: dict[URIRef, str]

    def name(self, resource):
        return self.labels.get(resource, str(resource).rsplit('#', 1)[-1].rsplit('/', 1)[-1])


def load_ontology(path: str | Path) -> Deck:
    graph = Graph().parse(str(path), format='turtle')
    # Determine the poker vocabulary from the type assertions, without relying on prefixes.
    candidates = {str(t)[:-len('Rank')] for _, _, t in graph.triples((None, RDF.type, None))
                  if str(t).endswith(('#Rank', '/Rank'))}
    if len(candidates) != 1:
        raise ValueError('Could not uniquely identify the poker namespace from Rank individuals.')
    ns = Namespace(candidates.pop())

    def ordered(cls):
        # The generator defines rank order using owl:oneOf; RDF iteration order is arbitrary.
        for expr in graph.objects(cls, OWL.equivalentClass):
            for head in graph.objects(expr, OWL.oneOf):
                return list(Collection(graph, head))
        for head in graph.objects(cls, OWL.oneOf):
            return list(Collection(graph, head))
        raise ValueError(f'Missing owl:oneOf enumeration for {cls}; rank order cannot be inferred.')

    ranks, suits = ordered(ns.Rank), ordered(ns.Suit)
    cards = {}
    for card in graph.subjects(RDF.type, ns.Card):
        rank = graph.value(card, ns.hasRank)
        suit = graph.value(card, ns.hasSuit)
        if rank is not None and suit is not None:
            key = (rank, suit)
            if key in cards:
                raise ValueError(f'Duplicate card for rank/suit: {key}')
            cards[key] = card
    if not cards:
        raise ValueError('No cards with hasRank and hasSuit found.')
    labels = {resource: str(next(iter(graph.objects(resource, RDFS.label)), resource))
              for resource in (*ranks, *suits)}
    ontologies = list(graph.subjects(RDF.type, OWL.Ontology))
    ontology_iri = ontologies[0] if len(ontologies) == 1 else URIRef(str(ns).rstrip('#/'))
    return Deck(graph, ns, ontology_iri, ranks, suits, cards, labels)


def category_of(hand, deck):
    counts = sorted(Counter(rank for rank, _ in hand).values(), reverse=True)
    positions = sorted(deck.ranks.index(rank) for rank, _ in hand)
    straight = len(set(positions)) == 5 and positions[-1] - positions[0] == 4
    flush = len({suit for _, suit in hand}) == 1
    royal = straight and positions == list(range(len(deck.ranks) - 5, len(deck.ranks)))
    if straight and flush:
        return 'royal_flush' if royal else 'straight_flush'
    if counts == [4, 1]: return 'four_of_a_kind'
    if counts == [3, 2]: return 'full_house'
    if flush: return 'flush'
    if straight: return 'straight'
    if counts == [3, 1, 1]: return 'three_of_a_kind'
    if counts == [2, 2, 1]: return 'two_pair'
    if counts == [2, 1, 1, 1]: return 'pair'
    return 'high_card'


def _candidate(category, deck, rng):
    ranks, suits = deck.ranks, deck.suits
    available = deck.cards
    by_rank = defaultdict(list)
    by_suit = defaultdict(list)
    for card in available:
        by_rank[card[0]].append(card)
        by_suit[card[1]].append(card)
    if category in ('straight', 'straight_flush', 'royal_flush'):
        if len(ranks) < 5: raise ValueError('At least five ranks are required.')
        if category == 'royal_flush':
            windows = [ranks[-5:]]
        elif category == 'straight_flush':
            windows = [ranks[i:i+5] for i in range(len(ranks)-5)]
        else:
            windows = [ranks[i:i+5] for i in range(len(ranks)-4)]
        if not windows: raise ValueError(f'No possible {category} rank sequence.')
        seq = rng.choice(windows)
        if category == 'straight':
            return [rng.choice(by_rank[r]) for r in seq]
        suit = rng.choice(suits)
        return [(r, suit) for r in seq]
    if category == 'flush':
        suit = rng.choice(suits)
        return rng.sample(by_suit[suit], 5)
    patterns = {
        'high_card': [1, 1, 1, 1, 1], 'pair': [2, 1, 1, 1],
        'two_pair': [2, 2, 1], 'three_of_a_kind': [3, 1, 1],
        'full_house': [3, 2], 'four_of_a_kind': [4, 1],
    }
    pattern = patterns[category]
    selected = rng.sample(ranks, len(pattern))
    return [card for rank, count in zip(selected, pattern)
            for card in rng.sample(by_rank[rank], count)]


def generate_hands(deck: Deck, hands_per_category: int = 4, seed: int | None = None):
    """Return {category: [five (rank, suit) pairs]}, with unique hands per category."""
    if hands_per_category < 1:
        raise ValueError('hands_per_category must be positive')
    rng = random.Random(seed)
    output = {}
    for category, _ in CATEGORIES:
        hands, seen, signatures = [], set(), set()
        for _ in range(hands_per_category):
            accepted = None
            for phase, attempts in ((True, 500), (False, 5000)):
                for _ in range(attempts):
                    try:
                        hand = _candidate(category, deck, rng)
                    except (ValueError, IndexError):
                        continue
                    if any(card not in deck.cards for card in hand):
                        continue
                    if category_of(hand, deck) != category:
                        continue
                    identity = frozenset(hand)
                    signature = tuple(sorted(deck.ranks.index(r) for r, _ in hand))
                    if identity in seen or (phase and signature in signatures):
                        continue
                    accepted = hand, identity, signature
                    break
                if accepted: break
            if not accepted:
                raise RuntimeError(f'Could not generate {hands_per_category} distinct {category} hands '
                                   f'for a deck of {len(deck.ranks)} ranks and {len(deck.suits)} suits.')
            hand, identity, signature = accepted
            seen.add(identity)
            signatures.add(signature)
            hands.append(hand)
        output[category] = hands
    return output


def describe_hand(category, hand, deck):
    counts = Counter(r for r, _ in hand)
    ranked = sorted(counts, key=lambda r: deck.ranks.index(r), reverse=True)
    def label(rank): return deck.name(rank)
    def plural(rank):
        word = label(rank)
        return word + ('es' if word.endswith(('s', 'x', 'z', 'ch', 'sh')) else 's')
    if category == 'high_card':
        return 'High card ' + ', '.join(label(r) for r in ranked)
    if category == 'pair':
        pair = next(r for r in ranked if counts[r] == 2)
        return f'Pair of {plural(pair)} with ' + ', '.join(label(r) for r in ranked if r != pair)
    if category == 'two_pair':
        pairs = [r for r in ranked if counts[r] == 2]
        kicker = next(r for r in ranked if counts[r] == 1)
        return f'Two pair, {plural(pairs[0])} and {plural(pairs[1])}, with {label(kicker)}'
    if category == 'three_of_a_kind':
        triple = next(r for r in ranked if counts[r] == 3)
        return f'Three {plural(triple)} with ' + ', '.join(label(r) for r in ranked if r != triple)
    if category == 'full_house':
        triple = next(r for r in ranked if counts[r] == 3)
        pair = next(r for r in ranked if counts[r] == 2)
        return f'Full house, {plural(triple)} over {plural(pair)}'
    if category == 'four_of_a_kind':
        four = next(r for r in ranked if counts[r] == 4)
        kicker = next(r for r in ranked if counts[r] == 1)
        return f'Four {plural(four)} with {label(kicker)}'
    if category == 'flush':
        return 'Flush of ' + deck.name(hand[0][1]) + ': ' + ', '.join(label(r) for r in ranked)
    if category == 'royal_flush':
        return 'Royal flush of ' + deck.name(hand[0][1])
    sequence = '-'.join(label(r) for r in reversed(ranked))
    return ('Straight flush' if category == 'straight_flush' else 'Straight') + ' ' + sequence + (
        ' of ' + deck.name(hand[0][1]) if category == 'straight_flush' else '')


def _make_graph(deck, categories, hands, include_has_pair, complete):
    graph = Graph()
    graph.bind('poker', deck.namespace)
    graph.bind('owl', OWL)
    graph.bind('rdfs', RDFS)
    ontology_suffix = 'all' if complete else categories[0]
    ontology_iri = URIRef(INSTANCE_BASE + ontology_suffix)
    graph.add((ontology_iri, RDF.type, OWL.Ontology))
    graph.add((ontology_iri, OWL.imports, deck.ontology_iri))
    graph.add((ontology_iri, RDFS.label, Literal('Poker hand instances' if complete else
               dict(CATEGORIES)[categories[0]] + ' instances', lang='en')))
    graph.add((ontology_iri, RDFS.comment, Literal('Generated five-card poker hands.', lang='en')))
    number = 0
    for category in categories:
        namespace = Namespace(INSTANCE_BASE + category + '#')
        graph.bind(category, namespace)
        individuals = []
        for hand in hands[category]:
            number = number + 1 if complete else len(individuals) + 1
            individual = namespace[f'Hand{number}']
            individuals.append(individual)
            graph.add((individual, RDF.type, deck.namespace.Hand))
            graph.add((individual, RDFS.label, Literal(describe_hand(category, hand, deck), lang='en')))
            for card in hand:
                graph.add((individual, deck.namespace.containsCard, deck.cards[card]))
            if include_has_pair and category in ('two_pair', 'full_house'):
                counts = Counter(r for r, _ in hand)
                paired = [r for r, count in counts.items() if count >= 2]
                for rank in paired:
                    graph.add((individual, deck.namespace.handHasPair, rank))
        node = BNode()
        graph.add((node, RDF.type, OWL.AllDifferent))
        head = BNode()
        Collection(graph, head, individuals)
        graph.add((node, OWL.distinctMembers, head))
    return graph


def write_complete(hands, deck, output_path, include_has_pair=False):
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    graph = _make_graph(deck, [c for c, _ in CATEGORIES], hands, include_has_pair, True)
    graph.serialize(destination=str(path), format='turtle')
    return path


def write_split(hands, deck, output_directory, base_name, include_has_pair=False):
    directory = Path(output_directory)
    directory.mkdir(parents=True, exist_ok=True)
    paths = []
    for category, _ in CATEGORIES:
        path = directory / f'instances_{base_name}_{category}.ttl'
        graph = _make_graph(deck, [category], hands, include_has_pair, False)
        graph.serialize(destination=str(path), format='turtle')
        paths.append(path)
    return paths
