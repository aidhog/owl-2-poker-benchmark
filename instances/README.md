# Instance generators

This directory contains generators for five-card poker-hand instances. Both generators take an ontology file as input and use its deck configuration.

## Complete instance set

```bash
python instances/generate_complete_instances.py ontologies/base_ontology/base_poker_ontology.ttl
```

## Instances separated by hand category

```bash
python instances/generate_split_instances.py ontologies/base_ontology/base_poker_ontology.ttl
```

The corresponding `.ps1` scripts support batch execution in PowerShell. The `base_poker_instances/` directory contains an example instance file for the base ontology.

The generated hand categories include high card, pair, two pair, three of a kind, straight, flush, full house, four of a kind, straight flush, and royal flush. Consult the source for generation constraints and selection procedures.
