"""Gera o relatorio.pdf a partir dos resultados (rodar da pasta raiz:
python relatorio/gerar_relatorio.py)."""
import csv
import os
from collections import defaultdict

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, KeepTogether, Paragraph, Preformatted,
                                SimpleDocTemplate, Spacer, Table, TableStyle)

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RES = os.path.join(RAIZ, "resultados")

F = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("Serif", F + "DejaVuSerif.ttf"))
pdfmetrics.registerFont(TTFont("Serif-B", F + "DejaVuSerif-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Serif-I", F + "DejaVuSerif-Italic.ttf"))
pdfmetrics.registerFont(TTFont("Serif-BI", F + "DejaVuSerif-BoldItalic.ttf"))
pdfmetrics.registerFont(TTFont("Mono", F + "DejaVuSansMono.ttf"))
from reportlab.pdfbase.pdfmetrics import registerFontFamily  # noqa: E402
registerFontFamily("Serif", normal="Serif", bold="Serif-B", italic="Serif-I", boldItalic="Serif-BI")

corpo = ParagraphStyle("corpo", fontName="Serif", fontSize=9.6, leading=13.4,
                       alignment=TA_JUSTIFY, spaceAfter=5)
titulo = ParagraphStyle("titulo", fontName="Serif-B", fontSize=15, leading=19,
                        alignment=TA_CENTER, spaceAfter=3)
sub = ParagraphStyle("sub", fontName="Serif", fontSize=9.6, leading=13, alignment=TA_CENTER,
                     textColor=colors.HexColor("#444444"))
h1 = ParagraphStyle("h1", fontName="Serif-B", fontSize=12, leading=15, spaceBefore=9, spaceAfter=4, keepWithNext=1)
h2 = ParagraphStyle("h2", fontName="Serif-B", fontSize=10.2, leading=13, spaceBefore=6, spaceAfter=3, keepWithNext=1)
legenda = ParagraphStyle("legenda", parent=corpo, fontSize=8.3, leading=11, alignment=TA_CENTER,
                         textColor=colors.HexColor("#444444"), spaceAfter=8)
celula = ParagraphStyle("celula", fontName="Serif", fontSize=8, leading=10)
item = ParagraphStyle("item", parent=corpo, leftIndent=12, bulletIndent=2, spaceAfter=2)
codigo = ParagraphStyle("codigo", fontName="Mono", fontSize=7.8, leading=9.6,
                        backColor=colors.HexColor("#f4f4f2"), borderPadding=4,
                        leftIndent=6, rightIndent=6, spaceBefore=3, spaceAfter=8)

S = []


def p(texto, estilo=corpo):
    S.append(Paragraph(texto, estilo))


def bullets(itens):
    for t in itens:
        S.append(Paragraph(t, item, bulletText="•"))
    S.append(Spacer(1, 3))


def figura(arquivo, largura_cm, texto):
    from reportlab.lib.utils import ImageReader
    caminho = os.path.join(RES, arquivo)
    w, h = ImageReader(caminho).getSize()
    larg = largura_cm * cm
    S.append(KeepTogether([Image(caminho, width=larg, height=larg * h / w),
                           Paragraph(texto, legenda)]))


def tabela(dados, larguras, cab=1):
    t = Table(dados, colWidths=larguras, hAlign="CENTER", repeatRows=cab)
    t.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, -1), "Serif", 8),
        ("FONT", (0, 0), (-1, cab - 1), "Serif-B", 8),
        ("LINEABOVE", (0, 0), (-1, 0), 0.8, colors.black),
        ("LINEBELOW", (0, cab - 1), (-1, cab - 1), 0.5, colors.black),
        ("LINEBELOW", (0, -1), (-1, -1), 0.8, colors.black),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 1.6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.6),
    ]))
    return t


# ---------------------------------------------------------------- dados
medias = {}
with open(os.path.join(RES, "resumo_medias.csv")) as f:
    for r in csv.DictReader(f):
        medias[(r["etapa"], r["algoritmo"], int(r["n"]))] = (float(r["media_ms"]), float(r["desvio_padrao_ms"]))
NS = sorted({k[2] for k in medias})

limiar = defaultdict(dict)
with open(os.path.join(RES, "resumo_limiar.csv")) as f:
    for r in csv.DictReader(f):
        limiar[int(r["n"])][int(r["limiar"])] = (float(r["media_ms"]), float(r["relativo_ao_melhor"]))

