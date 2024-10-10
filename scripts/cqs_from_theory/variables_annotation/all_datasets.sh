#!/usr/bin/env bash

echo 'us2016'
python3 scripts/cqs_from_theory/variables_annotation/annotation.py US2016

echo 'rrd'
python3 scripts/cqs_from_theory/variables_annotation/annotation.py rrd

echo 'EO_PC'
python3 scripts/cqs_from_theory/variables_annotation/annotation.py EO_PC

echo 'MORAL MAZE'
python3 scripts/cqs_from_theory/variables_annotation/annotation.py moral_maze_schemes

echo 'reddit'
python3 scripts/cqs_from_theory/variables_annotation/annotation.py us2016reddit