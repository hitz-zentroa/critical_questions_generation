#!/usr/bin/env bash

echo 'moral_maze'
python3 scripts/pre-process/structure_data_by_intervention.py moral_maze_schemes

echo 'us2016'
python3 scripts/pre-process/structure_data_by_intervention.py US2016

echo 'EO_PC'
python3 scripts/pre-process/structure_data_by_intervention.py EO_PC

echo 'rrd'
python3 scripts/pre-process/structure_data_by_intervention.py rrd

echo 'us2016reddit'
python3 scripts/pre-process/structure_data_by_intervention.py us2016reddit