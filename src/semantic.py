# ============================================================================
# Anthony Herrera, Paul Perdomo, Danilo Drouet
# Analizador Semántico - Proyecto Compiladores
# ============================================================================

semantic_errors = []
symbol_table = {}
function_table = {}

context = {
    'in_loop': False,
    'in_function': None,
    'return_type': None
}

# ============================================================================
# UTILIDADES COMPARTIDAS
# ============================================================================

def add_error(message, line=0):
    """Agrega un error semántico a la lista (sin duplicados)"""
    error = f"Línea {line}: {message}"
    if error not in semantic_errors:
        semantic_errors.append(error)
        print(f"❌ {error}")


def get_line_from_node(node):
    """Extrae el número de línea de un nodo si está disponible"""
    if isinstance(node, tuple) and len(node) > 0:
        # Buscar el número de línea al final de la tupla
        for item in reversed(node):
            if isinstance(item, int) and item > 0:
                return item
    return 0


def get_expression_type(node, line=0):
    """
    Retorna el tipo de una expresión del AST.
    También verifica que las variables usadas existan.
    """
    # CASO 1: Es un identificador (string)
    if isinstance(node, str):
        if node in symbol_table:
            return symbol_table[node]['type']
        # Si no está en la tabla, es un error (variable no declarada)
        if node not in function_table:  # No es una función tampoco
            add_error(f"Variable '{node}' no ha sido declarada", line)
        return None

    # CASO 2: Es un nodo complejo (tupla)
    if isinstance(node, tuple):
        head = node[0]
        node_line = get_line_from_node(node) or line
        
        # Literales
        if head == "literal":
            value = node[1]
            if isinstance(value, bool):
                return "bool"
            elif isinstance(value, int):
                return "i32"
            elif isinstance(value, float):
                return "f64"
            elif isinstance(value, str):
                # Si es un string que parece ser un ID, verificar si existe
                if value.isidentifier():
                    if value in symbol_table:
                        return symbol_table[value]['type']
                    elif value not in function_table:
                        add_error(f"Variable '{value}' no ha sido declarada", node_line)
                        return None
                # String literal normal
                return "char" if len(value) == 1 else "String"
        
        # Operaciones Binarias
        elif head == "binop":
            operator = node[1]
            left_type = get_expression_type(node[2], node_line)
            right_type = get_expression_type(node[3], node_line)
            
            if operator in ['+', '-', '*', '/', '%']:
                # Retorna el tipo dominante (f64 > i32)
                if left_type == "f64" or right_type == "f64":
                    return "f64"
                if left_type == "i32" or right_type == "i32":
                    return "i32"
                return left_type
            elif operator in ['==', '!=', '<', '>', '<=', '>=', '&&', '||']:
                return "bool"
        
        # Operaciones Unarias
        elif head == "unop":
            if node[1] == '!':
                return "bool"
            if node[1] == '-':
                return get_expression_type(node[2], node_line)

        # Llamadas a Función
        elif head == "func_call":
            func_name = node[1]
            if func_name in function_table:
                return function_table[func_name]['return_type']
            return None
        
        # Acceso a Arrays
        elif head == "array_access":
            arr_name = node[1]
            if isinstance(arr_name, str):
                if arr_name in symbol_table:
                    return symbol_table[arr_name].get('type')
            return None

    return None


# ============================================================================
# ANÁLISIS SEMÁNTICO - Anthony Herrera
# ============================================================================

def check_variable_declaration(node, line=0):
    """Verifica declaraciones de variables"""
    if node[0] == "var_decl":
        name = node[1]
        declared_type = node[2]
        value = node[3]
        is_mut = node[4]
        node_line = node[5] if len(node) > 5 else line

        # Error 1: Redeclaración
        if name in symbol_table:
            add_error(f"Variable '{name}' ya fue declarada previamente", node_line)
            return

        # Error 2: Tipos incompatibles
        if value is not None:
            value_type = get_expression_type(value, node_line)
            if declared_type and value_type:
                if value_type != declared_type:
                    add_error(f"Tipo incompatible: se esperaba '{declared_type}' pero se obtuvo '{value_type}'", node_line)
            # Si no hay tipo declarado, inferir del valor
            elif not declared_type:
                declared_type = value_type

        # Registrar en la tabla de símbolos
        symbol_table[name] = {
            'type': declared_type,
            'mutable': is_mut,
            'initialized': value is not None
        }


