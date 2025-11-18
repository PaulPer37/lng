# semantic.py
# Analizador Semántico - Proyecto Compiladores

# ============================================================================
# 1. VARIABLES GLOBALES Y CONTEXTO
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
# 2. UTILIDADES COMPARTIDAS
# ============================================================================
def add_error(line, message):
    """Agrega un error semántico a la lista"""
    error = f"Línea {line}: {message}"
    semantic_errors.append(error)
    print(f"❌ {error}")

def get_expression_type(node):
    """
    Retorna el tipo de una expresión del AST.
    CORREGIDO: Ahora busca variables y llamadas a funciones.
    """
    # CASO 1: Es una variable (Identifier)
    if isinstance(node, str):
        if node in symbol_table:
            return symbol_table[node]['type']
        return None

    # CASO 2: Es un nodo complejo (Tupla)
    if isinstance(node, tuple):
        head = node[0]
        
        # Literales
        if head == "literal":
            value = node[1]
            if isinstance(value, bool): return "bool"
            elif isinstance(value, int): return "i32"
            elif isinstance(value, float): return "f64"
            elif isinstance(value, str):
                return "char" if len(value) == 1 else "String"
        
        # Operaciones Binarias
        elif head == "binop":
            operator = node[1]
            if operator in ['+', '-', '*', '/', '%']:
                # Retorna el tipo del operando izquierdo (asume homogeneidad)
                return get_expression_type(node[2])
            elif operator in ['==', '!=', '<', '>', '<=', '>=', '&&', '||']:
                return "bool"
        
        # Operaciones Unarias
        elif head == "unop":
            if node[1] == '!': return "bool"
            if node[1] == '-': return get_expression_type(node[2])

        # Llamadas a Función (Retorna el tipo de retorno de la función)
        elif head == "func_call":
            func_name = node[1]
            if func_name in function_table:
                return function_table[func_name]['return_type']
        
        # Accesos a Array/Vector (Simplificado)
        elif head == "array_access":
            # Aquí idealmente buscaríamos el tipo interno del array en symbol_table
            # Por ahora asumimos que devuelve el tipo base de la colección
            arr_name = node[1]
            if isinstance(arr_name, str) and arr_name in symbol_table:
                full_type = symbol_table[arr_name]['type']
                # Si el tipo es "Vec<i32>" o "[i32; 5]", extraemos "i32"
                # Esta es una simplificación para que no falle
                if "i32" in str(full_type): return "i32"
                if "f64" in str(full_type): return "f64"
                if "bool" in str(full_type): return "bool"
            return None

    return None

# ============================================================================
# 3. ANÁLISIS SEMÁNTICO - Anthony Herrera
# ============================================================================

def check_variable_declaration(node, line=0):
    """Regla: No redeclarar y verificar tipos de inicialización"""
    # var_decl = ("var_decl", name, type, value, is_mut)
    if node[0] == "var_decl":
        name = node[1]
        declared_type = node[2]
        value = node[3]
        is_mut = node[4]

        if name in symbol_table:
            add_error(line, f"Variable '{name}' ya fue declarada previamente")
            return

        # Validación de tipos
        if value is not None:
            value_type = get_expression_type(value)
            # Solo verificamos si tenemos ambos tipos identificados
            if declared_type and value_type:
                if value_type != declared_type:
                    add_error(line, f"Tipo incompatible: se esperaba '{declared_type}' pero se obtuvo '{value_type}'")

        symbol_table[name] = {
            'type': declared_type,
            'mutable': is_mut,
            'initialized': value is not None
        }

def check_variable_usage(node, line=0):
    """Verifica que la variable exista"""
    if isinstance(node, str):
        if node not in symbol_table:
            add_error(line, f"Variable '{node}' no ha sido declarada")
            return False
    return True

def check_assignment(node, line=0):
    """Verifica asignaciones a variables existentes y mutables"""
    # assign = ("assign", name, operator, value)
    if node[0] == "assign":
        name = node[1]
        operator = node[2]
        value = node[3]

        if name not in symbol_table:
            add_error(line, f"No se puede asignar a '{name}': variable no declarada")
            return

        var_info = symbol_table[name]

        # Verificar mutabilidad
        if not var_info['mutable'] and var_info['initialized']:
            add_error(line, f"No se puede asignar a '{name}': variable no es mutable (use 'mut')")
            return

        # Verificar tipos
        value_type = get_expression_type(value)
        if var_info['type'] and value_type:
            if operator == '=':
                if var_info['type'] != value_type:
                    add_error(line, f"Tipo incompatible: '{name}' es '{var_info['type']}' pero se asigna '{value_type}'")
            else:
                # Para +=, -=, etc, deben ser números
                if var_info['type'] not in ['i32', 'f64']:
                    add_error(line, f"Operador '{operator}' no válido para tipo '{var_info['type']}'")

        var_info['initialized'] = True

# ============================================================================
# 4. ANÁLISIS SEMÁNTICO - Paul Perdomo
# ============================================================================

def check_data_structures(node, line=0):
    # Verificación de Vectores y Arrays
    if node[0] == "vector" or node[0] == "array":
        elements = node[1]
        if len(elements) > 0:
            first_type = get_expression_type(elements[0])
            for i, elem in enumerate(elements[1:], 1):
                elem_type = get_expression_type(elem)
                if elem_type and first_type and elem_type != first_type:
                    add_error(line, f"Tipo inconsistente en estructura: elemento {i} es '{elem_type}', se esperaba '{first_type}'")
    
    # Accesos a Array
    elif node[0] == "array_access":
        array_name, index = node[1], node[2]
        if isinstance(array_name, str):
            check_variable_usage(array_name, line)
        
        index_type = get_expression_type(index)
        if index_type and index_type != "i32":
            add_error(line, f"Índice de array debe ser entero (i32), se obtuvo '{index_type}'")
    
    # Accesos a Tuplas
    elif node[0] == "tuple_access":
        tuple_name = node[1]
        check_variable_usage(tuple_name, line)