maquina = open(os.path.join(RES, "maquina.txt")).read().strip().split("\n")


def fmt(v):
    if v >= 100:
        return f"{v:,.0f}".replace(",", ".")
    if v >= 10:
        return f"{v:.1f}".replace(".", ",")
    if v >= 1:
        return f"{v:.2f}".replace(".", ",")
    return f"{v:.3f}".replace(".", ",")


def br(x, casas=2):
    return f"{x:.{casas}f}".replace(".", ",")


def razao_dobra(etapa, alg):
    vals = [medias[(etapa, alg, n)][0] for n in NS]
    rs = [vals[i + 1] / vals[i] for i in range(len(vals) - 1)]
    return sum(rs) / len(rs)


# ---------------------------------------------------------------- texto
p("Trabalho Prático: Divisão e Conquista", titulo)
p("Projeto e Análise de Algoritmos – Relatório<br/>Ana Clara Macedo (trabalho individual)", sub)
S.append(Spacer(1, 10))

p("1. Introdução", h1)
p("Neste trabalho implementei, em Python, dois problemas resolvidos com a técnica de divisão e conquista "
  "(subarranjo de soma máxima e par de pontos mais próximos) e comparei cada um com a solução de força bruta. "
  "Para a Etapa 1 também fiz a versão O(n) (algoritmo de Kadane), que é a questão desafio. "
  "Depois medi os tempos para entradas de tamanhos crescentes e comparei com o que as recorrências preveem.")
p("Mesmo os problemas não sendo de ordenação, usei como base os códigos de <i>merge sort</i> e <i>quick sort</i> "
  "feitos em aula. A estrutura do <i>merge sort</i> (dividir no meio, resolver as duas metades e combinar) é "
  "o molde das duas soluções. A função <font name='Mono'>combinacao</font> dele é usada na Etapa 2 para intercalar "
  "os pontos por y, e o <i>quick sort</i> faz a ordenação inicial dos pontos por x. "
  "Antes de reaproveitar, corrigi um erro do meu <i>merge sort</i>: faltava o <font name='Mono'>i += 1</font> na "
  "função de combinação, o que causava um laço infinito.")

# ---------------------------------------------------------------- etapa 1
p("2. Etapa 1: Subarranjo de Soma Máxima", h1)
p("Dado um vetor com as variações diárias de uma ação, queremos o intervalo contínuo [i, j] com a maior soma. "
  "A entrada é n seguido dos n inteiros e a saída é <font name='Mono'>soma inicio fim</font>, com índices a partir de 0. "
  "Como o intervalo não pode ser vazio, se todos os valores forem negativos a resposta é o maior deles sozinho.")
p("<b>Regra de desempate.</b> Quando dois intervalos têm a mesma soma, escolhi devolver o de <b>menor início</b> e, "
  "se o início também empatar, o de <b>menor fim</b>. As três versões seguem essa mesma regra, então elas "
  "devolvem exatamente a mesma resposta (isso é verificado nos testes).")

p("2.1 Força bruta – O(n<super>2</super>)", h2)
p("Dois laços: para cada início i, o laço interno anda com j de i até n−1 acumulando a soma (aproveito a soma "
  "de [i, j−1] para calcular [i, j] em O(1)). O número de intervalos testados é "
  "n + (n−1) + … + 1 = n(n+1)/2, então T(n) = Θ(n<super>2</super>). "
  "Atualizando só quando a soma é <i>estritamente</i> maior, o primeiro máximo encontrado já obedece à regra de desempate.")

p("2.2 Divisão e conquista – O(n log n)", h2)
p("É o mesmo esqueleto do <i>merge sort</i>: divido o vetor em [low, meio] e [meio+1, high], resolvo cada metade "
  "recursivamente e, no lugar da intercalação, calculo o melhor subarranjo que <b>cruza o meio</b>. Para isso "
  "ando do meio para a esquerda guardando a maior soma de [i, meio], e do meio+1 para a direita guardando a maior "
  "soma de [meio+1, j]. O intervalo que cruza é a junção dos dois, e isso custa O(n). A resposta é a melhor "
  "das três (esquerda, cruzando, direita). Para manter o desempate, no lado esquerdo uso <font name='Mono'>&gt;=</font> "
  "(prefiro o início mais à esquerda) e no lado direito uso <font name='Mono'>&gt;</font> (prefiro o fim mais à esquerda).")