def check_assignment(node, line=0):
    """Verifica asignaciones a variables"""
    if node[0] == "assign":
        name = node[1]
        operator = node[2]
        value = node[3]
        node_line = node[4] if len(node) > 4 else line

        # Error: Variable no declarada
        if name not in symbol_table:
            add_error(f"No se puede asignar a '{name}': variable no declarada", node_line)
            return

        var_info = symbol_table[name]

        # Error: Variable no es mutable
        if not var_info['mutable'] and var_info['initialized']:
            add_error(f"No se puede asignar a '{name}': variable no es mutable (use 'mut')", node_line)
            return

        # Verificar compatibilidad de tipos
        value_type = get_expression_type(value, node_line)
        if var_info['type'] and value_type:
            if operator == '=':
                if var_info['type'] != value_type:
                    add_error(f"Tipo incompatible: '{name}' es '{var_info['type']}' pero se asigna '{value_type}'", node_line)

        var_info['initialized'] = True


# ============================================================================
# ANÁLISIS SEMÁNTICO - Paul Perdomo
# ============================================================================

def check_data_structures(node, line=0):
    """Verifica estructuras de datos (arrays, vectores, tuplas)"""
    node_line = get_line_from_node(node) or line
    
    # Error: Arrays/Vectores con tipos inconsistentes
    if node[0] == "vector" or node[0] == "array":
        elements = node[1]
        if len(elements) > 0:
            first_type = get_expression_type(elements[0], node_line)
            has_error = False
            for i, elem in enumerate(elements[1:], 1):
                elem_type = get_expression_type(elem, node_line)
                if elem_type and first_type and elem_type != first_type:
                    if not has_error:
                        add_error(f"Tipo inconsistente en {'vector' if node[0] == 'vector' else 'array'}: elementos tienen tipos diferentes ('{first_type}' y '{elem_type}')", node_line)
                        has_error = True
                    break
    
    # Error: Índice de array no entero
    elif node[0] == "array_access":
        array_name = node[1]
        index = node[2]
        
        # Verificar que el array existe
        if isinstance(array_name, str):
            if array_name not in symbol_table:
                add_error(f"Variable '{array_name}' no ha sido declarada", node_line)
        
        # Verificar que el índice es entero
        index_type = get_expression_type(index, node_line)
        if index_type and index_type != "i32":
            add_error(f"Índice de array debe ser entero (i32), se obtuvo '{index_type}'", node_line)
    
    # Acceso a tuplas
    elif node[0] == "tuple_access":
        tuple_name = node[1]
        if tuple_name not in symbol_table:
            add_error(f"Variable '{tuple_name}' no ha sido declarada", node_line)


def check_boolean_conditions(node, line=0):
    """Verifica que las condiciones sean booleanas"""
    node_line = get_line_from_node(node) or line
    
    if node[0] in ["if", "while"]:
        condition = node[1]
        condition_type = get_expression_type(condition, node_line)
        
        if condition_type and condition_type != "bool":
            add_error(f"Condición en '{node[0]}' debe ser booleana, se obtuvo '{condition_type}'", node_line)


# ============================================================================
# ANÁLISIS SEMÁNTICO - Danilo Drouet
# ============================================================================

def check_function_declaration(node, line=0):
    """Verifica el cuerpo de las funciones (ya registradas en fase 1)"""
    if node[0] == "func_decl":
        name = node[1]
        params = node[2]
        return_type = node[3]
        body = node[4]
        node_line = node[5] if len(node) > 5 else line
        
        # Cambiar contexto para analizar el cuerpo
        old_context = context.copy()
        old_symbols = list(symbol_table.keys())
        
        context['in_function'] = name
        context['return_type'] = return_type
        
        # Agregar parámetros como variables locales
        for param in params:
            param_name = param[1]
            param_type = param[2]
            symbol_table[param_name] = {
                'type': param_type,
                'mutable': False,
                'initialized': True
            }
        
        # Analizar cuerpo de la función
        analyze_node(body, node_line)
        
        # Limpiar parámetros del scope
        for param in params:
            if param[1] in symbol_table:
                del symbol_table[param[1]]
        
        # Restaurar contexto
        context.update(old_context)


