#!/usr/bin/env bash
# Lot 4 (passage à l'échelle, ~220 bugs TRAIN côté serveur) : démarre quand le lot 3 est fini, 2 instances (3 et 1).
cd /home/elrems/kaggle
while pgrep -f queue_lot3 >/dev/null; do sleep 300; done
read -ra ALL < runs/lot4.txt; H=$(( ${#ALL[@]} / 2 ))
PSB=3 python3 -u bench/gentest.py "${ALL[@]:0:$H}" --tries 4 --mode php >> runs/gentest_php4.log 2>&1 &
PSB=1 python3 -u bench/gentest.py "${ALL[@]:$H}" --tries 4 --mode php >> runs/gentest_php4.log 2>&1 &
wait
