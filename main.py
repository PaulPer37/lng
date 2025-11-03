"""
Main entry point for the Rust Analyzer.

This file manages the execution of the three modules:
- Lexical Analysis (src/lexer.py)
- Syntactic Analysis (src/parser.py)
- Semantic Analysis (src/semantic.py)
"""

import os
import sys
from datetime import datetime
import getpass
import contextlib
from io import StringIO
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import lexer as lexmod 

ALG = "algoritmo1.rs"
LOGS_DIR = "logs"

def make_log_name(user):
    now = datetime.now()
    return f"lexico-{user}-{now.day:02d}-{now.month:02d}-{now.year}-{now.hour:02d}h{now.minute:02d}.txt"

def main():
    if not os.path.isfile(ALG):
        print(f"Test file not found: {ALG}")
        return

    with open(ALG, "r", encoding="utf-8") as f:
        src = f.read()
    lexmod.lexer.lineno = 1

    err_capture = StringIO()
    tokens = []

    with contextlib.redirect_stdout(err_capture):
        lexmod.lexer.input(src)
        for tok in lexmod.lexer:
            tokens.append(tok)

    os.makedirs(LOGS_DIR, exist_ok=True)
    user = getpass.getuser() or "anon"
    user = user.replace(" ", "_")
    logname = make_log_name(user)
    logpath = os.path.join(LOGS_DIR, logname)

    with open(logpath, "w", encoding="utf-8") as lg:
        lg.write(f"LEXICO LOG - file: {ALG}\n")
        lg.write(f"Generated: {datetime.now().isoformat()}\n")
        lg.write(f"User: {user}\n")
        lg.write("=" * 60 + "\n\n")
        lg.write("TOKENS\n")
        lg.write("-" * 60 + "\n")
        if tokens:
            for t in tokens:
                lg.write(f"LINE {t.lineno:4d} | TYPE: {t.type:12s} | POS: {t.lexpos:6d} | VALUE: {repr(t.value)}\n")
        else:
            lg.write("No tokens recognized.\n")
        lg.write("\n" + "-" * 60 + "\n\n")
        lg.write("ERRORS / LEXER OUTPUT\n")
        lg.write("-" * 60 + "\n")
        errors_text = err_capture.getvalue()
        if errors_text.strip():
            lg.write(errors_text)
        else:
            lg.write("No errors reported by lexer (t_error did not print anything).\n")

    print(f"Log written: {logpath}")

if __name__ == "__main__":
    main()