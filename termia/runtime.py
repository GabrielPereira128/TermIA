"""
Runtime do TermIA
Executa comandos de SO e comandos IA com integração à API.
"""

from __future__ import annotations
import os
import json
import requests
from dataclasses import dataclass


IA_API_URL = "https://api.ninja-apps.work/v1/chat/completions"


@dataclass
class TermIARuntime:
    base_dir: str
    cwd: str

    @classmethod
    def create(cls, base_dir=None):
        base = os.path.abspath(base_dir or os.getcwd())
        return cls(base_dir=base, cwd=base)

    # ---------------------------------------------------------
    # Utilidades
    # ---------------------------------------------------------

    def _cmd_help(self):
        return (
            "Comandos disponíveis:\n"
            "  ls [path]\n"
            "  mkdir <nome>\n"
            "  cd [path]\n"
            "  ia ask \"texto\" ou \"\"\"texto\"\"\" em caso de texto com quebra de linha\n"
            "  ia summarize \"\"\"texto\"\"\"\n"
            "  ia codeexplain \"\"\"codigo\"\"\"\n"
            "  exit\n"
        )

    def _resolve(self, path: str | None) -> str:
        """Resolve diretórios dentro da sandbox com segurança."""
        if path is None:
            return self.cwd

        raw = path if os.path.isabs(path) else os.path.join(self.cwd, path)
        absolute = os.path.abspath(raw)

        if not absolute.startswith(self.base_dir):
            raise PermissionError(f"Caminho fora da sandbox: {absolute}")

        return absolute

    # ---------------------------------------------------------
    # Execução geral de AST
    # ---------------------------------------------------------
    def execute(self, ast):
        t = ast["type"]

        if t == "ls":
            return self._cmd_ls(ast.get("path"))
        if t == "mkdir":
            return self._cmd_mkdir(ast["name"])
        if t == "cd":
            return self._cmd_cd(ast.get("path"))
        if t == "exit":
            return "Encerrando TermIA."
        if t == "ia":
            return self._exec_ia(ast["action"])
        elif t == "help":
            return self._cmd_help()

        raise NotImplementedError(f"Comando não suportado: {t}")

    # ---------------------------------------------------------
    # Comandos de SO
    # ---------------------------------------------------------
    def _cmd_ls(self, path):
        p = self._resolve(path)
        if not os.path.isdir(p):
            raise NotADirectoryError(p)

        files = sorted(os.listdir(p))
        return "\n".join(files) if files else "(vazio)"

    def _cmd_mkdir(self, name):
        p = self._resolve(name)
        os.makedirs(p, exist_ok=True)
        return f"Diretório criado: {p}"

    def _cmd_cd(self, path):
        p = self._resolve(path)
        if not os.path.isdir(p):
            raise NotADirectoryError(p)

        self.cwd = p
        return f"Diretório atual: {self.cwd}"

    # ---------------------------------------------------------
    # Comandos IA
    # ---------------------------------------------------------
    def _exec_ia(self, action):
        t = action["type"]

        if t == "ia.ask":
            prompt = (
                "Você é o TermIA, um assistente em português brasileiro.\n"
                "Responda de forma objetiva e clara.\n\n"
                f"Pergunta do usuário:\n{action['prompt']}"
            )
            return self._call_ia(prompt)

        if t == "ia.summarize":
            prompt = (
                "Resuma o texto abaixo em português brasileiro, "
                "de forma clara e objetiva.\n\n"
                f"Texto:\n{action['text']}"
            )
            return self._call_ia(prompt)

        if t == "ia.codeexplain":
            prompt = (
                "Explique o seguinte código ou conteúdo técnico "
                "para um estudante de engenharia de computação.\n"
                "Seja claro, direto e não enrole.\n\n"
                f"Tipo: {action['kind']}\n"
                f"Conteúdo:\n{action['target']}"
            )
            return self._call_ia(prompt)

        raise NotImplementedError(f"Ação IA não suportada: {t}")


    # ---------------------------------------------------------
    # Chamada à API
    # ---------------------------------------------------------
    def _call_ia(self, prompt: str) -> str:
        data = {
            "messages": json.dumps(
                [{"role": "user", "content": prompt}],
                ensure_ascii=False
            ),
            "max_tokens": "500",
            "temperature": "0.4"
        }

        try:
            resp = requests.post(IA_API_URL, data=data, timeout=25)
            resp.raise_for_status()
        except Exception as e:
            return f"[Erro na IA] {e}"

        try:
            payload = resp.json()
        except Exception:
            return f"[Erro] Resposta não é JSON válido:\n{resp.text}"

        # Tenta formato padrão OpenAI-like
        try:
            msg = payload["choices"][0]["message"]["content"]
            return str(msg).strip()
        except Exception:
            # Fallback para qualquer outro formato
            return json.dumps(payload, ensure_ascii=False, indent=2)
