      (function () {
        "use strict";

        var NODES = {
          start: {
            w: "門 · O portão", g: "門", t: "Um portão sem letreiro",
            x: "Estás onde os três livros começam. Não há pontuação aqui, nem nível a alcançar, nem porta errada — só aquela que escolheres. Atrás da primeira há uma estrada; atrás da segunda, um homem sentado debaixo de uma árvore; atrás da terceira, uma escuridão que não está vazia.",
            s: "daoPoemBook.html", n: "O Livro Sexy — Poemas do 道",
            c: [["道 · Segue a estrada", "t1"], ["佛 · Senta-te debaixo da árvore", "b1"], ["玄 · Entra no escuro", "x1"], ["合 · Atravessa os dois manuais", "c1"], ["🐒 · Deixa o Macaco escolher", "@random"]]
          },

          t1: {
            w: "道 · O Caminho", g: "道", t: "O caminho que não diz o seu nome",
            x: "Não o vais encontrar na frase. A frase é uma mão, e o caminho não é a coisa que a mão segura. Diz o nome e levantaste uma cerca; permanece em silêncio e a cerca é tua para atravessar. O livro velho abre-se com um aviso: o caminho que pode ser falado não é o caminho constante.",
            s: "daoPoemBook.html", n: "O Livro Sexy — poema 1",
            c: [["Segue a água montanha abaixo", "t2"], ["Pergunta pelo bloco ainda por lapidar", "t3"], ["Desvia-te para o escuro", "d1"]]
          },
          t2: {
            w: "道 · O Caminho", g: "水", t: "A água guarda o lugar baixo",
            x: "A água não tem argumento. Vence a pedra permanecendo, não golpeando. Toma a forma do vaso e não é dele. As pessoas escalam para serem vistas; a água desce e está em todo lado. Sê o lugar baixo — o vale não persegue o rio, e o rio não o consegue passar ao largo.",
            s: "daoPoemBook.html", n: "O Livro Sexy — poema 17",
            c: [["Senta-te no vale", "t4"], ["Escala até às cinco fases", "x1"], ["Respira sem forçar", "c3"]]
          },
          t3: {
            w: "道 · O Caminho", g: "樸", t: "O bloco ainda por lapidar",
            x: "Antes de ser lapidado, o bloco pode tornar-se tudo. O carácter é madeira mais um som: madeira sem cabo, sem tigela, sem nome. O Daodejing volta sempre a ele — o bloco por lapidar, a seda simples, o vale — porque toda a coisa com nome já gastou parte das suas possibilidades.",
            s: "chineseMysticismManual.html", n: "O Escuro e os Cinco — 樸",
            c: [["Talha antes um carácter", "x4"], ["Desce até ao vale", "t4"]]
          },
          t4: {
            w: "道 · O Caminho", g: "谷", t: "O vale responde",
            x: "Grita contra uma montanha e ela devolve a tua voz. Grita para dentro de um vale e ele devolve a voz com o som retirado. O vale não é generoso; o vale está vazio, e vazio é uma forma de resposta. Guarda em ti uma divisão por onde ninguém entra — não um segredo, um espaço.",
            s: "daoPoemBook.html", n: "O Livro Sexy — poema 25",
            c: [["Escala até aos oito trigramas", "x3"], ["Segue antes o sonho", "e1"]]
          },

          b1: {
            w: "佛 · Buda", g: "佛", t: "As quatro visões",
            x: "Um príncipe muito protegido sai do palácio e encontra, por ordem: um velho, um doente, um cadáver e um asceta errante com ar sereno. Os três primeiros ensinam-lhe que o corpo é um empréstimo; o quarto mostra uma maneira de viver com esse saber. Sai do palácio, experimenta a ascese até quase morrer, e depois senta-se debaixo de uma árvore.",
            s: "buddhismManual.html", n: "O Som do Vazio — cap. 1",
            c: [["Ouve as quatro verdades", "b2"], ["Senta-te debaixo da árvore com ele", "b3"]]
          },
          b2: {
            w: "佛 · Buda", g: "諦", t: "Quatro verdades, oito passos",
            x: "O primeiro sermão tem a forma de um diagnóstico: há sofrimento; tem uma causa; pode terminar; há um caminho. O caminho tem oito factores, da visão correcta à concentração correcta, agrupados em ética, quietude e sabedoria. A ordem é uma espiral, não uma escada — a visão correcta orienta o resto, e o resto clarifica a visão correcta.",
            s: "buddhismManual.html", n: "O Som do Vazio — cap. 2",
            c: [["Pergunta o que significa vazio", "b4"], ["Abre os sutras", "b5"], ["Compara com os oito trigramas", "c8"]]
          },
          b3: {
            w: "佛 · Buda", g: "定", t: "Sentado debaixo da árvore",
            x: "A noite é descrita como uma batalha com Māra — exércitos, filhas, a oferta de um reino — e ao romper do dia ele está desperto. A tradição organiza o que vem depois em absorções: pensamento aplicado, pensamento sustentado, êxtase, felicidade, unidade, e depois os estados mais calmos em que cada uma destas coisas cai. O corpo não é o inimigo; é a embarcação.",
            s: "buddhismManual.html", n: "O Som do Vazio — cap. 1, 9",
            c: [["Pergunta o koan de uma só mão", "b6"], ["Ouve o cantochão", "b10"], ["Segue o sopro passo a passo", "c3"]]
          },
          b4: {
            w: "佛 · Buda", g: "空", t: "A forma é vazio",
            x: "Vazio não significa que nada exista. Significa que nada existe por si próprio: cada fenómeno depende de condições, de partes, de designação. O Sutra do Coração diz-no numa linha — a forma é vazio, o vazio é forma — e depois nega todo o resto, não para destruir o mundo mas para afrouxar o aperto que torna o sofrimento possível.",
            s: "buddhismManual.html", n: "O Som do Vazio — o Sutra do Coração",
            c: [["Segue o mantra gate gate", "b7"], ["Pergunta pela natureza de buda", "b8"], ["Abre a porta do escuro", "c1"]]
          },
          b5: {
            w: "佛 · Buda", g: "經", t: "Os sutras",
            x: "Um sutra abre com “assim ouvi”, e depois fixa um lugar, uma audiência e uma pergunta. O Sutra do Coração cabe em vinte e cinco linhas; o Lótus enche vinte e oito capítulos de parábolas; o Diamante termina com um lampejo de relâmpago. Nenhum deles é um ensaio. São textos para recitação, e as repetições são o ponto.",
            s: "buddhismManual.html", n: "O Som do Vazio — cap. 12",
            c: [["Entra numa parábola", "b9"], ["Fica no silêncio a seguir", "b11"]]
          },
          b6: {
            w: "佛 · Buda", g: "禪", t: "O som de uma só mão",
            x: "A pergunta de Hakuin não pode ser respondida a pensar, que é justamente o ponto. No Chan e no Zen as palavras chamam-se dedos que apontam à lua: servem até que alguém os confunda com a lua. A prática de Dōgen é mais simples — só sentar, sem objecto e sem ganho —, e o koan é o que resta quando até isso foi tirado.",
            s: "buddhismManual.html", n: "O Som do Vazio — cap. 13",
            c: [["Fica no silêncio", "b11"], ["Volta à estrada", "t1"]]
          },
          b7: {
            w: "佛 · Buda", g: "咒", t: "Os mantras",
            x: "Om mani padme hum — a joia no lótus — são as seis sílabas da compaixão. Gate gate paragate atravessa, no fecho do próprio Sutra do Coração. Um mantra é a fala da divindade, recitado até que recitante e recitação não sejam duas coisas; o mala conta 108, e a contagem liberta a atenção da própria contagem.",
            s: "buddhismManual.html", n: "O Som do Vazio — cap. 10–11",
            c: [["Segue o som até ao cantochão", "b10"], ["Pergunta quem tem natureza de buda", "b8"]]
          },
          b8: {
            w: "佛 · Buda", g: "性", t: "Natureza de buda, e um macaco",
            x: "O Sutra do Nirvana diz que todo o ser sensível tem natureza de buda — não nascida, não manchada, não notada. Na China, isso tornou-se o alicerce de toda a tradição. É também a piada dentro do nome do Rei Macaco: 悟空, Wukong, “desperto para o vazio”. O macaco que não sabe estar quieto chama-se como aquilo que não consegue ver.",
            s: "buddhismManual.html", n: "O Som do Vazio — cap. 8, 18",
            c: [["Encontra os Macacos da Ásia", "e2"], ["Volta ao vazio", "b4"], ["Vê a roda que gira", "c5"]]
          },
          b9: {
            w: "佛 · Buda", g: "喻", t: "Uma casa em chamas, uma joia na túnica",
            x: "Um pai atrai os filhos para fora de um incêndio com carrinhos de brincar, e depois dá a todos um só grande cocche. Um homem carrega, cosida ao casaco, uma joia sem preço, durante anos, sem saber. O Sutra do Lótus não argumenta; mostra a joia que já possues e o fogo em que já estás metido.",
            s: "buddhismManual.html", n: "O Som do Vazio — o Sutra do Lótus",
            c: [["Procura a joia em ti próprio", "b8"], ["Entra no silêncio", "b11"], ["Lê os símbolos sem saber ler", "c7"]]
          },
          b10: {
            w: "佛 · Buda", g: "音", t: "Cantochão, sino e peixe de madeira",
            x: "O peixe de madeira marca o ritmo; o grande sino é batido 108 vezes pelas 108 aflições; o chant tibetano grave faz uma só voz soar em vários tons. Nas salas chinesas e japonesas o texto é cantado, não lido, e o som faz metade do ensino. Os cinco tons mapeiam as cinco fases, e a sala inteira torna-se o instrumento.",
            s: "buddhismManual.html", n: "O Som do Vazio — cap. 13",
            c: [["Segue os cinco tons até às fases", "x1"], ["Deixa o som terminar", "b11"], ["Pergunta o que as culturas partilham", "e6"], ["Sobe ao tom e ao tubo", "c2"]]
          },
          b11: {
            w: "佛 · Buda", g: "默", t: "O silêncio de Vimalakīrti",
            x: "Trinta e dois bodhisattvas explicam a não-dualidade, cada um mais subtil que o anterior. Depois perguntam a Vimalakīrti, e ele nada diz. Mañjuśrī chama-lhe a verdadeira entrada. O silêncio do próprio Buda quanto às perguntas que não podem ser respondidas com proveito é o mesmo gesto: não fuga, mas a recusa de dar um dedo e chamá-lo lua.",
            s: "buddhismManual.html", n: "O Som do Vazio — cap. 13",
            c: [["Volta ao portão", "start"], ["Entra no escuro", "d1"], ["Pergunta o que é uma religião", "e7"], ["Pergunta o que atravessa", "c6"]]
          },

          x1: {
            w: "玄 · O Escuro", g: "五", t: "As cinco fases",
            x: "A madeira alimenta o fogo, o fogo faz a terra, a terra contém o metal, o metal transporta a água, a água faz crescer a madeira. Cada uma também refreia outra, e assim nada foge com o mundo. São fases, não elementos: o fogo não é uma matéria, é um movimento ascendente e aquecedor. A tabela inteira — estações, órgãos, cores, notas, planetas — pende destes cinco verbos.",
            s: "chineseMysticismManual.html", n: "O Escuro e os Cinco — 五行",
            c: [["Segue o tigre e o dragão", "x2"], ["Vira para o yin e o yang", "x3"]]
          },
          x2: {
            w: "玄 · O Escuro", g: "龍", t: "Tigre a oeste, dragão a este",
            x: "Quatro criaturas marcam os pontos cardeais: o dragão azul-céladon no este, a ave vermelhão no sul, o tigre branco no oeste, a tartaruga negra no norte. São também estações, horas e temperamentos. O poema deste sítio diz-o sem rodeios: “Eu sou o Macaco, o Macaco que pode falar — enquanto também sou o Dragão.”",
            s: "DragonFire.html", n: "Fogo do Dragão (龙火)",
            c: [["Encontra os Macacos da Ásia", "e2"], ["Lê uma paisagem", "x5"]]
          },
          x3: {
            w: "玄 · O Escuro", g: "卦", t: "Yin, yang, e oito trigramas",
            x: "Yin é a encosta sombria; yang é a vertente ao sol. Empilha três linhas, contínuas ou rompidas, e tens um trigrama: céu, terra, trovão, vento, água, fogo, montanha, lago. Todo o Yijing se constrói a partir destes oito, e a roda do ano gira na mesma polaridade.",
            s: "chineseMysticismManual.html", n: "O Escuro e os Cinco — 陰陽, 八卦",
            c: [["Lança as sessenta e quatro", "x6"], ["Volta-te para o escuro", "d1"], ["Oito factores ao lado dos trigramas", "c8"]]
          },
          x4: {
            w: "玄 · O Escuro", g: "字", t: "O carácter é a fotografia de uma caminhada",
            x: "道 é uma estrada mais uma cabeça: o caminho percorrido por quem presta atenção. A maioria dos caracteres não são fotografias mas compostos — metade sentido, metade som —, e as formas mais antigas são incisões em osso. Cuidado com as etimologias bonitas: algumas são verdade, muitas são moralizações posteriores, e o osso é a única testemunha que conta.",
            s: "chineseMysticismManual.html", n: "O Escuro e os Cinco — cap. 13",            c: [["Volta ao caminho", "t1"], ["Entra no sonho", "e1"], ["Abre os selos e a roda", "c7"]]},
          x5: {
            w: "玄 · O Escuro", g: "風", t: "Ler uma paisagem",
            x: "Acolhe o vento, reúne o qi: uma cumeeira atrás, uma elevação a cada lado, um átrio aberto e luminoso à frente, água adiante. O sítio ideal é uma cadeira com braços. Seja o que for que se pense da metafísica, o conselho é com frequência apenas bom desenho — abrigo, luz do dia, drenagem —, e a bússola que acha o sul é o mesmo instrumento que outrora achava as estrelas.",
            s: "chineseMysticismManual.html", n: "O Escuro e os Cinco — 風水",
            c: [["Desce ao escuro", "d1"], ["Volta ao portão", "start"]]
          },
          x6: {
            w: "玄 · O Escuro", g: "易", t: "As sessenta e quatro",
            x: "Dois trigramas fazem um hexagrama: oito vezes oito, sessenta e quatro situações, cada uma com seis linhas lidas de baixo para cima. Uma linha em transformação inverte-se e produz uma segunda figura — a situação dentro da situação. Nenhum par de comentários concorda por inteiro, e isso não é um defeito: o livro é uma máquina para te obrigar a olhar.",
            s: "chineseMysticismManual.html", n: "O Escuro e os Cinco — cap. 6",
            c: [["Lê os caracteres", "x4"], ["Entra no sonho", "e1"], ["Dez minutos ao fim das listas", "c9"]]
          },

          d1: {
            w: "玄 · O Escuro", g: "玄", t: "O escuro não está vazio",
            x: "玄 é escuro com um tom de vinho por baixo: a cor de uma profundidade cujo fundo não se vê. O Daodejing duplica-o — escuro e outra vez escuro, o portão de todas as maravilhas — e chama à fonte o espírito do vale, a fêmea misteriosa. O escuro não é a ausência de luz. É a divisão que se deu à luz.",
            s: "chineseMysticismManual.html", n: "O Escuro e os Cinco — cap. 10",
            c: [["Senta-te no vale", "t4"], ["Volta a luz ao contrário", "d2"], ["Deixa o escuro virar vazio", "c1"]]
          },
          d2: {
            w: "玄 · O Escuro", g: "光", t: "Virar a luz ao contrário",
            x: "Os manuais de meditação falam de 回光返照 — virar a luz ao contrário e fazê-la brilhar de volta. A atenção, normalmente gasta para fora sobre objectos, volta-se sobre a própria fonte. Jung leu o texto chinês como individuação e daí retirou a palavra sincronicidade; o texto em si é um manual taoísta da luz, não uma psicologia, e a diferença vale a pena manter.",
            s: "chineseMysticismManual.html", n: "O Escuro e os Cinco — cap. 10",
            c: [["Desce ao elixir", "d3"], ["Volta aos caracteres", "x4"]]
          },
          d3: {
            w: "玄 · O Escuro", g: "丹", t: "O elixir interior",
            x: "A alquimia externa cozinhou cinabre e chumbo à procura da imortalidade, e matou vários imperadores Tang. A alquimia interna guardou o aparelho e trouxe-o para dentro: o corpo é o caldeirão, o sopro o fole, e a essência, o sopro e o espírito os ingredientes. A órbita sobe pela coluna e desce pela frente. Não comas as receitas antigas; o mercúrio era verdadeiro.",
            s: "chineseMysticismManual.html", n: "O Escuro e os Cinco — cap. 17",
            c: [["Volta ao caminho", "t1"], ["Volta ao portão", "start"], ["Vê o corpo como embarcação", "c4"]]
          },

          e1: {
            w: "夢 · O Sonho", g: "夢", t: "O Caminho e o Sonho",
            x: "A energia primordial da vida é o 道. O som primordial da terra é o 🕉. Juntos criam uma Expressão para Todos. E depois a frase que fecha o laço: o sonho cria o caminho, e o caminho cria o sonho. Sem dúvidas quanto ao estilo de Deus.",
            s: "dreampath.html", n: "O Caminho e o Sonho",
            c: [["Pergunta pelo estilo de Deus", "e3"], ["Ouve o som de que fala", "b10"], ["Volta ao caminho", "t1"]]
          },
          e2: {
            w: "猴 · O Macaco", g: "猴", t: "O que os macacos simbolizam na Ásia",
            x: "No Japão, o macaco media entre os humanos e os deuses, e é também o trapaceiro. Na China é a liberdade vistoso, a engenhosidade e a sociabilidade — lembrete de que só o dever não é uma vida em equilíbrio. No Vietname é a memória, e a importância do que de facto foi vivido. Quatro países, um animal, quatro argumentos diferentes.",
            s: "asianMonkey.html", n: "O que simbolizam os Macacos nas culturas asiáticas?",
            c: [["Encontra o Rei Macaco", "b8"], ["Volta ao tigre e ao dragão", "x2"]]
          },
          e3: {
            w: "書 · O Livro", g: "神", t: "O Estilo de Deus",
            x: "A nossa capacidade de imaginar constrói-se com o que conhecemos; é assim que uma ideia nova se torna imagem, texto, um objecto que fala. A página vai buscar-lhe a velha maquinaria por trás — Māyā, o véu da aparência, e o modo de as escolas Zen seleccionarem os estudantes pelo que conseguem imaginar. A criação é um caminho lógico que escolhemos, e o estilo é a escolha.",
            s: "style_of_god.html", n: "O Estilo de Deus",
            c: [["Lê o sonho que o antecede", "e5"], ["Lê a equação 1 + 1 = 1", "e4"], ["Volta ao caminho do sonho", "e1"]]
          },
          e4: {
            w: "書 · O Livro", g: "合", t: "1 + 1 = 1, ou 3",
            x: "Hidrogénio mais oxigénio é água: uma coisa nova com propriedades que nenhum dos gases tinha. Duas ideas fundem-se num descobrimento; duas células tornam-se um zigoto. O ensaio chama-lhe emergência, e lê-o pela equação antiga. O seu sexto capítulo tem um título que há que lembrar: “O Macaco e o Buda São Uma Cabeça.”",
            s: "ArtOfCreation.html", n: "Resolução da Mente — Imagination + Logic = Application",
            c: [["Encontra o Macaco", "e2"], ["Volta ao vazio", "b4"]]
          },
          e5: {
            w: "書 · O Livro", g: "幻", t: "Antes que alguma coisa exista",
            x: "Antes de alguma coisa existir na realidade, precisa primeiro de ser uma ilusão pura: um arranha-céus, uma sociedade, ou um universo começa como uma visão não realizada — um sonho necessário que faz nascer a vontade de criar. Sem o esboço interno, não haveria qualquer necessidade de construir. A página do 道 Expression começa aí, e o jogo também.",
            s: "taoExpression.html", n: "道 Expression",
            c: [["Volta ao sonho", "e1"], ["Caminha a estrada", "t1"]]
          },
          e6: {
            w: "書 · O Livro", g: "歌", t: "Uma só canção humana",
            x: "Toda a cultura ensina hospitalidade, honra a cor e canta. A página reúne apenas o lado construtivo: provérbios que curam, cores que celebram, música que constrói. Línguas diferentes, um só coração. É uma reivindicação estranha e útil para trazer para um jogo de sutras e trigramas — as mesmas três notas vão aparecendo sempre.",
            s: "CommonCultures.html", n: "Uma Canção Humana — Provérbios, Cores & Música das Culturas do Mundo",
            c: [["Segue as cores até às fases", "x1"], ["Ouve o cantochão", "b10"]]
          },
          e7: {
            w: "書 · O Livro", g: "教", t: "O que são as religiões",
            x: "Um livro pode ser amado pelo que ensina sobre a realidade, e amá-lo cria a necessidade de ver essa realidade. A página nota que a leitura taoísta espera o inesperado, enquanto outros livros definem o que deve ser esperado e constroem à volta disso mecanismos de exclusão. É um aviso para cada cânone, incluindo os deste jogo.",
            s: "religions.html", n: "O que são as Religiões?",
            c: [["Volta à estrada", "t1"], ["Fica no silêncio", "b11"]]
          },

          c1: {
            w: "合 · O Cruzamento", g: "冥", t: "O vazio e o escuro",
            x: "Duas tradições chegaram à mesma porta por lados diferentes. O Sutra do Coração nega nascimento e destruição para retirar a solidez imaginária que torna o sofrimento possível: a vacuidade não diz que nada existe, diz que nada existe do seu próprio lado. O Daodejing dobra o seu escuro — 玄之又玄，眾妙之門 — e escuro ali não é ausência de luz nem é o mal: é o indiferenciado, o estado antes de uma figura ser recortada do fundo, a cor de uma profundidade cujo fundo não se vê.",
            s: "manualDaMisticaChinesa.html", n: "O Escuro e os Cinco — 玄",
            c: [["Volta ao vazio do Coração", "b4"], ["Volta ao escuro por dentro", "d1"], ["Segue para o som", "c2"]]
          },
          c2: {
            w: "合 · O Cruzamento", g: "樂", t: "O peixe de madeira e os doze tubos",
            x: "O som é nas duas tradições o próprio ensino. No templo, o peixe de madeira marca o compasso, o grande sino é batido 108 vezes pelas 108 aflições, e a campainha tântrica soa a vacuidade. Na corte chinesa, os cinco tons — 宮商角徵羽 — correspondem às cinco fases e aos cinco órgãos, e os doze tubos de afinação dão ao ano o seu calendário: perder a afinação era perder o mandato. Os dois chegam à mesma sobriedade — 大音希聲, o maior som é difícil de ouvir.",
            s: "manualDaMisticaChinesa.html", n: "O Escuro e os Cinco — 音",
            c: [["Ouve o cantochão", "b10"], ["Volta às cinco fases", "x1"], ["Segue o sopro", "c3"]]
          },
          c3: {
            w: "合 · O Cruzamento", g: "氣", t: "Dezasseis passos, quatro e seis",
            x: "A respiração é a prática mínima das duas casas. O Ānāpānasati Sutta dá dezasseis passos só sobre o sopro, de saber uma respiração longa até contemplar a impermanência. O manual chinês pede menos, na mesma moeda: sentar em silêncio (靜坐), inspirar quatro, expirar seis, sem forçar; quando a mente vagueia, nota-o e volta — esse regresso é a prática. O qi é isto mesmo em escala: vapor a subir do arroz, não uma substância mas uma família de processos — tempo, ar, vitalidade, humor de uma época.",
            s: "manualDoBudismo.html", n: "O Som da Vacuidade — a meditação",
            c: [["Senta-te com ele", "b3"], ["Vê o corpo como cadinho", "c4"], ["Volta à água que não força", "t2"]]
          },
          c4: {
            w: "合 · O Cruzamento", g: "身", t: "Embarcação e cadinho",
            x: "Ao corpo, as duas tradições dão o mesmo ofício. Na noite do despertar, o corpo não é o inimigo: é a embarcação, e a memória da calma sob uma árvore de infância ensina-o melhor que a ascese. Na alquimia interna é ainda mais instrumental: o corpo é o cadinho, o sopro o fole, e os três tesouros — jing, qi, shen — os ingredientes, refinados na órbita que sobe pela coluna e desce pela frente. O par 性命 fecha a conversa: treinar só o corpo é cego; treinar só a mente é vazio.",
            s: "manualDaMisticaChinesa.html", n: "O Escuro e os Cinco — 內丹",
            c: [["Cozinha o elixir", "d3"], ["Volta à árvore", "b3"], ["Sente a roda girar", "c5"]]
          },
          c5: {
            w: "合 · O Cruzamento", g: "轉", t: "Tudo gira, e a semente viaja",
            x: "As três marcas do budismo resumem-se a uma: anicca, tudo o que é condicionado muda — e a roda dos seis reinos é esse virar desenhado, com os três venenos a morderem-se ao centro. O yin-yang diz o mesmo noutra gramática: no extremo, cada um torna-se o outro — o meio-dia vira tarde — e cada peixe do diagrama carrega um ponto do seu oposto, a semente do outro no coração de cada fase. O nome do próprio jogo vem daí: 轉 não descreve um destino, descreve um girar.",
            s: "manualDoBudismo.html", n: "O Som da Vacuidade — 緣起",
            c: [["Pergunta o que atravessa", "c6"], ["Volta ao carma e ao macaco", "b8"], ["Lança as sessenta e quatro", "x6"]]
          },
          c6: {
            w: "合 · O Cruzamento", g: "魂", t: "O que atravessa a morte",
            x: "Nenhuma das duas transporta uma alma com passaporte. A China parte a pessoa em duas: o hun, yang e leve, parte com o sopro e tem de ser chamado ou guiado pelo rito — um hun que se demora torna-se fantasma — e o po, yin, fica com o corpo e com a sepultura. O budismo compara o renascimento a uma chama que passa a outra chama: nada de material viaja, e no entanto a chama seguinte não é alheia. Os bardos tibetanos dão ao estado intermédio quarenta e nove dias, lidos em voz alta; o que continua é um padrão causal, não um passageiro.",
            s: "manualDoBudismo.html", n: "O Som da Vacuidade — 生死",
            c: [["Volta a luz para dentro", "d2"], ["Fica no silêncio", "b11"], ["Volta ao vazio", "b4"]]
          },
          c7: {
            w: "合 · O Cruzamento", g: "印", t: "Símbolos que se leem sem saber ler",
            x: "A arte é nas duas uma tecnologia da memória. O budista comprimiu o ensino em oito símbolos auspiciosos — lótus, roda de oito raios, nó infinito —, em mudrā de mão e numa stupa cujas partes codificam os cinco elementos. O chinês gravou padrões em ossos oraculares, ordenou os caracteres em seis scripts e ainda hoje sela com o script de selo, 篆書. Os dois dão o mesmo aviso: desconfia das leituras bonitas — apenas a forma mais antiga atestada conta.",
            s: "manualDoBudismo.html", n: "O Som da Vacuidade — 法輪",
            c: [["Volta ao carácter", "x4"], ["Reconhece a roda nas parábolas", "b9"], ["Volta ao portão", "start"]]
          },
          c8: {
            w: "合 · O Cruzamento", g: "八", t: "Duas rodas de oito",
            x: "O caminho óctuplo não é uma escada: é uma espiral agrupada em três treinos — ética, concentração, sabedoria —, da visão correta à concentração correta. Os oito trigramas também não são uma lista: céu, terra, trovão, vento, água, fogo, montanha e lago combinam-se por pares nas sessenta e quatro situações do Yijing. Oito factores travam a vida de girar às cegas; oito trigramas deixam-na girar com nome. Nas duas rodas, o oito é o número com que se descreve tudo sem esgotar nada.",
            s: "manualDaMisticaChinesa.html", n: "O Escuro e os Cinco — 八卦",
            c: [["Refaz o diagnóstico do Buda", "b2"], ["Volta ao tigre e ao dragão", "x2"], ["Senta-te ao fim das listas", "c9"]]
          },
          c9: {
            w: "合 · O Cruzamento", g: "坐", t: "Os dois manuais terminam nos mesmos dez minutos",
            x: "Os dois manuais fecham com doze semanas sóbrias. A budista: um capítulo do Dhammapada por dia, mettā por amigo e por pessoa difícil, um mantra recitado 108 vezes. A chinesa: um capítulo do Daodejing em voz alta, um caractere por dia, sentar-se dez minutos, ficar de pé cinco (站樁) e, uma vez por semana, não fazer nada durante vinte — 無為, que o mundo moderno chama insuportável. É a única escala que sobrevive a um dia de trabalho, e o jogo segue-a: uma página, uma escolha, outra página.",
            s: "manualDoBudismo.html", n: "O Som da Vacuidade — 行",
            c: [["Volta ao primeiro portão", "start"], ["Volta ao caminho", "t1"], ["Fica no silêncio", "b11"]]
          }
        };

        var panel = document.getElementById("panel");
        var worldEl = document.getElementById("world");
        var placeEl = document.getElementById("place");
        var whereTop = document.getElementById("whereTop");
        var glyphEl = document.getElementById("glyph");
        var titleEl = document.getElementById("title");
        var textEl = document.getElementById("text");
        var sourceEl = document.getElementById("source");
        var choicesEl = document.getElementById("choices");
        var threadEl = document.getElementById("thread");
        var backBtn = document.getElementById("back");
        var resetBtn = document.getElementById("reset");
        var hintEl = document.getElementById("hint");

        var current = "start";
        var history = [];
        var thread = ["start"];
        var randomTargets = ["t1", "b1", "x1", "e1", "e2", "d1", "b7"];

        function go(id) {
          if (id === "@random") {
            id = randomTargets[Math.floor(Math.random() * randomTargets.length)];
          }
          if (!NODES[id]) { return; }
          history.push(current);
          current = id;
          thread.push(id);
          if (thread.length > 18) { thread = thread.slice(thread.length - 18); }
          render("turn");
        }

        function back() {
          if (!history.length) { return; }
          current = history.pop();
          thread.pop();
          render("back");
        }

        function reset() {
          current = "start";
          history = [];
          thread = ["start"];
          render("turn");
        }

        function render(direction) {
          var node = NODES[current];
          worldEl.textContent = node.w;
          placeEl.textContent = node === NODES.start ? "início" : "estás aqui";
          if (whereTop) { whereTop.textContent = node.w.split(" · ")[1] || node.w; }
          glyphEl.textContent = node.g;
          titleEl.textContent = node.t;
          textEl.textContent = node.x;

          sourceEl.textContent = "";
          sourceEl.appendChild(document.createTextNode("de "));
          var link = document.createElement("a");
          link.href = "./" + node.s;
          link.textContent = node.n + " · " + node.s;
          sourceEl.appendChild(link);

          choicesEl.textContent = "";
          choicesEl.classList.toggle("doors", current === "start");
          node.c.forEach(function (pair, i) {
            var btn = document.createElement("button");
            btn.type = "button";
            btn.className = "choice";
            var num = document.createElement("span");
            num.className = "n";
            num.textContent = String(i + 1);
            var lbl = document.createElement("span");
            lbl.className = "lbl";
            lbl.textContent = pair[0];
            var goIcon = document.createElement("span");
            goIcon.className = "go";
            goIcon.textContent = "→";
            btn.appendChild(num);
            btn.appendChild(lbl);
            btn.appendChild(goIcon);
            btn.addEventListener("click", function () { go(pair[1]); });
            choicesEl.appendChild(btn);
          });

          if (current === "start") {
            var picked = choicesEl.querySelectorAll(".choice");
            if (picked.length === 4) {
              var doors = ["道", "佛", "玄", "猴"];
              picked.forEach(function (b, i) {
                var g = document.createElement("span");
                g.className = "door-glyph";
                g.textContent = doors[i] || "·";
                b.insertBefore(g, b.children[1] || null);
              });
            }
          }

          backBtn.disabled = history.length === 0;
          hintEl.textContent = "1–" + node.c.length + " para escolher · Backspace para voltar";

          threadEl.textContent = "";
          var lab = document.createElement("span");
          lab.className = "lbl";
          lab.textContent = "Fio";
          threadEl.appendChild(lab);
          thread.forEach(function (id) {
            var s = document.createElement("span");
            s.textContent = NODES[id].g;
            threadEl.appendChild(s);
          });

          if (direction) {
            panel.classList.remove("is-turning", "is-back");
            void panel.offsetWidth;
            panel.classList.add(direction === "back" ? "is-back" : "is-turning");
          }
        }

        backBtn.addEventListener("click", back);
        resetBtn.addEventListener("click", reset);

        document.addEventListener("keydown", function (event) {
          if (event.metaKey || event.ctrlKey || event.altKey) { return; }
          var tag = event.target && event.target.tagName;
          if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") { return; }
          if (event.key === "Backspace") {
            event.preventDefault();
            back();
            return;
          }
          if (event.key === "r" || event.key === "R") {
            reset();
            return;
          }
          var n = Number(event.key);
          if (n >= 1 && n <= 9) {
            var node = NODES[current];
            var pair = node.c[n - 1];
            if (pair) {
              event.preventDefault();
              go(pair[1]);
            }
          }
        });

        render(0);
      })();
    