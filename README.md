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
