"""
Gera as tabelas-resumo e os graficos a partir dos CSVs de resultados/.

Rodar da pasta raiz (depois dos experimentos):
    python experimentos/graficos.py
"""
import csv
import math
import os
import statistics
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RES = os.path.join(RAIZ, "resultados")

# cores e marcadores fixos por algoritmo (a mesma cor em todos os graficos)
ESTILO = {
    "bruta": {"cor": "#eb6834", "marcador": "s", "nome": "Força bruta"},
    "dc": {"cor": "#2a78d6", "marcador": "o", "nome": "Divisão e conquista"},
    "kadane": {"cor": "#1baf7a", "marcador": "^", "nome": "Kadane O(n)"},
}
TINTA = "#52514e"

plt.rcParams.update({
    "font.size": 10,
    "axes.edgecolor": "#c3c2b7",
    "axes.labelcolor": TINTA,
    "xtick.color": TINTA,
    "ytick.color": TINTA,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": "#e6e5e0",
    "grid.linewidth": 0.6,
    "legend.frameon": False,
    "lines.linewidth": 2,
    "lines.markersize": 6,
})


def ler_medicoes():
    dados = defaultdict(list)   # (etapa, alg, n) -> [tempos]
    with open(os.path.join(RES, "medicoes.csv")) as f:
        for linha in csv.DictReader(f):
            dados[(linha["etapa"], linha["algoritmo"], int(linha["n"]))].append(float(linha["tempo_s"]))
    return dados


def inclinacao_loglog(ns, ts):
    # minimos quadrados em log2(t) x log2(n): inclinacao ~ expoente de n
    xs = [math.log2(n) for n in ns]
    ys = [math.log2(t) for t in ts]
    mx, my = statistics.mean(xs), statistics.mean(ys)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)


def previsto(alg, n):
    if alg == "bruta":
        return n * n
    if alg == "dc":
        return n * math.log2(n)
    return n


def resumo(dados):
    linhas = []
    for (etapa, alg, n), tempos in sorted(dados.items()):
        linhas.append([etapa, alg, n, len(tempos),
                       f"{statistics.mean(tempos) * 1000:.4f}",
                       f"{statistics.stdev(tempos) * 1000:.4f}"])
    with open(os.path.join(RES, "resumo_medias.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["etapa", "algoritmo", "n", "execucoes", "media_ms", "desvio_padrao_ms"])
        w.writerows(linhas)


def grafico_tempos(dados, etapa, algs, titulo, arquivo):
    fig, ax = plt.subplots(figsize=(6.4, 3.9))
    texto_inclinacoes = []
    for alg in algs:
        ns = sorted(n for (e, a, n) in dados if e == etapa and a == alg)
        ts = [statistics.mean(dados[(etapa, alg, n)]) * 1000 for n in ns]
        s = ESTILO[alg]
        incl = inclinacao_loglog(ns, ts)
        texto_inclinacoes.append((alg, incl))
        ax.plot(ns, ts, color=s["cor"], marker=s["marcador"],
                label=f"{s['nome']}  (inclinação {incl:.2f})")
        ax.annotate(s["nome"], (ns[-1], ts[-1]), xytext=(6, 0), textcoords="offset points",
                    va="center", fontsize=9, color=TINTA)
    ax.set_xscale("log", base=2)
    ax.set_yscale("log")
    ax.set_xticks(ns)
    ax.set_xticklabels([str(n) for n in ns])
    ax.set_xlim(ns[0] * 0.85, ns[-1] * 2.6)
    ax.set_xlabel("n (tamanho da entrada)")
    ax.set_ylabel("tempo médio (ms, escala log)")
    ax.set_title(titulo, fontsize=11, loc="left", color="#0b0b0b")
    ax.legend(loc="upper left", fontsize=8.5)
    fig.tight_layout()
    fig.savefig(os.path.join(RES, arquivo), dpi=200)
    plt.close(fig)
    return texto_inclinacoes


def grafico_razao(dados, arquivo):
    """tempo / complexidade prevista, normalizado para 1 em n = 100.
    Se a analise estiver certa, a curva fica perto de 1 (horizontal)."""
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.2), sharey=True)
    for ax, etapa, algs in ((axs[0], "etapa1", ["bruta", "dc", "kadane"]),
                            (axs[1], "etapa2", ["bruta", "dc"])):
        for alg in algs:
            ns = sorted(n for (e, a, n) in dados if e == etapa and a == alg)
            r = [statistics.mean(dados[(etapa, alg, n)]) / previsto(alg, n) for n in ns]
            r = [x / r[0] for x in r]
            s = ESTILO[alg]
            rotulo = {"bruta": "t / n²", "dc": "t / (n log n)", "kadane": "t / n"}[alg]
            ax.plot(ns, r, color=s["cor"], marker=s["marcador"], label=f"{s['nome']}: {rotulo}")
        ax.axhline(1, color="#9c9b94", linewidth=1, linestyle="--")
        ax.set_xscale("log", base=2)
        ax.set_xticks(ns)
        ax.set_xticklabels([str(n) for n in ns], fontsize=8)
        ax.set_ylim(0, 2)
        ax.set_title("Etapa 1" if etapa == "etapa1" else "Etapa 2", fontsize=10, loc="left")
        ax.set_xlabel("n")
        ax.legend(fontsize=7.5, loc="upper right")
    axs[0].set_ylabel("razão normalizada (n=100 → 1)")
    fig.tight_layout()
    fig.savefig(os.path.join(RES, arquivo), dpi=200)
    plt.close(fig)