def check_function_call(node, line=0):
    """Verifica llamadas a funciones"""
    if node[0] == "func_call":
        name = node[1]
        args = node[2]
        node_line = node[3] if len(node) > 3 else line
        
        # Error: Función no declarada
        if name not in function_table:
            add_error(f"Función '{name}' no ha sido declarada", node_line)
            return
        
        func_info = function_table[name]
        
        # Error: Número incorrecto de argumentos
        if len(args) != len(func_info['params']):
            add_error(f"Función '{name}' espera {len(func_info['params'])} argumentos, se recibieron {len(args)}", node_line)
            return
        
        # Error: Tipos de argumentos incorrectos
        for i, (arg, expected_type) in enumerate(zip(args, func_info['params'])):
            arg_type = get_expression_type(arg, node_line)
            if arg_type and expected_type and arg_type != expected_type:
                add_error(f"Argumento {i+1} de '{name}': se esperaba '{expected_type}', se obtuvo '{arg_type}'", node_line)


def check_control_flow(node, line=0):
    """Verifica break, continue y return"""
    node_line = get_line_from_node(node) or line
    
    # Error: break/continue fuera de loop
    if node[0] == "break" or node[0] == "continue":
        if not context['in_loop']:
            add_error(f"'{node[0]}' solo puede usarse dentro de un loop", node_line)
    
    # Error: return con problemas
    elif node[0] == "return":
        # Error: return fuera de función
        if context['in_function'] is None:
            add_error("'return' solo puede usarse dentro de una función", node_line)
            return
        
        return_value = node[1] if len(node) > 1 else None
        expected_type = context['return_type']
        
        # Error: return con valor cuando no debe
        if expected_type is None and return_value is not None:
            add_error(f"Función '{context['in_function']}' no debe retornar un valor", node_line)
        # Error: return sin valor cuando debe
        elif expected_type is not None and return_value is None:
            add_error(f"Función '{context['in_function']}' debe retornar un valor de tipo '{expected_type}'", node_line)
        # Error: tipo de retorno incorrecto
        elif expected_type is not None and return_value is not None:
            return_type = get_expression_type(return_value, node_line)
            if return_type and return_type != expected_type:
                add_error(f"Tipo de retorno incorrecto: se esperaba '{expected_type}', se obtuvo '{return_type}'", node_line)


# ============================================================================
# FUNCIÓN PRINCIPAL DE ANÁLISIS RECURSIVO
# ============================================================================

