# Ontology generator

`generate_ontologies.py` creates OWL 2 DL ontologies for decks with configurable suits and ranks. Each generated ontology contains the relevant classes, properties, and deck individuals in Turtle syntax.

`generate_benchmark.py` creates a specific test-suite of OWL 2 DL ontologies using the aforementioned script. Suit names beyond the usual may or may not be inspired by Pokémon.

## Usage

```bash
python ontology_generator/generate_ontologies.py
```

```bash
python ontology_generator/generate_benchmark.py
```

The program prompts for the deck name, suits, and ranks. Its output directory is `ontologies/generated_ontologies/`. The corresponding PowerShell script, `generate_ontologies.ps1`, supports batch generation.

The base ontology in `ontologies/base_ontology/` provides the reference vocabulary and axiomatization. Generated ontologies should be checked for compatibility with the English identifiers used by the base ontology.
