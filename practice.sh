# Wall Street Journal
for i in {7..11}
do
    for j in {1..29}
    do
        python3 wsj.py --month $i --day $j
        read -t 10
    done
done

# New York Times
for i in {0..23}
do
    python3 nytimes.py --numRuns $i
    read -t 10
done

# News API
for i in {0..5}
do
    python3 nytimes.py --numRuns $i
    read -t 3600
done

# Twitter
python3 twitter.py

# ML Calculation
python3 database.py

# Visualizations and Calculation File
python3 visualizations.py