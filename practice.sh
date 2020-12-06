# for i in {0..10}
# do
#     python3 nytimes.py --numRuns $i
#     read -t 10
# done

for i in {7..11}
do
    for j in {1..5}
    do
        python3 wsj.py --month $i --day $j
        read -t 10
    done
done


# python wsj.py --month 7 --day 1