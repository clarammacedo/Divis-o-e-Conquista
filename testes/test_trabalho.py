"""
Bateria de testes do trabalho.

Rodar a partir da pasta raiz do projeto:
    python -m unittest discover -s testes -v

O que e testado:
  1. Todos os casos dos arquivos casos_etapa1.txt e casos_etapa2.txt,
     chamando o programa de verdade pela linha de comando (entrada padrao -> saida),
     para cada algoritmo.
  2. Testes aleatorios: as versoes de divisao e conquista (e o Kadane) tem que dar
     exatamente a mesma resposta da forca bruta em milhares de entradas pequenas.
  3. Entradas grandes / pior caso (ja ordenadas, todas no mesmo x, etc.).
"""
import math
import os
import random
import subprocess
import sys
import unittest

PASTA_TESTES = os.path.dirname(os.path.abspath(__file__))
PASTA_SRC = os.path.join(PASTA_TESTES, "..", "src")
sys.path.insert(0, PASTA_SRC)

import etapa1_subarranjo as e1   # noqa: E402
import etapa2_par_proximo as e2  # noqa: E402


def ler_casos(nome_arquivo):
    """Le o arquivo de casos e devolve lista de (nome, entrada, saida)."""
    caminho = os.path.join(PASTA_TESTES, nome_arquivo)
    casos = []
    nome = None
    modo = None
    entrada, saida = [], []
    with open(caminho, encoding="utf-8") as f:
        for linha in f:
            linha = linha.rstrip("\n")
            if linha.startswith("###"):
                if nome:
                    casos.append((nome, "\n".join(entrada) + "\n", " ".join(saida).strip()))
                nome = linha[3:].strip()
                entrada, saida, modo = [], [], None
            elif linha.startswith("#") or not linha.strip():
                continue
            elif linha.strip() == "entrada:":
                modo = "entrada"
            elif linha.strip() == "saida:":
                modo = "saida"
            elif modo == "entrada":
                entrada.append(linha)
            elif modo == "saida":
                saida.append(linha)
    if nome:
        casos.append((nome, "\n".join(entrada) + "\n", " ".join(saida).strip()))
    return casos


def rodar_programa(arquivo, algoritmo, entrada):
    resultado = subprocess.run(
        [sys.executable, os.path.join(PASTA_SRC, arquivo), algoritmo],
        input=entrada, capture_output=True, text=True, timeout=60,
    )
    if resultado.returncode != 0:
        raise RuntimeError(resultado.stderr)
    return resultado.stdout.strip()


# ======================================================================
# Etapa 1
# ======================================================================
class TestEtapa1Arquivo(unittest.TestCase):
    """Casos do arquivo, rodando o programa pela linha de comando."""

    def test_casos_do_arquivo(self):
        casos = ler_casos("casos_etapa1.txt")
        self.assertGreater(len(casos), 0)
        for nome, entrada, esperado in casos:
            for alg in ("bruta", "dc", "kadane"):
                with self.subTest(caso=nome, algoritmo=alg):
                    self.assertEqual(rodar_programa("etapa1_subarranjo.py", alg, entrada), esperado)


class TestEtapa1Aleatorio(unittest.TestCase):

    def test_dc_e_kadane_iguais_a_bruta(self):
        random.seed(1)
        for _ in range(3000):
            n = random.randint(1, 30)
            # valores pequenos -> aparecem muitos empates
            vetor = [random.randint(-5, 5) for _ in range(n)]
            esperado = e1.forca_bruta(vetor)
            self.assertEqual(e1.divisao_conquista(vetor), esperado, vetor)
            self.assertEqual(e1.kadane(vetor), esperado, vetor)

    def test_resposta_e_consistente(self):
        # a soma devolvida tem que ser a soma real do intervalo devolvido
        random.seed(2)
        for _ in range(500):
            vetor = [random.randint(-100, 100) for _ in range(random.randint(1, 200))]
            for f in (e1.forca_bruta, e1.divisao_conquista, e1.kadane):
                soma, ini, fim = f(vetor)
                self.assertTrue(0 <= ini <= fim < len(vetor))
                self.assertEqual(sum(vetor[ini:fim + 1]), soma)

    def test_vetor_grande(self):
        random.seed(3)
        vetor = [random.randint(-1000, 1000) for _ in range(20000)]
        self.assertEqual(e1.divisao_conquista(vetor), e1.kadane(vetor))

    def test_grande_so_negativos(self):
        vetor = [-random.randint(1, 1000) for _ in range(5000)]
        maior = max(vetor)
        esperado = (maior, vetor.index(maior), vetor.index(maior))
        self.assertEqual(e1.divisao_conquista(vetor), esperado)
        self.assertEqual(e1.kadane(vetor), esperado)


# ======================================================================
# Etapa 2
# ======================================================================
class TestEtapa2Arquivo(unittest.TestCase):

    def test_casos_do_arquivo(self):
        casos = ler_casos("casos_etapa2.txt")
        self.assertGreater(len(casos), 0)
        for nome, entrada, esperado in casos:
            pontos = e2.ler_entrada(entrada)
            d_esperada = float(esperado.split()[0])
            for alg in ("bruta", "dc"):
                with self.subTest(caso=nome, algoritmo=alg):
                    saida = rodar_programa("etapa2_par_proximo.py", alg, entrada).split()
                    d, i, j = float(saida[0]), int(saida[1]), int(saida[2])
                    self.assertAlmostEqual(d, d_esperada, places=6)
                    # o par devolvido tem que existir e ter essa distancia (vale para empates)
                    self.assertTrue(0 <= i < j < len(pontos))
                    real = math.dist(pontos[i], pontos[j])
                    self.assertAlmostEqual(real, d_esperada, places=6)


class TestEtapa2Aleatorio(unittest.TestCase):

    def conferir(self, pontos, limiar=None):
        d_bruta, _ = e2.forca_bruta(pontos)
        d, (i, j) = e2.divisao_conquista(pontos, limiar)
        self.assertAlmostEqual(d, d_bruta, places=9)
        self.assertAlmostEqual(math.dist(pontos[i], pontos[j]), d, places=9)

    def test_dc_igual_a_bruta(self):
        random.seed(10)
        for _ in range(1500):
            n = random.randint(2, 60)
            # faixa pequena de coordenadas -> muitos pontos repetidos / alinhados
            r = random.choice([2, 5, 50, 10**6])
            pontos = [(random.randint(0, r), random.randint(0, r)) for _ in range(n)]
            self.conferir(pontos)

    def test_varios_limiares(self):
        random.seed(11)
        for limiar in (2, 3, 4, 8, 16, 64):
            for _ in range(200):
                pontos = [(random.uniform(-10, 10), random.uniform(-10, 10))
                          for _ in range(random.randint(2, 100))]
                self.conferir(pontos, limiar)

    def test_grande_ja_ordenado(self):
        pontos = [(x, (x * 37) % 1001) for x in range(3000)]
        self.conferir(pontos)

    def test_grande_mesmo_x(self):
        pontos = [(7, 3 * y) for y in range(3000)]
        random.shuffle(pontos)
        self.assertAlmostEqual(e2.divisao_conquista(pontos)[0], 3.0)

    def test_grande_aleatorio(self):
        random.seed(12)
        pontos = [(random.randint(0, 10**6), random.randint(0, 10**6)) for _ in range(2000)]
        self.conferir(pontos)


if __name__ == "__main__":
    unittest.main()
