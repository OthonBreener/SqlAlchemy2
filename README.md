# SqlAlchemy

O sqlalchmey é dividido em dois modulos chamados de Core e ORM.

* Core: Contém lógicas de integração de banco de dados para todos os dialetos
de banco de dados supotado, uma coleção de classes para descrever tabelas de
banco de dados e um sistema sofisticado para gerar declarações de SQL usando
construtores da linguagem python.

* ORM: Introduz uma camada de abstração entre a aplicação python e o banco de dados,
permite muitas operações de banco de dados serem derivadas automaticamente de
ações realizando em objetos python.

## Abrindo o sqllite no vscode

Dica para usar o sqlite no vscode:

Aperte: CTRL + P e digite >sqlite

## Metadata

O SqlAlchmey mantém a definição de todas as tabelas que compõem o banco de dados
em um objeto de classe, MetaData. Por padrão classes que herdam de DeclarativeBase
tem um metadata padrão, o metadata está diponível como Model.metadata. Quando uma 
classe como Produto é definida, o SqlAlchemy  cria uma definição de tabela correspondente 
neste atributo.

A configuração padrão do MetaData tem uma importante limitação que causa problemas quando
o projeto alcança certo tamanho ou complexidade. Isto está relacionado a opção do MetaData
'name_convention', a qual fala para o SqlAlchemy como nomear indexes e constraints 
(constraints ou restrições, são regras definidas para garantir a integridade dos dados armazenados,
algumas restrições famosas: NOT NULL, UNIQUE, PRIMARY KEY.) criados no banco de dados.

O problema é que o name_convention padrão usado no MetaData, defini uma regra para nomear
indexs, mas não constrains, então o SqlAlchmey cria todos os constrains sem um nome explicito,
resultando em nomes arbitrarios escolhidos pelo banco de dados. Se em algum momento a constraint
precisar ser modificada ou deletada, o SqlAlchmey não saberia de imediato como encontrar a constraint
pelo seu nome. Para evitar esse problema é possível definir uma convenção mais completa:

```python
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import DeclarativeBase

class Modelo(DeclarativeBase):
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_lable)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)",
        }
    )
```

O objeto MetaData tem o método **create_all()** que é usado para criar as tabelas de banco de dados
associadas com os modelos definidos. Uma limitação importante do create_all é que ele apenas cria
tabelas que não existem no banco de dados, não sendo possível atualizar ou mudar uma tabela já
existente, para isso é necessário utilziar o Alembic. Por conviniência, o MetaData tambem tem o 
objeto **drop_all()**, usado para apagar todas as tabelas.

## Session

Outra entidade importante em aplicações baseadas em ORM é a sessão (session). O objeto sessão mantém a
lista de instâncias de modelos novos, lidos, modificados e excluídos. Mudanças que são acumuladas na 
sessão sçao passadas para o banco de dados no contexto de uma transação de banco de dados, quando
a sessão é flushed (liberada), em muitos casos a operação é publicada automaticamente pelo SQLAlchemy.
Uma operação de flush escreve as mudanças no banco de dados, mas mantém aberta a transação.

Quando a sessão é comitada (committed), a transação de banco de dados correspondente é comitada 
também, fazendo com que todas as mudanças sejam permanentemente escritas no banco de dados. Transações
são o mais importante beneficio de bancos de dados relacionais, desenhada para manter a integridade
dos dados. As mudanças que são comitadas como parte de uma transação, são escritas como uma operação
atômica, logo, erros ou interrupções inesperadas nunca vão resultar em dados parciais ou incompletos.

Se um erro ocorrer enquanto a sessão está ativa, uma operação de **rollback** na sessão vai reverter a 
transação e todas as mudanças feitas naquele ponto da sessão será desfeito. O exemplo abaixo mostra como
um objeto criado pode ser adicionado na sessão e comitado:

```python
from sqlalchemy.orm import Session

with Session(engine) as session:
    try:
        session.add(objeto)
        session.commit()
    except:
        session.rollback()
        raise
```

Objetos de sessão são desenhados para acumular mundaças até que elas sejam comitadas ou revertidas (rollback).
O método **add()** é usado para inserir um novo objeto dentro da sessão, o bloco de try/except garante que
a sessão vai ser sempre comitada ou revertida. Essa não é a melhor forma de lidar com uma sessão, a melhor
maneira é criando um gerenciador de contexto, este garante que a sessão é sempre propriamente fechada.
Pensando nisso, o SQLAlchemy fornece um caminho mais conciso para trabalhar com sessão. A função 
**sessionmaker** fornece uma classe de Sessão customizada com todas as opções incorporadas:

```python
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(engine)

with Session() as session:
    with session.begin():
        session.add(objeto)
```

