# Base poker ontology

`base_poker_ontology.ttl` defines an OWL 2 DL representation of a standard 52-card deck and five-card poker hands.

The principal classes are `Card`, `Suit`, `Rank`, and `Hand`. The ontology defines individual cards, their ranks and suits, and class expressions for poker-hand categories. Enumerations and distinctness axioms constrain the deck, while property restrictions support hand classification.

The ontology uses the namespace `http://www.poker-ontology.org/poker#` (which is artificial: it does not dereference; if anyone wants to register the domain to make it dereference, they are welcome).

We also provide two variants, based on preliminary experiment that indicate that two pair is complex to classify:

- `base_poker_ontology_fullhouse.ttl` provides an alternative definition independent of two-pair, based on cardinalities of individual ranks (in a full house, each rank appears 0, 2 or 3 times).

- `base_poker_ontology_haspair.ttl` provides a simplfied definition, in which instances specify the ranks of the pairs it contains via `poker:handHasPair`. Thus the definition of two pair simplifies to having two unique ranks as values of this property. Full house is defined as the intersection of two pair and three-of-a-kind.
