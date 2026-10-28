// Alegrete Summit 2026 — jogo "Kauã e o Kaá Sentinela" (Canvas e JS puro, sem dependências)
// Fases: 1 conectar (mirar a antena nos satélites), 2 criar com a IA (conversa e blocos),
// 3 proteger (sensores e alertas), 4 investir (melhorias na aldeia) e tela final com a moral.
(function () {
  "use strict";
  var root = document.getElementById("jogo-kaua");
  if (!root || !document.createElement("canvas").getContext) return;

  var lang = (document.documentElement.lang || "pt").slice(0, 2);
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // ---------------------------------------------------------------- textos
  var I18N = {
    pt: {
      locale: "pt-BR",
      money: function (v) { return "R$ " + v.toLocaleString("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + " mi"; },
      phases: ["Conectar", "Criar com a IA", "Proteger", "Investir"],
      phase: "Fase",
      intro: {
        title: "Kauã e o Kaá Sentinela",
        text: "Ajude Kauã, um jovem indígena da Amazônia, a conectar a aldeia, criar uma solução com a IA, proteger a floresta e transformar a aldeia. São quatro fases curtas.",
        keys: "<b>Mouse ou toque:</b> mire, toque e escolha. <b>Teclado:</b> <kbd>←</kbd> <kbd>→</kbd> <kbd>↑</kbd> <kbd>↓</kbd> ou <kbd>W</kbd><kbd>A</kbd><kbd>S</kbd><kbd>D</kbd> para mover, <kbd>Enter</kbd> ou <kbd>Espaço</kbd> para agir, <kbd>1</kbd>–<kbd>5</kbd> para escolher opções.",
        start: "Começar",
        note: "Fábula: personagem, produto e números fictícios."
      },
      p1: {
        title: "Fase 1 · Conectar",
        text: "A antena de internet via satélite chegou! Mire nos satélites de órbita baixa que cruzam o céu e mantenha o feixe sobre eles até o sinal chegar a 100%.",
        keys: "<b>Mouse ou toque:</b> aponte para o satélite. <b>Teclado:</b> <kbd>←</kbd> <kbd>→</kbd> ou <kbd>A</kbd> <kbd>D</kbd>.",
        hud: "Sinal", locked: "travado!",
        done: "Aldeia conectada! Sem cabo e sem torre: a internet desceu do céu até o meio da mata."
      },
      p2: {
        title: "Fase 2 · Criar com a IA",
        text: "Um projeto de inclusão digital entregou um notebook a Kauã. Ele nunca estudou computação, mas sabe explicar o problema. Converse com a IA e monte a solução.",
        ai: "IA", kaua: "Kauã",
        slots: ["Ouvido", "Energia", "Dados da mata", "Modelo de IA"],
        steps: [
          { q: "Olá, Kauã! Qual problema da sua aldeia você quer resolver?", o: [
            ["Motosserras ilegais e queimadas destroem a mata, e a gente só descobre tarde demais", 1, "Esse é um problema real, urgente, e você o conhece como ninguém. Vamos criar a solução juntos!"],
            ["O peixe está sumindo do rio", 2, "Também é um problema real! Guarde essa ideia: outra jovem da aldeia vai resolvê-lo. Qual dói mais agora?"],
            ["O barco da saúde demora a chegar", 2, "Outro problema real! Guarde essa ideia para outro jovem da aldeia. Qual é o mais urgente agora?"]] },
          { q: "Primeiro: como escutar a mata o dia inteiro?", o: [
            ["Câmeras de cinema importadas", 0, "São caríssimas e não aguentam a umidade da floresta. Pense em algo mais simples."],
            ["Celulares velhos reaproveitados, presos no alto das árvores", 1, "Ótimo! São baratos, leves e todos têm microfone. Reaproveitar é inovar."],
            ["Um drone voando 24 horas por dia", 0, "A bateria de um drone dura minutos, não dias."]] },
          { q: "E a energia, no meio da mata?", o: [
            ["Um gerador a diesel", 0, "Faz barulho, polui e precisa de combustível. Atrapalharia até a escuta!"],
            ["Puxar um fio da cidade", 0, "A cidade mais próxima fica a centenas de quilômetros."],
            ["Um pequeno painel solar em cada celular", 1, "Isso! Energia limpa e de graça, com o painel no alto da árvore."]] },
          { q: "Para aprender, a IA precisa de exemplos. Que dados vamos usar?", o: [
            ["Gravações dos sons da mata: guariba, chuva, trovão, pássaros, motosserra e fogo", 1, "Perfeito: é o seu conhecimento da floresta virando dados."],
            ["Fotos de cidades baixadas da internet", 0, "Fotos de cidade não ensinam a reconhecer os sons da floresta."],
            ["Nenhum, a IA já sabe tudo", 0, "Não sabe! Sem exemplos locais, o modelo erraria com confiança."]] },
          { q: "Agora a parte técnica, que eu te ajudo a programar: que tipo de modelo usamos?", o: [
            ["Uma planilha onde alguém anota os barulhos", 0, "Alguém teria de ouvir a mata 24 horas por dia…"],
            ["Um modelo que classifica sons e roda no próprio celular", 1, "Isso! Eu escrevo o código com você e explico cada parte."],
            ["Um site de previsão do tempo", 0, "Previsão do tempo não detecta motosserras."]] },
          { test: true, q: "Tudo montado! Vamos testar o Kaá Sentinela.", run: "Rodar o teste",
            fail: "Teste 1: alarme falso! O modelo confundiu um trovão com uma motosserra.",
            q2: "Errar no teste é normal. Como corrigimos?", o: [
            ["Desligar os sensores quando chover", 0, "Aí os desmatadores aproveitariam a chuva."],
            ["Aumentar o volume dos microfones", 0, "Mais volume não ensina o modelo a diferenciar os sons."],
            ["Gravar mais exemplos de trovão e de guariba para a IA aprender a diferença", 1, "Exatamente. Treinando de novo… Teste 2: 97% de acerto!"]] }
        ],
        saved: "ideia guardada",
        done: "Nasceu o <b>Kaá Sentinela</b> (Kaá quer dizer mata, em tupi). Kauã entrou com o conhecimento da floresta; a IA, com a técnica."
      },
      p3: {
        title: "Fase 3 · Proteger",
        place: function (n) { return "Posicione <b>" + n + " sensores Kaá</b> na floresta: toque ou clique num ponto (ou mova com as setas e aperte <kbd>Enter</kbd>). Toque num sensor para tirá-lo. O alerta só chega se a ameaça estiver dentro do círculo de algum sensor."; },
        text: "Quando um sensor ouvir motosserra ou fogo, um alerta pisca: toque nele (ou <kbd>Enter</kbd>) antes que o tempo acabe para enviar os guardiões. A cada alerta atendido, mais comunidades querem o Kaá Sentinela.",
        keys: "<b>Teclado:</b> setas ou <kbd>W</kbd><kbd>A</kbd><kbd>S</kbd><kbd>D</kbd> movem, <kbd>Enter</kbd> ou <kbd>Espaço</kbd> agem, <kbd>R</kbd> vai ao alerta mais urgente.",
        sensors: "Sensores", forest: "Mata", saved: "Alertas", comm: "Comunidades", countries: "países", time: "Tempo",
        go: "Guardiões a caminho!", plus: function (n) { return "+" + n + " comunidades"; }, lost: "Mata perdida",
        saw: "motosserra", fire: "fogo",
        fail: "A mata sofreu demais. Reposicione os sensores para cobrir mais floresta e tente de novo.", retry: "Tentar de novo",
        done: function (c, p, m) { return "Missão cumprida! O desmatamento ilegal despencou. O Kaá Sentinela virou sucesso internacional: <b>" + c + " comunidades</b> em <b>" + p + " países</b> usam o produto, e Kauã ficou milionário, com <b>" + m + "</b>."; }
      },
      p4: {
        title: "Fase 4 · Investir",
        text: "Com o dinheiro, Kauã investe onde tudo começou. Escolha as melhorias para a aldeia.",
        items: { solar: ["Energia solar", "Luz e carga para todas as casas"], agua: ["Água potável", "Poço e filtro para todos"], saude: ["Posto de saúde", "Atendimento perto de casa"], escola: ["Escola conectada", "Internet e notebooks para estudar"], lab: ["Laboratório de criação", "Outros jovens criando soluções com IA"] },
        balance: "Saldo", done: "feito", cant: "saldo insuficiente", finish: "Ver o final"
      },
      end: {
        title: "A moral da história",
        moral: ["Qualquer pessoa, em qualquer lugar, com internet, um notebook e um modelo de IA sofisticado, pode criar empresas, produtos e transformar realidades.",
          "Criar soluções digitais não é mais privilégio de quem é da computação ou de quem tem muito dinheiro.",
          "Quem conhece o problema local tem um grande diferencial. Internet e IA democratizam o poder de criar."],
        summary: function (a, h, k) { return a + " alertas atendidos · " + h + "% da mata preservada · " + k + " melhorias na aldeia"; },
        again: "Jogar de novo", read: "Ler a fábula"
      },
      next: "Próxima fase", cont: "Continuar"
    },
    en: {
      locale: "en-US",
      money: function (v) { return "US$ " + v.toFixed(1) + "M"; },
      phases: ["Connect", "Create with AI", "Protect", "Invest"],
      phase: "Phase",
      intro: {
        title: "Kauã and the Kaá Sentinel",
        text: "Help Kauã, a young Indigenous man from the Amazon, connect his village, build a solution with AI, protect the forest and transform the village. Four short phases.",
        keys: "<b>Mouse or touch:</b> aim, tap and choose. <b>Keyboard:</b> <kbd>←</kbd> <kbd>→</kbd> <kbd>↑</kbd> <kbd>↓</kbd> or <kbd>W</kbd><kbd>A</kbd><kbd>S</kbd><kbd>D</kbd> to move, <kbd>Enter</kbd> or <kbd>Space</kbd> to act, <kbd>1</kbd>–<kbd>5</kbd> to pick options.",
        start: "Start",
        note: "A fable: character, product and numbers are fictional."
      },
      p1: {
        title: "Phase 1 · Connect",
        text: "The satellite internet dish has arrived! Aim at the low-orbit satellites crossing the sky and keep the beam on them until the signal reaches 100%.",
        keys: "<b>Mouse or touch:</b> point at the satellite. <b>Keyboard:</b> <kbd>←</kbd> <kbd>→</kbd> or <kbd>A</kbd> <kbd>D</kbd>.",
        hud: "Signal", locked: "locked!",
        done: "Village connected! No cables, no towers: the internet came down from the sky into the heart of the forest."
      },
      p2: {
        title: "Phase 2 · Create with AI",
        text: "A digital inclusion project gave Kauã a laptop. He never studied computing, but he knows how to explain the problem. Talk to the AI and build the solution.",
        ai: "AI", kaua: "Kauã",
        slots: ["Ears", "Power", "Forest data", "AI model"],
        steps: [
          { q: "Hi, Kauã! Which problem in your village do you want to solve?", o: [
            ["Illegal chainsaws and fires destroy the forest, and we only find out when it's too late", 1, "That's a real, urgent problem, and nobody knows it better than you. Let's build the solution together!"],
            ["The fish are disappearing from the river", 2, "That's a real problem too! Save that idea: another young woman from the village will solve it. Which one hurts most right now?"],
            ["The health boat takes too long to arrive", 2, "Another real problem! Save that idea for another young person in the village. Which one is most urgent now?"]] },
          { q: "First: how do we listen to the forest all day long?", o: [
            ["Imported cinema cameras", 0, "They are very expensive and can't handle the forest's humidity. Think of something simpler."],
            ["Old, reused phones fixed high up in the trees", 1, "Great! They're cheap, light and they all have a microphone. Reusing is innovating."],
            ["A drone flying 24 hours a day", 0, "A drone's battery lasts minutes, not days."]] },
          { q: "And the power, in the middle of the forest?", o: [
            ["A diesel generator", 0, "It's noisy, it pollutes and it needs fuel. It would even ruin the listening!"],
            ["Run a cable from the city", 0, "The nearest city is hundreds of kilometers away."],
            ["A small solar panel on each phone", 1, "Yes! Clean, free energy, with the panel high up in the tree."]] },
          { q: "To learn, the AI needs examples. What data will we use?", o: [
            ["Recordings of forest sounds: howler monkeys, rain, thunder, birds, chainsaws and fire", 1, "Perfect: your knowledge of the forest turned into data."],
            ["Photos of cities downloaded from the internet", 0, "City photos don't teach anyone to recognize forest sounds."],
            ["None, the AI already knows everything", 0, "It doesn't! Without local examples, the model would be confidently wrong."]] },
          { q: "Now the technical part, which I'll help you code: what kind of model do we use?", o: [
            ["A spreadsheet where someone writes down the noises", 0, "Someone would have to listen to the forest 24 hours a day…"],
            ["A model that classifies sounds and runs on the phone itself", 1, "Yes! I'll write the code with you and explain every part."],
            ["A weather forecast website", 0, "Weather forecasts don't detect chainsaws."]] },
          { test: true, q: "Everything is assembled! Let's test the Kaá Sentinel.", run: "Run the test",
            fail: "Test 1: false alarm! The model mistook thunder for a chainsaw.",
            q2: "Failing a test is normal. How do we fix it?", o: [
            ["Turn the sensors off when it rains", 0, "Then loggers would take advantage of the rain."],
            ["Turn up the microphone volume", 0, "More volume doesn't teach the model to tell sounds apart."],
            ["Record more examples of thunder and howler monkeys so the AI learns the difference", 1, "Exactly. Retraining… Test 2: 97% accuracy!"]] }
        ],
        saved: "idea saved",
        done: "The <b>Kaá Sentinel</b> is born (Kaá means forest in Tupi). Kauã brought the knowledge of the forest; the AI brought the technique."
      },
      p3: {
        title: "Phase 3 · Protect",
        place: function (n) { return "Place <b>" + n + " Kaá sensors</b> in the forest: tap or click a spot (or move with the arrows and press <kbd>Enter</kbd>). Tap a sensor to remove it. An alert only arrives if the threat is inside a sensor's circle."; },
        text: "When a sensor hears a chainsaw or fire, an alert flashes: tap it (or press <kbd>Enter</kbd>) before time runs out to send the guardians. Every alert answered makes more communities want the Kaá Sentinel.",
        keys: "<b>Keyboard:</b> arrows or <kbd>W</kbd><kbd>A</kbd><kbd>S</kbd><kbd>D</kbd> move, <kbd>Enter</kbd> or <kbd>Space</kbd> act, <kbd>R</kbd> jumps to the most urgent alert.",
        sensors: "Sensors", forest: "Forest", saved: "Alerts", comm: "Communities", countries: "countries", time: "Time",
        go: "Guardians on the way!", plus: function (n) { return "+" + n + " communities"; }, lost: "Forest lost",
        saw: "chainsaw", fire: "fire",
        fail: "The forest suffered too much. Reposition the sensors to cover more of it and try again.", retry: "Try again",
        done: function (c, p, m) { return "Mission accomplished! Illegal deforestation plummeted. The Kaá Sentinel became an international hit: <b>" + c + " communities</b> in <b>" + p + " countries</b> use it, and Kauã became a millionaire, with <b>" + m + "</b>."; }
      },
      p4: {
        title: "Phase 4 · Invest",
        text: "With the money, Kauã invests where it all began. Choose the improvements for the village.",
        items: { solar: ["Solar power", "Light and charging for every home"], agua: ["Clean water", "A well and filters for everyone"], saude: ["Health post", "Care close to home"], escola: ["Connected school", "Internet and laptops to study"], lab: ["Creation lab", "Other young people building solutions with AI"] },
        balance: "Balance", done: "done", cant: "not enough money", finish: "See the ending"
      },
      end: {
        title: "The moral of the story",
        moral: ["Anyone, anywhere, with internet, a laptop and a sophisticated AI model, can create companies and products and transform realities.",
          "Building digital solutions is no longer a privilege of computer scientists or of people with a lot of money.",
          "Knowing a local problem is a big advantage. Internet and AI democratize the power to create."],
        summary: function (a, h, k) { return a + " alerts answered · " + h + "% of the forest preserved · " + k + " improvements in the village"; },
        again: "Play again", read: "Read the fable"
      },
      next: "Next phase", cont: "Continue"
    },
    es: {
      locale: "es-ES",
      money: function (v) { return "US$ " + v.toLocaleString("es-ES", { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + " M"; },
      phases: ["Conectar", "Crear con IA", "Proteger", "Invertir"],
      phase: "Fase",
      intro: {
        title: "Kauã y el Kaá Centinela",
        text: "Ayuda a Kauã, un joven indígena de la Amazonia, a conectar su aldea, crear una solución con IA, proteger la selva y transformar la aldea. Son cuatro fases cortas.",
        keys: "<b>Ratón o toque:</b> apunta, toca y elige. <b>Teclado:</b> <kbd>←</kbd> <kbd>→</kbd> <kbd>↑</kbd> <kbd>↓</kbd> o <kbd>W</kbd><kbd>A</kbd><kbd>S</kbd><kbd>D</kbd> para moverte, <kbd>Enter</kbd> o <kbd>Espacio</kbd> para actuar, <kbd>1</kbd>–<kbd>5</kbd> para elegir opciones.",
        start: "Empezar",
        note: "Fábula: personaje, producto y números ficticios."
      },
      p1: {
        title: "Fase 1 · Conectar",
        text: "¡Llegó la antena de internet satelital! Apunta a los satélites de órbita baja que cruzan el cielo y mantén el haz sobre ellos hasta que la señal llegue al 100%.",
        keys: "<b>Ratón o toque:</b> apunta al satélite. <b>Teclado:</b> <kbd>←</kbd> <kbd>→</kbd> o <kbd>A</kbd> <kbd>D</kbd>.",
        hud: "Señal", locked: "¡enganchado!",
        done: "¡Aldea conectada! Sin cables y sin torres: internet bajó del cielo hasta el corazón de la selva."
      },
      p2: {
        title: "Fase 2 · Crear con IA",
        text: "Un proyecto de inclusión digital le entregó un portátil a Kauã. Nunca estudió informática, pero sabe explicar el problema. Conversa con la IA y arma la solución.",
        ai: "IA", kaua: "Kauã",
        slots: ["Oído", "Energía", "Datos de la selva", "Modelo de IA"],
        steps: [
          { q: "¡Hola, Kauã! ¿Qué problema de tu aldea quieres resolver?", o: [
            ["Las motosierras ilegales y los incendios destruyen la selva, y nos enteramos demasiado tarde", 1, "Es un problema real, urgente, y lo conoces como nadie. ¡Creemos la solución juntos!"],
            ["Los peces están desapareciendo del río", 2, "¡También es un problema real! Guarda esa idea: otra joven de la aldea lo resolverá. ¿Cuál duele más ahora?"],
            ["El barco de salud tarda mucho en llegar", 2, "¡Otro problema real! Guarda esa idea para otro joven de la aldea. ¿Cuál es el más urgente ahora?"]] },
          { q: "Primero: ¿cómo escuchamos la selva todo el día?", o: [
            ["Cámaras de cine importadas", 0, "Son carísimas y no aguantan la humedad de la selva. Piensa en algo más simple."],
            ["Celulares viejos reutilizados, sujetos en lo alto de los árboles", 1, "¡Genial! Son baratos, livianos y todos tienen micrófono. Reutilizar es innovar."],
            ["Un dron volando 24 horas al día", 0, "La batería de un dron dura minutos, no días."]] },
          { q: "¿Y la energía, en medio de la selva?", o: [
            ["Un generador diésel", 0, "Hace ruido, contamina y necesita combustible. ¡Arruinaría hasta la escucha!"],
            ["Traer un cable desde la ciudad", 0, "La ciudad más cercana está a cientos de kilómetros."],
            ["Un pequeño panel solar en cada celular", 1, "¡Eso! Energía limpia y gratis, con el panel en lo alto del árbol."]] },
          { q: "Para aprender, la IA necesita ejemplos. ¿Qué datos usamos?", o: [
            ["Grabaciones de los sonidos de la selva: monos aulladores, lluvia, truenos, pájaros, motosierras y fuego", 1, "Perfecto: tu conocimiento de la selva convertido en datos."],
            ["Fotos de ciudades bajadas de internet", 0, "Las fotos de ciudades no enseñan a reconocer los sonidos de la selva."],
            ["Ninguno, la IA ya lo sabe todo", 0, "¡No lo sabe! Sin ejemplos locales, el modelo se equivocaría con confianza."]] },
          { q: "Ahora la parte técnica, que te ayudo a programar: ¿qué tipo de modelo usamos?", o: [
            ["Una planilla donde alguien anota los ruidos", 0, "Alguien tendría que escuchar la selva las 24 horas…"],
            ["Un modelo que clasifica sonidos y funciona en el propio celular", 1, "¡Eso! Escribo el código contigo y te explico cada parte."],
            ["Un sitio de pronóstico del tiempo", 0, "El pronóstico del tiempo no detecta motosierras."]] },
          { test: true, q: "¡Todo armado! Probemos el Kaá Centinela.", run: "Ejecutar la prueba",
            fail: "Prueba 1: ¡falsa alarma! El modelo confundió un trueno con una motosierra.",
            q2: "Fallar en una prueba es normal. ¿Cómo lo corregimos?", o: [
            ["Apagar los sensores cuando llueva", 0, "Entonces los taladores aprovecharían la lluvia."],
            ["Subir el volumen de los micrófonos", 0, "Más volumen no le enseña al modelo a distinguir los sonidos."],
            ["Grabar más ejemplos de truenos y de monos aulladores para que la IA aprenda la diferencia", 1, "Exacto. Reentrenando… Prueba 2: ¡97% de acierto!"]] }
        ],
        saved: "idea guardada",
        done: "Nació el <b>Kaá Centinela</b> (Kaá significa selva, en tupí). Kauã aportó el conocimiento de la selva; la IA, la técnica."
      },
      p3: {
        title: "Fase 3 · Proteger",
        place: function (n) { return "Coloca <b>" + n + " sensores Kaá</b> en la selva: toca o haz clic en un punto (o muévete con las flechas y pulsa <kbd>Enter</kbd>). Toca un sensor para quitarlo. La alerta solo llega si la amenaza está dentro del círculo de algún sensor."; },
        text: "Cuando un sensor oiga una motosierra o fuego, parpadea una alerta: tócala (o pulsa <kbd>Enter</kbd>) antes de que se acabe el tiempo para enviar a los guardianes. Cada alerta atendida hace que más comunidades quieran el Kaá Centinela.",
        keys: "<b>Teclado:</b> flechas o <kbd>W</kbd><kbd>A</kbd><kbd>S</kbd><kbd>D</kbd> mueven, <kbd>Enter</kbd> o <kbd>Espacio</kbd> actúan, <kbd>R</kbd> va a la alerta más urgente.",
        sensors: "Sensores", forest: "Selva", saved: "Alertas", comm: "Comunidades", countries: "países", time: "Tiempo",
        go: "¡Guardianes en camino!", plus: function (n) { return "+" + n + " comunidades"; }, lost: "Selva perdida",
        saw: "motosierra", fire: "fuego",
        fail: "La selva sufrió demasiado. Reubica los sensores para cubrir más selva e inténtalo de nuevo.", retry: "Intentar de nuevo",
        done: function (c, p, m) { return "¡Misión cumplida! La deforestación ilegal se desplomó. El Kaá Centinela se volvió un éxito internacional: <b>" + c + " comunidades</b> en <b>" + p + " países</b> lo usan, y Kauã se hizo millonario, con <b>" + m + "</b>."; }
      },
      p4: {
        title: "Fase 4 · Invertir",
        text: "Con el dinero, Kauã invierte donde todo empezó. Elige las mejoras para la aldea.",
        items: { solar: ["Energía solar", "Luz y carga para todas las casas"], agua: ["Agua potable", "Pozo y filtros para todos"], saude: ["Puesto de salud", "Atención cerca de casa"], escola: ["Escuela conectada", "Internet y portátiles para estudiar"], lab: ["Laboratorio de creación", "Otros jóvenes creando soluciones con IA"] },
        balance: "Saldo", done: "hecho", cant: "saldo insuficiente", finish: "Ver el final"
      },
      end: {
        title: "La moraleja",
        moral: ["Cualquier persona, en cualquier lugar, con internet, un portátil y un modelo de IA sofisticado, puede crear empresas y productos y transformar realidades.",
          "Crear soluciones digitales ya no es privilegio de quien estudió informática o de quien tiene mucho dinero.",
          "Conocer el problema local es una gran ventaja. Internet y la IA democratizan el poder de crear."],
        summary: function (a, h, k) { return a + " alertas atendidas · " + h + "% de la selva preservada · " + k + " mejoras en la aldea"; },
        again: "Jugar de nuevo", read: "Leer la fábula"
      },
      next: "Siguiente fase", cont: "Continuar"
    }
  };
  var T = I18N[lang] || I18N.pt;

  // ---------------------------------------------------------------- estrutura
  root.innerHTML = "";
  var stage = document.createElement("div");
  stage.style.position = "relative";
  var canvas = document.createElement("canvas");
  canvas.tabIndex = 0;
  canvas.setAttribute("role", "img");
  canvas.setAttribute("aria-label", T.intro.title);
  var hud = document.createElement("div");
  hud.className = "kg-hud";
  hud.setAttribute("aria-hidden", "true");
  stage.appendChild(canvas);
  stage.appendChild(hud);
  var panel = document.createElement("div");
  panel.className = "kg-panel";
  panel.setAttribute("aria-live", "polite");
  root.appendChild(stage);
  root.appendChild(panel);
  var ctx = canvas.getContext("2d");

  var W = 0, H = 0, DPR = 1;
  function resize() {
    W = stage.clientWidth || 360;
    var vh = window.innerHeight || 800;
    H = W < 640 ? Math.round(Math.min(W * 1.22, Math.max(380, vh * 0.62))) : Math.round(Math.min(W * 0.56, 620, Math.max(360, vh * 0.66)));
    DPR = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.round(W * DPR);
    canvas.height = Math.round(H * DPR);
    canvas.style.height = H + "px";
    if (S.phase === "p3") layoutGrid();
  }

  // ---------------------------------------------------------------- utilidades
  function rng(seed) { var s = seed; return function () { s = (s * 16807) % 2147483647; return (s - 1) / 2147483646; }; }
  function clamp(v, a, b) { return v < a ? a : v > b ? b : v; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function num(v) { return Math.round(v).toLocaleString(T.locale); }
  var R0 = rng(42);
  var STARS = []; for (var i = 0; i < 120; i++) STARS.push([R0(), R0(), 0.5 + R0() * 1.3, R0() * 6]);
  var TREES = []; for (i = 0; i < 26; i++) TREES.push([i / 25 + (R0() - 0.5) * 0.03, 0.55 + R0() * 0.45, R0()]);

  // ---------------------------------------------------------------- desenho comum
  function sky(c1, c2) {
    var g = ctx.createLinearGradient(0, 0, 0, H);
    g.addColorStop(0, c1); g.addColorStop(1, c2);
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  }
  function stars(t, maxY) {
    ctx.fillStyle = "#fff";
    STARS.forEach(function (s) {
      ctx.globalAlpha = reduce ? 0.6 : 0.35 + 0.65 * Math.abs(Math.sin(t * 0.8 + s[3]));
      ctx.fillRect(s[0] * W, s[1] * maxY, s[2], s[2]);
    });
    ctx.globalAlpha = 1;
  }
  function forest(yBase, hMax, color, shift) {
    ctx.fillStyle = color;
    TREES.forEach(function (tr) {
      var x = ((tr[0] + (shift || 0)) % 1.04) * W - 10, h = tr[1] * hMax, r = h * 0.28;
      ctx.fillRect(x - 3, yBase - h + r, 6, h);
      ctx.beginPath(); ctx.arc(x, yBase - h + r, r, 0, 7); ctx.arc(x - r * 0.7, yBase - h + r * 1.4, r * 0.75, 0, 7); ctx.arc(x + r * 0.7, yBase - h + r * 1.35, r * 0.7, 0, 7); ctx.fill();
    });
    ctx.fillRect(0, yBase, W, H - yBase);
  }
  function rr(x, y, w, h, r) { ctx.beginPath(); ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r); ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath(); }
  function label(text, x, y, color, size, align) {
    ctx.font = "600 " + (size || 14) + "px 'Chakra Petch', system-ui, sans-serif";
    ctx.textAlign = align || "center"; ctx.textBaseline = "middle";
    ctx.fillStyle = "rgba(0,0,0,.6)"; ctx.fillText(text, x + 1, y + 1);
    ctx.fillStyle = color || "#fff"; ctx.fillText(text, x, y);
  }

  // Kauã: as mesmas formas do SVG da página da fábula (cabelo liso com franja, urucum, colar de sementes, camiseta)
  var KP = {};
  function P(d) { return new Path2D(d); }
  try {
    KP = {
      legs: P("M38 196 L44 150 L76 150 L82 196 Z"),
      shirt: P("M30 104 Q60 92 90 104 L96 152 L24 152 Z M30 106 L14 150 L22 154 L36 120 Z M90 106 L106 150 L98 154 L84 120 Z"),
      hair: P("M35 60 C33 24 87 24 85 60 L85 72 L79 72 L79 46 Q70 49 61 45 Q52 49 41 46 L41 72 L35 72 Z"),
      long: P("M33 50 L31 100 L89 100 L87 50 Z"),
      paint: P("M43 65 h8 M43 69 h7 M69 65 h8 M70 69 h7"),
      mouth: P("M53 74 Q60 78 67 74"),
      string: P("M44 100 Q60 116 76 100")
    };
  } catch (e) { KP = null; }
  function kaua(x, y, h, shirt, longHair) {
    if (!KP) return;
    var s = h / 210;
    ctx.save(); ctx.translate(x - 60 * s, y - 210 * s); ctx.scale(s, s);
    if (longHair) { ctx.fillStyle = "#0b0b0d"; ctx.fill(KP.long); }
    ctx.fillStyle = "#1f2a33"; ctx.fill(KP.legs);
    ctx.fillStyle = "#6b4126"; ctx.fillRect(38, 194, 18, 8); ctx.fillRect(64, 194, 18, 8);
    ctx.fillStyle = shirt || "#ffb547"; ctx.fill(KP.shirt);
    ctx.fillStyle = "#9c5f37"; ctx.beginPath(); ctx.arc(18, 154, 6, 0, 7); ctx.arc(102, 154, 6, 0, 7); ctx.fill(); ctx.fillRect(52, 78, 16, 20);
    ctx.fillStyle = "#a8693f"; ctx.beginPath(); ctx.ellipse(60, 56, 23, 27, 0, 0, 7); ctx.fill();
    ctx.fillStyle = "#0b0b0d"; ctx.fill(KP.hair);
    ctx.fillStyle = "#1a0f08"; ctx.beginPath(); ctx.ellipse(51, 58, 2.6, 3, 0, 0, 7); ctx.ellipse(69, 58, 2.6, 3, 0, 0, 7); ctx.fill();
    ctx.lineCap = "round"; ctx.strokeStyle = "#d6362a"; ctx.lineWidth = 2.4; ctx.stroke(KP.paint);
    ctx.strokeStyle = "#5a2f19"; ctx.lineWidth = 2; ctx.stroke(KP.mouth);
    ctx.strokeStyle = "#3b2414"; ctx.lineWidth = 1.4; ctx.stroke(KP.string);
    [[46, 103, "#7a1f17"], [52, 108, "#7a1f17"], [68, 108, "#7a1f17"], [74, 103, "#7a1f17"], [49, 106, "#2a1a10"], [71, 106, "#2a1a10"], [60, 111, "#c98a2c"]].forEach(function (c) {
      ctx.fillStyle = c[2]; ctx.beginPath(); ctx.arc(c[0], c[1], 2.6, 0, 7); ctx.fill();
    });
    ctx.restore();
  }
  function satellite(x, y, s, lit) {
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
    ctx.fillStyle = "#1b4fa8"; ctx.strokeStyle = "#8fb6ff"; ctx.lineWidth = 1;
    ctx.fillRect(-40, -6, 26, 12); ctx.strokeRect(-40, -6, 26, 12); ctx.fillRect(14, -6, 26, 12); ctx.strokeRect(14, -6, 26, 12);
    ctx.fillStyle = "#dfe7ee"; ctx.fillRect(-12, -8, 24, 16);
    ctx.fillStyle = lit ? "#1df28c" : "#7f8c85"; ctx.beginPath(); ctx.arc(0, 0, 3.5, 0, 7); ctx.fill();
    ctx.restore();
  }
  function hut(x, y, w, color) {
    ctx.fillStyle = color || "#8a6630";
    ctx.beginPath(); ctx.moveTo(x - w / 2, y); ctx.quadraticCurveTo(x - w / 2, y - w * 0.55, x, y - w * 0.62); ctx.quadraticCurveTo(x + w / 2, y - w * 0.55, x + w / 2, y); ctx.closePath(); ctx.fill();
    ctx.fillStyle = "#3a2810"; ctx.fillRect(x - w * 0.1, y - w * 0.26, w * 0.2, w * 0.26);
  }

  // ---------------------------------------------------------------- estado
  var S = { phase: "intro", t: 0, money: 0, comm: 0, answered: 0, health: 100, bought: {}, keys: {}, cursorVisible: false };
  var floats = [];
  function float(text, x, y, color) { floats.push({ text: text, x: x, y: y, c: color, life: 1.6 }); }
  function drawFloats(dt) {
    floats = floats.filter(function (f) { f.life -= dt; return f.life > 0; });
    floats.forEach(function (f) { ctx.globalAlpha = Math.min(1, f.life); label(f.text, f.x, f.y - (1.6 - f.life) * 30, f.c, 15); });
    ctx.globalAlpha = 1;
  }

  var hudLast = "";
  function setHud(html) { if (html !== hudLast) { hud.innerHTML = html; hudLast = html; } }
  function phaseTag(n) { return '<span class="kg-phase">' + T.phase + " " + n + "/4 · " + T.phases[n - 1] + "</span>"; }

  function setPanel(html, focusFirst) {
    panel.innerHTML = html;
    if (focusFirst) {
      var b = panel.querySelector("button:not([disabled])");
      if (b) try { b.focus({ preventScroll: true }); } catch (e) { b.focus(); }
    }
  }
  function focusCanvas() { try { canvas.focus({ preventScroll: true }); } catch (e) { canvas.focus(); } }
  function btn(act, text, cls, arg) {
    return '<button type="button" class="btn ' + (cls || "") + '" data-act="' + act + '"' + (arg != null ? ' data-arg="' + arg + '"' : "") + ">" + text + "</button>";
  }
  function interactive(on) { canvas.style.touchAction = on ? "none" : "auto"; }

  // ---------------------------------------------------------------- introdução
  function intro() {
    S = { phase: "intro", t: 0, money: 0, comm: 0, answered: 0, health: 100, bought: {}, keys: {}, cursorVisible: false };
    interactive(false);
    setHud("");
    setPanel('<h2 class="kg-title">' + T.intro.title + "</h2><p>" + T.intro.text + '</p><p class="kg-keys">' + T.intro.keys +
      '</p><div class="kg-actions">' + btn("p1", T.intro.start + " ▶", "solid") + '</div><p class="meta" style="margin-top:12px">' + T.intro.note + "</p>");
  }
  function drawIntro(t) {
    sky("#04100b", "#0b2a1c"); stars(t, H * 0.55);
    var g = ctx.createRadialGradient(W * 0.82, H * 0.66, 10, W * 0.82, H * 0.66, W * 0.3);
    g.addColorStop(0, "rgba(255,90,42," + (0.45 + 0.15 * Math.sin(t * 2)) + ")"); g.addColorStop(1, "rgba(255,90,42,0)");
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    forest(H * 0.78, H * 0.38, "#0b2418", 0.37);
    forest(H * 0.9, H * 0.3, "#0f3321", 0);
    kaua(W * (W < 640 ? 0.5 : 0.3), H * 0.97, H * 0.62);
    for (var k = 0; k < 8; k++) {
      ctx.fillStyle = "rgba(233,255,138," + (0.3 + 0.7 * Math.abs(Math.sin(t * 1.3 + k))) + ")";
      ctx.beginPath(); ctx.arc(W * (0.15 + k * 0.1) + Math.sin(t + k) * 12, H * (0.5 + 0.2 * Math.sin(k * 3)) + Math.cos(t * 0.7 + k) * 10, 2.2, 0, 7); ctx.fill();
    }
  }

  // ---------------------------------------------------------------- fase 1: conectar
  function p1() {
    S.phase = "p1"; S.angle = 0; S.target = 0; S.signal = 0; S.sats = []; S.spawn = 0; S.done = false; S.lockT = 0;
    interactive(true);
    setPanel("<h2>" + T.p1.title + "</h2><p>" + T.p1.text + '</p><p class="kg-keys">' + T.p1.keys + "</p>");
    focusCanvas();
    root.scrollIntoView({ block: "start", behavior: reduce ? "auto" : "smooth" });
  }
  function pivot() {
    var u = Math.min(W, H) / 400, top = H * 0.95 - 130 * u * 0.62;
    return { x: W / 2, y: top - 30 * u, roof: top, u: u };
  }
  function satAngle(s) { var p = pivot(); return Math.atan2(s.x - p.x, p.y - s.y); }
  function updateP1(dt) {
    var MAX = 1.35;
    if (S.keys.left) S.target -= 1.6 * dt;
    if (S.keys.right) S.target += 1.6 * dt;
    S.target = clamp(S.target, -MAX, MAX);
    S.angle += (S.target - S.angle) * Math.min(1, dt * 12);
    S.spawn -= dt;
    if (S.spawn <= 0 && S.sats.length < 3) {
      var fromLeft = Math.random() < 0.5;
      S.sats.push({ x: fromLeft ? -40 : W + 40, y: H * (0.12 + Math.random() * 0.3), vx: (fromLeft ? 1 : -1) * W / (6 + Math.random() * 2.5) });
      S.spawn = 1.8 + Math.random() * 1.6;
    }
    S.sats.forEach(function (s) { s.x += s.vx * dt; });
    S.sats = S.sats.filter(function (s) { return s.x > -60 && s.x < W + 60; });
    S.locked = null;
    S.sats.forEach(function (s) { if (Math.abs(satAngle(s) - S.angle) < 0.12) S.locked = s; });
    if (!S.done) {
      S.signal = clamp(S.signal + (S.locked ? 17 : -3.5) * dt, 0, 100);
      if (S.signal >= 100) {
        S.done = true; interactive(false);
        setPanel("<h2>" + T.p1.title + " ✓</h2><p>" + T.p1.done + '</p><div class="kg-actions">' + btn("p2", T.next + " ▶", "solid") + "</div>", true);
      }
    }
    setHud(phaseTag(1) + "<span>" + T.p1.hud + ": <b>" + Math.floor(S.signal) + "%</b>" + (S.locked && !S.done ? " · " + T.p1.locked : "") + "</span>");
  }
  function drawP1(t) {
    sky("#030812", "#0a1c2c"); stars(t, H * 0.7);
    ctx.strokeStyle = "rgba(143,182,255,.18)"; ctx.setLineDash([4, 8]); ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(-20, H * 0.32); ctx.quadraticCurveTo(W / 2, H * 0.02, W + 20, H * 0.32); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(-20, H * 0.5); ctx.quadraticCurveTo(W / 2, H * 0.2, W + 20, H * 0.5); ctx.stroke();
    ctx.setLineDash([]);
    var p = pivot(), len = Math.hypot(W, H);
    // feixe
    ctx.save(); ctx.translate(p.x, p.y); ctx.rotate(S.angle);
    var g = ctx.createLinearGradient(0, 0, 0, -len);
    var on = S.locked || S.done;
    g.addColorStop(0, on ? "rgba(29,242,140,.55)" : "rgba(255,255,255,.18)"); g.addColorStop(1, "rgba(29,242,140,0)");
    ctx.fillStyle = g; ctx.beginPath(); ctx.moveTo(-4, 0); ctx.lineTo(-len * 0.12, -len); ctx.lineTo(len * 0.12, -len); ctx.lineTo(4, 0); ctx.fill();
    if (on) {
      ctx.strokeStyle = "#c9ffe4"; ctx.lineWidth = 2; ctx.setLineDash([2, 12]); ctx.lineDashOffset = -t * 60;
      ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(0, -len); ctx.stroke(); ctx.setLineDash([]);
    }
    ctx.restore();
    var u = Math.min(W, H) / 400;
    S.sats.forEach(function (s) { satellite(s.x, s.y, u * 0.9, s === S.locked); });
    forest(H * 0.86, H * 0.25, "#0a2418", 0.2);
    // oca e antena
    hut(p.x, H * 0.95, 130 * u, "#7a5a2a");
    ctx.fillStyle = "#9aa5ad"; ctx.fillRect(p.x - 2.5 * u, p.y, 5 * u, p.roof - p.y + 4);
    ctx.save(); ctx.translate(p.x, p.y); ctx.rotate(S.angle);
    ctx.fillStyle = "#dfe7ee"; ctx.strokeStyle = "#9aa5ad"; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(-26 * u, -4 * u); ctx.quadraticCurveTo(0, 16 * u, 26 * u, -4 * u); ctx.closePath(); ctx.fill(); ctx.stroke();
    ctx.fillStyle = "#9aa5ad"; ctx.fillRect(-1.5 * u, -20 * u, 3 * u, 18 * u);
    ctx.fillStyle = S.locked || S.done ? "#1df28c" : "#ff8a7a"; ctx.beginPath(); ctx.arc(0, -21 * u, 3.5 * u, 0, 7); ctx.fill();
    ctx.restore();
    // medidor
    var bw = Math.min(260, W * 0.5), bx = W / 2 - bw / 2, by = H - 22;
    rr(bx, by, bw, 10, 5); ctx.fillStyle = "rgba(0,0,0,.6)"; ctx.fill();
    rr(bx, by, bw * S.signal / 100, 10, 5); ctx.fillStyle = "#1df28c"; ctx.fill();
  }

  // ---------------------------------------------------------------- fase 2: criar com a IA
  function p2() {
    S.phase = "p2"; S.step = 0; S.slots = [false, false, false, false]; S.saved = {}; S.testing = 0; S.testFail = false; S.chosen = null;
    interactive(false);
    renderStep();
  }
  function renderStep(reply) {
    var st = T.p2.steps[S.step];
    var html = "<h2>" + T.p2.title + "</h2>";
    if (S.step === 0 && !reply && !Object.keys(S.saved).length) html += "<p>" + T.p2.text + "</p>";
    var q = st.test && S.testFail ? st.q2 : st.q;
    if (st.test && S.testFail) html += '<div class="kg-ai"><span class="kg-who">' + T.p2.ai + "</span><p>" + st.fail + "</p></div>";
    html += '<div class="kg-ai"><span class="kg-who">' + T.p2.ai + "</span><p>" + q + "</p></div>";
    if (reply) {
      html += '<div class="kg-ai"><span class="kg-who k">' + T.p2.kaua + "</span><p>" + esc(reply.said) + "</p></div>";
      html += '<div class="kg-ai"><span class="kg-who">' + T.p2.ai + "</span><p>" + (reply.ok ? "✓ " : "") + reply.text + "</p></div>";
    }
    if (st.test && !S.testFail) {
      html += '<div class="kg-actions">' + btn("runtest", T.p2.steps[5].run + " ▶", "solid") + "</div>";
    } else if (reply && reply.ok) {
      html += '<div class="kg-actions">' + btn("nextstep", T.cont + " ▶", "solid") + "</div>";
    } else {
      html += '<div class="kg-choices">';
      st.o.forEach(function (o, i) {
        var state = S.wrong && S.wrong[i] ? " wrong" : S.saved[S.step + ":" + i] ? " wrong" : "";
        var dis = state ? " disabled" : "";
        html += '<button type="button" class="kg-choice' + state + '" data-act="choose" data-arg="' + i + '"' + dis + '><span class="n">' + (i + 1) + "</span><span>" + esc(o[0]) +
          (S.saved[S.step + ":" + i] ? "<small>" + T.p2.saved + "</small>" : "") + "</span></button>";
      });
      html += "</div>";
    }
    setPanel(html, true);
  }
  function choose(i) {
    var st = T.p2.steps[S.step], o = st.o[i];
    if (!o) return;
    if (o[1] === 1) {
      S.wrong = null;
      if (S.step >= 1 && S.step <= 4) S.slots[S.step - 1] = true;
      if (st.test) { S.testing = 2.2; S.fixed = true; }
      renderStep({ ok: true, text: o[2], said: o[0] });
    } else {
      if (o[1] === 2) S.saved[S.step + ":" + i] = true;
      else { S.wrong = S.wrong || {}; S.wrong[i] = true; }
      renderStep({ ok: false, text: o[2], said: o[0] });
    }
  }
  function nextStep() {
    S.wrong = null;
    if (S.step === 5) {
      S.slotsDone = true;
      setPanel("<h2>" + T.p2.title + " ✓</h2><p>" + T.p2.done + '</p><div class="kg-actions">' + btn("p3", T.next + " ▶", "solid") + "</div>", true);
      return;
    }
    S.step++;
    renderStep();
  }
  function runTest() {
    S.testing = 2.2; S.fixed = false;
    var b = panel.querySelector('[data-act="runtest"]'); if (b) b.disabled = true;
    setTimeout(function () { if (S.phase === "p2") { S.testFail = true; renderStep(); } }, reduce ? 300 : 2000); }
  function slotRects() {
    var n = 4, rects = [];
    if (W < 640) {
      var w = (W - 48) / 2, h = Math.min(H * 0.2, 120);
      for (var i = 0; i < n; i++) rects.push({ x: 16 + (i % 2) * (w + 16), y: H * 0.36 + Math.floor(i / 2) * (h + 16), w: w, h: h });
    } else {
      var x0 = W * 0.3, ww = (W * 0.66 - 3 * 14) / 4, hh = Math.min(H * 0.3, 150);
      for (i = 0; i < n; i++) rects.push({ x: x0 + i * (ww + 14), y: H * 0.38, w: ww, h: hh });
    }
    return rects;
  }
  function slotIcon(i, x, y, s, on) {
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
    ctx.globalAlpha = on ? 1 : 0.28;
    if (i === 0) { ctx.fillStyle = "#111"; ctx.strokeStyle = "#1df28c"; ctx.lineWidth = 2; rr(-10, -18, 20, 36, 4); ctx.fill(); ctx.stroke(); ctx.fillStyle = "#0b3322"; ctx.fillRect(-7, -13, 14, 24); }
    if (i === 1) { ctx.fillStyle = "#1b4fa8"; ctx.strokeStyle = "#8fb6ff"; ctx.lineWidth = 1.5; ctx.fillRect(-20, -10, 40, 20); ctx.strokeRect(-20, -10, 40, 20); ctx.beginPath(); ctx.moveTo(-7, -10); ctx.lineTo(-7, 10); ctx.moveTo(7, -10); ctx.lineTo(7, 10); ctx.stroke(); ctx.fillStyle = "#ffd27a"; ctx.beginPath(); ctx.arc(16, -18, 6, 0, 7); ctx.fill(); }
    if (i === 2) { ctx.strokeStyle = "#ffb547"; ctx.lineWidth = 3; ctx.beginPath(); for (var k = -20; k <= 20; k += 4) { ctx.moveTo(k, -Math.abs(Math.sin(k * 0.7)) * 14 - 2); ctx.lineTo(k, Math.abs(Math.sin(k * 0.7)) * 14 + 2); } ctx.stroke(); }
    if (i === 3) { ctx.fillStyle = "#0b3322"; ctx.strokeStyle = "#1df28c"; ctx.lineWidth = 2; rr(-14, -14, 28, 28, 4); ctx.fill(); ctx.stroke(); ctx.beginPath(); for (k = -8; k <= 8; k += 8) { ctx.moveTo(k, -14); ctx.lineTo(k, -20); ctx.moveTo(k, 14); ctx.lineTo(k, 20); ctx.moveTo(-14, k); ctx.lineTo(-20, k); ctx.moveTo(14, k); ctx.lineTo(20, k); } ctx.stroke(); label("IA", 0, 1, "#1df28c", 11); }
    ctx.restore();
  }
  function drawP2(t, dt) {
    sky("#050b09", "#0b1a14");
    ctx.strokeStyle = "rgba(29,242,140,.07)"; ctx.lineWidth = 1;
    for (var x = 0; x < W; x += 28) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke(); }
    for (var y = 0; y < H; y += 28) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }
    var rects = slotRects(), all = S.slots.every(Boolean);
    if (W >= 640) {
      kaua(W * 0.13, H * 0.93, H * 0.66);
      // notebook
      var nx = W * 0.13, ny = H * 0.93 - H * 0.66 * 0.3;
      ctx.fillStyle = "#1d2320"; rr(nx - 42, ny - 52, 84, 52, 6); ctx.fill();
      ctx.fillStyle = "#04140c"; ctx.fillRect(nx - 36, ny - 46, 72, 40);
      ctx.fillStyle = "#1df28c"; ctx.font = "600 10px ui-monospace, monospace"; ctx.textAlign = "left"; ctx.fillText("> _", nx - 30, ny - 26);
      ctx.fillStyle = "#3a443f"; ctx.fillRect(nx - 50, ny, 100, 7);
    }
    var title = all ? "KAÁ SENTINELA" : "";
    if (lang === "es" && all) title = "KAÁ CENTINELA";
    if (lang === "en" && all) title = "KAÁ SENTINEL";
    var cx = W < 640 ? W / 2 : W * 0.3 + W * 0.33, cy = W < 640 ? H * 0.24 : H * 0.24;
    if (all) {
      ctx.font = "400 " + Math.round(Math.min(34, W / 14)) + "px 'Russo One', 'Chakra Petch', sans-serif"; ctx.textAlign = "center"; ctx.textBaseline = "middle";
      ctx.fillStyle = "#1df28c"; ctx.shadowColor = "#1df28c"; ctx.shadowBlur = 18; ctx.fillText(title, cx, cy); ctx.shadowBlur = 0;
    } else {
      label(T.p2.title.split("·")[1].trim().toUpperCase(), cx, cy, "#ffb547", Math.min(22, W / 20));
    }
    rects.forEach(function (r, i) {
      var on = S.slots[i];
      if (all) {
        ctx.strokeStyle = "rgba(29,242,140,.5)"; ctx.setLineDash([4, 6]); ctx.lineDashOffset = reduce ? 0 : -t * 30;
        ctx.beginPath(); ctx.moveTo(r.x + r.w / 2, r.y); ctx.lineTo(cx, cy + 18); ctx.stroke(); ctx.setLineDash([]);
      }
      rr(r.x, r.y, r.w, r.h, 12);
      ctx.fillStyle = on ? "rgba(29,242,140,.12)" : "rgba(255,255,255,.03)"; ctx.fill();
      ctx.strokeStyle = on ? "#1df28c" : "rgba(255,255,255,.18)"; ctx.lineWidth = on ? 2 : 1; ctx.setLineDash(on ? [] : [6, 6]); ctx.stroke(); ctx.setLineDash([]);
      slotIcon(i, r.x + r.w / 2, r.y + r.h * 0.42, Math.min(1.6, r.h / 70), on);
      label(T.p2.slots[i], r.x + r.w / 2, r.y + r.h - 16, on ? "#fff" : "#7f8c85", 13);
    });
    // onda sonora do teste
    if (S.testing > 0 || S.step === 5) {
      if (S.testing > 0) S.testing -= dt;
      var wy = W < 640 ? H * 0.88 : H * 0.84, ww = W < 640 ? W - 40 : W * 0.6, wx = W < 640 ? 20 : W * 0.33;
      ctx.strokeStyle = S.testFail && !S.fixed ? "#ff8a7a" : "#1df28c"; ctx.lineWidth = 2; ctx.beginPath();
      for (var k = 0; k <= ww; k += 3) {
        var amp = S.testing > 0 ? 18 * Math.sin(k * 0.05 + t * 9) * Math.sin(k * 0.013 + t) : 3 * Math.sin(k * 0.2);
        if (k === 0) ctx.moveTo(wx + k, wy + amp); else ctx.lineTo(wx + k, wy + amp);
      }
      ctx.stroke();
      if (S.fixed && S.testing <= 0) label("97% ✓", wx + ww / 2, wy - 22, "#1df28c", 18);
      else if (S.testFail && !S.fixed && S.testing <= 0) label("✗", wx + ww / 2, wy - 22, "#ff8a7a", 18);
    }
    setHud(phaseTag(2));
  }

  // ---------------------------------------------------------------- fase 3: proteger
  var G = {};
  function layoutGrid() {
    var top = W < 640 ? 64 : 48;
    G.cols = W < 640 ? 7 : 12; G.rows = W < 640 ? 8 : 7;
    G.cell = Math.floor(Math.min((W - 16) / G.cols, (H - top - 10) / G.rows));
    G.x0 = Math.round((W - G.cell * G.cols) / 2); G.y0 = top + Math.round((H - top - 10 - G.cell * G.rows) / 2);
  }
  function p3() {
    S.phase = "p3"; layoutGrid();
    S.trees = []; for (var i = 0; i < G.cols * G.rows; i++) S.trees.push(0);
    S.sensors = []; S.maxSensors = W < 640 ? 4 : 5; S.threats = []; S.running = false; S.time = 45; S.spawn = 1.2;
    S.answered = 0; S.comm = 0; S.money = 0; S.health = 100; S.cur = { c: Math.floor(G.cols / 2), r: Math.floor(G.rows / 2) }; S.over = false; floats = [];
    S.cursorVisible = false;
    interactive(true);
    setPanel("<h2>" + T.p3.title + "</h2><p>" + T.p3.place(S.maxSensors) + "</p><p>" + T.p3.text + '</p><p class="kg-keys">' + T.p3.keys + "</p>");
    focusCanvas();
  }
  var RANGE = 1.8; // alcance do sensor, em casas (centro a centro)
  function cellCenter(c, r) { return { x: G.x0 + (c + 0.5) * G.cell, y: G.y0 + (r + 0.5) * G.cell }; }
  function covered(c, r) { return S.sensors.some(function (s) { return Math.hypot(s.c - c, s.r - r) <= RANGE; }); }
  function actAt(c, r) {
    if (S.phase !== "p3" || S.over) return;
    if (c < 0 || r < 0 || c >= G.cols || r >= G.rows) return;
    // atender alerta (tolerância de uma casa ao redor)
    var best = null, bd = 9;
    S.threats.forEach(function (th) { if (!th.det) return; var d = Math.hypot(th.c - c, th.r - r); if (d < 1.01 && d < bd) { bd = d; best = th; } });
    if (best) {
      S.threats.splice(S.threats.indexOf(best), 1);
      S.answered++;
      var n = 40 + Math.floor(Math.random() * 50); S.comm += n; S.money += 0.55;
      var p = cellCenter(best.c, best.r); float(T.p3.go, p.x, p.y - 10, "#1df28c"); float(T.p3.plus(n), p.x, p.y + 14, "#ffb547");
      return;
    }
    if (!S.running) {
      var idx = -1; S.sensors.forEach(function (s, i) { if (s.c === c && s.r === r) idx = i; });
      if (idx > -1) S.sensors.splice(idx, 1);
      else if (S.sensors.length < S.maxSensors) S.sensors.push({ c: c, r: r });
      if (S.sensors.length === S.maxSensors) {
        S.running = true; S.startDelay = 1.2;
        setPanel("<h2>" + T.p3.title + "</h2><p>" + T.p3.text + '</p><p class="kg-keys">' + T.p3.keys + "</p>");
      }
    }
  }
  function spawnThreat() {
    var free = [];
    for (var i = 0; i < S.trees.length; i++) {
      var c = i % G.cols, r = Math.floor(i / G.cols);
      if (S.trees[i] === 0 && !S.threats.some(function (t) { return t.c === c && t.r === r; })) free.push([c, r]);
    }
    if (!free.length) return;
    var f = free[Math.floor(Math.random() * free.length)];
    S.threats.push({ c: f[0], r: f[1], type: Math.random() < 0.6 ? "saw" : "fire", t: 0, max: 6.5, det: covered(f[0], f[1]) });
  }
  function destroy(th) {
    var cells = [[th.c, th.r]];
    var nb = [[1, 0], [-1, 0], [0, 1], [0, -1]];
    if (th.type === "fire") nb.forEach(function (d) { if (Math.random() < 0.6) cells.push([th.c + d[0], th.r + d[1]]); });
    else { var d = nb[Math.floor(Math.random() * 4)]; cells.push([th.c + d[0], th.r + d[1]]); }
    cells.forEach(function (x) { if (x[0] >= 0 && x[1] >= 0 && x[0] < G.cols && x[1] < G.rows) { var k = x[1] * G.cols + x[0]; if (S.trees[k] === 0) S.trees[k] = th.type === "fire" ? 2 : 1; } });
    var p = cellCenter(th.c, th.r); float(T.p3.lost, p.x, p.y, "#ff8a7a");
  }
  function updateP3(dt) {
    if (S.running && !S.over) {
      if (S.startDelay > 0) S.startDelay -= dt;
      else {
        S.time -= dt;
        S.spawn -= dt;
        if (S.spawn <= 0) { spawnThreat(); var prog = 1 - S.time / 45; S.spawn = 2.5 - 1.1 * prog + Math.random() * 0.5; }
        S.threats = S.threats.filter(function (th) { th.t += dt; if (th.t >= th.max) { destroy(th); return false; } return true; });
        var alive = S.trees.filter(function (v) { return v === 0; }).length;
        S.health = Math.round(alive / S.trees.length * 100);
        if (S.health < 45) {
          S.over = true; interactive(false);
          setPanel("<h2>" + T.p3.title + "</h2><p>" + T.p3.fail + '</p><div class="kg-actions">' + btn("p3", T.p3.retry, "solid") + "</div>", true);
        } else if (S.time <= 0) {
          S.over = true; S.threats = []; interactive(false);
          S.money = Math.max(S.money, 6.5);
          var countries = Math.min(37, 3 + Math.floor(S.comm / 30));
          S.countries = countries;
          setPanel("<h2>" + T.p3.title + " ✓</h2><p>" + T.p3.done(num(S.comm), countries, T.money(S.money)) + '</p><div class="kg-actions">' + btn("p4", T.next + " ▶", "solid") + "</div>", true);
        }
      }
    }
    var info = phaseTag(3) + "<span>" + T.p3.sensors + ": <b>" + S.sensors.length + "/" + S.maxSensors + "</b></span>" +
      "<span>" + T.p3.forest + ": <b>" + S.health + "%</b></span>";
    if (S.running) info += "<span>" + T.p3.time + ": <b>" + Math.max(0, Math.ceil(S.time)) + "s</b></span><span>" + T.p3.saved + ": <b>" + S.answered + "</b></span>";
    info += '<span class="kg-money">' + T.p3.comm + ": " + num(S.comm) + " · " + T.money(S.money) + "</span>";
    setHud(info);
  }
  function drawThreatIcon(type, x, y, s, t) {
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
    if (type === "saw") {
      ctx.fillStyle = "#ff7a1a"; rr(-14, -6, 16, 12, 3); ctx.fill();
      ctx.fillStyle = "#c9d1d6"; rr(2, -3, 18, 6, 3); ctx.fill();
      ctx.strokeStyle = "#ff6b3d"; ctx.lineWidth = 2; ctx.beginPath(); var j = reduce ? 0 : Math.sin(t * 40) * 1.5; ctx.moveTo(-16, -12 + j); ctx.lineTo(-11, -16 + j); ctx.lineTo(-6, -12 + j); ctx.lineTo(-1, -16 + j); ctx.stroke();
    } else {
      var f = reduce ? 1 : 1 + 0.12 * Math.sin(t * 18);
      ctx.fillStyle = "#ff5a2a"; ctx.beginPath(); ctx.moveTo(0, -16 * f); ctx.quadraticCurveTo(12, -2, 8, 8); ctx.quadraticCurveTo(0, 14, -8, 8); ctx.quadraticCurveTo(-12, -2, 0, -16 * f); ctx.fill();
      ctx.fillStyle = "#ffd27a"; ctx.beginPath(); ctx.moveTo(0, -6 * f); ctx.quadraticCurveTo(5, 2, 3, 7); ctx.quadraticCurveTo(0, 10, -3, 7); ctx.quadraticCurveTo(-5, 2, 0, -6 * f); ctx.fill();
    }
    ctx.restore();
  }
  function drawP3(t) {
    ctx.fillStyle = "#06140e"; ctx.fillRect(0, 0, W, H);
    var c = G.cell;
    for (var i = 0; i < S.trees.length; i++) {
      var cc = i % G.cols, r = Math.floor(i / G.cols), p = cellCenter(cc, r), st = S.trees[i];
      ctx.fillStyle = (cc + r) % 2 ? "#0b2418" : "#0c2819"; ctx.fillRect(G.x0 + cc * c, G.y0 + r * c, c, c);
      if (st === 0) {
        ctx.fillStyle = (i * 7) % 3 === 0 ? "#1b5e38" : (i * 7) % 3 === 1 ? "#17502f" : "#206b41";
        ctx.beginPath(); ctx.arc(p.x - c * 0.12, p.y + c * 0.04, c * 0.3, 0, 7); ctx.arc(p.x + c * 0.14, p.y - c * 0.08, c * 0.28, 0, 7); ctx.arc(p.x + c * 0.08, p.y + c * 0.18, c * 0.24, 0, 7); ctx.fill();
      } else {
        ctx.fillStyle = st === 1 ? "#6b4a2a" : "#2a2a2a";
        ctx.beginPath(); ctx.ellipse(p.x, p.y + c * 0.1, c * 0.16, c * 0.1, 0, 0, 7); ctx.fill();
        if (st === 2) { ctx.fillStyle = "rgba(90,90,90,.5)"; ctx.beginPath(); ctx.arc(p.x, p.y - c * 0.1, c * 0.25, 0, 7); ctx.fill(); }
      }
    }
    // alcance e sensores (círculos recortados na área da floresta)
    ctx.save(); ctx.beginPath(); ctx.rect(G.x0, G.y0, G.cols * c, G.rows * c); ctx.clip();
    S.sensors.forEach(function (s) {
      var p = cellCenter(s.c, s.r);
      ctx.fillStyle = "rgba(29,242,140,.08)"; ctx.strokeStyle = "rgba(29,242,140,.45)"; ctx.lineWidth = 1.5;
      ctx.beginPath(); ctx.arc(p.x, p.y, RANGE * c, 0, 7); ctx.fill(); ctx.stroke();
      if (S.running && !reduce) {
        var k = (t * 0.6 + s.c * 0.13) % 1;
        ctx.strokeStyle = "rgba(29,242,140," + (0.5 * (1 - k)) + ")"; ctx.beginPath(); ctx.arc(p.x, p.y, k * (RANGE * c), 0, 7); ctx.stroke();
      }
    });
    if (S.hover && !S.running && !S.cursorVisible) {
      ctx.strokeStyle = "rgba(29,242,140,.35)"; ctx.setLineDash([4, 6]); ctx.lineWidth = 1.5;
      var hp = cellCenter(S.hover.c, S.hover.r); ctx.beginPath(); ctx.arc(hp.x, hp.y, RANGE * c, 0, 7); ctx.stroke(); ctx.setLineDash([]);
    }
    ctx.restore();
    S.sensors.forEach(function (s) {
      var p = cellCenter(s.c, s.r), sc = c / 50;
      ctx.save(); ctx.translate(p.x, p.y); ctx.scale(sc, sc);
      ctx.fillStyle = "#1b4fa8"; ctx.fillRect(-12, -24, 24, 8); ctx.strokeStyle = "#8fb6ff"; ctx.lineWidth = 1; ctx.strokeRect(-12, -24, 24, 8);
      ctx.fillStyle = "#111"; ctx.strokeStyle = "#1df28c"; ctx.lineWidth = 2; rr(-8, -14, 16, 28, 3); ctx.fill(); ctx.stroke();
      ctx.fillStyle = "#1df28c"; ctx.fillRect(-5, -9, 10, 16);
      ctx.restore();
    });
    // ameaças detectadas
    S.threats.forEach(function (th) {
      if (!th.det) return;
      var p = cellCenter(th.c, th.r), left = 1 - th.t / th.max;
      var pulse = reduce ? 0.5 : 0.5 + 0.5 * Math.sin(t * 10);
      ctx.fillStyle = "rgba(255,107,61," + (0.18 + 0.2 * pulse) + ")"; ctx.beginPath(); ctx.arc(p.x, p.y, c * 0.55, 0, 7); ctx.fill();
      ctx.strokeStyle = left < 0.35 ? "#ff3b3b" : "#ffb547"; ctx.lineWidth = Math.max(3, c * 0.08);
      ctx.beginPath(); ctx.arc(p.x, p.y, c * 0.5, -Math.PI / 2, -Math.PI / 2 + left * Math.PI * 2); ctx.stroke();
      drawThreatIcon(th.type, p.x, p.y, c / 44, t);
      label("!", p.x + c * 0.42, p.y - c * 0.42, "#fff", Math.max(12, c * 0.3));
    });
    // cursor de teclado
    if (S.cursorVisible && !S.over) {
      ctx.strokeStyle = "#fff"; ctx.lineWidth = 2; ctx.setLineDash([5, 4]);
      ctx.strokeRect(G.x0 + S.cur.c * c + 2, G.y0 + S.cur.r * c + 2, c - 4, c - 4); ctx.setLineDash([]);
    }
  }

  // ---------------------------------------------------------------- fase 4: investir
  var ITEMS = [["solar", 1.4], ["agua", 1.1], ["saude", 1.9], ["escola", 1.6], ["lab", 2.2]];
  function p4() {
    S.phase = "p4"; S.bought = {}; S.grow = {}; interactive(false);
    renderShop(true);
  }
  function renderShop(focus) {
    var html = "<h2>" + T.p4.title + "</h2><p>" + T.p4.text + "</p><p><b>" + T.p4.balance + ":</b> <span class=\"hl-amber\">" + T.money(S.money) + '</span></p><div class="kg-choices">';
    var anyAffordable = false;
    ITEMS.forEach(function (it, i) {
      var name = T.p4.items[it[0]], has = S.bought[it[0]], can = S.money + 1e-9 >= it[1];
      if (!has && can) anyAffordable = true;
      html += '<button type="button" class="kg-choice buy' + (has ? " bought" : !can ? " cant" : "") + '" data-act="buy" data-arg="' + i + '"' + (has || !can ? " disabled" : "") +
        '><span class="n">' + (i + 1) + "</span><span><b>" + name[0] + "</b> · " + T.money(it[1]) + "<small>" + (has ? "✓ " + T.p4.done : !can ? T.p4.cant : name[1]) + "</small></span></button>";
    });
    html += "</div>";
    var count = Object.keys(S.bought).length;
    if (count && (count === ITEMS.length || !anyAffordable || count >= 1)) html += '<div class="kg-actions">' + btn("end", T.p4.finish + " ▶", count === ITEMS.length || !anyAffordable ? "solid" : "") + "</div>";
    setPanel(html, focus);
  }
  function buy(i) {
    var it = ITEMS[i];
    if (!it || S.bought[it[0]] || S.money + 1e-9 < it[1]) return;
    S.money = Math.round((S.money - it[1]) * 10) / 10; S.bought[it[0]] = true; S.grow[it[0]] = 0;
    renderShop(false);
    var b = panel.querySelector(".kg-choice:not([disabled])") || panel.querySelector(".kg-actions .btn");
    if (b) try { b.focus({ preventScroll: true }); } catch (e) { b.focus(); }
  }
  function drawVillage(t, dt, party) {
    var day = Object.keys(S.bought).length / ITEMS.length;
    sky(day > 0 ? "#3d8fc4" : "#0a1a2a", day > 0 ? "#bfe3f5" : "#173040");
    if (day > 0) { ctx.fillStyle = "#ffd27a"; ctx.beginPath(); ctx.arc(W * 0.85, H * 0.15, Math.min(W, H) * 0.06, 0, 7); ctx.fill(); }
    else stars(t, H * 0.5);
    forest(H * 0.55, H * 0.25, day > 0 ? "#1e5a35" : "#0d2a1b", 0.1);
    ctx.fillStyle = day > 0 ? "#3f7a37" : "#16331c"; ctx.fillRect(0, H * 0.55, W, H);
    ctx.fillStyle = "#1b5f8a"; ctx.beginPath(); ctx.moveTo(0, H * 0.95); ctx.quadraticCurveTo(W * 0.5, H * 0.91, W, H * 0.96); ctx.lineTo(W, H); ctx.lineTo(0, H); ctx.fill();
    for (var k in S.grow) S.grow[k] = Math.min(1, S.grow[k] + dt * (reduce ? 10 : 1.5));
    var u = Math.min(W / 800, H / 450), base = H * 0.72;
    var narrow = W < 640;
    var hx = narrow ? [0.18, 0.5, 0.82] : [0.1, 0.24, 0.38];
    hx.forEach(function (fx, i) {
      var x = W * fx, y = narrow ? H * 0.5 : base, w = (narrow ? 90 : 110) * u * (narrow ? 1.6 : 1);
      hut(x, y, w, "#8a6630");
      if (S.bought.solar) {
        var g = S.grow.solar;
        ctx.save(); ctx.globalAlpha = g; ctx.translate(x - w * 0.18, y - w * 0.45); ctx.rotate(-0.35);
        ctx.fillStyle = "#1b4fa8"; ctx.strokeStyle = "#8fb6ff"; ctx.fillRect(-w * 0.16, -w * 0.06, w * 0.32, w * 0.12); ctx.strokeRect(-w * 0.16, -w * 0.06, w * 0.32, w * 0.12); ctx.restore();
        ctx.fillStyle = "rgba(255,210,122," + 0.8 * g + ")"; ctx.fillRect(x - w * 0.1, y - w * 0.26, w * 0.2, w * 0.26);
      }
    });
    function build(key, fn) { if (!S.bought[key]) return; ctx.save(); ctx.globalAlpha = S.grow[key]; fn(1 - S.grow[key]); ctx.restore(); }
    var spots = narrow
      ? { agua: [0.14, 0.72], saude: [0.42, 0.72], escola: [0.76, 0.72], lab: [0.42, 0.88] }
      : { agua: [0.5, 0.72], saude: [0.64, 0.72], escola: [0.82, 0.72], lab: [0.36, 0.86] };
    var su = narrow ? u * 1.5 : u;
    build("agua", function (off) {
      var x = W * spots.agua[0], y = H * spots.agua[1] + off * 30;
      ctx.fillStyle = "#6c757d"; ctx.fillRect(x - 24 * su, y - 70 * su, 5 * su, 70 * su); ctx.fillRect(x + 19 * su, y - 70 * su, 5 * su, 70 * su);
      ctx.fillStyle = "#3aa0d8"; rr(x - 32 * su, y - 110 * su, 64 * su, 44 * su, 8 * su); ctx.fill();
      ctx.fillStyle = "#e8f6ff"; ctx.beginPath(); ctx.moveTo(x, y - 102 * su); ctx.quadraticCurveTo(x + 12 * su, y - 84 * su, x, y - 78 * su); ctx.quadraticCurveTo(x - 12 * su, y - 84 * su, x, y - 102 * su); ctx.fill();
    });
    build("saude", function (off) {
      var x = W * spots.saude[0], y = H * spots.saude[1] + off * 30;
      ctx.fillStyle = "#eef2f0"; ctx.fillRect(x - 55 * su, y - 80 * su, 110 * su, 80 * su);
      ctx.fillStyle = "#9aa5ad"; ctx.beginPath(); ctx.moveTo(x - 62 * su, y - 78 * su); ctx.lineTo(x, y - 110 * su); ctx.lineTo(x + 62 * su, y - 78 * su); ctx.fill();
      ctx.fillStyle = "#1df28c"; ctx.fillRect(x - 8 * su, y - 70 * su, 16 * su, 40 * su); ctx.fillRect(x - 20 * su, y - 58 * su, 40 * su, 16 * su);
    });
    build("escola", function (off) {
      var x = W * spots.escola[0], y = H * spots.escola[1] + off * 30;
      ctx.fillStyle = "#ffb547"; ctx.fillRect(x - 65 * su, y - 80 * su, 130 * su, 80 * su);
      ctx.fillStyle = "#a8571c"; ctx.beginPath(); ctx.moveTo(x - 72 * su, y - 78 * su); ctx.lineTo(x, y - 115 * su); ctx.lineTo(x + 72 * su, y - 78 * su); ctx.fill();
      ctx.fillStyle = "#0b3322"; ctx.fillRect(x - 50 * su, y - 60 * su, 26 * su, 20 * su); ctx.fillRect(x + 24 * su, y - 60 * su, 26 * su, 20 * su);
      ctx.strokeStyle = "#1df28c"; ctx.lineWidth = 3 * su; ctx.lineCap = "round";
      for (var a = 1; a <= 2; a++) { ctx.globalAlpha = S.grow.escola * (reduce ? 1 : 0.5 + 0.5 * Math.sin(t * 4 - a)); ctx.beginPath(); ctx.arc(x, y - 112 * su, a * 12 * su, -Math.PI * 0.8, -Math.PI * 0.2); ctx.stroke(); }
    });
    build("lab", function (off) {
      var x = W * spots.lab[0], y = H * spots.lab[1] + off * 20, h = (narrow ? 105 : 90) * su;
      [["#1df28c", false], ["#ff8a7a", true], ["#8fb6ff", false]].forEach(function (k, i) {
        var kx = x + (i - 1) * h * 0.75;
        kaua(kx, y, h, k[0], k[1]);
        ctx.fillStyle = "#1df28c"; ctx.shadowColor = "#1df28c"; ctx.shadowBlur = 10; ctx.fillRect(kx + h * 0.08, y - h * 0.32, h * 0.22, h * 0.13); ctx.shadowBlur = 0;
      });
    });
    var ky = narrow ? H * 0.93 : H * 0.9;
    if (!S.bought.lab || !narrow) kaua(narrow ? W * 0.86 : W * 0.56, ky, (narrow ? 110 : 150) * su * (narrow ? 0.8 : 1));
    if (party && !reduce) fireworks(t, dt);
  }
  var sparks = [];
  function fireworks(t, dt) {
    if (Math.random() < dt * 1.6) {
      var x = W * (0.15 + Math.random() * 0.7), y = H * (0.1 + Math.random() * 0.25), col = Math.random() < 0.5 ? "#1df28c" : "#ffb547";
      for (var i = 0; i < 26; i++) { var a = i / 26 * Math.PI * 2, v = 60 + Math.random() * 60; sparks.push({ x: x, y: y, vx: Math.cos(a) * v, vy: Math.sin(a) * v, life: 1.2, c: col }); }
    }
    sparks = sparks.filter(function (s) { s.life -= dt; s.x += s.vx * dt; s.y += s.vy * dt; s.vy += 40 * dt; return s.life > 0; });
    sparks.forEach(function (s) { ctx.globalAlpha = Math.max(0, s.life); ctx.fillStyle = s.c; ctx.fillRect(s.x, s.y, 3, 3); });
    ctx.globalAlpha = 1;
  }
  function end() {
    S.phase = "end"; interactive(false);
    var m = T.end.moral.map(function (l) { return "<p>" + l + "</p>"; }).join("");
    setPanel('<h2 class="kg-title">' + T.end.title + '</h2><div class="kg-moral">' + m + '</div><p class="meta">' + T.end.summary(S.answered, S.health, Object.keys(S.bought).length) + " · " + T.intro.note +
      '</p><div class="kg-actions">' + btn("again", "↺ " + T.end.again, "solid") + '<a class="btn amber" href="fabula-kaua.html">' + T.end.read + "</a></div>", true);
    setHud('<span class="kg-phase">✓ ' + T.intro.title + "</span>");
  }

  // ---------------------------------------------------------------- entrada
  var ACTIONS = {
    p1: p1, p2: p2, p3: p3, p4: p4, end: end, again: intro,
    choose: function (a) { choose(+a); }, nextstep: nextStep, runtest: runTest, buy: function (a) { buy(+a); }
  };
  panel.addEventListener("click", function (e) {
    var b = e.target.closest("[data-act]");
    if (!b || b.disabled) return;
    ACTIONS[b.getAttribute("data-act")](b.getAttribute("data-arg"));
  });
  function pos(e) { var r = canvas.getBoundingClientRect(); return { x: e.clientX - r.left, y: e.clientY - r.top }; }
  function aim(p) { var pv = pivot(); S.target = clamp(Math.atan2(p.x - pv.x, pv.y - p.y), -1.35, 1.35); }
  function cellAt(p) { return { c: Math.floor((p.x - G.x0) / G.cell), r: Math.floor((p.y - G.y0) / G.cell) }; }
  var down = false;
  canvas.addEventListener("pointerdown", function (e) {
    var p = pos(e); down = true;
    if (S.phase === "p1") { aim(p); e.preventDefault(); }
    if (S.phase === "p3") { S.cursorVisible = false; var k = cellAt(p); actAt(k.c, k.r); e.preventDefault(); }
    if (S.phase === "p1" || S.phase === "p3") focusCanvas();
  });
  canvas.addEventListener("pointermove", function (e) {
    var p = pos(e);
    if (S.phase === "p1" && (e.pointerType === "mouse" || down)) aim(p);
    if (S.phase === "p3") S.hover = cellAt(p);
  });
  window.addEventListener("pointerup", function () { down = false; });
  canvas.addEventListener("pointerleave", function () { if (S.phase === "p3") S.hover = null; });

  var KEYMAP = { ArrowLeft: "left", a: "left", A: "left", ArrowRight: "right", d: "right", D: "right", ArrowUp: "up", w: "up", W: "up", ArrowDown: "down", s: "down", S: "down" };
  root.addEventListener("keydown", function (e) {
    var onCanvas = e.target === canvas;
    var dir = KEYMAP[e.key];
    if (/^[1-5]$/.test(e.key) && (S.phase === "p2" || S.phase === "p4")) {
      var b = panel.querySelector('.kg-choice[data-arg="' + (+e.key - 1) + '"]:not([disabled])');
      if (b) { b.click(); e.preventDefault(); }
      return;
    }
    if (!onCanvas) return;
    if (S.phase === "p1" && dir) { S.keys[dir] = true; e.preventDefault(); }
    if (S.phase === "p3" && !S.over) {
      if (dir) {
        S.cursorVisible = true;
        S.cur.c = clamp(S.cur.c + (dir === "left" ? -1 : dir === "right" ? 1 : 0), 0, G.cols - 1);
        S.cur.r = clamp(S.cur.r + (dir === "up" ? -1 : dir === "down" ? 1 : 0), 0, G.rows - 1);
        e.preventDefault();
      } else if (e.key === "Enter" || e.key === " ") { S.cursorVisible = true; actAt(S.cur.c, S.cur.r); e.preventDefault(); }
      else if (e.key === "r" || e.key === "R") {
        var urgent = S.threats.filter(function (th) { return th.det; }).sort(function (a, b) { return (b.t / b.max) - (a.t / a.max); })[0];
        if (urgent) { S.cursorVisible = true; S.cur = { c: urgent.c, r: urgent.r }; }
        e.preventDefault();
      }
    }
    if (S.phase === "intro" && (e.key === "Enter" || e.key === " ")) { p1(); e.preventDefault(); }
  });
  root.addEventListener("keyup", function (e) { var dir = KEYMAP[e.key]; if (dir) S.keys[dir] = false; });
  canvas.addEventListener("blur", function () { S.keys = {}; });

  // ---------------------------------------------------------------- laço principal
  var last = 0, visible = true;
  if ("IntersectionObserver" in window) new IntersectionObserver(function (en) { visible = en[0].isIntersecting; }).observe(root);
  function loop(now) {
    var dt = Math.min(0.05, (now - (last || now)) / 1000); last = now;
    S.t += dt;
    if (visible || S.phase === "p1" || S.phase === "p3") {
      ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
      var t = S.t;
      if (S.phase === "intro") { drawIntro(t); }
      else if (S.phase === "p1") { updateP1(dt); drawP1(t); }
      else if (S.phase === "p2") { drawP2(t, dt); }
      else if (S.phase === "p3") { updateP3(dt); drawP3(t); }
      else if (S.phase === "p4") { drawVillage(t, dt, false); setHud(phaseTag(4) + '<span class="kg-money">' + T.p4.balance + ": " + T.money(S.money) + "</span>"); }
      else if (S.phase === "end") { drawVillage(t, dt, true); }
      drawFloats(dt);
    }
    requestAnimationFrame(loop);
  }
  window.addEventListener("resize", resize);
  resize();
  intro();
  requestAnimationFrame(loop);

  // estado legível para testes automatizados
  window.KauaJogo = { estado: function () { return { fase: S.phase, sinal: S.signal, saude: S.health, alertas: S.answered, dinheiro: S.money, sensores: S.sensors && S.sensors.length, cursor: S.cur, mira: (function () { if (S.phase !== "p1" || !S.sats || !S.sats.length) return 0; var best = S.sats.slice().sort(function (p, q) { return Math.abs(p.x - W / 2) - Math.abs(q.x - W / 2); })[0]; return satAngle(best) - S.angle; })(), satelites: S.sats && S.sats.map(function (x) { return { x: x.x, y: x.y }; }), ameacas: S.threats && S.threats.map(function (th) { var p = cellCenter(th.c, th.r); return { x: p.x, y: p.y, det: th.det }; }), grade: G }; } };
})();
