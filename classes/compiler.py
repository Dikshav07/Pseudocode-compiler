import os
import random
import subprocess

from classes.general_functions import remove_quotes, make_string_variable_friendly


class PseudocodeCompiler:
    binop_cond_psc_to_cpp = {
        "=": "==",
        "<>": "!=",
        "<": "<",
        ">": ">",
        "<=": "<=",
        ">=": ">=",
        "+": "+",
        "-": "-",
        "*": "*",
        "/": "/",
        "MOD": "%",
        "DIV": "/",
        "AND": "&&",
        "OR": "||",
        "NOT": "!",
        "&": "+",
    }

    datatype_for_print = {
        'number': '%d',
        'string': '%s',
        'INTEGER': '%d',
        'STRING': '%s',
    }

    datatype_python_to_cpp = {
        'int': 'int',
        'str': 'std::string',
        'bool': 'bool',
        'float': 'float',
    }

    datatypes_to_cpp = {
        'INTEGER': 'int',
        'STRING': 'std::string',
        'BOOLEAN': 'bool',
        'CHAR': 'char',
        'REAL': 'float'
    }

    declare_defaults = {
        'INTEGER': 0,
        'STRING': '""',
        'BOOLEAN': 'false',
        'CHAR': "' '",
        'REAL': 0.0
    }

    def __init__(self, cpp_file: str = "temp/temp.cpp", output_file: str = "temp/temp", random_seed: int = 42):
        self.enums = {}
        self.ast = None
        self.cpp_code = ""

        self.cpp_file = cpp_file
        self.output_file = output_file

        self.variables = {}
        self.procedures = []

        random.seed(random_seed)

        self.generated_randoms = []

        self.main_body_flag = True

    def generate_random(self):
        random_num = random.randint(0, 1000)
        while random_num in self.generated_randoms:
            random_num = random.randint(0, 1000)
        self.generated_randoms.append(random_num)
        return random_num

    def set_main_body_flag(self, flag):
        self.main_body_flag = flag
        return ''

    def walk(self, node):
        # node could be a tuple or a list of tuples
        if isinstance(node, tuple):
            match node[0]:
                case 'binop':
                    if node[1] == 'NOT':
                        return f'!{self.walk(node[2])}'
                    return f'({self.walk(node[2])} {self.binop_cond_psc_to_cpp[node[1]]} {self.walk(node[3])})'
                case 'number':
                    return str(node[1])
                case 'string':
                    return f'"{node[1]}"'
                case 'char':
                    return f"'{node[1]}'"
                case 'variable':
                    return node[1]
                case 'boolean':
                    return str(node[1]).lower()
                case 'assign':
                    return f'{node[1]} = {self.walk(node[2])};'
                case 'print':
                    return f'''
                    std::cout << {self.walk(node[1])} << std::endl;                
                    '''
                case 'procedure_no_param':
                    if self.main_body_flag:
                        self.procedures.append(node)
                        return ''
                    else:
                        return f'''
                        void {node[1]}() {{
                            {self.walk(node[2])}
                        }}
                        '''
                case 'call_procedure_no_param':
                    return f'{node[1]}();'
                case 'input':
                    # get the datatype of the variable
                    datatype = self.variables[node[1]]
                    if datatype == 'STRING' or datatype == 'INTEGER' or datatype == 'REAL' or datatype == 'CHAR':
                        return f'std::cin >> {node[1]};'
                    if datatype == 'BOOLEAN':
                        return f'''
                        std::string {node[1]}_str;
                        std::cin >> {node[1]}_str;
                        {node[1]} = string_to_bool({node[1]}_str);
                        '''
                case 'if':
                    return f'if ({self.walk(node[1])}) {{\n{self.walk(node[2])}\n}} else {{\n{self.walk(node[3])}\n}}'
                case 'return':
                    return f'return {self.walk(node[1])};'
                case 'run_function_with_params':
                    return f'{node[1]}({", ".join([self.walk(param) for param in node[2]])})'
                case 'procedure_with_params':
                    if self.main_body_flag:
                        self.procedures.append(node)
                        return ''
                    else:
                        return f'''
                        void {node[1]}({', '.join([f'{self.datatypes_to_cpp[param[2]]} {param[1]}' for param in node[2]])}) {{
                            {self.walk(node[3])}
                        }}
                        '''
                case 'call_procedure_with_params':
                    return f'{node[1]}({", ".join([self.walk(param) for param in node[2]])});'
                case 'run_function_no_params':
                    return f'{node[1]}()'
                case 'if_no_else':
                    return f'if ({self.walk(node[1])}) {{\n{self.walk(node[2])}\n}}'
                case 'repeat':
                    random_num = self.generate_random()
                    return f'''
                    bool {node[0]}_cond_{random_num} = true;
                    while ({node[0]}_cond_{random_num}) {{
                        {self.walk(node[1])}
                        {node[0]}_cond_{random_num} = !({self.walk(node[2])});
                    }}
                    '''
                case 'function_with_params':
                    if self.main_body_flag:
                        self.procedures.append(node)
                        return ''
                    else:
                        return f'''
                        {self.datatypes_to_cpp[node[3]]} {node[1]}({', '.join([f'{self.datatypes_to_cpp[param[2]]} {param[1]}' for param in node[2]])}) {{
                            {self.walk(node[4])}
                        }}
                        '''
                case 'function_no_params':
                    if self.main_body_flag:
                        self.procedures.append(node)
                        return ''
                    else:
                        return f'''
                        {self.datatypes_to_cpp[node[2]]} {node[1]}() {{
                            {self.walk(node[3])}
                        }}
                        '''

                case 'case_statement':
                    codee = f'''
                    switch ({node[1]}) {{
                    {self.walk(node[2])}
                    }}
                    '''

                    return codee

                case 'case':
                    if node[1] == "OTHERWISE":
                        return f'''
                        default: {{
                            {self.walk(node[2])}
                        }}
                        '''
                    codee = f'''
                    case {self.walk(node[1])}: {{
                        {self.walk(node[2])}
                        break;
                    }} 
                    '''
                    return codee

                case 'declare_array':
                    self.variables[node[1]] = {
                        'type': node[4],
                        'length': node[3],
                        'starting': node[2]
                    }
                    length = (node[3] - node[2]) + 1
                    return f'{self.datatypes_to_cpp[node[4]]} {node[1]}[{length}];'

                case 'assign_array':
                    index = f'{self.walk(node[2])} - {self.variables[node[1]]["starting"]}'
                    return f'{node[1]}[{index}] = {self.walk(node[3])};'

                case 'array_index':
                    index = f'{self.walk(node[2])} - {self.variables[node[1]]["starting"]}'
                    return f'{node[1]}[{index}]'

                case 'open_file':
                    file_handle_type = node[2]
                    if file_handle_type == 'READ':
                        return f'''
                            std::ifstream {remove_quotes(make_string_variable_friendly(self.walk(node[1])))}_file_handle({self.walk(node[1])}); // Open the file
                            if (!{remove_quotes(make_string_variable_friendly(self.walk(node[1])))}_file_handle.is_open()) {{
                                std::cerr << "Unable to open file: " << {self.walk(node[1])} << std::endl;
                                return 1;
                            }}
                        '''
                    elif file_handle_type == 'WRITE':
                        return f'''
                            std::ofstream {remove_quotes(make_string_variable_friendly(self.walk(node[1])))}_file_handle({self.walk(node[1])}); // Open the file
                            if (!{remove_quotes(make_string_variable_friendly(self.walk(node[1])))}_file_handle.is_open()) {{
                                std::cerr << "Unable to open file: " << {self.walk(node[1])} << std::endl;
                                return 1;
                            }}
                        '''
                    elif file_handle_type == 'APPEND':
                        return f'''
                            std::ofstream {remove_quotes(make_string_variable_friendly(self.walk(node[1])))}_file_handle({self.walk(node[1])}, std::ios::app); // Open the file
                            if (!{remove_quotes(make_string_variable_friendly(self.walk(node[1])))}_file_handle.is_open()) {{
                                std::cerr << "Unable to open file: " << {self.walk(node[1])} << std::endl;
                                return 1;
                            }}
                        '''

                case 'EOF_check':
                    return f'EOF_check({remove_quotes(make_string_variable_friendly(self.walk(node[1])))}_file_handle)'

                case 'read_file':
                    return f'''
                            std::getline({remove_quotes(make_string_variable_friendly(self.walk(node[1])))}_file_handle, {node[2]});
                        '''

                case 'close_file':
                    return f'''
                            {remove_quotes(make_string_variable_friendly(self.walk(node[1])))}_file_handle.close();
                        '''

                case 'write_file':
                    return f'''
                            {remove_quotes(make_string_variable_friendly(self.walk(node[1])))}_file_handle << {self.walk(node[2])} << std::endl;
                        '''

                case 'declare_variable_list':
                    codee = ''
                    for variable in node[1]:
                        self.variables[variable] = node[2]
                        codee += f'{self.datatypes_to_cpp[node[2]]} {variable} = {self.declare_defaults[node[2]]};\n'
                    return codee

                case 'declare_array_2d':
                    self.variables[node[1]] = {
                        'type': node[6],
                        'starting1': node[2],
                        'length1': node[3],
                        'starting2': node[4],
                        'length2': node[5]
                    }
                    length1 = (node[3] - node[2]) + 1
                    length2 = (node[5] - node[4]) + 1
                    return f'{self.datatypes_to_cpp[node[6]]} {node[1]}[{length1}][{length2}];'

                case 'declare_constant':
                    value = self.walk(node[2])
                    datatype = eval(f"type({value}).__qualname__")
                    datatype = self.datatype_python_to_cpp[datatype]
                    self.variables[node[1]] = datatype
                    return f'const {datatype} {node[1]} = {value};'

                case 'assign_array_2d':
                    index1 = f'{self.walk(node[2])} - {self.variables[node[1]]["starting1"]}'
                    index2 = f'{self.walk(node[3])} - {self.variables[node[1]]["starting2"]}'
                    return f'{node[1]}[{index1}][{index2}] = {self.walk(node[4])};'

                case 'array_index_2d':
                    index1 = f'{self.walk(node[2])} - {self.variables[node[1]]["starting1"]}'
                    index2 = f'{self.walk(node[3])} - {self.variables[node[1]]["starting2"]}'
                    return f'{node[1]}[{index1}][{index2}]'

                case 'declare_record':
                    self.variables[node[1]] = node[2]
                    return f'struct {node[1]} {{\n{self.walk(node[2])}\n}};'

                case 'declare_custom_datatype':
                    # making a new variable of the custom datatype
                    self.variables[node[1]] = node[2]
                    return f'{node[2]} {node[1]};'

                case 'declare_array_custom_datatype':
                    self.variables[node[1]] = {
                        'type': node[4],
                        'length': node[3],
                        'starting': node[2]
                    }
                    length = (node[3] - node[2]) + 1
                    return f'{node[4]} {node[1]}[{length}];'

                case 'declare_array_2d_custom_datatype':
                    self.variables[node[1]] = {
                        'type': node[6],
                        'starting1': node[2],
                        'length1': node[3],
                        'starting2': node[4],
                        'length2': node[5]
                    }
                    length1 = (node[3] - node[2]) + 1
                    length2 = (node[5] - node[4]) + 1
                    return f'{node[6]} {node[1]}[{length1}][{length2}];'

                case 'assign_access':
                    return f'{self.walk(node[1])} = {self.walk(node[2])};'

                case 'access':
                    # access the variable from (presumably) a record(struct)
                    # for evaluate-able accessors, we will evaluate them
                    if isinstance(node[1], tuple) and isinstance(node[2], tuple):  # eg. a[x].b[y]
                        return f'{self.walk(node[1])}.{self.walk(node[2])}'
                    elif isinstance(node[2], tuple):  # eg. a[x].b
                        return f'{node[1]}.[{self.walk(node[2])}]'
                    elif isinstance(node[1], tuple):  # eg. a.b[x]
                        return f'{self.walk(node[1])}.{node[2]}'

                    # for normal variables, it will just return the variable name
                    return f'{node[1]}.{node[2]}'

                case 'enum_declaration':
                    enum_values = ', '.join(node[2])
                    self.enums[node[1]] = enum_values
                    return f'enum {node[1]} {{\n{enum_values}\n}};'

                case 'print_multiple':
                    # Evaluate each expression, print with no separator
                    codee = 'std::cout << '
                    for i, expr in enumerate(node[1]):
                        codee += f'{self.walk(expr)}'
                        if i != len(node[1]) - 1:
                            codee += ' << '
                    codee += ' << std::endl;'
                    return codee
                case 'while':
                    return f'while ({self.walk(node[1])}) {{\n{self.walk(node[2])}\n}}'
                case 'for':
                    return f'for (int {node[1]} = {self.walk(node[2])}; {node[1]} <= {self.walk(node[3])}; {node[1]}++) {{\n{self.walk(node[4])}\n}}'
                case 'condition':
                    if node[1] == 'NOT':
                        return f'!{self.walk(node[2])}'
                    return f'({self.walk(node[2])} {self.binop_cond_psc_to_cpp[node[1]]} {self.walk(node[3])})'
                case 'program':
                    if not node[1]:
                        return ""
                    return '\n'.join([self.walk(child) for child in node[1]])
                case 'declare':
                    self.variables[node[1]] = node[2]
                    return f'{self.datatypes_to_cpp[node[2]]} {node[1]} = {self.declare_defaults[node[2]]};'
        elif isinstance(node, list):
            if not node:
                return ""
            return '\n'.join([self.walk(child) for child in node])
        else:
            raise ValueError(f"Unknown node type {node}")

    def compile_to_cpp(self):
        if self.ast is None:
            raise ValueError("AST is None")

        main_body_code = self.walk(self.ast)

        self.set_main_body_flag(False)
        procedure_code = '\n'.join([self.walk(proc) for proc in self.procedures])

        cpp_code = f"""
        #include <cstdlib>
        #include <cstring>
        #include <iostream>
        #include <cctype>
        #include <random>
        #include <fstream>
        
        // user-defined functions and procedures
        {procedure_code}        
        
        int main() {{
            {main_body_code}
        return 0;
        }}
        
        """

        # Prettify the code
        # Remove empty lines
        cpp_code = '\n'.join([line for line in cpp_code.split('\n') if line.strip()])
        # Remove trailing & leading spaces
        cpp_code = '\n'.join([line.strip() for line in cpp_code.split('\n')])

        # TODO: Indentaion

        self.cpp_code = cpp_code
        return cpp_code

    def write_to_file(self):
        # Make sure the directory exists
        try:
            os.mkdir(os.path.dirname(self.cpp_file))
        except FileExistsError:
            pass
        with open(self.cpp_file, 'w') as f:
            f.write(self.cpp_code)

    def invoke_gcc(self):
        # Make sure the directory exists
        try:
            os.mkdir(os.path.dirname(self.output_file))
        except FileExistsError:
            pass

        process = subprocess.Popen(['g++', self.cpp_file, '-o', self.output_file], stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        if stderr:
            return False, stderr
        return True, None

    def reset(self):
        self.ast = None
        self.cpp_code = ""