p("<b>Recorrência:</b> T(1) = Θ(1) e T(n) = 2T(n/2) + Θ(n). Pelo Teorema Mestre, a = 2, b = 2 e f(n) = Θ(n) = "
  "Θ(n<super>log<sub>2</sub>2</super>), que é o caso 2, então <b>T(n) = Θ(n log n)</b>. Pela árvore de recursão "
  "dá para ver a mesma coisa: são log<sub>2</sub> n níveis e, em cada nível, os pedaços somam n elementos, "
  "ou seja, cn de trabalho por nível.")

p("2.3 Questão desafio: Kadane – O(n)", h2)
p("Mantenho a melhor soma de um subarranjo que <i>termina</i> na posição j. Na posição j+1 só há duas opções: "
  "estender esse subarranjo ou começar um novo em j+1. Estender só vale a pena se a soma atual for ≥ 0 (com "
  "o “=” o início fica mais à esquerda, que é a regra de desempate). Cada elemento é visto uma vez, então "
  "T(n) = T(n−1) + Θ(1) = <b>Θ(n)</b>. Um erro comum é começar a melhor soma em 0, o que dá resposta errada "
  "quando todos os valores são negativos. Por isso a variável começa em vetor[0].")

# ---------------------------------------------------------------- etapa 2
p("3. Etapa 2: Par de Pontos Mais Próximos", h1)
p("A entrada é n seguido de n linhas <font name='Mono'>x y</font>, e a saída é <font name='Mono'>distancia i j</font>, "
  "com os índices das duas estações na ordem da entrada. Cada ponto é guardado como a tupla (x, y, índice), "
  "o que também resolve empates na ordenação, porque não existem duas tuplas iguais.")
p("3.1 Força bruta – O(n<super>2</super>)", h2)
p("Compara todos os n(n−1)/2 pares e guarda a menor distância, então T(n) = Θ(n<super>2</super>).")

p("3.2 Divisão e conquista – O(n log n)", h2)
bullets([
    "<b>Pré-processamento:</b> ordeno os pontos por x uma única vez com o <i>quick sort</i> da aula. Mudei só o pivô, "
    "que agora é sorteado: com o pivô fixo no último elemento, uma entrada já ordenada cairia no pior caso O(n<super>2</super>) "
    "e estouraria a pilha de recursão do Python. Com pivô aleatório o custo esperado é O(n log n).",
    "<b>Dividir:</b> a linha vertical passa pelo ponto da mediana (posição meio do vetor ordenado por x).",
    "<b>Conquistar:</b> resolvo cada lado e obtenho δ = min(δ<sub>esq</sub>, δ<sub>dir</sub>). Se o subproblema tem "
    "n ≤ LIMIAR pontos, uso a força bruta.",
    "<b>Combinar:</b> cada chamada devolve também os seus pontos <b>ordenados por y</b>, e junto as duas listas com a "
    "<font name='Mono'>combinacao</font> do <i>merge sort</i> (adaptada para comparar o y) em O(n). Depois filtro a faixa "
    "|x − x<sub>meio</sub>| &lt; δ, que já sai ordenada por y, e comparo cada ponto da faixa com no máximo os "
    "<b>7 seguintes</b>, parando antes se a diferença em y já for ≥ δ.",
])
p("Usar a intercalação em vez de reordenar a faixa por y em cada chamada é o que deixa o algoritmo em "
  "O(n log n). Se eu ordenasse a faixa toda vez, a combinação custaria O(n log n) e o total seria O(n log<super>2</super> n).")
p("<b>Recorrência:</b> T(n) = Θ(1) para n ≤ LIMIAR (o limiar é uma constante, então a força bruta na folha custa "
  "no máximo LIMIAR<super>2</super>/2 comparações) e T(n) = 2T(n/2) + Θ(n), em que o Θ(n) é a intercalação por y, o filtro da faixa "
  "e as no máximo 7·|faixa| comparações. Pelo caso 2 do Teorema Mestre, T(n) = Θ(n log n). Somando a "
  "ordenação inicial por x, que custa O(n log n) esperado, o total continua <b>Θ(n log n)</b>.")

