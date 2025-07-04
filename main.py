import os
import argparse
import subprocess

from classes.general_functions import eprint
from classes.lexer import make_psuedocode_lexer
from classes.parser import make_pseudocode_parser
from classes.compiler import PseudocodeCompiler

# CIE Pseudocode compiler

lexer = make_psuedocode_lexer()
parser = make_pseudocode_parser()
compiler = PseudocodeCompiler()

# Get arguments
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("file", help="The file to compile")
arg_parser.add_argument("-o", "--output", help="The output file")
arg_parser.add_argument("-c", "--cfile", help="The C file to generate")
arg_parser.add_argument("-r", "--run", help="Run the compiled file", action="store_true")
arg_parser.add_argument("-d", "--debug", help="Debug output", action="store_true")
arg_parser.add_argument("--input", help="Provide input to compiled code")  # ✅ NEW
args = arg_parser.parse_args()

# Read the file
file = args.file
if not os.path.exists(file):
    print(f"File {file} does not exist")
    exit(1)

with open(file, 'r', encoding='utf-8') as f:
    code = f.read()

# Lex and parse the code
print("Lexing and parsing")
lexer.input(code)
if args.debug:
    print("==== LEX ====")
    for tok in lexer:
        print(tok)
    lexer.input(code)
    lexer.lineno = 1
    lexer.lexpos = 0
    print("==== PARSE ====")
ast = parser.parse(code, lexer=lexer)
if args.debug:
    print(ast)

# Compile the code
compiler.ast = ast
if ast is None:
    eprint("Parsing failed, look for syntax errors")
    exit(2)

print("Compiling")
compiler.compile_to_cpp()
c_code = compiler.cpp_code
if args.debug:
    print("==== C CODE ====")
    print(c_code)

# Write and compile the C code
compiler.cpp_file = args.cfile or 'temp/temp.cpp'
compiler.output_file = args.output or 'temp/temp'

print("Writing to file")
compiler.write_to_file()
print("Compiling with gcc")
res, stderr = compiler.invoke_gcc()
if not res:
    eprint("Compilation failed")
    eprint("==== STDERR from g++ ====")
    eprint(stderr)
    eprint("==== C CODE ====")
    eprint(c_code)
    eprint("========")
    exit(3)

# ✅ Run the compiled file if needed
if args.run:
    print("==== OUTPUT ====")
    ext = ".exe" if os.name == 'nt' else ""
    binary_path = f'{compiler.output_file}{ext}'

    try:
        # Allow optional simulated user input
        user_input = (args.input + "\n") if args.input else ""

        result = subprocess.run(
            [binary_path],
            input=user_input,
            capture_output=True,
            text=True,
            timeout=5
        )
        print(result.stdout.strip())
        if result.stderr:
            eprint("STDERR:")
            eprint(result.stderr.strip())
    except Exception as e:
        eprint(f"Execution failed: {str(e)}")
