for i in {0..23}
do
    python nytimes.py --numRuns $i
    read -t 5
done