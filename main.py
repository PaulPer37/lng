import os
import sys
from datetime import datetime
import getpass
import contextlib
from io import StringIO

HERE = os.path.dirname(os.path.abspath(_file_))
SRC = os.path.join(HERE, "src")

if SRC not in sys.path:
    sys.path.insert(0, SRC)

import lexer as lexmod
import parser as parsemod
import semantic as semmod  # ← NUEVO
import utils

ALG = "algoritmo2.rs"


def run_lexer_analysis(src, user):
    """Ejecuta análisis léxico y genera log"""
    lexmod.lexer.lineno = 1
    err_capture = StringIO()
    tokens = []

    with contextlib.redirect_stdout(err_capture):
        lexmod.lexer.input(src)
        for tok in lexmod.lexer:
            tokens.append(tok)

    # Usar utilidad centralizada para guardar log
    logpath = utils.save_lexer_log(user, tokens, err_capture.getvalue(), ALG)
    print(f"✓ Lexer log written: {logpath}")

    return tokens, err_capture.getvalue()


def run_parser_analysis(src, user):
    """Ejecuta análisis sintáctico y genera AST"""
    print("\n" + "=" * 60)
    print("INICIANDO ANÁLISIS SINTÁCTICO")
    print("=" * 60)

    ast, errors = parsemod.parse_code(src)

    # Guardar log usando utilidad centralizada
    logpath = utils.save_syntax_log(user, errors)

    if not errors:
        print("✓ Código analizado correctamente")
        print("\nAST generado:")
        print(ast)
    else:
        print(f"✗ Se encontraron {len(errors)} errores sintácticos")
        for err in errors:
            print(f"  - {err}")

    print(f"\n✓ Parser log written: {logpath}")
    return ast, errors


def run_semantic_analysis(ast, user):
    """Ejecuta análisis semántico y genera log"""
    print("\n" + "=" * 60)
    print("INICIANDO ANÁLISIS SEMÁNTICO")
    print("=" * 60)

    errors = semmod.analyze(ast)

    # Guardar log usando utilidad centralizada
    logpath = utils.save_semantic_log(user, errors, semmod.symbol_table, semmod.function_table)

    if not errors:
        print("✓ Análisis semántico completado sin errores")
        print(f"\nVariables declaradas: {len(semmod.symbol_table)}")
        print(f"Funciones declaradas: {len(semmod.function_table)}")
    else:
        print(f"✗ Se encontraron {len(errors)} errores semánticos")
        for err in errors[:5]:  # Mostrar solo los primeros 5
            print(f"  - {err}")
        if len(errors) > 5:
            print(f"  ... y {len(errors) - 5} errores más")

    print(f"\n✓ Semantic log written: {logpath}")
    return errors


def main():
    if not os.path.isfile(ALG):
        print(f"Test file not found: {ALG}")
        return

    with open(ALG, "r", encoding="utf-8") as f:
        src = f.read()

    user = getpass.getuser() or "anon"
    user = user.replace(" ", "_")

    print("=" * 60)
    print("RUST ANALYZER - COMPILADOR")
    print("=" * 60)
    print(f"Archivo: {ALG}")
    print(f"Usuario: {user}")
    print(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 60)

    print("\n[FASE 1] Análisis Léxico")
    print("-" * 60)
    tokens, lex_errors = run_lexer_analysis(src, user)
    print(f"Tokens reconocidos: {len(tokens)}")

    print("\n[FASE 2] Análisis Sintáctico")
    print("-" * 60)
    ast, syntax_errors = run_parser_analysis(src, user)

    # ========================================================================
    # NUEVA FASE 3: ANÁLISIS SEMÁNTICO
    # ========================================================================
    semantic_errors = []
    if not syntax_errors and ast:
        print("\n[FASE 3] Análisis Semántico")
        print("-" * 60)
        semantic_errors = run_semantic_analysis(ast, user)
    else:
        print("\n[FASE 3] Análisis Semántico")
        print("-" * 60)
        print("⚠ Análisis semántico omitido debido a errores sintácticos")

    print("\n" + "=" * 60)
    print("RESUMEN DE ANÁLISIS")
    print("=" * 60)
    print(f"Tokens léxicos: {len(tokens)}")
    print(f"Errores léxicos: {'Sí' if lex_errors.strip() else 'No'}")
    print(f"Errores sintácticos: {len(syntax_errors)}")
    print(f"Errores semánticos: {len(semantic_errors) if not syntax_errors else 'No analizado'}")
    print(f"AST generado: {'Sí' if ast and not syntax_errors else 'No'}")
    
    if not lex_errors.strip() and not syntax_errors and not semantic_errors:
        print("\n✅ ¡CÓDIGO VÁLIDO! Sin errores detectados.")
    
    print("=" * 60)


if _name_ == "_main_":
    main()