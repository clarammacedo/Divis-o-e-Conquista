"""
Experimento para escolher o LIMIAR da Etapa 2.

Na divisao e conquista do par mais proximo, quando o subproblema tem
n <= LIMIAR pontos a recursao para e usa a forca bruta. Aqui eu testo
varios limiares com n = 6400 pontos (o maior tamanho do trabalho) e com
n = 1600, sempre com 20 execucoes (mais que o minimo de 5, porque as diferencas sao pequenas) e as MESMAS entradas para todos os limiares.

Saida: resultados/medicoes_limiar.csv
Rodar da pasta raiz:  python experimentos/experimento_limiar.py
"""
import csv
import os
import random
import sys
import gc
import time

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(RAIZ, "src"))
import etapa2_par_proximo as e2  # noqa: E402

LIMIARES = [2, 3, 4, 5, 6, 8, 12, 16, 24, 32, 48, 64, 128]
TAMANHOS = [1600, 6400]
REPETICOES = 20


def main():
    gc.disable()   # desliga o coletor de lixo para ele nao interferir nas medicoes
    random.seed(2026)
    linhas = []
    for n in TAMANHOS:
        entradas = [[(random.uniform(0, 10**6), random.uniform(0, 10**6)) for _ in range(n)]
                    for _ in range(REPETICOES)]
        # as repeticoes ficam "intercaladas" (rep 1 de todos os limiares, depois rep 2...)
        # para que uma oscilacao da maquina num momento nao prejudique so um limiar
        tempos = {limiar: [] for limiar in LIMIARES}
        for rep, pontos in enumerate(entradas, start=1):
            for limiar in LIMIARES:
                inicio = time.perf_counter()
                e2.divisao_conquista(pontos, limiar)
                tempo = time.perf_counter() - inicio
                tempos[limiar].append(tempo)
                linhas.append(["etapa2", "dc", n, limiar, rep, f"{tempo:.6f}"])
        for limiar in LIMIARES:
            media = sum(tempos[limiar]) / REPETICOES
            print(f"n={n:5d} limiar={limiar:4d} media={media * 1000:8.2f} ms")

    os.makedirs(os.path.join(RAIZ, "resultados"), exist_ok=True)
    with open(os.path.join(RAIZ, "resultados", "medicoes_limiar.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["etapa", "algoritmo", "n", "limiar", "repeticao", "tempo_s"])
        w.writerows(linhas)


if __name__ == "__main__":
    main()
