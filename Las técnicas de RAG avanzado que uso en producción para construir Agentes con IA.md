---
title: "Las técnicas de RAG avanzado que uso en producción para construir Agentes con IA"
source: "https://www.youtube.com/watch?v=yz6PNct3XvQ"
author:
  - "[[Julio Andres Dev]]"
published: 2026-06-17
created: 2026-07-28
description: "Si quieres construir Agentes con inteligencia artificial, tienes que usar RAG para pasarle la información de tu empresa. RAG simple no es suficiente y no te va a funcionar bien, aquí te explico las té"
tags:
  - "clippings"
---
![](https://www.youtube.com/watch?v=yz6PNct3XvQ)

Si quieres construir Agentes con inteligencia artificial, tienes que usar RAG para pasarle la información de tu empresa. RAG simple no es suficiente y no te va a funcionar bien, aquí te explico las técnicas avanzadas que realmente hacen la diferencia.  
  
¿Quieres automatizar tu empresa pero no sabes por donde empezar? Mira acá: https://julioandres.dev/ia-para-empresas  
  
🚀 ¿Quieres concretar un proyecto de Inteligencia Artificial y no sabes como empezar, o como abordarlo? Agéndame una reunión y hablemos: https://cal.com/julioandres/consultoria-ia  
  
► Háblame por acá  
https://www.linkedin.com/in/julio-andres-olivares/  
  
► Suscríbete a mi newsletter acá  
https://julioandres.dev

## Transcript

**0:00** · El concepto de rag es simple, tienes un montón de información de tu empresa o de alguna base de conocimiento que quieres que tus agentes o tus chatbots usen, pero es mucha, entonces no cabe en la ventana de contexto de los LLMs o de la gente. Entonces, hay que hacer de alguna forma que de toda esa cantidad de información el LLM o el agente pueda obtener lo necesario para responder la pregunta que le están haciendo.

**0:24** · Hay un rag que se le llama el rag ingenuo o naiv en inglés, que es básicamente lo que te explican todos los youtubers, los blog post, porque es lo más fácil de hacer y es rápido para sacar un prototipo, no producción, un prototipo rápido para mostrar cómo funcionaría esto. ¿Cuál es el rag ingenuo o na? Supongamos tenemos un montón de texto que puede ser un PDF o una doc un texto plano, un montón de conocimiento. Lo que te dice el rag ingenuo es que agarres el texto y primero lo separes en chanks fijos de tokens o de caracteres.

**1:00** · Luego tienes esta división y dices, "Ya voy a dividir aquí, voy a dividir aquí, voy a dividir aquí, voy a dividir aquí." Luego agarras estos pedazos, los conviertes en embeddings, los guardas en una base de datos de vectores. Luego el usuario te hace una pregunta, agarras la pregunta, también la conviertes en embedding y vas a buscar eh los chanks que están en la base de datos, cuál tiene más simulitud para luego pasárselo al ll.

**1:26** · Esto es ingenuo y en producción no te va a funcionar, va a fallar en el día uno cuando usueros reales empiecen a ocupar tu app. En este video te voy a explicar técnicas de rack avanzado que yo uso en producción con los agentes que he hecho para distintas empresas que funcionan bastante bien y en verdad son técnicas que tienes que usar sí o sí porque rag ingenuo no te va a funcionar si necesitas poner un poco más de inteligencia en el rag en las distintas

**1:57** · partes y te voy a explicar cuáles son pero primero te voy a explicar también por qué el rag ingenuo falla imaginemos tenemos este base de conocimiento que es un producto ficticio que se llama Nimbus Cloud y es super una base de conocimiento super pequeña que en verdad cabe en la ventana de contexto, pero para es para ejemplificar por qué falla el rag en vamos a empezar a separar. Imagina, separamos en chunks y ponemos este chunk, después cortamos y el siguiente chunk, después cortamos y el siguiente chunk. Y aquí imagino que ya ves el primer error de esto, ¿por qué va a fallar?

**2:32** · Porque si agarramos chanks, pedazos fijos de digamos 100 tokens o 100 caracteres, como sea, cualquiera de los dos caracteres, separar por número fijo de caracteres o número fijo de tokens, es un mal método porque imaginemos que el chank parte aquí, empieza aquí, termina acá. Entonces tienes un chank que dice esto y corta la información a la mitad. Después el siguiente chunk eh, termina acá.

**3:01** · Entonces te queda un chunk que se va a embebrar en la base de datos, en el espacio de vectores y va a decir esto y después el otro va a decir que incluye 1 TB de almacenamiento 5 usuarios, bla bla bla. Incluso va a quedar con el plan enterprise después del punto. Entonces queda muy raro. Es como las ideas no se terminan, se cortan a la mitad. Esto hay que pensar siempre que estos chankss tienen que embebse en un espacio de vectores, que es un espacio de muchas dimensiones donde cada vector tiene una semántica, un significado. Entonces, el significado de esto que se corta acá va a ser raro.

**3:32** · El significado de esto que se corta acá quizás va a incluir, quizás va a estar más cerca de enterprise, pero en verdad está hablando de Pro, entonces es raro. Eso es lo primero. con chan ingenuo cortas en partes que dejan la información rara, sin contexto o con contexto erróneo. El segundo error es que a veces la búsqueda semántica no es necesaria o no es lo suficientemente buena cuando en verdad nos sirve más tener match exactos.

**3:59** · Aquí, por ejemplo, en esta sección, si un usuario hace la pregunta, aquí está ah, pregunta por R 4021, porque la aplicación le está arrojando ese error. Dice, sale un popup, alerta, error 4021, así tal cual.

**4:19** · Si estás con embeddings y semántica, tal vez toda esta parte va a quedar almacenada en un embedding, esto que estoy marcando. Y esto semánticamente, ¿qué significa? son errores. Tal vez te va a devolver esto y te va a devolver esto y te va a devolver otra parte donde hable de errores. En fin, la semántica con palabras exactas, conceptos o nombres, es menos útil que buscar a la antigua como un buscador común que que busca por el match de las palabras.

**4:45** · Entonces, en este caso particular, que el usuario te está preguntando por el R4021 textual, funciona muy bien buscar simplemente por el match de esto, buscar por el keyword, no está, buscar esto en el en el talk, en el chank en que esté esta palabra exacta, devolver ese chank ahí ll va a poder leer el error. Y la tercera razón de por qué falla en la búsqueda RAC NIV \[resoplido\] es por los usuarios, las preguntas que hacen, que a veces la pregunta que hace el usuario no es fácil de hacerle match temáticamente con la base de conocimiento. Voy a explicar en detalle más adelante por qué cuando de la solución de esto.

**5:17** · Un ejemplo fácil sería si un usuario te hace dos preguntas en una. Por ejemplo, te dice, "¿Qué integraciones tengo en Pro y cuánto cuesta ese plan?" Son dos preguntas. Bien, ahora vamos a ir a ver las técnicas avanzadas de rag. Vamos a empezar por el chanking que tiene que ser más inteligente. Primero vamos a empezar por el chanking semántico.

**5:35** · El chanking semántico significa que los chanks se van separando o el texto se va separando en partes donde cada parte tiene un sentido y de una idea clara contenida, no se separa, no es que se corte en medio y que la idea no se termina de decir, queda un pedazo más adelante y cosas así. ¿Cómo funciona? Tiene dos pasos. Uno, se empieza a separar.

**6:05** · Bueno, siempre hay que limpiar los PDFs o los documentos que tengas de cosas como los títulos, por ejemplo, por si esto va en el chank, no tiene sentido. Este quizás sí, aunque quizás no. Quizás solo nos interesa esto. En verdad en todo esto depende mucho de tus documentos. Eso es lo que muchos no quieren aceptar, pero hay un trabajo manual super arduo, bueno, no s, quizás solo arduo al principio, donde tienes que agarrar los documentos y trabajarlos y ver qué técnica es la mejor y cómo separarlo y todo eso.

**6:36** · No es, lamentablemente, no hay una varita mágica o un script mágico en que le pasas cualquier PDF, cualquier documento, cualquier libro y te lo separa de la mejor forma. Esa es la primera regla. hay alto trabajo y depende de cada documento. Bueno, semanticing, imaginemos que esto parte aquí lo va dividiendo en oraciones. Puede ser que separa esta, agarra este párrafo y lo va separando por oraciones. Corta este, después corta este, después corta este, después corta este.

**7:08** · Cada una de estas oraciones las convierte en un embeding semántico. Y luego va comparando con la siguiente, si es que la diferencia de similitud, por ejemplo, la diferencia de coseno, si es que están muy alejados en el en el significado, en la semántica o si es que no es tanto y de acuerdo a eso lo agrega al chan general o no. Ejemplo, agarramos este, lo convierte en biddings. Cuando digo lo convierte es el script que tienen ustedes, el Python o lo que sea que estén usando cuando empiecen a procesar los documentos.

**7:41** · Esto se lo pasan a su programa, a su app, en la función chanen semántico y va a empezar a dividir el texto por oraciones o tiene que hacer eso. Agarra esta oración, la convierte en un embeding que tiene, no sé, dirección hacia allá.

**8:03** · Acuérdense que los embedings son vectores. Agarra la segunda oración, la siguiente a esta, la vuelve a convertir en un embeding y compara con la anterior. ¿Es muy diferente o no es tan diferente? Ahí tiene que haber un corte, un threshold para decidir eso. Entonces, en este caso dice Nebus Cl ofrece tres planes, hay un vector. La siguiente es el plan starter, bla bla bla. Esto no es muy distinto, está hablando del mismo tema, planes. Entonces el algoritmo de de Chank semántico dice, "Ah, estas son bastante parecidas. Voy a unirnas." Después sigue avanzando. Siguiente oración.

**8:35** · El plan bla bla también habla de planes, no es tan distinta. Voy a unirlas. Después la siguiente oración es esta. El plan enterprise incluye soporte prioritario, bla bla. Ahí llegaste acá. Lo convierten en beding y compara con la anterior. Es muy distinto. No sabemos. Habría que ver el corte porque si bien sigue hablando de los planes, empieza a hablar de ya aquí empieza a hablar del soporte.

**9:04** · Entonces, quizás decide, imaginemos que que la diferencia con el chan anterior, perdón, con el vector anterior, eh, pasa el rango, así que dice, "Ah, este es otro tema." Y empieza a hacer otro chan y así. Después llega acá para dar debajo un plan entra y aquí es totalmente distinto. Ya no habla de soporte. Entonces dice, "Okay, esto está muy distinto al laaboración anterior. Vamos a empezar otro chank." Y así, así va. Es el chank semántico y la verdad es que funciona muy bien.

**9:31** · Cuesta un poco más de dinero porque tienes que estar convirtiendo en vectores cada oración y también se demora un poco más, pero es bien efectivo y este proceso uno debería hacerlo una vez mientras tu documentación o tu base de conocimiento no cambie tanto. El siguiente es el chunking por estructura. Este es bien intuitivo y también es uno de mis favoritos. se refiere a que hay que separar el documento en las separaciones que ella tiene. Por ejemplo, acá hay una separación clara entre estas secciones. Esto sería un chank, esto sería un chank, eh, esto sería un chunk, esto sería un chunk y así. Por aquí tengo otro documento. Vamos a ver.

**10:06** · Aquí tengo un PDF de Anthropic que habla de cero trust para gentes, cosas de seguridad.

**10:20** · Pero bueno, imaginemos queremos hacer una base de conocimiento de este PDF que tiene, ¿cuántas páginas? 36, no es tanto, pero bueno. En el chanking por estructura lo que haríamos sería agarrar esta misma estructura. Si vemos la tabla de contenido, ya está separado en en partes. Tenemos building for the next thread landscape, es una página. Podemos decir, "Okay, este va a ser un chunk." Podemos decir, "Esto va a ser otro chunk.

**10:45** · Esto va a ser otro." Eso es una forma. Lo otro es que tú puedes decir, "Okay, estos chanks son muy grandes." Voy a tratar de usar chanks más pequeños. Y de acuerdo al documento. Este va a ser uno, pero aquí este va a ser otro y luego este va a ser otro. Después voy aquí abajo y este va a ser otro. Este va a ser otro y este de aquí abajo va a ser otro. Como digo, este es muy efectivo porque ya porque usa el orden natural de quien sea que escribió esto, que ya hizo el trabajo de separarlo semánticamente las ideas de las partes. Ahora, este requiere un poco de más de trabajo de cómo separar esto para que sea de forma automática.

**11:21** · Hay muchos parcsers, por ejemplo, hay uno muy bueno que se llama Dockling, que te puede ayudar a esto. Entonces, te vas sacando eh los párrafos, los párrafos, después dice, "Ah, esto es un nuevo header, un encabezado." Y cuando detecta un header dice, "Es una nueva sección." Entonces, la idea conceptual es separarlo por secciones, pero de ahí cómo hacerlo programáticamente depende de el lenguaje y la librería y o el script que ustedes tengan. También se puede hacer a mano. Perfectamente. Podrías ir agarrando esto, copiándolo y pegando la mano y decir, "Este es un nuevo chank. Este es un nuevo chank."

**11:52** · Para 36 páginas no te vas a demorar tanto. Entonces, hay que ver qué es lo que más conviene. Esas son par de técnicas avanzadas de Chanking.

**12:06** · También hay otras, pero por ahora creo que eso es suficiente y te va a dar muy buenos resultados. Y la siguiente parte es es respecto a la búsqueda. Primero ya resolvimos el chunking, que queda perfecto, queda ideal, ¿no? Perfecto, queda ideal. El siguiente paso en el RAG, en rag es la búsqueda, cómo mejorar la búsqueda. Y aquí es algo que les mencioné, que a veces la búsqueda semántica no es necesaria o no es la mejor.

**12:31** · Entonces, usamos búsca híbrida y esto normalmente es con el algoritmo algoritmo BM25, que pueden buscarlo en más detalle a qué se refiere, pero es básicamente lo que hacen los buscadores, que es indexar los documentos o los chanks con el número de frecuencia de una palabra. Entonces, si yo busco, vamos a ver aquí el ejemplo este, si yo quiero buscar er 4021, ese término exacto, probablemente no va a estar en ningún chank, excepto en el que incluya este error. Entonces, la frecuencia va a ser uno. Entonces, ahí está.

**13:04** · Ese es el el documento o el chunk número uno que va a devolver. Y no hay más porque es laun es el término exacto. Si buscamos enterprise, eh eh ¿dónde está? Acá. Si alguien busca por enterprise, la pregunta es como, ¿qué incluye? El usuario está preguntando, ¿qué incluye el plan Enterprise? La búsqueda semántica va a sacar los chanks que hablen del plan Enterprise y la búsqueda léxica va a buscar por la palabra el keyboard enterprise y va a también sacar los documentos que hablen de eso. Los va a ranquear de acuerdo a el algoritmo BM25.

**13:38** · La cosa es que esto te va una búsqueda híbrida. Es como atacar la pregunta por dos lados. Nuevamente si buscamos, si alguien pregunta cuál es el plan enterprise, va a devolver dos listas. Una que va a ser la semántica con los chunks, listas de chunks que incluyen esto, enterprise o el que incluye el plan enterprise. Y la otra lista es con las documentos o los chanks que buscó básicamente como como un Google donde el keyword estaba presente. ¿Qué se hace con esas dos listas? Se usa algo que se llama reciprocal rank fusion o rff.

**14:09** · RRF, perdón. Y tienes dos listas, una que va a incluir los documentos que encontró por la búsqueda semántica y la otra lista que es los documentos, los chanks que encontró con la búsqueda léxica. Entonces agarras el primer chank y va a decir este chank aparece en la lista en la posición tres. Entonces su puntuación es 0,06. En la lista léxica dice el mismo chank aparece en la posición 10, entonces su puntuación es 0,003. Después sumas esos dos números y te da un valor.

**14:41** · Luego comparas todos los eh chunks con ese valor de las cosas sumadas. Espero se haya entendido. Si no, pueden preguntármelo, pero si buscan en Google o le preguntan a chat GPT, reciprocar rank fusion es una algoritmo s simple. ¿Ya? Entonces, búsqueda híbrida para solucionar la búsqueda.

**15:02** · Luego tenemos la segunda, la siguiente técnica de búsqueda que es ranking, que si quieren hacer una cosa, solo una cosa, y notar una mejora en la búsqueda de de los documentos, pueden hacer ranking. Con eso ya van a mejorar mucho su rag. ¿Qué es reranking? Reranking, re ranking, rag. Vamos a ver aquí voy a usar este material de alguien. Ranking es la idea de reranking.

**15:35** · Es super fácil de entender y tiene todo el sentido. Tú buscas primero entre tus embedings, todos tus embedings y te va a devolver 20. Por ejemplo, buscaste lo de qué incluye el plan enterprise y te devolvió tu algoritmo base, tu script base, 20 embedings que estaban que que tienen simulitud con la pregunta. Pero de esa de esos 20 probablemente muchos no tienen tanto sentido.

**16:02** · Por ejemplo, en la lista de 20 embedings que te devolvieron, el que está en la posición 15 responde mucho mejor la pregunta, pero como la pregunta fue preguntado, fue preguntada de una forma eh extraña que en verdad decía, ¿qué incluye el plan Enterprise y el Word y cómo está formulado en el texto? dice el plan enterprise te permite o te o dice los features del plan enterprise son entonces la pregunta que hizo el usuario o cómo la hizo no se alínea tanto como está en la base de conocimiento.

**16:37** · Por lo tanto, este chank que tenía la información justa quedó en la posición 15 que es bien abajo y probablemente se pierda ese chank porque tú vas a cortar en los primeros cinco. Entonces aquí es donde entra ranking. tú le vuelves a pasar estos 20 a al algoritmo, al modelo de rer ranking más la pregunta, ¿y qué es lo que hace ranking?

**16:56** · Es reordena estos 20 y dice, "Mira, en verdad el que está en la posición 15, que es como sale acá en este diagrama, el que está en la posición 15 o aquí abajo 15 es más relevante para tu pregunta, así que lo paso arriba y lo ordena esos 20 y dice, "Mira, ahora los cinco primeros sí que son los más relevantes." ¿Cómo funciona esto? por debajo es es bien técnico que la respuesta técnica es que la búsqueda vectorial usa un modelo B encoder y el rerranker usa un modelo cross encoder.

**17:33** · ¿Qué quiere decir esto? Básicamente que en el embeding, cuando tú haces los embedings tú no tienes la pregunta. Tú cortas el documento en embedings antes de lanzarlo para que tus usuarios pregunten. Entonces tienes todos tus embedings guardados en la base de datos previos. Después el usuario viene, hace la pregunta. Eso tú lo conviertes en beding y comparas. Ya reanking. Tú le pasas la pregunta más el documento o más los chunks. Entonces mete la pregunta más los chans o los o el documento juntos para ser analizados por el modelo. Entonces puede comparar inmediatamente.

**18:08** · ¿Se entiende? En uno tú haces el embeding inicialmente hace un mes atrás el documento lo convertés en embedings, luego el usuario va hacer la pregunta y esto no tiene mucha relación hasta ese momento en que comparas la similitud, pero los convertiste por separado. En el reranker tú tienes el documento y metes la pregunta y todo junto lo conviertes en embedings en embedings, por eso da mejor resultado.

**18:31** · Lo único problema es que es un poco más lento y es más caro, así que por eso se hace con los chanks que te devuelve el la primera búsqueda, los 20 y no los 1000 que tienes guardados. Para hacer esto existen varios modelos. El más famoso cogir que es una llamada, una API.

**18:54** · Tú usas el modelo de, a ver si está aquí, product, el reranker, una llamada, una API, le pasas la pregunta, los chunks y te devuelve el documento ordenado con con una métrica para saber cuál es más tiene más valor. Hay varios otros. Si tú buscas rerranker models, Pine contiene otro y demás que hay otros. Hay unos también que son locales si quieres usarlo, pero no son tan buenos, pero bueno, depende de ahí de tu caso de uso. Ya. Siguiente. Reranking. Reranking.

**19:23** · Luego la siguiente técnica avanzada es de el cómo el usuario hace las preguntas, que estos son de los cambios que más me gustan porque son divertidos de hacer. Entonces, cinco. Los usuarios puede que hagan preguntas de una forma rara. y no te vas a dar cuenta hasta que tu app esté en producción. Primero es query rewriting, que es reescribir la pregunta.

**19:47** · Por ejemplo, volvamos a nuestro documento de ejemplo y imaginemos el el cliente, el usuario pregunta cuáles son los planes y el bot o el agente le dice, "Okay, va a buscar, entiende los planes." Le dice, "Está el starter, el pro y el enterprise y luego el usuario le dice, ah, ¿cuánto cuesta el último o qué incluye el último?" Entonces, la pregunta es, ¿qué incluye el último? Por si sola, esa pregunta no dice nada. Tiene que leer la conversación anterior, los mensajes para saber qué es lo que hace este query rewriting.

**20:20** · Es que en este caso en vez de decir que incluye el último, el querer writing sería que incluye el plan enterprise. Esto se hace con un llm que tú le dices, reescribe la pregunta del usuario para que sea más legible o bla bla bla, lo que tú quieras. Incluso le puedes pasar un en el prompts de tu empresa para saber a qué se está refiriendo y que es lo que hace es que agarra la pregunta del usuario o la conversación. Generalmente se le envía los últimos cinco o seis, siete mensajes y le dices, reescribe la pregunta del usuario para bla bla bla.

**20:53** · Entonces va a agarrar la conversación, la pregunta y va a hacer un rewrite. Lo va a reescribir de la forma que sea más fácil buscar en tu base de conocimiento.

**21:06** · También este es superútil y yo diría que por defecto hay que hacerlo porque los usuarios pueden preguntar de forma muy raras, pueden incluso preguntar con faltas de ortografía o typos o usar palabras que no están en tu base de conocimiento. Por ejemplo, algo que me pasó hace poco, que teníamos un bot en Telegram que ayuda a buscar en la base de datos de una empresa sobre distintas métricas. Entonces, hay una función que ayuda al LLM a buscar por recaudación. Entonces, la todo toda la recaudación e la función, la descripción, todo.

**21:35** · Pero llegó un usuario y pregunta por cuál fue la pregunta, la palabra que usó, creo que usó ingresos o algo así, una palabra distinta que, claro, que no hace match directo con todas las que estábamos usando. Por suerte tenemos un un reescribimos la pregunta del usuario e basando los conceptos que están en la base de datos o en la base de conocimiento.

**21:53** · Entonces el usuario preguntó por ingresos, no recuerdo que si fue ingreso, fue algo más más raro, pero bueno, imaginemos pregunta por dame los ingresos de la última semana y el paso por el query rewriting está con un prompt que le dice al que reescribe esta query. Estos son los conceptos que manejamos en la base de datos o en la base de conocimiento. Por ejemplo, dice recaudación, dos puntos, ingresos, revenue, ventas, cosas así. Entonces, cuando reescribe la pregunta, ya sabe que en vez de decir ingresos, va a decir recaudación. Así que query rewriting.

**22:31** · Después tenemos uno que se \[resoplido\] llama, este, no lo he usado mucho, multiquery, que tienes una pregunta y se generan cinco preguntas. También es bien intuitivo. El usuario hace una pregunta y tu llgo en el medio genera más preguntas. Entonces, por eso se llama multiquery. En vez de usar una directo ir a buscar la pregunta la agarras y la conviertes en cinco, tres o tres preguntas y vas a buscar los documentos con esas tres preguntas. ¿Qué es lo que hace? Abarca, abarca más.

**23:00** · Básicamente eso es en el caso que hablé recién, si el uso pregunta, "Dame los ingresos de la semana pasada, este multiquery puede que también genere dame las ventas de la semana pasada y dame los eh la recaudación de la semana pasada. Estas tres, cada una de tus preguntas van a recolectar documentos o chanks relativamente distintos. Que sea la pregunta uno, agarro el documento 300 o el chang 300 que la pregunta dos y tres no agarró.

**23:28** · Entonces ahí tienes más hay más variedad y luego al final puedes usar un reranking o simplemente pasar los top cinco y generar la respuesta y hay como más simplemente hay más información para que Llm pueda generar la respuesta. Luego tenemos la siguiente técnica, que es una muy curiosa que se llama hide, que voy a pegar acá al significado. Es hypothetical documents embedding.

**23:55** · El usuario hace una pregunta y en vez de buscar por tu pregunta, tú buscas por generas una respuesta ticia y con eso buscas. Es bien curiosa, bien creativa también y también hace sentido.

**24:14** · Vamos a mover esto aquí. Ahí está. ¿Por qué? ¿Cómo funciona? Por ejemplo, yo le pregunto, ¿dónde está el documento de prueba? Aquí. Por ejemplo, la pregunta del usuario es, "¿En cuánto tiempo responden si mi plan es enterprise?"

**24:25** · Tú agarras esa pregunta y generas una respuesta ficticia con un ll sin conocimiento, lo cual puedes usar simplemente haiku o un modelo pequeño porque necesitas que invente algo. Por fin puedes usar las alucinaciones a tu favor. Entonces, la respuesta ficticia que va a generar con esta pregunta puede ser la respuesta en Plan Enterprise es en 30 minutos o es en 24 horas. Esa es la respuesta efecticia. Entonces tú enedes envedes, generas un embeding de esa respuesta y con eso vas a buscar a la base de datos de vectores.

**24:59** · Si uno lo piensa bien, funcionaría mejor que la pregunta, porque a veces la pregunta, el embeding de la pregunta no tiene nada que ver o es menos es menos relacionado con el embeding que está guardado a la respuesta. ¿Se entiende? Y tenemos dos oraciones, una que es cuál es el tiempo de respuesta del plan enterprise y tenemos otra que es el tiempo de respuesta es 30 minutos. ¿Cuál creen que va a estar más cerca? ¿Va a ser más igual? A la respuesta. El planner enterprise incluye soporte bla bla bla en menos de una hora. E la respuesta es ficticia, ¿cierto? Está más relacionada.

**25:41** · Eso es básicamente el principio de este height. Ya. Y el último que también es superútil y yo lo ocupo bastante es el descomposición. Composición que como su nombre lo dice es descomponer la pregunta en varias. Esto también recomiendo que lo hagan sí o sí. Y esto es muy sencillo. Si el usuario pregunta, por aquí tengo una de esta, si alguien pregunta, "¿Qué integraciones tengo en Pro y cuánto cuesta ese plan?" Aquí hay dos preguntas en verdad.

**26:11** · Entonces tú le pasas un LLM y le dices, separa la pregunta del usuario en varias preguntas si es que tiene sentido. Si el usuario solamente pregunta cuánto cuesta el plan pro, no hay que separar nada. Pero si el usuario pregunta estas dos cosas, hay que separarlo en dos preguntas. ¿Qué integraciones tengo en Pro y cuánto cuesta el plan Pro? ¿Por qué? Eso cl

**26:33** · pregunta completa lo vas a buscar directo en la embeding, te va a entregar información rara, quizá te va a incluir mucho más, va a tener mucho más peso las integraciones porque están primero y el cuánto cuesta va a estar en otra, no lo va a considerar, puede formarse una, no sabemos qué puede pasar, es mejor separarlo. ¿Qué integraciones tengo en Pro? Vo a buscar todo relacionado a eso, cuánto cuesta el plan, todo relacionado a eso. Después puedes juntar los chunks y pasárselo al LLM para que genere la respuesta final. Incluso decirle, el usuario hizo dos preguntas, esta, estos son los chunks que la responden.

**27:05** · Y esta otra pregunta y estos son los chunks que la responden. Y la te aseguro que la respuesta va a ser muy muy buena. Ya hay uno final, una técnica final que es más nueva, me van a entender por qué es más nueva que se que se llama ragéntico, que es el agente decide, que todavía es un poco experimental, hay algunos frameworks, pero es experimental. Puedes hacerlo tú mismo en Python, porque por ejemplo, ¿cómo funciona esto? Uno, si el usuario dice, "Hola, ¿cómo estás?" El rag agéntico o el agente de rag dice, "Necesito buscar información para responder esto."

**27:37** · No, es un simple saludo. Respondo. Después el usuario se te pregunta, "¿Cuál es el plan pro? ¿Cuánto vale el plan pro?" Y este rack agéntico va a decir, "Ah, mira, necesito buscar información." Sí, ¿qué información necesito buscar? Es referente al a los precios de los planes. Y ahí quizás hay otra parte de este agente de Rank que dice de dónde sacar o aplica alguna de estas otras técnicas. Y finalmente, en verdad, lo importante de este rack géntico, lo nuevo es que evalúa la respuesta. Dice, "Esta fue la pregunta del usuario y esta es la respuesta que generé."

**28:07** · Y la evalua. Dice, "¿Realmente responde la pregunta?" y te dice, y si fuera un loop, los famosos loops, te dice, dice sí, la responde, todavía la manda y si es que dice no, va a buscar de nuevo más, lo cual, la verdad, en teoría debería potenciar mucho tus respuestas o tu sistema porque tienes a alguien analizando la pregun la respuesta en ese mismo momento.

**28:34** · Lo único sí que es más es más caro porque vas a tener una un LM que tiene que ser inteligente quizás con razonamiento para analizar si es que la respuesta que le estás dando tiene sentido o no o responde la pregunta. Si es que no, tiene que ir de nuevamente a buscar más o hacer algo más un poco más caro, pero si tu sistema necesita realmente respuestas eh exactas o responder bien, por ejemplo, un sistema de para abogados, de leyes o de medicina, un ragazo.

**29:10** · Y bien, eso es técnicas de avanzadas de rag que les puedo contar. Vamos a resumir. Aquí tenemos las de chanking, que es chanking semántico y chankin por estructura. Tenemos las de búsqueda, que es búsqueda híbrida, reranking. Y luego tenemos todas las que son de la query, que es el query rewriting, multiquery y he descomposición. Y finalmente hay una nueva técnica avanzada surgiendo que es el ragéntico. Ahora puedes aplicar todo esto, pero lo importante es tener visibilidad de si están funcionando o no.

**29:42** · Entonces siempre tienes que una rama muy importante de lo que es ingeniería de IA evaluar. Si no puedes, si no estás evaluando tu rag, no vas a saber si es bueno o malo o si agregas otra técnica, si mejora o empeora. Para eso tienes que aprender evals en rag. Y para eso mira este otro video donde explico en detalle cómo evaluar tu arquitectura de rag. Nos vemos en la próxima y suscríbete y que tengas un buen día o noche o tarde.