def check_boolean_conditions(node, line=0):
    # Verificación de condiciones booleanas (if/while)
    if node[0] in ["if", "while"]:
        condition = node[1]
        condition_type = get_expression_type(condition)
        if condition_type and condition_type != "bool":
            add_error(line, f"Condición en '{node[0]}' debe ser booleana, se obtuvo '{condition_type}'")

# ============================================================================
# 5. ANÁLISIS SEMÁNTICO - Danilo Drouet
# ============================================================================

def check_function_declaration(node, line=0):
    if node[0] == "func_decl":
        name = node[1]
        params = node[2]
        return_type = node[3]
        body = node[4]
        
        if name in function_table:
            add_error(line, f"Función '{name}' ya fue declarada previamente")
            return
        
        param_types = [p[2] for p in params]
        function_table[name] = {'params': param_types, 'return_type': return_type}
        
        old_context = context.copy()
        context['in_function'] = name
        context['return_type'] = return_type
        
        # Parametros como variables locales
        for param in params:
            symbol_table[param[1]] = {'type': param[2], 'mutable': False, 'initialized': True}
        
        analyze_node(body, line)
        context.update(old_context)

def check_function_call(node, line=0):
    if node[0] == "func_call":
        name = node[1]
        args = node[2]
        
        if name not in function_table:
            add_error(line, f"Función '{name}' no ha sido declarada")
            return
        
        func_info = function_table[name]
        if len(args) != len(func_info['params']):
            add_error(line, f"Función '{name}' espera {len(func_info['params'])} argumentos, se recibieron {len(args)}")
            return
        
        for i, (arg, expected_type) in enumerate(zip(args, func_info['params'])):
            arg_type = get_expression_type(arg)
            if arg_type and expected_type and arg_type != expected_type:
                add_error(line, f"Argumento {i+1} de '{name}': se esperaba '{expected_type}', se obtuvo '{arg_type}'")

def check_control_flow(node, line=0):
    if node[0] == "break" or node[0] == "continue":
        if not context['in_loop']:
            add_error(line, f"'{node[0]}' solo puede usarse dentro de un loop")
    
    elif node[0] == "return":
        if context['in_function'] is None:
            add_error(line, "'return' solo puede usarse dentro de una función")
            return
        
        return_value = node[1] if len(node) > 1 else None
        expected_type = context['return_type']
        
        if expected_type is None and return_value is not None:
            add_error(line, f"Función '{context['in_function']}' no debe retornar un valor")
        elif expected_type is not None and return_value is None:
            add_error(line, f"Función '{context['in_function']}' debe retornar un valor de tipo '{expected_type}'")
        elif expected_type is not None and return_value is not None:
            return_type = get_expression_type(return_value)
            if return_type and return_type != expected_type:
                add_error(line, f"Tipo de retorno incorrecto: se esperaba '{expected_type}', se obtuvo '{return_type}'")

# ============================================================================
# 6. FUNCIÓN PRINCIPAL DE ANÁLISIS
# ============================================================================

def analyze_node(node, line=0):
    """Analiza recursivamente un nodo del AST"""
    if node is None or not isinstance(node, tuple):
        return
    
    node_type = node[0]
    
    # Anthony Herrera - Variables y asignaciones
    if node_type == "var_decl":
        check_variable_declaration(node, line)
    elif node_type == "assign" or node_type == "assign_index":
        check_assignment(node, line)
    
    # Paul Perdomo - Estructuras de datos y condiciones
    elif node_type in ["vector", "array", "array_access", "tuple_access"]:
        check_data_structures(node, line)
    elif node_type in ["if", "while"]:
        check_boolean_conditions(node, line)
        if node_type == "while":
            old_in_loop = context['in_loop']
            context['in_loop'] = True
            analyze_node(node[2], line)
            context['in_loop'] = old_in_loop
    
    # Danilo Drouet - Funciones y control de flujo
    elif node_type == "func_decl":
        check_function_declaration(node, line)
    elif node_type == "func_call":
        check_function_call(node, line)
    elif node_type in ["return", "break", "continue"]:
        check_control_flow(node, line)
    
    # Paul Perdomo - Loop For
    elif node_type == "for":
        old_in_loop = context['in_loop']
        context['in_loop'] = True
        iter_var = node[1]
        symbol_table[iter_var] = {'type': 'i32', 'mutable': False, 'initialized': True}
        analyze_node(node[3], line)
        context['in_loop'] = old_in_loop
    
    # Recursividad general
    elif node_type == "program":
        for stmt in node[1]:
            analyze_node(stmt, line)
    elif node_type == "block":
        for stmt in node[1]:
            analyze_node(stmt, line)
    elif node_type == "binop":
        analyze_node(node[2], line)
        analyze_node(node[3], line)
    elif node_type == "unop":
        analyze_node(node[2], line)

def analyze(ast):
    global semantic_errors, symbol_table, function_table
    # Reiniciar estado para cada análisis
    semantic_errors = []
    symbol_table = {}
    function_table = {}
    
    analyze_node(ast)
    return semantic_errors