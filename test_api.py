import requests

url = "http://127.0.0.1:5000/compile"

data = {
    "code": """DECLARE num, fact, i : INTEGER
OUTPUT "Enter a number:"
INPUT num
fact <- 1
i <- 1
WHILE i <= num
    fact <- fact * i
    i <- i + 1
ENDWHILE
OUTPUT "Factorial is:"
OUTPUT fact"""
}

res = requests.post(url, json=data)
print(res.json())
