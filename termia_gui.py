#!/usr/bin/env python3
"""
TermIA - Interface gráfica Tkinter (corrigida)

Melhorias principais:
 - normalização de aspas tipográficas
 - suporte a entrada multilinha via diálogo (quando usar triple-quotes)
 - validações para evitar colagem de código Python
 - execução única do parse/exec por envio
 - mensagens de erro claras
"""

import tkinter as tk
from tkinter import scrolledtext, simpledialog
import re

from termia.parser import build_parser
from termia.runtime import TermIARuntime


class MultilineDialog(simpledialog.Dialog):
    """Dialog simples com Text para colagem/edição de múltiplas linhas."""
    def __init__(self, parent, title: str, initial_text: str = ""):
        self.initial_text = initial_text
        super().__init__(parent, title=title)

    def body(self, master):
        self.text = tk.Text(master, width=80, height=20, wrap=tk.WORD, font=("Consolas", 11))
        self.text.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        if self.initial_text:
            self.text.insert("1.0", self.initial_text)
        return self.text

    def apply(self):
        self.result = self.text.get("1.0", tk.END).rstrip("\n")


class TermIAGui(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("TermIA - Terminal Inteligente")
        self.geometry("900x550")
        self.configure(bg="#0a0e27")

        # Parser + runtime
        self.parse = build_parser()
        self.runtime = TermIARuntime.create()

        # Cores
        self.colors = {
            'bg_primary': '#0a0e27',
            'bg_secondary': '#0f172a',
            'border': '#1e293b',
            'text_primary': '#e2e8f0',
            'text_secondary': '#cbd5e1',
            'text_dim': '#64748b',
            'accent_green': '#10b981',
            'accent_cyan': '#38bdf8',
            'accent_teal': '#5eead4',
            'error_red': '#f87171'
        }

        self._create_widgets()
        self.entry.focus_set()
        self._print_banner()

    # ---------------------------------------------------------
    # Widgets
    # ---------------------------------------------------------
    def _create_widgets(self):
        container = tk.Frame(self, bg=self.colors['bg_primary'])
        container.pack(fill=tk.BOTH, expand=True)

        # Header
        header = tk.Frame(container, bg=self.colors['bg_secondary'], height=45)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="▶  root@termia:~$",
            font=("Consolas", 12, "bold"),
            fg=self.colors['accent_green'],
            bg=self.colors['bg_secondary']
        ).pack(side=tk.LEFT, padx=16)

        # Help
        help_btn = tk.Label(
            header,
            text="?",
            font=("Consolas", 16, "bold"),
            fg=self.colors['text_dim'],
            bg=self.colors['bg_secondary'],
            cursor="hand2"
        )
        help_btn.pack(side=tk.RIGHT, padx=16)
        help_btn.bind("<Button-1>", lambda e: self._show_help())

        # Output
        out_frame = tk.Frame(container, bg=self.colors['bg_primary'])
        out_frame.pack(fill=tk.BOTH, expand=True)

        self.output = scrolledtext.ScrolledText(
            out_frame,
            wrap=tk.WORD,
            font=("Consolas", 11),
            bg=self.colors['bg_primary'],
            fg=self.colors['text_primary'],
            insertbackground=self.colors['accent_green'],
            relief=tk.FLAT
        )
        self.output.pack(fill=tk.BOTH, expand=True)

        self.output.tag_config("prompt", foreground=self.colors['accent_green'])
        self.output.tag_config("command", foreground=self.colors['accent_cyan'])
        self.output.tag_config("output", foreground=self.colors['accent_teal'])
        self.output.tag_config("error", foreground=self.colors['error_red'])
        self.output.tag_config("banner", foreground=self.colors['accent_green'])

        # Input
        bottom = tk.Frame(container, bg=self.colors['bg_secondary'], height=60)
        bottom.pack(fill=tk.X)
        bottom.pack_propagate(False)

        input_area = tk.Frame(bottom, bg=self.colors['bg_secondary'])
        input_area.pack(fill=tk.BOTH, expand=True, padx=16, pady=12)

        tk.Label(
            input_area, text="›", font=("Consolas", 20, "bold"),
            fg=self.colors['accent_green'], bg=self.colors['bg_secondary']
        ).pack(side=tk.LEFT)

        entry_frame = tk.Frame(input_area, bg=self.colors['border'])
        entry_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        self.entry = tk.Entry(
            entry_frame,
            font=("Consolas", 11),
            bg=self.colors['border'],
            fg=self.colors['text_primary'],
            insertbackground=self.colors['accent_green'],
            relief=tk.FLAT
        )
        self.entry.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self.entry.bind("<Return>", self._enter_pressed)

        send_btn = tk.Label(
            input_area, text="↑", font=("Consolas", 20),
            fg=self.colors['text_dim'], bg=self.colors['bg_secondary'],
            cursor="hand2"
        )
        send_btn.pack(side=tk.RIGHT)
        send_btn.bind("<Button-1>", lambda e: self._send())

    # ---------------------------------------------------------
    # Banner
    # ---------------------------------------------------------
    def _print_banner(self):
        self.output.insert(tk.END, "TermIA - GUI adaptada para multiline\n", "banner")
        self.output.insert(tk.END, f"Base: {self.runtime.base_dir}\n", "banner")
        self.output.insert(tk.END, f"CWD:  {self.runtime.cwd}\n", "banner")
        self.output.insert(tk.END, "-----------------------------------------\n", "banner")
        self.output.insert(tk.END, "Comandos:\n", "banner")
        self.output.insert(tk.END, "  ls [path]\n", "banner")
        self.output.insert(tk.END, "  mkdir <nome>\n", "banner")
        self.output.insert(tk.END, "  cd [path] (\\NomeDoDiretorio para entrar em uma pasta e \\.. para voltar uma pasta)\n", "banner")
        self.output.insert(tk.END, "  ia ask \"texto\" (para textos que nao possuem quebra de linha)\n", "banner")
        self.output.insert(tk.END, "  ia summarize \"texto\" (para textos que nao possuem quebra de linha)\n", "banner")
        self.output.insert(tk.END, "  ia summarize \"\"\"texto\"\"\"  (abre diálogo multilinha)\n", "banner")
        self.output.insert(tk.END, "  ia codeexplain \"\"\"código\"\"\"  (abre diálogo multilinha)\n", "banner")
        self.output.insert(tk.END, "  exit (encerra o terminal)\n", "banner")        
        self.output.insert(tk.END, "-----------------------------------------\n", "banner")

    # ---------------------------------------------------------
    # Normalização / validação
    # ---------------------------------------------------------
    def _normalize(self, text: str) -> str:
        return (
            text
            .replace("“", '"')
            .replace("”", '"')
            .replace("‘", "'")
            .replace("’", "'")
        )

    def _is_suspicious_code(self, text: str) -> bool:
        """Detecta entradas que parecem ser código Python colado por engano."""
        stripped = text.lstrip()
        if not stripped:
            return False
        first_word = stripped.split(None, 1)[0]
        if first_word in ("import", "from", "def", "class", "#!"):
            return True
        # heurística: contém "import " ou "ply.yacc" em qualquer lugar
        if "import " in text or "ply.yacc" in text:
            return True
        return False

    # ---------------------------------------------------------
    # Eventos
    # ---------------------------------------------------------
    def _enter_pressed(self, event):
        self._send()

    # ---------------------------------------------------------
    # Envio / processamento do comando
    # ---------------------------------------------------------
    def _send(self):
        raw = self.entry.get()
        if raw is None:
            return
        command = raw.strip()
        if not command:
            return

        self.entry.delete(0, tk.END)


        # Normalize quotes immediately
        command = self._normalize(command)

        # Quick sanity: reject ambiguous 4-quote sequences
        if '""""' in command or "''''" in command:
            self._append_error("Sequência de aspas inválida: use \"\" para vazio ou \"\"\"...\"\"\" para multilinha.")
            return

        # If user pasted a triple-quote opener but didn't close it, open multiline dialog
        # Patterns: ia summarize """ or ia codeexplain """
        m = re.match(r'^(ia\s+(summarize|codeexplain))\s+("""{0,1})(.*)$', command, flags=re.IGNORECASE)
        if m:
            cmd_head = m.group(1)  # e.g. "ia summarize"
            remainder = m.group(3)
            # if remainder starts with triple quotes or we have opener without closer
            if remainder.startswith('"""'):
                # command contains opener; check if it also contains closer
                after = remainder[3:]
                if '"""' in after:
                    # already closed in-line; nothing special: treat as normal command
                    pass
                else:
                    # need multiline content from user: open dialog
                    self._open_multiline_and_process(cmd_head, initial_text=after)
                    return

        # final sanity: check for pasted Python code
        if self._is_suspicious_code(command):
            self._append_error("Entrada parece conter código-fonte (import/def/class). Cole apenas o comando/argumento desejado.")
            return

        # Proceed to process single-line command
        # echo
        self.output.insert(tk.END, "\n> ", "prompt")
        self.output.insert(tk.END, f"{command}\n", "command")
        self.output.see(tk.END)

        # Execute once
        try:
            ast = self.parse(command)
        except Exception as e:
            self._append_error(f"Erro no parser: {e}")
            return

        try:
            result = self.runtime.execute(ast)
        except Exception as e:
            self._append_error(f"Erro na execução: {e}")
            return

        self.output.insert(tk.END, result + "\n", "output")
        self.output.see(tk.END)

        # close on exit
        if isinstance(ast, dict) and ast.get("type") == "exit":
            self.after(400, self.destroy)

    # ---------------------------------------------------------
    # Multiline dialog flow
    # ---------------------------------------------------------
    def _open_multiline_and_process(self, cmd_head: str, initial_text: str = ""):
        """
        Abre um diálogo multiline para o usuário colar/escrever o conteúdo
        e, quando enviado, monta o comando completo e processa.
        cmd_head exemplo: "ia summarize" (sem trailing space)
        initial_text: texto já presente após the opener (pode estar vazio)
        """
        dlg = MultilineDialog(self, title=f"{cmd_head} — conteúdo multilinha", initial_text=initial_text)
        content = getattr(dlg, "result", None)
        if content is None:
            # user cancelled
            return

        # build command with triple quotes explicit
        # Note: we escape any triple-quote occurrences inside content safely by replacing """ with '\"\"\"'
        safe_content = content.replace('"""', '\\"""')
        full_command = f'{cmd_head} """{safe_content}"""'

        # Final sanity check
        if self._is_suspicious_code(full_command):
            self._append_error("Entrada multilinha parece conter código-fonte; operação cancelada.")
            return

        # echo
        self.output.insert(tk.END, "\n> ", "prompt")
        self.output.insert(tk.END, f"{full_command}\n", "command")
        self.output.see(tk.END)

        # parse + execute
        try:
            ast = self.parse(full_command)
        except Exception as e:
            self._append_error(f"Erro no parser (multiline): {e}")
            return

        try:
            result = self.runtime.execute(ast)
        except Exception as e:
            self._append_error(f"Erro na execução: {e}")
            return

        self.output.insert(tk.END, result + "\n", "output")
        self.output.see(tk.END)

    # ---------------------------------------------------------
    # Output helpers
    # ---------------------------------------------------------
    def _append_error(self, text: str):
        self.output.insert(tk.END, f"{text}\n", "error")
        self.output.see(tk.END)

    # ---------------------------------------------------------
    # Help (fills entry with help command)
    # ---------------------------------------------------------
    def _show_help(self):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, "help")
        self._send()


if __name__ == "__main__":
    app = TermIAGui()
    app.mainloop()