p("3.3 Por que bastam 7 comparações por ponto na faixa", h2)
p("Seja p um ponto da faixa e considere os pontos q com y<sub>p</sub> ≤ y<sub>q</sub> &lt; y<sub>p</sub> + δ (os únicos "
  "que ainda podem estar a menos de δ de p e vêm depois dele na ordem por y). Todos eles ficam dentro de um retângulo "
  "de largura 2δ (δ de cada lado da linha) e altura δ. Divido esse retângulo em <b>8 quadrados de lado δ/2</b>, "
  "4 do lado esquerdo e 4 do direito. A diagonal de cada quadrado mede δ/√2 &lt; δ, então dois pontos do mesmo lado "
  "dentro do mesmo quadrado estariam a menos de δ um do outro. Isso é impossível, porque δ já é a menor distância "
  "dentro de cada lado. Logo, cada quadrado tem no máximo um ponto, o retângulo tem no máximo 8 pontos contando "
  "o próprio p, e sobram <b>no máximo 7 outros</b>. Por isso basta comparar p com os 7 pontos seguintes da faixa "
  "ordenada por y. No código o laço vai até i+7 e ainda para antes quando y<sub>q</sub> − y<sub>p</sub> ≥ δ.")

# ---------------------------------------------------------------- testes
p("4. Testes", h1)
p("Os casos de teste ficam em <font name='Mono'>testes/casos_etapa1.txt</font> (17 casos) e "
  "<font name='Mono'>testes/casos_etapa2.txt</font> (11 casos), cada um com entrada, saída esperada e uma linha "
  "explicando por que o caso existe. O arquivo <font name='Mono'>test_trabalho.py</font> roda cada caso chamando o "
  "programa pela linha de comando, para testar também a leitura da entrada e o formato da saída, com todas "
  "as versões. Os principais casos de borda e a justificativa de cada um:")
borda = [
    ["Caso", "Por que testar"],
    ["E1: n = 1 (positivo e negativo)", "caso base da recursão; com valor negativo a resposta não pode virar 0"],
    ["E1: só negativos (com e sem empate)", "resposta é o maior elemento sozinho; pega o erro de começar a soma em 0"],
    ["E1: empates (intervalos separados, mesmo início, zeros)", "verifica a regra de desempate igual nas 3 versões"],
    ["E1: máximo cruzando o meio / nas pontas", "testa a função de cruzamento e os limites do vetor"],
    ["E1: valores grandes", "soma passa de 32 bits (em C/Java daria overflow)"],
    ["E2: n = 2 e n = 3", "menor entrada possível; caso base direto"],
    ["E2: pontos repetidos", "distância 0, faixa vazia (δ = 0) não pode quebrar"],
    ["E2: par cruzando a linha", "só a etapa da faixa encontra a resposta"],
    ["E2: todos com o mesmo x / mesmo y", "a faixa contém todos os pontos; testa o limite de 7 vizinhos"],
    ["E2: grade 3×3, negativos e decimais", "muitos empates; leitura de valores não inteiros"],
    ["E2: entrada já ordenada por x", "seria o pior caso do quick sort sem pivô aleatório"],
]
S.append(tabela([[Paragraph(c, celula) for c in linha] for linha in borda], [6.4 * cm, 9.6 * cm]))
S.append(Spacer(1, 6))
p("Além disso, há testes aleatórios. A divisão e conquista e o Kadane são comparados com a força bruta em 3.000 vetores "
  "pequenos com valores entre −5 e 5 (para forçar muitos empates), e a Etapa 2 em 1.500 conjuntos de pontos com "
  "coordenadas em faixas pequenas (muitos pontos repetidos e alinhados) e com limiares de 2 a 64. Também há "
  "entradas grandes (até 20.000 elementos, 3.000 pontos já ordenados ou todos no mesmo x). Todos os testes passam.")

# ---------------------------------------------------------------- experimentos
p("5. Análise Experimental", h1)
p("<b>Máquina:</b> " + "; ".join(maquina) + ". "
  "<b>Metodologia:</b> para cada n ∈ {100, 200, …, 6400} fiz 5 execuções. Cada execução usa uma entrada aleatória "
  "nova (inteiros em [−1000, 1000] ou pontos com coordenadas reais em [0, 10<super>6</super>]), e a mesma entrada é "
  "dada a todos os algoritmos. Medi com <font name='Mono'>time.perf_counter()</font> e com o coletor de lixo "
  "desligado. As medições brutas estão em <font name='Mono'>resultados/medicoes.csv</font>. Rodei os "
  "experimentos duas vezes. A primeira rodada teve mais oscilação (a máquina é compartilhada) e ficou guardada "
  "em <font name='Mono'>medicoes_rodada1_descartada.csv</font>; os números abaixo são da segunda.")