def analyze_node(node, line=0):
    """Analiza recursivamente un nodo del AST"""
    if node is None or not isinstance(node, tuple):
        return
    
    node_type = node[0]
    node_line = get_line_from_node(node) or line
    
    # Anthony Herrera - Variables y asignaciones
    if node_type == "var_decl":
        check_variable_declaration(node, node_line)
        # También analizar el valor de inicialización
        if len(node) > 3 and node[3] is not None:
            analyze_node(node[3], node_line)
    
    elif node_type == "assign" or node_type == "assign_index":
        check_assignment(node, node_line)
        # Analizar el valor asignado
        if len(node) > 3:
            analyze_node(node[3], node_line)
    
    # Paul Perdomo - Estructuras de datos y condiciones
    elif node_type in ["vector", "array"]:
        check_data_structures(node, node_line)
        # Analizar cada elemento
        if len(node) > 1:
            for elem in node[1]:
                analyze_node(elem, node_line)
    
    elif node_type == "array_access":
        check_data_structures(node, node_line)
        # Analizar el índice
        if len(node) > 2:
            analyze_node(node[2], node_line)
    
    elif node_type == "tuple_access":
        check_data_structures(node, node_line)
    
    elif node_type in ["if", "while"]:
        check_boolean_conditions(node, node_line)
        # Analizar condición
        if len(node) > 1:
            analyze_node(node[1], node_line)
        # Analizar bloque then
        if len(node) > 2:
            if node_type == "while":
                old_in_loop = context['in_loop']
                context['in_loop'] = True
                analyze_node(node[2], node_line)
                context['in_loop'] = old_in_loop
            else:
                analyze_node(node[2], node_line)
        # Analizar bloque else
        if len(node) > 3 and node[3] is not None:
            analyze_node(node[3], node_line)
    
    # Danilo Drouet - Funciones y control de flujo
    elif node_type == "func_decl":
        check_function_declaration(node, node_line)
    
    elif node_type == "func_call":
        check_function_call(node, node_line)
        # Analizar argumentos
        if len(node) > 2:
            for arg in node[2]:
                analyze_node(arg, node_line)
    
    elif node_type in ["return", "break", "continue"]:
        check_control_flow(node, node_line)
        # Si es return con valor, analizar el valor
        if node_type == "return" and len(node) > 1 and node[1] is not None:
            analyze_node(node[1], node_line)
    
    # For loops
    elif node_type == "for":
        old_in_loop = context['in_loop']
        context['in_loop'] = True
        
        # Variable de iteración
        iter_var = node[1]
        old_var = symbol_table.get(iter_var)
        symbol_table[iter_var] = {
            'type': 'i32',
            'mutable': False,
            'initialized': True
        }
        
        # Analizar rango y cuerpo
        if len(node) > 2:
            analyze_node(node[2], node_line)
        if len(node) > 3:
            analyze_node(node[3], node_line)
        
        # Restaurar
        if old_var:
            symbol_table[iter_var] = old_var
        elif iter_var in symbol_table:
            del symbol_table[iter_var]
        
        context['in_loop'] = old_in_loop
    
    # Recursividad general
    elif node_type == "program":
        for stmt in node[1]:
            analyze_node(stmt, node_line)
    
    elif node_type == "block":
        for stmt in node[1]:
            analyze_node(stmt, node_line)
    
    elif node_type == "binop":
        # Analizar ambos operandos
        if len(node) > 2:
            analyze_node(node[2], node_line)
        if len(node) > 3:
            analyze_node(node[3], node_line)
    
    elif node_type == "unop":
        # Analizar operando
        if len(node) > 2:
            analyze_node(node[2], node_line)
    
    elif node_type == "expr_stmt":
        # Analizar la expresión
        if len(node) > 1:
            analyze_node(node[1], node_line)
    
    elif node_type == "print":
        # Analizar argumentos de print
        if len(node) > 2 and node[2]:
            for arg in node[2]:
                analyze_node(arg, node_line)


# ============================================================================
# FUNCIÓN PRINCIPAL PÚBLICA
# ============================================================================

def register_functions(node):
    """Primera pasada: Registrar todas las declaraciones de funciones"""
    if node is None or not isinstance(node, tuple):
        return
    
    node_type = node[0]
    
    # Registrar función sin analizar su cuerpo
    if node_type == "func_decl":
        name = node[1]
        params = node[2]
        return_type = node[3]
        node_line = node[5] if len(node) > 5 else 0
        
        # Verificar redeclaración
        if name in function_table:
            add_error(f"Función '{name}' ya fue declarada previamente", node_line)
        else:
            param_types = [p[2] for p in params]
            function_table[name] = {
                'params': param_types,
                'return_type': return_type
            }
    
    # Recursión solo en nodos que contienen otras declaraciones
    elif node_type == "program":
        for stmt in node[1]:
            register_functions(stmt)
    elif node_type == "block":
        for stmt in node[1]:
            register_functions(stmt)


def analyze(ast):
    """Punto de entrada del análisis semántico"""
    global semantic_errors, symbol_table, function_table, context
    
    # Reiniciar estado
    semantic_errors = []
    symbol_table = {}
    function_table = {}
    context = {
        'in_loop': False,
        'in_function': None,
        'return_type': None
    }
    
    if ast:
        # FASE 1: Registrar todas las funciones primero
        register_functions(ast)
        
        # FASE 2: Analizar el contenido completo
        analyze_node(ast)
    
    return semantic_errors