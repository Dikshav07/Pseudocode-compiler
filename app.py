from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess

from classes.lexer import make_psuedocode_lexer
from classes.parser import make_pseudocode_parser
from classes.compiler import PseudocodeCompiler

app = Flask(__name__)
CORS(app)

lexer = make_psuedocode_lexer()
parser = make_pseudocode_parser()
compiler = PseudocodeCompiler()

@app.route("/compile", methods=["POST"])
def compile_code():
    data = request.json
    code = data.get("code", "")
    user_input = data.get("input", "")

    # Save code to file
    with open("code.psc", "w", encoding="utf-8") as f:
        f.write(code)

    try:
        # Parse pseudocode manually
        lexer.input(code)
        ast = parser.parse(code, lexer=lexer)
        compiler.ast = ast
        compiler.compile_to_cpp()

        # Write and compile C++ code
        compiler.write_to_file()
        compiler.invoke_gcc()

        # Run the compiled executable with or without input
        output = ""
        if user_input:
            process = subprocess.Popen(
                [compiler.output_file + ".exe"],  # Use ".exe" for Windows
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            output, _ = process.communicate(user_input + "\n")
        else:
            output = subprocess.check_output(
                [compiler.output_file + ".exe"],
                text=True
            )

        return jsonify({
            "output": output,
            "cpp_code": compiler.cpp_code
        })

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
