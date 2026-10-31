"""
Etapa 3 - Analise experimental.

Mede o tempo de cada algoritmo para tamanhos crescentes de entrada,
com 5 execucoes por tamanho (cada execucao com uma entrada aleatoria
diferente, mas a MESMA entrada para todos os algoritmos daquela execucao).

Tambem mede tamanhos bem pequenos (2 a 128) com mais repeticoes, para
ver onde a forca bruta ganha da divisao e conquista.

Saidas:
  resultados/medicoes.csv          (medicoes brutas, uma linha por execucao)
  resultados/medicoes_pequenos.csv (tamanhos pequenos)
  resultados/maquina.txt           (configuracao da maquina)

Rodar da pasta raiz:  python experimentos/experimentos.py
"""
import csv
import os
import platform
import random
import sys
import gc
import time

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(RAIZ, "src"))
import etapa1_subarranjo as e1   # noqa: E402
import etapa2_par_proximo as e2  # noqa: E402

TAMANHOS = [100, 200, 400, 800, 1600, 3200, 6400]
REPETICOES = 5

TAMANHOS_PEQUENOS = [2, 4, 8, 16, 32, 64, 128]
REPETICOES_PEQUENOS = 300   # tempos muito curtos -> preciso de mais repeticoes

ETAPA1 = {"bruta": e1.forca_bruta, "dc": e1.divisao_conquista, "kadane": e1.kadane}
ETAPA2 = {"bruta": e2.forca_bruta, "dc": e2.divisao_conquista}


def gera_vetor(n):
    return [random.randint(-1000, 1000) for _ in range(n)]


def gera_pontos(n):
    return [(random.uniform(0, 10**6), random.uniform(0, 10**6)) for _ in range(n)]


def cronometra(funcao, entrada):
    inicio = time.perf_counter()
    funcao(entrada)
    return time.perf_counter() - inicio


def medir(tamanhos, repeticoes, so_media=False):
    linhas = []
    for etapa, algoritmos, gerador in (("etapa1", ETAPA1, gera_vetor),
                                       ("etapa2", ETAPA2, gera_pontos)):
        for n in tamanhos:
            if etapa == "etapa2" and n < 2:
                continue
            tempos = {nome: [] for nome in algoritmos}
            for rep in range(1, repeticoes + 1):
                entrada = gerador(n)
                for nome, funcao in algoritmos.items():
                    t = cronometra(funcao, entrada)
                    tempos[nome].append(t)
                    if not so_media:
                        linhas.append([etapa, nome, n, rep, f"{t:.7f}"])
            for nome in algoritmos:
                media = sum(tempos[nome]) / repeticoes
                if so_media:
                    linhas.append([etapa, nome, n, repeticoes, f"{media:.9f}"])
                print(f"{etapa} {nome:7s} n={n:5d} media={media * 1000:10.4f} ms")
    return linhas


def salva_maquina():
    info = [
        f"Sistema: {platform.system()} {platform.release()}",
        f"Processador: {processador()}",
        f"Nucleos logicos: {os.cpu_count()}",
        f"Memoria: {memoria()}",
        f"Python: {platform.python_version()} ({platform.python_implementation()})",
    ]
    with open(os.path.join(RAIZ, "resultados", "maquina.txt"), "w") as f:
        f.write("\n".join(info) + "\n")
    print("\n".join(info))


def processador():
    try:
        with open("/proc/cpuinfo") as f:
            for linha in f:
                if linha.startswith("model name"):
                    return linha.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or "desconhecido"


def memoria():
    try:
        with open("/proc/meminfo") as f:
            kb = int(f.readline().split()[1])
            return f"{kb / 1024 / 1024:.1f} GB"
    except OSError:
        return "desconhecida"


def main():
    gc.disable()   # desliga o coletor de lixo para ele nao interferir nas medicoes
    random.seed(42)
    os.makedirs(os.path.join(RAIZ, "resultados"), exist_ok=True)
    salva_maquina()

    linhas = medir(TAMANHOS, REPETICOES)
    with open(os.path.join(RAIZ, "resultados", "medicoes.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["etapa", "algoritmo", "n", "repeticao", "tempo_s"])
        w.writerows(linhas)

    linhas = medir(TAMANHOS_PEQUENOS, REPETICOES_PEQUENOS, so_media=True)
    with open(os.path.join(RAIZ, "resultados", "medicoes_pequenos.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["etapa", "algoritmo", "n", "repeticoes", "tempo_medio_s"])
        w.writerows(linhas)


if __name__ == "__main__":
    main()
