#!/bin/sh
# Deactivate the telescope tracking
chimera-dome --stand
# Set dome to az = 0
chimera-dome --to=0
sleep 10
for angle in `seq 15 15 360`
do
   # Go Forward
   echo 0 $angle `/usr/bin/time chimera-dome --to=$angle 2>&1 >/dev/null`
   sleep 10
   # Go Back
   echo $angle 0 `/usr/bin/time chimera-dome --to=0 2>&1 >/dev/null`
   sleep 10
done >> dome_bench.txt