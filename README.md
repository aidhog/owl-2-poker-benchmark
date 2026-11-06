# OWL 2 Poker Benchmark

This repository contains OWL 2 DL ontologies and generators for evaluating reasoning over poker hands. The benchmark models cards, suits, ranks, and five-card hands. It supports parameterized decks and generates instance data for hand classification experiments.

## Repository structure

- [`ontologies/base_ontology/`](ontologies/base_ontology/): base ontology for a standard 52-card deck.
- [`ontology_generator/`](ontology_generator/): Python generator for parameterized deck ontologies.
- [`instances/`](instances/): Python generators for complete and category-separated hand instances, together with a small base example.
- [`ontologies/generated_ontologies/`](ontologies/generated_ontologies/): destination for generated ontology variants.

The benchmark execution code and experimental results are outside the scope of this source-only distribution.

## Requirements

Python 3 is required for the generators. Install any additional dependencies with `pip install -r requirements.txt`. The supplied PowerShell scripts provide batch execution on systems with PowerShell.

## Generate an ontology

Run `python ontology_generator/generate_ontologies.py` and provide the requested deck name, suits, and ranks. The generator writes Turtle files under `ontologies/generated_ontologies/`.

## Generate hand instances

Pass the path to an ontology in Turtle format to either generator:

```bash
python instances/generate_complete_instances.py path/to/ontology.ttl
python instances/generate_split_instances.py path/to/ontology.ttl
```

The complete generator produces a combined set of hand instances. The split generator produces separate files for hand categories. See the module documentation for details of the generated data.

## Ontology vocabulary

The English ontology uses `Card`, `Hand`, `Suit`, and `Rank`, together with standard English poker-hand categories. The ontology namespace remains `http://www.poker-ontology.org/poker#`.

## Scope of this draft

The large collections of previously generated ontologies and instances have been excluded. They should be regenerated from the English source files after the generators have been fully reviewed and tested.
