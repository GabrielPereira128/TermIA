"""
TermIA - Demo (parcial): REPL que apenas "parseia" os comandos e imprime AST.
Execução de comandos e IA serão integradas na próxima etapa.
Uso:
    python -m termia.main_demo
"""
import json
from .parser import build_parser

def main():
    parse = build_parser()
    print("TermIA (parcial) - apenas parser. Digite 'exit' para sair.\n")
    while True:
        try:
            line = input("termia> ").strip()
        except EOFError:
            break
        if not line:
            continue
        try:
            ast = parse(line)
            print(json.dumps(ast, ensure_ascii=False, indent=2))
            if ast.get("type") == "exit":
                break
        except Exception as e:
            print(f"[erro] {e}")

if __name__ == "__main__":
    main()
