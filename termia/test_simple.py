#!/usr/bin/env python3

import sys
import requests
import json

def main():
    # Obter a mensagem do primeiro argumento da linha de comando ou usar uma padrão
    message = sys.argv[1] if len(sys.argv) > 1 else "Qual a capital da França?"
    api_url = "https://api.ninja-apps.work/v1/chat/completions"
    
    print(f"Enviando mensagem: {message}")
    print(f"Para: {api_url}")
    print("")
    
    # Dados a serem enviados como formulário
    data = {
        "messages": json.dumps([{"role": "user", "content": message}]),
        "max_tokens": "150",
        "temperature": "0.7"
    }
    
    try:
        # Enviar requisição POST
        response = requests.post(api_url, data=data)
        response.raise_for_status()  # Levantar exceção para códigos de erro HTTP
        
        # Imprimir a resposta formatada
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        
    except requests.exceptions.RequestException as e:
        print(f"Erro ao enviar requisição: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON da resposta: {e}")
        print("Resposta bruta:", response.text)
        sys.exit(1)

if __name__ == "__main__":
    main()