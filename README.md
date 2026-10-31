# Trabalho Prático – Divisão e Conquista

**Aluna:** Ana Clara Macedo (trabalho individual)
**Linguagem:** Python 3 (testado no 3.13; não usa nenhuma biblioteca externa, só o matplotlib para os gráficos)

## Estrutura

```
src/
  etapa1_subarranjo.py     # Etapa 1: força bruta O(n²), divisão e conquista O(n log n), Kadane O(n)
  etapa2_par_proximo.py    # Etapa 2: força bruta O(n²), divisão e conquista O(n log n)
testes/
  casos_etapa1.txt         # casos de teste da Etapa 1 (entrada + saída esperada + justificativa)
  casos_etapa2.txt         # casos de teste da Etapa 2
  test_trabalho.py         # bateria de testes automática (unittest)
experimentos/
  experimento_limiar.py    # escolhe o limiar da Etapa 2
  experimentos.py          # mede os tempos (Etapa 3)
  graficos.py              # gera tabelas-resumo e gráficos
resultados/
  medicoes.csv             # medições brutas (5 execuções por tamanho)
  medicoes_pequenos.csv    # tamanhos pequenos (2 a 128), média de 300 execuções
  medicoes_limiar.csv      # medições do experimento do limiar
  resumo_medias.csv        # média e desvio padrão por tamanho
  maquina.txt              # configuração da máquina usada
  *.png                    # gráficos
relatorio/
  relatorio.pdf
```

## Como executar

Todos os comandos são rodados na pasta raiz do projeto.

### Etapa 1 – Subarranjo de soma máxima

Entrada: `n` e depois os `n` inteiros. Saída: `soma inicio fim` (índices começam em **0**).

```
python src/etapa1_subarranjo.py dc      < entrada.txt    # divisão e conquista (padrão)
python src/etapa1_subarranjo.py bruta   < entrada.txt    # força bruta
python src/etapa1_subarranjo.py kadane  < entrada.txt    # O(n)
```

Exemplo:
```
$ echo "6  -1 -2 5 6 -3 -4" | python src/etapa1_subarranjo.py
11 2 3
```

Regra de desempate: se dois intervalos têm a mesma soma, vale o de **menor início**; se o início também empatar, vale o de **menor fim**.

### Etapa 2 – Par de pontos mais próximos

Entrada: `n` e depois `n` linhas `x y` (inteiros ou decimais). Saída: `distancia i j` (6 casas decimais, índices dos pontos na ordem da entrada, começando em 0, com `i < j`).

```
python src/etapa2_par_proximo.py dc     < pontos.txt
python src/etapa2_par_proximo.py bruta  < pontos.txt
```

O limiar (abaixo dele a recursão usa força bruta) é a constante `LIMIAR = 16` no começo do arquivo.

### Testes

```
python -m unittest discover -s testes -v
```

Roda os casos dos arquivos `casos_etapa*.txt` chamando os programas pela linha de comando, compara divisão e conquista e Kadane com a força bruta em milhares de entradas aleatórias e testa entradas grandes (já ordenadas, todos os pontos no mesmo x etc.).

### Experimentos e gráficos

```
pip install -r requirements.txt
python experimentos/experimento_limiar.py   # ~1 min
python experimentos/experimentos.py         # ~30 s
python experimentos/graficos.py
python relatorio/gerar_relatorio.py         # gera relatorio/relatorio.pdf
```

## Máquina usada nas medições

Ver `resultados/maquina.txt`: Linux, Intel Xeon @ 2.10 GHz (2 núcleos lógicos), 7,8 GB de RAM, CPython 3.13.

## Observação sobre os códigos de ordenação

O trabalho não é de ordenação, mas reaproveitei os códigos feitos em aula:
- a estrutura do `merge_sort` (divide no meio → resolve as metades → combina) é a base das duas divisões e conquistas;
- a função `combinacao` do merge sort (corrigida, faltava o `i += 1`) junta as listas ordenadas por y na Etapa 2;
- o `quick_sort` (com pivô aleatório) faz a ordenação inicial dos pontos por x.
