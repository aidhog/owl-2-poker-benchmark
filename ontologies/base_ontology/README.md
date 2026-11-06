# Base poker ontology

`base_poker_ontology.ttl` defines an OWL 2 DL representation of a standard 52-card deck and five-card poker hands.

The principal classes are `Card`, `Suit`, `Rank`, and `Hand`. The ontology defines individual cards, their ranks and suits, and class expressions for poker-hand categories. Enumerations and distinctness axioms constrain the deck, while property restrictions support hand classification.

The ontology uses the namespace `http://www.poker-ontology.org/poker#`.
