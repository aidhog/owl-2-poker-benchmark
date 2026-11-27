# OWL 2 Poker Benchmark

The OWL 2 Poker Benchmark (OWL2PB) is a parameterizable benchmark for OWL 2 DL based on classifying poker hands.

This repository contains OWL 2 DL ontologies and generators for evaluating reasoning over poker hands. The benchmark models cards, suits, ranks, and five-card hands. It supports parameterized decks and generates instance data for hand classification experiments.

## Repository structure

- [`ontologies/`](ontologies/): base ontology for a standard 52-card deck.
- [`ontology_generator/`](ontology_generator/): Python generator for parameterized deck ontologies.
- [`instances/`](instances/): instances for the base ontology that require classification.
- [`instance_generador_`](instance_generator/): Python generators for instances of hands that require classification.

## Requirements

Python 3 is required for the generators. Install any additional dependencies with `pip install -r requirements.txt`.

## Generate ontologies

Run `python ontology_generator/generate_ontologies.py` to generate a custom ontology and provide the requested deck name, suits, and ranks. There is also an option to indicate whether or not the `handHasPair` shortcut should be used to simply the definition of pairs and two-pair. The generator writes Turtle files under `ontologies/generated_ontologies/`.

Run `python ontology_generator/generate_benchmark.py` to generate a fixed suite of 24 ontologies varying the number of ranks and suits. If you wish to include the `handHasPair` shortcut, append the ` --include-has-pair` flag to the previous command.

See the [module documentation](ontologies/) for details of the generated ontologies and for more options.

## Generate hand instances

Pass the path to an ontology in Turtle format to either generator:

```bash
python instances/generate_complete_instances.py path/to/ontology.ttl
python instances/generate_split_instances.py path/to/ontology.ttl
```

The complete generator produces a combined set of hand instances. The split generator produces separate files for hand categories. There are also options for generating instances with the `handHasPair` shortcut, for generating a certain number of instances for each hand type, and also for batch generation for ontologies recursively contained in a folder (useful for generating instances for the benchmark varying suits and hands).

See the [module documentation](instances/) for details of the generated hand instances and for more options.

> Note that the instance generator may fail if the requested number of instances for each hand type is not possible for that deck. For example, the number of possible distinct instances of royal flush is limited by the number of suits in the deck.

## Citation

If you use this benchmark in your research, a citation to our paper would always be appreciated:

> Guillermo Garda, Aidan Hogan. **Can Owls Play Poker? (An OWL 2 DL Benchmark)** Proceedings of the 17th Alberto Mendelzon International Workshop on Foundations of Data Management, AMW 2026.

```bibtex
@inproceedings{owl2poker,
  author    = {Guillermo Garda and Aidan Hogan},
  title     = {Can Owls Play Poker? (An OWL 2 DL Benchmark)},
  booktitle = {Proceedings of the 17th Alberto Mendelzon International Workshop on Foundations of Data Management (AMW)},
  year      = {2026}
}
```

Note that the results presented in this paper used [this version of the repository](https://github.com/Guillineitor/poker-ontology) (in Spanish, which also includes a benchmark harness via the OWL API not included here). The current repository has, with some AI assistance, translated resources to English, converted Windows scripts to Python, simplified some core definitions (hand now uses exact cardinality rather than both min and max cardinality, and high card is simply defined to be equivalent to hand rather than the intersection of hand and having a card) and refactored the repository structure.