O exemplo acima faz o mesmo que o primeiro, porém, subistituimos o bloco de try/except pelo contexto de 
session.begin(), que implementa a mesma lógica internamente. Podemos definir o objeto Session no arquivo de
banco de dados e apenas importar ele para outros locais.

## Querys

SqlAlchemy fornece um método similar a palavra chave SELECT do sql para buscar
dados no banco. O método select pode ser usado para buscar os dados de um determinado
objeto no banco de dados, se dermos um print na query, obtemos o código SQL que está
associado ao objeto query do SQLAlchemy.

```python
from db import Session
from models import Produto
from sqlalchemy import select

query = select(Produto)

>>> print(query)
SELECT produtos.id, produtos.nome, produtos.fabricado, produtos.ano, produtos.pais, produtos.cpu 
FROM produtos
```

Depois de criar a query, podemos executa-la usando a session, o qual vai enviar para
o driver do banco de dados para executar através de uma conexão mantida pela engine.
Isso pode ser feito da seguinte maneira:

```python
session = Session()

resultado = session.execute(query)

>>> list(resultado)

[
    (Produto(1, "Acorn Atom"),),
    (Produto(2, "BBC Micro"),),
    ...
]
```

O resultado retornado é um objeto iteravel onde cada linha da tabela é convertida
automaticamente para a classe modelo utilizada. O SQLAlchemy retorna para cada resultado uma
tupla, por que querys podem algumas vezes retornar multiplos valores por linha. Como o
SQLAlchemy não sabe quantos resultados por linha são esperados, ele sempre retorna
cada linha como uma tupla. 

Se você sabe que vai ser retornado apenas um valor por linha, então você pode usar
o conviniente método scalars() ao executar a query, este vai retornar o primeiro valor
da tupla. Caso você use o scalars() e o resultado esteja retornando mais de um valor por
linha, os valores restantes serão descartados.

```python
>>> session.scalars(query).all()

[Produto(1, "Acorn Atom"), Produto(2, "BBC Micro"), ...]
```

O método all() é usado para retornar diretamente uma lista. Existe outros métodos igualmente interessantes:

* first(): retorna o primeiro resultado da query ou None se não existir resultados, se existir
mais resultados, eles são descartados.

* one(): retorna o primeiro resultado e apenas ele, se existe zero ou mais que um resultado,
uma exceção é levantada.
  
* one_or_none(): retorna o primeiro resultado e apenas ele, ou None se não existir
resultado. Se existir dois ou mais resultados, uma exceção é levantada.

Para todos esses métodos é possível usar o scalars(), porém há metodos prontos similares
aos métodos de busca do execute:

* scalar(query): similar a scalars(query).first()
* scalar_one(query): similar a scalars(query).one()
* scalar_one_or_one(query): similar a scalars(query).one_or_none()

## Filtros

As querys que incluem apenas uma declaração select() retornam todos os itens disponiveis,
que são utéis algumas vezes, mas não todas. Existem muitas situações no qual uma 
aplicação quer apenas um subconjunto de todos os itens, respeitando algum criterio.

A aplicação pode retornar todos os resultados como mostrado acima e então descartar
os que não são interessantes, mas isto pode ser muito ineficiente, especialmente para
tabelas muito grandes. Banco de dados são desenhados para executar filtros e retornar
apenas os resultados desejados, um caminho que é muito mais eficiente do que a 
propria aplicação fazer isto por conta própria.

Com SQLAlchemy, um filtro pode ser adicionado em um objeto query com a clausa **where()**.
O seguinte exemplo mostra como retornar apenas produtos feitos por 'Commodore':

```python
# busca todos os produtos
query = select(Produto)
todos_produtos = session.scalars(query).all()

>>> len(todos_produtos)
149

# busca apenas os fabricados por 'Commodore'
query = select(Produto).where(Produto.fabricado == 'Commodore')
filtrados = session.scalars(query).all()

>> len(filtrados)
10
```

O SqlAlchemy implementa uma solucação altamente sofisticada para definir filtros
que combinam os atributos da classe modelo com operadores padrão do Python como
'==', '>=', '<=', '!=', exemplo de query:

```python
query = select(Produto).where(Produto.ano >= 1990)
```

Multipos where() podem ser usados para especificar multiplos filtros:

```python
query = select(Produto).where(Produto.fabricado == 'Commodore').where(Produto.ano == 1980)
```

Multiplos filtros também podem ser implementados dentro de um único where():

```python
query = select(Produto).where(Produto.fabricado == 'Commodore', Produto.ano == 1980)
```

