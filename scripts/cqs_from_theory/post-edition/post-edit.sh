#!/usr/bin/env bash

echo 'us2016'
python3 scripts/cqs_from_theory/post-edition/from_annotations_to_postedition.py US2016

echo 'rrd'
python3 scripts/cqs_from_theory/post-edition/from_annotations_to_postedition.py rrd

echo 'EO_PC'
python3 scripts/cqs_from_theory/post-edition/from_annotations_to_postedition.py EO_PC

echo 'MORAL MAZE'
python3 scripts/cqs_from_theory/post-edition/from_annotations_to_postedition.py moral_maze_schemes

echo 'reddit'
python3 scripts/cqs_from_theory/post-edition/from_annotations_to_postedition.py us2016reddit
