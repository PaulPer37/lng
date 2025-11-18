import os
import sys
from datetime import datetime
import getpass
import contextlib
from io import StringIO

# Configuración de rutas base
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")

# Agregar src al path para importar módulos
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import lexer as lexmod
import parser as parsemod
import semantic as semmod
import utils


def run_lexer_analysis(src, user, filename, logs_path):
    """Ejecuta análisis léxico y genera log en la carpeta logs_path"""
    lexmod.lexer.lineno = 1
    err_capture = StringIO()
    tokens = []

    with contextlib.redirect_stdout(err_capture):
        lexmod.lexer.input(src)
        for tok in lexmod.lexer:
            tokens.append(tok)

    # Pasamos logs_path a la utilidad
    logpath = utils.save_lexer_log(
        user, tokens, err_capture.getvalue(), filename, logs_path
    )
    print(f"✓ Lexer log escrito en: {logpath}")

    return tokens, err_capture.getvalue()


def run_parser_analysis(src, user, logs_path):
    """Ejecuta análisis sintáctico y genera AST en la carpeta logs_path"""
    print("\n" + "=" * 60)
    print("INICIANDO ANÁLISIS SINTÁCTICO")
    print("=" * 60)

    ast, errors = parsemod.parse_code(src)

    # Pasamos logs_path a la utilidad
    logpath = utils.save_syntax_log(user, errors, logs_path)

    if not errors:
        print("✓ Código analizado correctamente")
        # Opcional: imprimir AST si es pequeño
    else:
        print(f"✗ Se encontraron {len(errors)} errores sintácticos")
        for err in errors:
            print(f"  - {err}")

    print(f"\n✓ Parser log escrito en: {logpath}")
    return ast, errors


def run_semantic_analysis(ast, user, logs_path):
    """Ejecuta análisis semántico y genera log en la carpeta logs_path"""
    print("\n" + "=" * 60)
    print("INICIANDO ANÁLISIS SEMÁNTICO")
    print("=" * 60)

    errors = semmod.analyze(ast)

    # Pasamos logs_path a la utilidad
    logpath = utils.save_semantic_log(
        user, errors, semmod.symbol_table, semmod.function_table, logs_path
    )

    if not errors:
        print("✓ Análisis semántico completado sin errores")
        print(f"\nVariables declaradas: {len(semmod.symbol_table)}")
        print(f"Funciones declaradas: {len(semmod.function_table)}")
    else:
        print(f"✗ Se encontraron {len(errors)} errores semánticos")
        for err in errors[:5]:
            print(f"  - {err}")

    print(f"\n✓ Semantic log escrito en: {logpath}")
    return errors


def main():
    # ==========================================
    # CONFIGURACIÓN DE RUTAS (Dinámico)
    # ==========================================
    NOMBRE_ARCHIVO = "semantic-algorithm-1.rs"

    # 1. Directorio base (donde está main.py)
    DIR_ACTUAL = os.path.dirname(os.path.abspath(__file__))

    # 2. Ruta del archivo de entrada (en carpeta test/semantic vecina a main)
    ruta_entrada = os.path.join(DIR_ACTUAL, "test", "semantic", NOMBRE_ARCHIVO)
    ruta_entrada = os.path.normpath(ruta_entrada)

    # 3. Ruta de la carpeta de LOGS (vecina a main)
    ruta_logs = os.path.join(DIR_ACTUAL, "logs")

    # Crear carpeta logs si no existe
    if not os.path.exists(ruta_logs):
        try:
            os.makedirs(ruta_logs)
            print(f"📁 Carpeta de logs creada en: {ruta_logs}")
        except OSError as e:
            print(f"❌ Error creando carpeta logs: {e}")
            return

    # ==========================================
    # VERIFICACIÓN
    # ==========================================
    if not os.path.isfile(ruta_entrada):
        print("=" * 60)
        print(f"❌ ERROR: No se encuentra el archivo de prueba.")
        print(f"Buscando en: {ruta_entrada}")
        print("=" * 60)
        return

    with open(ruta_entrada, "r", encoding="utf-8") as f:
        src = f.read()

    user = getpass.getuser() or "anon"
    user = user.replace(" ", "_")

    print("=" * 60)
    print("RUST ANALYZER - COMPILADOR")
    print("=" * 60)
    print(f"Archivo: {NOMBRE_ARCHIVO}")
    print(f"Logs en: {ruta_logs}")
    print(f"Usuario: {user}")
    print(f"Fecha:   {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 60)

    # [FASE 1] LÉXICO
    print("\n[FASE 1] Análisis Léxico")
    print("-" * 60)
    # Pasamos ruta_logs y el nombre del archivo para el log
    tokens, lex_errors = run_lexer_analysis(src, user, NOMBRE_ARCHIVO, ruta_logs)
    print(f"Tokens reconocidos: {len(tokens)}")

    # [FASE 2] SINTÁCTICO
    print("\n[FASE 2] Análisis Sintáctico")
    print("-" * 60)
    # Pasamos ruta_logs
    ast, syntax_errors = run_parser_analysis(src, user, ruta_logs)

    semantic_errors = []
    if not syntax_errors and ast:
        # [FASE 3] SEMÁNTICO
        print("\n[FASE 3] Análisis Semántico")
        print("-" * 60)
        # Pasamos ruta_logs
        semantic_errors = run_semantic_analysis(ast, user, ruta_logs)
    else:
        print("\n[FASE 3] Análisis Semántico")
        print("-" * 60)
        print("⚠ Análisis semántico omitido debido a errores sintácticos")

    print("\n" + "=" * 60)
    print("RESUMEN DE ANÁLISIS")
    print("=" * 60)
    print(f"Tokens léxicos: {len(tokens)}")
    print(f"Errores sintácticos: {len(syntax_errors)}")
    print(
        f"Errores semánticos: {len(semantic_errors) if not syntax_errors else 'No analizado'}"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()
