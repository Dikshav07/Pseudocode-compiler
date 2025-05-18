DECLARE num, fact, i : INTEGER

OUTPUT "Enter a number:"
INPUT num

fact <- 1
i <- 1

WHILE i <= num
    fact <- fact * i
    i <- i + 1
ENDWHILE

OUTPUT "Factorial is:"
OUTPUT fact
