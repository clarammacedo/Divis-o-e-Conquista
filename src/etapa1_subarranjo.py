"""
Etapa 1 - Subarranjo de Soma Maxima
Aluna: Ana Clara Macedo

Tres versoes:
  - forca_bruta(vetor)        -> O(n^2)
  - divisao_conquista(vetor)  -> O(n log n)  (mesma ideia do merge sort)
  - kadane(vetor)             -> O(n)        (questao desafio)

Todas devolvem (soma, inicio, fim), com indices comecando em 0.

Regra de desempate (igual nas 3 versoes):
  se dois intervalos tem a mesma soma, ganha o de MENOR inicio;
  se o inicio tambem empatar, ganha o de MENOR fim (o mais curto).

Uso:
  python src/etapa1_subarranjo.py [bruta|dc|kadane] < entrada.txt
  Entrada: n e depois os n inteiros (podem estar em linhas diferentes)
  Saida:   soma inicio fim
"""
import sys


# ----------------------------------------------------------------------
# 1) Forca bruta: testa todos os intervalos [i, j]
# ----------------------------------------------------------------------
def forca_bruta(vetor):
    n = len(vetor)
    melhor_soma = vetor[0]
    melhor_ini = 0
    melhor_fim = 0

    for i in range(n):
        soma = 0
        for j in range(i, n):
            soma += vetor[j]          # soma de vetor[i..j] aproveitando a anterior
            # ">" estrito: como i e j crescem, o primeiro maximo encontrado
            # ja e o de menor inicio e menor fim (regra de desempate)
            if soma > melhor_soma:
                melhor_soma = soma
                melhor_ini = i
                melhor_fim = j

    return melhor_soma, melhor_ini, melhor_fim


# ----------------------------------------------------------------------
# 2) Divisao e conquista
#    Mesmo esqueleto do merge_sort: divide no meio, resolve as duas
#    metades e "combina". So que aqui a combinacao e achar o melhor
#    subarranjo que CRUZA o meio.
# ----------------------------------------------------------------------
def melhor_cruzando(vetor, low, meio, high):
    # parte da esquerda: comeca em meio e vai voltando ate low
    soma = 0
    soma_esq = None
    ini = meio
    for i in range(meio, low - 1, -1):
        soma += vetor[i]
        # ">=" porque, se empatar, quero o inicio mais a esquerda
        if soma_esq is None or soma >= soma_esq:
            soma_esq = soma
            ini = i

    # parte da direita: comeca em meio+1 e vai ate high
    soma = 0
    soma_dir = None
    fim = meio + 1
    for j in range(meio + 1, high + 1):
        soma += vetor[j]
        # ">" porque, se empatar, quero o fim mais a esquerda (mais curto)
        if soma_dir is None or soma > soma_dir:
            soma_dir = soma
            fim = j

    return soma_esq + soma_dir, ini, fim


def melhor_dos_tres(a, b, c):
    # escolhe a maior soma; no empate, menor inicio e depois menor fim
    melhor = a
    for candidato in (b, c):
        if (candidato[0] > melhor[0]
                or (candidato[0] == melhor[0] and (candidato[1], candidato[2]) < (melhor[1], melhor[2]))):
            melhor = candidato
    return melhor


def dc_recursivo(vetor, low, high):
    if low == high:                       # caso base: 1 elemento
        return vetor[low], low, low

    meio = (low + high) // 2
    esquerda = dc_recursivo(vetor, low, meio)
    direita = dc_recursivo(vetor, meio + 1, high)
    cruzando = melhor_cruzando(vetor, low, meio, high)

    return melhor_dos_tres(esquerda, cruzando, direita)


def divisao_conquista(vetor):
    return dc_recursivo(vetor, 0, len(vetor) - 1)


# ----------------------------------------------------------------------
# 3) Questao desafio - Kadane, O(n)
#    Guarda a melhor soma de um subarranjo que TERMINA na posicao j.
# ----------------------------------------------------------------------
def kadane(vetor):
    melhor_soma = vetor[0]
    melhor_ini = 0
    melhor_fim = 0

    soma_atual = vetor[0]   # melhor soma terminando em j
    ini_atual = 0

    for j in range(1, len(vetor)):
        # se o que eu tenho ate agora e negativo, e melhor comecar de novo em j.
        # Se for exatamente 0, continuo (assim o inicio fica mais a esquerda)
        if soma_atual >= 0:
            soma_atual += vetor[j]
        else:
            soma_atual = vetor[j]
            ini_atual = j

        if soma_atual > melhor_soma:
            melhor_soma = soma_atual
            melhor_ini = ini_atual
            melhor_fim = j

    return melhor_soma, melhor_ini, melhor_fim


# ----------------------------------------------------------------------
# Leitura da entrada / programa principal
# ----------------------------------------------------------------------
ALGORITMOS = {
    "bruta": forca_bruta,
    "dc": divisao_conquista,
    "kadane": kadane,
}


def ler_entrada(texto):
    numeros = texto.split()
    n = int(numeros[0])
    vetor = [int(x) for x in numeros[1:1 + n]]
    if n < 1 or len(vetor) != n:
        raise ValueError("entrada invalida: precisa de n >= 1 e n numeros")
    return vetor


if __name__ == "__main__":
    nome = sys.argv[1] if len(sys.argv) > 1 else "dc"
    if nome not in ALGORITMOS:
        print("uso: python etapa1_subarranjo.py [bruta|dc|kadane] < entrada")
        sys.exit(1)

    vetor = ler_entrada(sys.stdin.read())
    soma, inicio, fim = ALGORITMOS[nome](vetor)
    print(soma, inicio, fim)
