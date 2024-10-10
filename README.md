
# Critical Questions Generation: Motivation and Challenges

This repository collects the scripts and data for the CoNLL 2024 paper "Critical Questions Generation: Motivation and Challenges".

The development of Large Language Models (LLMs) has brought impressive performances on mitigation strategies against misinformation, such as counterargument generation. However, LLMs are still seriously hindered by outdated knowledge and by their tendency to generate hallucinated content. In order to circumvent these issues, we propose a new task, namely, \textit{Critical Questions Generation}, consisting of processing an argumentative text to generate the critical questions (CQs) raised by it.
In argumentation theory CQs are tools designed to lay bare the blind spots of an argument by pointing at the information it could be missing.
Thus, instead of trying to deploy LLMs to produce knowledgeable and relevant counterarguments, we use them to question arguments, without requiring any external knowledge.
Research on CQs Generation using LLMs requires a reference dataset for large scale experimentation. Thus, in this work we investigate two complementary methods to create such a resource: (i) instantiating CQs templates as defined by Walton's argumentation theory and (ii), using LLMs as CQs generators. By doing so, we contribute with a procedure to establish what is a valid CQ and conclude that, while LLMs are reasonable CQ generators, they still have a wide margin for improvement in this task.

## Data Pre-processing:

- Structure dataset by interventions
```
sh scripts/pre-process/preprocess.sh
```

## Data Annotation and Post-edition

- Annotate the variables
```
sh scripts/cqs_from_theory/variables_annotation/all_datasets.sh
```

- Post-edit
```
sh scripts/cqs_from_theory/post-edition/post-edit.sh
```

- After post-edition
```
sh scripts/cqs_from_theory/post-edition/final_theory.sh
```

## Generate CQs from LLMs

- To generate cqs from LLMs
```
python scripts/cqs_from_llms/cqs_from_llms.py moral_maze_schemes
python scripts/cqs_from_llms/split_cqs.py moral_maze_schemes

python scripts/cqs_from_llms/cqs_from_llms.py US2016
python scripts/cqs_from_llms/split_cqs.py US2016
```

## Three evaluation steps

- Evaluations: relevance, relation and validate
