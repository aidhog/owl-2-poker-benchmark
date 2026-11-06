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

## Batch generation (Python replacements for PowerShell)

```bash
python generate_batch_complete_instances.py --ontologies-dir path/to/ontologies --output-dir path/to/output
python generate_batch_split_instances.py --ontologies-dir path/to/ontologies --output-dir path/to/output
```

Batch commands support `--filter 'deck_6r_*'`, `--dry-run`, `--force`, `--seed`, `--hands-per-category`, and `--include-has-pair`. They recursively discover `.ttl` files, preserve the original `instances_decks_<N>_ranks` output grouping, and skip complete existing outputs unless forced.

## Notes

- Rank order must be declared in the ontology through `owl:oneOf`.
- The standard five-card hand categories are used, with the royal flush distinguished from other straight flushes. The top five ranks in the declared rank order define a royal flush.
- `--seed` makes a given invocation reproducible. To obtain the **same** random hands in complete and split outputs, run both with the same seed and input deck.
- The generator does not assert a specific poker-hand category for each hand: the ontology's class axioms are intended to infer those categories.