Combinar múltiplos filtros como mostrado acima, aplica efetivamente o operador lógico **AND**.
Algumas querys podem precisar de filtros com o operador **OR**, que é oferecido pelo
SQLAlchemy com a função **or_()**. O exemplo abaixo mostra como implementar uma query
que retorna produtos de antes de 1970 ou de depois de 1990:

```python
from sqlalchemy import or_

query = select(Produto).where(or_(Produto.ano < 1970, Produto.ano > 1990))
```

Além do or_(), também está disponível uma função para o operador **AND** and_() e a 
função not_() implementa o operador unário **NOT**:

```python
from sqlalchemy import and_, not_

query = select(Produto).where(and_(Produto.ano == 1980, Produto.fabricado == 'Commodore'))
query = select(Produto).where(not_(Produto.fabricado == 'Commodore'))
```

Outro filtro útil é o operador LIKE, que pode ser usado para implementar uma função
de busca simples. O seguinte exemplo retorna todos produtos que tem a palavra 'Sinclair'
no nome:

```python
query = select(Produto).where(Produto.nome.like('%Sinclair%'))

>>> session.scalars(query).all()

[Produto(128, "Sinclair QL"),
 Produto(138, "Timex Sinclair 1000"),
 Produto(139, "Timex Sinclair 1500"),
 Produto(140, "Timex Sinclair 2048")]
```

O método like() disponível nos atributos das colunas do modelo, aceita uma string
de padrão (pattern) de pesquisa e retorna todos os resultados que combinam com 
esse padrão. O padrão contém o texto para pesquisar expandido com o caracter %,
aqui estão alguns outros exemplos do padrão para like():

* Sinclair% (Retorna os itens que começam com Sinclair)
* %Sinclair (Retorna os itens que terminam com Sinclair)
* % Sinclair (Retorna itens que possuem o final com espaço seguinda de Sinclair)
* R__% (Retorna itens que começam com a letra R seguidos por mais dois caracteres)
* _ (Retorna itens que são um caracter longo)

A função **like()** é case-sensitive (ou seja, não diferencia entre maiúsculas e minúsculas),
caso precise de case-insensitive, você pode usar a função **ilike()**.

A função **between()** pode ser usada para buscar itens dentro de duas condições,
semelhante ao feito com dois where():

```python
query = select(Produto).where(Produto.ano.between(1970, 1979))
```

## Ordenando resultados

As querys acima retornam os resultados requisitados na ordem que o servidor de banco
de dados escolher, mas bancos de dados relacionais conseguem retornar resultados
ordenados de forma eficiente. O método **order_by()** pode ser adicionado na query
para especificar uma ordem desejada.

```python
query = select(Produto).order_by(Produto.nome)
```

Também é possível organizar em ordem decrescente usando o método desc() no atributo
da coluna dado na clausa order_by(). O exemplo abaixo retorna os produtos organizados
pelo ano na ordem descrecente:

```python
query = select(Produto).order_by(Produto.ano.desc())
```

Existe muitas situações em que apenas um único critério de ordem é insuficiente, por exemplo,
a query acima retorna todos os itens construidos no mesmo ano em ordem aleatória.
O método order_by() aceita multiplos argumentos, cada um adiciona um nível de organização.
O exemplo abaixo pode ser melhorado com um segundo critério:

```python
query = select(Produto).order_by(Produto.ano.desc(), Produto.nome.asc())
```

Note o método **asc()** o qual é usado para especificar que o resultado deve ser 
ordenado pelo nome do produto na ordem crescente. A ordem crescente é o padrão, mas
é interessante adicionar nesse caso para que fica claro qual a ordem a query está
especificando.

## Acessando colunas individuais

Nos exemplos de query até agora foi requisitado linhas inteiras da tabela de produtos,
no qual o SQLAlchemy ORM mapeia instâncias da classe modelo Produto. A função select()
é muito flexível e pode trabalhar com dados mais granulados também. Por exemplo, uma
aplicação pode precisar recuperar apenas uma coluna individual:

```python
query = select(Produto.nome)

>>> session.scalars(query).all()
['Acorn Atom',
 'BBC Micro',
 'Electron',
 'BBC Master',
 ...]
```

Como discutido anteriormente, a função select() não é limitada para retornar um único
valor por resultado, é possível requisitar multiplos resultados na mesma query.
O exemplo abaixo obtém o nome e fabricante de cada produto:

```python
query = select(Produto.nome, Produto.fabricado)

>>> session.execute(query).all()
[('Acorn Atom', 'Acorn Computers Ltd'),
 ('BBC Micro', 'Acorn Computers Ltd'),
 ('Electron', 'Acorn Computers Ltd'),
 ('BBC Master', 'Acorn Computers Ltd'),
 ...]
```

Note que como este exemplo foi executado com session.execute(), o resultado retornado
é um par de valores em cada linha do resultado retornados como tuplas.