cab = ["n", "E1 bruta", "E1 D&amp;C", "E1 Kadane", "E2 bruta", "E2 D&amp;C"]
linhas = [[Paragraph(f"<b>{c}</b>", celula) for c in cab]]
for n in NS:
    l = [str(n)]
    for e, a in (("etapa1", "bruta"), ("etapa1", "dc"), ("etapa1", "kadane"), ("etapa2", "bruta"), ("etapa2", "dc")):
        m, d = medias[(e, a, n)]
        l.append(f"{fmt(m)} ± {fmt(d)}")
    linhas.append(l)
S.append(KeepTogether([tabela(linhas, [1.4 * cm] + [2.9 * cm] * 5),
                       Paragraph("Tabela 1 – Tempo médio ± desvio padrão (ms), 5 execuções por tamanho.", legenda)]))

figura("grafico_etapa1.png", 13.2,
       "Figura 1 – Etapa 1, escala log-log. A inclinação de cada reta é o expoente de n estimado por mínimos quadrados.")
figura("grafico_etapa2.png", 13.2, "Figura 2 – Etapa 2, escala log-log.")

r_b1, r_d1, r_k = razao_dobra("etapa1", "bruta"), razao_dobra("etapa1", "dc"), razao_dobra("etapa1", "kadane")
r_b2, r_d2 = razao_dobra("etapa2", "bruta"), razao_dobra("etapa2", "dc")
spd1 = medias[("etapa1", "bruta", 6400)][0] / medias[("etapa1", "dc", 6400)][0]
spd2 = medias[("etapa2", "bruta", 6400)][0] / medias[("etapa2", "dc", 6400)][0]

p("5.1 Comparação com o previsto", h2)
p("Num gráfico log-log, um algoritmo Θ(n<super>k</super>) vira uma reta de inclinação k. As forças brutas deram "
  "inclinação de aproximadamente 2 nas duas etapas, como previsto. Quando n dobra, o tempo multiplicou em média por "
  f"{br(r_b1)} (Etapa 1) e {br(r_b2)} (Etapa 2), e o esperado era 4. Para n log n, dobrar n multiplica o tempo por "
  "2·log(2n)/log n, que fica entre 2,3 e 2,2 nessa faixa de tamanhos (inclinação esperada ≈ 1,15). "
  f"As divisões e conquistas multiplicaram em média por {br(r_d1)} (Etapa 1) e {br(r_d2)} (Etapa 2), "
  f"e o Kadane por {br(r_k)} (esperado 2).")
figura("grafico_razao.png", 14.2,
       "Figura 3 – Tempo dividido pela complexidade prevista, normalizado para 1 em n = 100. "
       "Se a análise estiver certa, a curva fica aproximadamente horizontal.")
p("A Figura 3 mostra a mesma coisa de outro jeito. Se o tempo é c·f(n), então t/f(n) deve ficar constante. "
  "Para as forças brutas e para a divisão e conquista da Etapa 2 a razão fica perto de 1, ou seja, n<super>2</super> e "
  "n log n explicam bem os dados. Já a divisão e conquista da Etapa 1 e o Kadane ficaram abaixo do previsto "
  "(a razão cai até ≈ 0,55–0,65). Minha interpretação é que, para n pequeno, existe um custo fixo que não "
  "depende de n (chamar a função, criar variáveis), e ele pesa mais quando o tempo total é de microssegundos. "
  "Esse custo fixo infla o tempo em n = 100, que é o ponto usado para normalizar, e faz a curva parecer descer. "
  "No caso da Etapa 1, o fator log n também é pequeno perto do custo das ~2n chamadas recursivas, que é "
  "linear, então a curva se parece mais com n do que com n log n nessa faixa. Algumas oscilações isoladas "
  "(por exemplo o pulo em n = 800 na Etapa 2) aparecem também no desvio padrão da Tabela 1 e são ruído "
  "da máquina, que é virtual e compartilhada.")

