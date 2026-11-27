# Ontology generator

`generate_ontologies.py` creates OWL 2 DL ontologies for decks with configurable suits and ranks. Each generated ontology contains the relevant classes, properties, and deck individuals in Turtle syntax. It includes an option to add a `handHasPair` shortcut that simplifies the definition and classification of pairs and two-pair (and thus also full house).

`generate_benchmark.py` creates a specific test-suite of OWL 2 DL ontologies using the aforementioned script. Suit names beyond the usual may or may not be inspired by Pokémon. By default it creates 24 ontologies with the product of { 6, 13, 19, 25, 31, 37 } distinct ranks and { 4, 8, 12, 16 } distinct suits. It includes the option to use the `handHasPair` shortcut, disabled by default.

## Usage

```bash
python ontology_generator/generate_ontologies.py
```

```bash
python ontology_generator/generate_benchmark.py
```

The program prompts for the deck name, suits, and ranks. Its output directory is `ontologies/generated_ontologies/`. The corresponding PowerShell script, `generate_ontologies.ps1`, supports batch generation.

The base ontology in `ontologies/base_ontology/` provides the reference vocabulary and axiomatization.