def grafico_pequenos(arquivo):
    dados = defaultdict(dict)
    with open(os.path.join(RES, "medicoes_pequenos.csv")) as f:
        for linha in csv.DictReader(f):
            dados[(linha["etapa"], linha["algoritmo"])][int(linha["n"])] = float(linha["tempo_medio_s"]) * 1e6
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.2))
    for ax, etapa, algs in ((axs[0], "etapa1", ["bruta", "dc"]), (axs[1], "etapa2", ["bruta", "dc"])):
        for alg in algs:
            ns = sorted(dados[(etapa, alg)])
            s = ESTILO[alg]
            ax.plot(ns, [dados[(etapa, alg)][n] for n in ns], color=s["cor"], marker=s["marcador"],
                    label=s["nome"])
        ax.set_xscale("log", base=2)
        ax.set_yscale("log")
        ax.set_xticks(ns)
        ax.set_xticklabels([str(n) for n in ns], fontsize=8)
        ax.set_xlabel("n")
        ax.set_title("Etapa 1" if etapa == "etapa1" else "Etapa 2", fontsize=10, loc="left")
        ax.legend(fontsize=8, loc="upper left")
    axs[0].set_ylabel("tempo médio (µs, escala log)")
    fig.tight_layout()
    fig.savefig(os.path.join(RES, arquivo), dpi=200)
    plt.close(fig)


def grafico_limiar(arquivo):
    dados = defaultdict(list)
    with open(os.path.join(RES, "medicoes_limiar.csv")) as f:
        for linha in csv.DictReader(f):
            dados[(int(linha["n"]), int(linha["limiar"]))].append(float(linha["tempo_s"]))
    tamanhos = sorted({n for n, _ in dados})
    limiares = sorted({l for _, l in dados})
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    cores = {tamanhos[0]: "#2a78d6", tamanhos[-1]: "#eb6834"}
    marc = {tamanhos[0]: "o", tamanhos[-1]: "s"}
    tabela = []
    for n in tamanhos:
        medias = [statistics.mean(dados[(n, l)]) for l in limiares]
        melhor = min(medias)
        ax.plot(limiares, [m / melhor for m in medias], color=cores[n], marker=marc[n],
                label=f"n = {n}  (melhor: {melhor * 1000:.1f} ms)")
        for l, m in zip(limiares, medias):
            tabela.append([n, l, f"{m * 1000:.2f}", f"{m / melhor:.3f}"])
    ax.axvline(16, color="#9c9b94", linewidth=1, linestyle="--")
    ax.annotate("limiar escolhido = 16", (16, 2.1), xytext=(5, 0), textcoords="offset points",
                fontsize=8.5, color=TINTA)
    ax.set_xscale("log", base=2)
    ax.set_xticks(limiares)
    ax.set_xticklabels([str(l) for l in limiares], fontsize=8)
    ax.set_xlabel("limiar (n ≤ limiar → força bruta)")
    ax.set_ylabel("tempo / melhor tempo")
    ax.legend(fontsize=8.5, loc="upper left")
    fig.tight_layout()
    fig.savefig(os.path.join(RES, arquivo), dpi=200)
    plt.close(fig)
    with open(os.path.join(RES, "resumo_limiar.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["n", "limiar", "media_ms", "relativo_ao_melhor"])
        w.writerows(tabela)


if __name__ == "__main__":
    dados = ler_medicoes()
    resumo(dados)
    print(grafico_tempos(dados, "etapa1", ["bruta", "dc", "kadane"],
                         "Etapa 1 – Subarranjo de soma máxima", "grafico_etapa1.png"))
    print(grafico_tempos(dados, "etapa2", ["bruta", "dc"],
                         "Etapa 2 – Par de pontos mais próximos", "grafico_etapa2.png"))
    grafico_razao(dados, "grafico_razao.png")
    grafico_pequenos("grafico_n_pequeno.png")
    grafico_limiar("grafico_limiar.png")
    print("graficos salvos em resultados/")