p("5.2 Quando a força bruta vence e quando a técnica vence", h2)
p(f"Para n grande a divisão e conquista ganha com folga: em n = 6400 ela foi cerca de {spd1:.0f} vezes mais rápida "
  f"na Etapa 1 e {spd2:.0f} vezes na Etapa 2, e a diferença cresce com n porque n<super>2</super>/(n log n) = n/log n. "
  "Para n pequeno é o contrário (Figura 4, média de 300 execuções por tamanho). A força bruta tem laços simples, "
  "sem recursão, sem criar listas e, na Etapa 2, sem ordenar, então o custo por operação dela é bem menor. A "
  "divisão e conquista faz menos operações, mas cada uma é mais cara (chamadas de função, fatiamento e "
  "intercalação de listas, ordenação inicial). O ponto de cruzamento ficou entre 32 e 64 na Etapa 1 e por volta de "
  "32 na Etapa 2. O Kadane vence as duas em todos os tamanhos, porque faz uma passada só com um laço simples.")
figura("grafico_n_pequeno.png", 14.2, "Figura 4 – Tamanhos pequenos (2 a 128): região onde a força bruta é mais rápida.")

p("5.3 Escolha do limiar da Etapa 2", h2)
p("Por causa do que foi visto na Figura 4, vale a pena parar a recursão antes de chegar em 2 ou 3 pontos e "
  "resolver o pedaço pequeno por força bruta. Testei limiares de 2 a 128 com n = 1600 e n = 6400. Fiz 20 execuções "
  "por limiar (mais que o mínimo, porque as diferenças são pequenas) e intercalei as execuções, rodando a "
  "repetição 1 de todos os limiares, depois a repetição 2, e assim por diante, para que uma oscilação da "
  "máquina não prejudicasse só um deles. O resultado está na Figura 5.")
figura("grafico_limiar.png", 13.0, "Figura 5 – Tempo de cada limiar dividido pelo melhor tempo do mesmo n.")
l64 = limiar[6400]
p(f"Limiares muito pequenos são piores: com limiar 2 o tempo foi {br(l64[2][1])}× o melhor, por causa de "
  "muitas chamadas recursivas para pedaços minúsculos. Limiares grandes também são piores, porque a folha "
  "volta a ser quadrática: com limiar 128 o tempo foi "
  f"{br(l64[128][1])}× o melhor. Entre 8 e 24 a curva fica praticamente plana. Escolhi <b>LIMIAR = 16</b>, "
  "que está no meio dessa região plana e foi o melhor ou empatado com o melhor nos dois tamanhos. "
  "Um detalhe que percebi: como 6400/2<super>9</super> = 1600/2<super>7</super> = 12,5, com qualquer limiar entre "
  "13 e 24 as folhas da recursão têm 12 ou 13 pontos, então a execução é a mesma e os tempos ficam iguais. Pelo mesmo "
  "motivo, 32 e 48 dão folhas de 25 pontos e tempos parecidos. Também reparei que o limiar ótimo (≈ 16) é menor que o "
  "ponto de cruzamento da Figura 4 (≈ 32). Isso acontece porque, na Figura 4, a divisão e conquista ainda paga a "
  "ordenação inicial e a criação das tuplas, que não existem dentro da recursão.")

# ---------------------------------------------------------------- conclusao
p("6. Conclusão", h1)
p("As implementações por divisão e conquista ficaram corretas (conferidas com a força bruta em milhares de "
  "entradas) e os tempos medidos seguiram as recorrências: inclinação ≈ 2 para as forças brutas e perto de 1 para "
  "as versões n log n e para o Kadane. A técnica só compensa a partir de algumas dezenas de elementos, e por isso "
  "usar força bruta nos subproblemas pequenos (o limiar) deixou a Etapa 2 cerca de 25% mais rápida que recursar "
  "até 2 pontos. Também deu para ver na prática que o <i>merge sort</i> e o <i>quick sort</i> da aula servem para mais coisas além de "
  "ordenar: a ideia de devolver a lista já ordenada e intercalar na volta da recursão foi o que permitiu o "
  "O(n log n) do par mais próximo.")


def rodape(canvas, doc):
    canvas.saveState()
    canvas.setFont("Serif", 8)
    canvas.setFillColor(colors.HexColor("#777777"))
    canvas.drawCentredString(A4[0] / 2, 1.2 * cm, f"{doc.page}")
    canvas.restoreState()


doc = SimpleDocTemplate(os.path.join(RAIZ, "relatorio", "relatorio.pdf"), pagesize=A4,
                        leftMargin=2.2 * cm, rightMargin=2.2 * cm, topMargin=2 * cm, bottomMargin=2 * cm,
                        title="Trabalho Prático: Divisão e Conquista", author="Ana Clara Macedo")
doc.build(S, onFirstPage=rodape, onLaterPages=rodape)
print("ok")
