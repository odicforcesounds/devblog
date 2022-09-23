# Notas sobre o JavaScript

O JavaScript pode ser usado para qualquer plataforma e para qualquer fim. Desde páginas web, aplicações web, gestão de base-de-dados, programar robots, aplicações para desktop, servidor, etc.. 

## Javascript para a web

- Front-end: Manipula a interface gráfica dos componentes do site usando o **V8** ou o **SpiderMonkey** 
- Back-end: Apresenta os dados de uma base-de-dados e apresenta-os no site usando o **NodeJS**

## JavaScript para outros dispositovos

- Android e Apple: Uso do **NodeJ** com a framework **React-Native**
- PC: ( desktop ou servidor ) Usando somente o **NodeJS**

## Plataformas mais usadas 

- [Angular](https://angular.io): Plataforma que usa **TypeScript** 
- [React](https://reactjs.org): Plataforma que usa **Javascript** 
- [VueJS](https://vuejs.org): Plataforma que usa **JavaScript** 
- [EmberJS](https://emberjs.com): Plataforma que usa **Javascript** 

## Termos comuns no uso do Javascript

- **VanillaJS**: é o termo ao uso do JavaScript sem usar librarias externas. 
- **ES6** ou **ES2015**: é o termo que se usa para referir uma versão especifica do Javascript, que é implementada pela organização [ECMAScript](https://262.ecma-international.org/) ( e que actualmente tem suporte em quase todos os browsers )

## Formas de usar o JavaScript 

- Na **consola**: é a interface de comando do Browser (firefox || chromium): Ctrl+I para aceder
- No **HTML**: VanillaJS - Os resultados podem ser só dados (na consola) ou manipulação dos elementos (na página)

```HTML
<!-- a primeira opção é a seguinte -->
<script>CODIGO</script>
<!-- a segunda opção é a seguinte -->
<script src="ficheiro.js"></script>
```

## Primeiros passos

- Normalmente usa-se a segunda opção para escrever o código de Javascript e a consola para ler os avisos e os erros do código. 

## Tipo de Dados

- Valores Primitivos: 

1. Undefined: o valor não foi definido: ( resultado constante do fim de cada ciclo no JavaScript )<br>
2. Null: valor é nulo. <br>
3. Boolean: valor é verdadeiro ou falso <br> 
4. Number: valor numérico  <br>
5. String: conteudo entre " " ou \' \',  isto é, "texto" (conjunto de caractéres com ou sem espaço entre eles)<br>  
6. NaN: função do JavaScript que declara que um valor não é um número <br>
7. BigInt: valor primitivo que corresponde a um valor numérico de precisão<br>
8. infinite: função do Javascript que declara que um valor é infinito <br>

### Definição da estrutura de Objectos em JavaScript 

- Uma coleção de propriedades que tem um único prototype-object associado. Cada propriedade (chave) **key**, tem um valor associado. 

```js
let todoList = {
    a: "Arrumar e limpar",
    b: "Organizar e Estruturar",
    c: "Definir e Planificar",
    d: "Trabalhar e Comprar"
}
console.log(todoList)
```

- Note-se que 


```js
const ob = new Object(); 
ob.name = "Oscar";
ob.name = ""
ob.do = function() {
    console.log(`do something ${ob.name} with your ${ob.email}` )
    console.log(ob)
  };
ob.do(); 
```

1. ordinary object: é um objecto que usa os métodos internos essenciais que têm suporte em todos os objectos. <br>
2. exotic object: é um objecto que não tem um comportamento estandarizado para um ou mais métodos internos essenciais. <br>
3. standart object: é um objecto que usa a semantica definida pela especificação do ECMAScript. <br>
4. built-in object: é um objecto que também é um **constructor** <br>
5. propriety: parte do objecto que associa uma chave a um valor. <br>
6. attribute: valor interno que define uma característica de uma propriedade.<br>
7. construtor: Cria e inicia objectos. A propriedade de um prototype-constructor é um prototype-object que é usado para receber propriedades de outros objectos e partilha-los. 
8. prototype: Objecto que partilha propriedades de outros objectos.

### Funções 

- function(): propriedade de um objecto que poderá ser envocado como uma sub-rotina.

1. built-in function: é um built-in-Object que é uma função. <br>
2. method: função que é o valor da propriedade. Quando uma função é chamada como método de um objecto, o objecto é partilhado para a função como o (seu) (**this**) valor. <br>
3. built-in method: é uma built-in-function.

## Operadores 

- Os operadores são formas de comparar informação, que usa simbolos matemáticos para esse fim, ou funções que já são built-in-function's. 

```js 
var x = 20; 
var y = 20; 
```

| Nome | Exemplo | Symbolo | Resultado | Tradução | Tipo | 
| ---- | ---- | ---- | ---- | ---- | ---- | 
| Unary Operator|  - x; | - | -10 | x fica negativo | Número | 
| Bitwise Operator | ~ x | ~ | ; -21 | x menos x menos 1 | Número | 
| Exponention Operator|  x ** y | ** | 1.04..+26| Expoente de x com y | Número | 
| Multiply Operator | x * y;| * |  400 | x multiplicado por y | Número |
| Divide Operator |  x / y; | / |  1 | x a dividir por y | Número | 
| Number Add |  x++; | ++ | 21 | Adicionar 1 a x | Número | 
| Number Subtract| y--;| --  |19 | Subtrair 1 a y | Número |
|Bigger than|  x > 10; | > | true | x maior do que y? | Boolean | 
|Bigger or Equal| x >= y;| >= |true | x maior ou igual a y? | Boolean | 
|Small than|  x < y;| < | false | x menor do que y? | Boolean | 
|Small or Equal| x <= y;| <= | true | x menor ou igual a y? | Boolean | 
|Equal to |  x === y;| === | true | x igual a y? | Boolean | 
|Not-Equal to|  x !== y;| !== | false | x não é igual a y? | Boolean | 
|AND operator| x & y;| & | 20 | x e y | Boolean | 
|OR operator| x \| y;| \| | 20 | x ou y | Boolean |  

## Nomes reservados 

- Os nomes reservados são todos aqueles que fazem parte da funcionalidade que o próprio JavaScript oferece. O uso destes nomes de forma errónea, produz erros, que por sua vez, poderão parar a aplicação (erro fatal). Estes nomes não podem ser usados como identificadores de valores. E.g: 

```js 
var var = var2; // ERRO ( o nome 'var' não pode ser usado para declarar uma variavel)
```

| Reserved Word | Descrição |
| ---- | ---- | 
| await | ... | 
| break | quando usado com o **case**, quebra o ciclo da função. | 
| case | built-in-function para criar um estilo de "loop" | 
| class | serve para criar classes que definem objectos | 
| const | forma de declarar uma variavel e impedir que o valor da mesma, mude | 
| continue | ...  | 
| debugger |..  | 
| default | .. | 
| delete | .. | 
| do | ciclo do-while|
| else | acrescentar condição | 
| enum | .. | 
| export | exporta variavel para ser acessível noutro modulo | 
| extends | amplia uma classe ou um objecto | 
| false | valor que declara a pergunta como falsa | 
| finally | | 
| for | ciclo for | 
| function | built-in-function que define e chama uma função() | 
| if | condição se | 
| import | acrescenta variaveis exportadas | 
| in | | 
| instanceof | | 
| let | forma de declarar uma variavel e impedir que o tipo de dado associado, mude | 
| new | cria um novo objecto a partir da definição de outro objecto ou classe | 
| null | valor é vazio | 
| return | retoma um resultado e pára o ciclo | 
| super | | 
| switch | usado no ciclo **case** para definir opções ou condições | 
| this | refere o conteúdo que está no **scope** (enquadramento) do contexto | 
| throw | atira - envio de mensagem para a consola ou aplicação | 
| true | valor que declara a pergunta como verdadeira | 
| try | | 
| typeof | diz qual o tipo de dado que um valor contém | 
| var | forma de declarar uma variavel | 
| void | | 
|while | ciclo while | 
| with | | 
| yield | | 


