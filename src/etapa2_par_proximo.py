"""
Etapa 2 - Par de Pontos Mais Proximos
Aluna: Ana Clara Macedo

Duas versoes:
  - forca_bruta(pontos)        -> O(n^2)
  - divisao_conquista(pontos)  -> O(n log n)

Reaproveitei os codigos de ordenacao da disciplina:
  - quick_sort: ordena os pontos por x UMA vez, no comeco
    (coloquei pivo aleatorio para nao cair no pior caso quando a
    entrada ja vem ordenada)
  - combinacao (do merge_sort): dentro da recursao, junta as duas
    metades ja ordenadas por y em O(n). Assim nao preciso reordenar
    por y em cada nivel, e o total fica O(n log n).

Cada ponto e guardado como a tupla (x, y, indice_original).

Uso:
  python src/etapa2_par_proximo.py [bruta|dc] < entrada.txt
  Entrada: n e depois n linhas "x y"
  Saida:   distancia i j   (distancia com 6 casas; indices comecam em 0, i < j)
"""
import math
import random
import sys

sys.setrecursionlimit(10000)

# Abaixo (ou igual) desse tamanho a recursao para e usa forca bruta.
# O valor foi escolhido pelo experimento do limiar (ver relatorio).
LIMIAR = 16


def distancia(p, q):
    return math.hypot(p[0] - q[0], p[1] - q[1])


def par_ordenado(p, q):
    # devolve os indices originais com o menor primeiro
    return (p[2], q[2]) if p[2] < q[2] else (q[2], p[2])


# ----------------------------------------------------------------------
# 1) Forca bruta: compara todos os pares
# ----------------------------------------------------------------------
def bruta_lista(pts):
    melhor = math.inf
    par = None
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            d = distancia(pts[i], pts[j])
            if d < melhor:
                melhor = d
                par = par_ordenado(pts[i], pts[j])
    return melhor, par


def forca_bruta(pontos):
    pts = [(x, y, k) for k, (x, y) in enumerate(pontos)]
    return bruta_lista(pts)


# ----------------------------------------------------------------------
# quick_sort da aula, adaptado: pivo aleatorio.
# Compara tuplas (x, y, indice), entao ordena por x e desempata por y.
# ----------------------------------------------------------------------
def quick_sort(vetor, low, high):
    if low >= high:
        return

    sorteado = random.randint(low, high)          # pivo aleatorio
    vetor[sorteado], vetor[high] = vetor[high], vetor[sorteado]

    pivot = vetor[high]
    i = low
    for j in range(low, high):
        if vetor[j] < pivot:
            vetor[i], vetor[j] = vetor[j], vetor[i]
            i += 1

    vetor[i], vetor[high] = vetor[high], vetor[i]
    quick_sort(vetor, low, i - 1)
    quick_sort(vetor, i + 1, high)


# ----------------------------------------------------------------------
# combinacao do merge_sort, adaptada para comparar pela coordenada y
# (ja com o i += 1 que faltava na versao original)
# ----------------------------------------------------------------------
def combinacao_por_y(esquerda, direita):
    resultado_ordenado = []
    i = 0
    j = 0
    while i < len(esquerda) and j < len(direita):
        if esquerda[i][1] <= direita[j][1]:
            resultado_ordenado.append(esquerda[i])
            i += 1
        else:
            resultado_ordenado.append(direita[j])
            j += 1
    resultado_ordenado.extend(esquerda[i:])
    resultado_ordenado.extend(direita[j:])
    return resultado_ordenado


# ----------------------------------------------------------------------
# 2) Divisao e conquista
# ----------------------------------------------------------------------
def resolver(px, low, high, limiar):
    """px[low..high] esta ordenado por x.
    Devolve (menor distancia, par, mesmos pontos ordenados por y)."""
    n = high - low + 1

    # caso base: poucos pontos -> forca bruta
    if n <= limiar:
        pedaco = px[low:high + 1]
        d, par = bruta_lista(pedaco)
        pedaco.sort(key=lambda p: p[1])          # ordena por y (no maximo "limiar" pontos)
        return d, par, pedaco

    # DIVIDIR: linha vertical na mediana de x
    meio = (low + high) // 2
    x_meio = px[meio][0]

    # CONQUISTAR: resolve cada lado
    d_esq, par_esq, py_esq = resolver(px, low, meio, limiar)
    d_dir, par_dir, py_dir = resolver(px, meio + 1, high, limiar)

    if d_esq <= d_dir:
        delta, par = d_esq, par_esq
    else:
        delta, par = d_dir, par_dir

    # COMBINAR
    py = combinacao_por_y(py_esq, py_dir)

    # faixa de largura 2*delta em volta da linha, ja ordenada por y
    faixa = [p for p in py if abs(p[0] - x_meio) < delta]

    # cada ponto so precisa ser comparado com os proximos 7 da faixa
    for i in range(len(faixa)):
        for j in range(i + 1, min(i + 8, len(faixa))):
            if faixa[j][1] - faixa[i][1] >= delta:
                break                  # os proximos estao ainda mais longe em y
            d = distancia(faixa[i], faixa[j])
            if d < delta:
                delta = d
                par = par_ordenado(faixa[i], faixa[j])

    return delta, par, py


def divisao_conquista(pontos, limiar=None):
    if limiar is None:
        limiar = LIMIAR
    limiar = max(limiar, 2)   # com 1 ponto so nao existe par
    if len(pontos) < 2:
        raise ValueError("precisa de pelo menos 2 pontos")

    px = [(x, y, k) for k, (x, y) in enumerate(pontos)]
    quick_sort(px, 0, len(px) - 1)               # ordena por x uma vez so
    d, par, _ = resolver(px, 0, len(px) - 1, limiar)
    return d, par


# ----------------------------------------------------------------------
# Programa principal
# ----------------------------------------------------------------------
ALGORITMOS = {
    "bruta": forca_bruta,
    "dc": divisao_conquista,
}


def ler_numero(texto):
    valor = float(texto)
    return int(valor) if valor.is_integer() else valor


def ler_entrada(texto):
    partes = texto.split()
    n = int(partes[0])
    numeros = [ler_numero(t) for t in partes[1:1 + 2 * n]]
    if n < 2 or len(numeros) != 2 * n:
        raise ValueError("entrada invalida: precisa de n >= 2 e n pares x y")
    return [(numeros[2 * k], numeros[2 * k + 1]) for k in range(n)]


if __name__ == "__main__":
    nome = sys.argv[1] if len(sys.argv) > 1 else "dc"
    if nome not in ALGORITMOS:
        print("uso: python etapa2_par_proximo.py [bruta|dc] < entrada")
        sys.exit(1)

    pontos = ler_entrada(sys.stdin.read())
    d, (i, j) = ALGORITMOS[nome](pontos)
    print(f"{d:.6f} {i} {j}")
