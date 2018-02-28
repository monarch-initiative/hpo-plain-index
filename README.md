### HPO Plain Language Indexer

Builds a solr index of HPO plain language synonyms, including phenotype
and anatomy groupings to enable faceting.  For example:

````
[
  {
    "id": "HP:0000464",
    "exact_synonym": [
      "Abnormality of the neck"
    ],
    "phenotype_closure": [
      "HP:0000464",
      "HP:0000152",
      "HP:0000118"
    ],
    "phenotype_closure_label": [
      "Abnormality of the neck",
      "Abnormality of head or neck",
      "Phenotypic abnormality"
    ],
    "anatomy_closure": [
      "UBERON_0007811",
      "UBERON_0000153",
      "UBERON_0013702"
    ],
    "anatomy_closure_label": [
      "craniocervical region",
      "anterior region of body",
      "body proper"
    ]
  }
]
````

### Building and running with Docker Compose

Build and initialize:

    docker-compose up

Run the integration tests:

    docker-compose run loader integration-tests

Run the unit tests:

    docker-compose run loader test

Load the data:

    docker-compose run loader load-index

Copy index to local filesystem

    something



