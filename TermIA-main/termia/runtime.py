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

    def _resolve(self, path):

        if path is None:
            return self.cwd

        # Normaliza separadores
        path = path.replace("\\", "/").strip()

        # Caminho sobe relativo ao cwd
        if path.startswith("/.."):
            raw = os.path.join(self.cwd, path.lstrip("/"))
        # Caminho absoluto dentro da pasta atual (incremental)
        elif path.startswith("/"):
            candidate = os.path.join(self.cwd, path.lstrip("/"))
            if os.path.exists(candidate):
                raw = candidate
            else:
                # se não existe em cwd, assume base_dir
                raw = os.path.join(self.base_dir, path.lstrip("/"))
        else:
            # Caminho relativo normal
            raw = os.path.join(self.cwd, path)

        # Normaliza para remover ./ e ../
        absolute = os.path.normpath(raw)

        # Bloqueio da sandbox
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
        # Se nenhum path foi passado, volta ao diretório base (comportamento comum)
        if path is None or path.strip() == "":
            self.cwd = self.base_dir
            return f"Diretório atual: {self.cwd}"

        try:
            # Usa o resolve com suporte a barras invertidas, ., .., etc.
            resolved = self._resolve(path)
        except PermissionError as e:
            return str(e)

        # Se o caminho existe e é diretório → atualiza o cwd
        if os.path.isdir(resolved):
            self.cwd = resolved
            return f"Diretório atual: {self.cwd}"

        return f"Caminho não encontrado: {path}"



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
