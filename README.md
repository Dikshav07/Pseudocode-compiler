# Pseudo-Code to C++ code Compiler

This is a pseudo-code compiler for the CIE IGCSE and AS&A Levels Computer Science course. It is designed to be used with 0478/9718/9708.

I am using the official CIE pseudo-code specification as a reference for this compiler. You can find the specification [here](https://www.cambridgeinternational.org/Images/697401-2026-pseudocode-guide-for-teachers.pdf).

## Small rant
WHY IS IT CALLED PSEUDOCODE IF IT CAN BE COMPILED? IT'S NOT PSEUDOCODE IF IT CAN BE COMPILED. IT'S A REAL PROGRAMMING LANGUAGE. IT'S NOT PSEUDO.

## How does it work?
The compiler is not exactly a compiler, I am using `ply` (Python Lex-Yacc) to parse the pseudo-code and convert it to an abstract syntax tree (AST).
I then use the AST to generate C++ code, and call `g++` to compile the generated C++ code.

## How to use
1. Write your pseudo-code in a file (e.g. `code.psc`)
2. Run the compiler with the file as an argument (e.g. `python main.py code.psc`)
3. The generated C++ code will be in `temp/temp.cpp`
4. The compiled binary will be in `temp/temp(.exe)`
5. If the `-r` flag is used, the compiled binary will be run


## Requirements
- Python 3
- gcc (for compiling the generated C++ code)

## Limitations (for now)
- No PEMDAS/BODMAS support, use brackets to enforce order of operations
- Only the following are supported right now
  - `IF` statements (with or without `ELSE`)
  - `REPEAT` loops
  - `FOR` loops
  - `WHILE` loops
  - All data types except `DATE`
  - All variable types except `CONSTANT`
  - `OUTPUT` and `INPUT` statements
  - Multi-expression `OUTPUT` statements
  - All arithmetic operators
  - `AND`, `OR`, `NOT` logical operators
  - All comparison operators
  - `DECLARE` and `<-` assignment operators
  - More things I can't remember right now
  - `PROCEDURE` definitions with or without parameters
  - `FUNCTION` definitions with or without parameters
  - expression evaluation of function calls
  - `CALL` statements with or without parameters
- Haven't tested on linux or mac yet, probably won't work

## Usage
```bash
$ python main.py -h
usage: main.py [-h] [-o OUTPUT] [-c CFILE] [-r] [-d] file

positional arguments:
  file                  The file to compile

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        The output file
  -c CFILE, --cfile CFILE
                        The C file to generate
  -r, --run             Run the compiled file
  -d, --debug           Debug output
```

## Run This Project
This project also includes a Flask backend and a React frontend to provide a user interface for writing and compiling pseudocode.<br>
Step 1: Clone the Repository
```bash
git clone https://github.com/Dikshav07/Pseudocode-compiler.git
cd Pseudocode-compiler
```
Step 2: Run the Python Backend (Flask)
Make sure Python 3 is installed, then:
```bash
python app.py
```
Step 3: Run the Frontend
```bash
cd frontend
npm install
npm run dev
```
## OUTPUT 
![Image](https://github.com/user-attachments/assets/9f0cb289-83a2-4db5-8e7e-dacfd9374576)
<br>
![Image](https://github.com/user-attachments/assets/1b81ba13-778c-477e-bbf1-8fda02c06c4c)



