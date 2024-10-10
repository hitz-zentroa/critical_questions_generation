#!/usr/bin/env bash

echo 'us2016'
python scripts/cqs_from_theory/post-edition/to_postedited.py US2016

echo 'rrd'
python scripts/cqs_from_theory/post-edition/to_postedited.py rrd

echo 'EO_PC'
python scripts/cqs_from_theory/post-edition/to_postedited.py EO_PC

echo 'MORAL MAZE'
python scripts/cqs_from_theory/post-edition/to_postedited.py moral_maze_schemes

echo 'reddit'
python scripts/cqs_from_theory/post-edition/to_postedited.py us2016reddit
