# Poker instance generators

These scripts generate English-language RDF/Turtle instances for five-card poker hands from a parameterized OWL deck ontology. Python 3.10+ and RDFLib are required (`pip install rdflib`).

The shared `poker_instance_generator.py` module parses deck ontologies with RDFLib, reads the ordered rank and suit enumerations from `owl:oneOf`, generates distinct hands for ten categories, and serializes Turtle output. Card IRIs are taken directly from the input ontology. The generators require the translated vocabulary (`Rank`, `Suit`, `Card`, `Hand`, `hasRank`, `hasSuit`, `containsCard`).

## Generate instances for one deck

```bash
python generate_complete_instances.py path/to/deck.ttl
python generate_split_instances.py path/to/deck.ttl --output-dir output
```

Complete generation writes `instances_<deck>.ttl` (40 hands by default); split generation writes ten `instances_<deck>_<category>.ttl` files (four hands per category).

Both commands support `--hands-per-category N`, `--seed 42`, and `--include-has-pair`. The last option adds `handHasPair` assertions for two-pair and full-house hands; it is **off by default**.

## Batch generation

The following can be used to generate instances for each ontology recursively found in a given folder (e.g., after generating a benchmark of ontologies).

```bash
python generate_batch_complete_instances.py --ontologies-dir path/to/ontologies --output-dir path/to/output
python generate_batch_split_instances.py --ontologies-dir path/to/ontologies --output-dir path/to/output
```

Batch commands can include arguments for `--filter 'deck_6r_*'` (include only files with the given pattern, default `*.ttl`), `--dry-run` (preview the outputs, default disabled), `--force` (overwrite existing files, default disabled), `--seed` (an integer used for repeatible pseudorandom behaviour), `--hands-per-category` (how many instances for each type of hand, default `4`), and `--include-has-pair` (to include the shortcut that simplfies pairs, two-pair and, indirectly, full house). They recursively discover `.ttl` files for ontologies, preserve the original `instances_decks_<N>_ranks` output grouping, and skip complete existing outputs unless forced.

## Notes

- By default, instances are written to the `instances/generated_instances` folder.
- The rank order (e.g., for straights) is assumed to be the same ascending order as presented in the ontology's `owl:oneOf` enumeration of the ranks.
- The standard five-card hand categories are used, with the royal flush distinguished from other straight flushes. The top five ranks in the declared rank order define a royal flush.
- `--seed` makes a given invocation reproducible. To obtain the **same** random hands in complete and split outputs, run both with the same seed and input deck.
- The generator does not assert a specific poker-hand category for each hand: the ontology's class axioms are intended to infer those categories.
- The generator makes thousands of attempts to pseudorandomly create at least the number of hands requested (all pairwise distinct). If it cannot create the required number of hands, it will throw a runtime error. This will often be due to request being impossible. For example, if a deck has three suits, and we request four instances of each hand type, this will fail for royal flush since the number of possible unique instances of this hand type is equal to the number of suits.