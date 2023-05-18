# SqlAlchemy

O sqlalchmey é dividido em dois modulos chamados de Core e ORM.

* Core: Contém lógicas de integração de banco de dados para todos os dialetos
de banco de dados supotado, uma coleção de classes para descrever tabelas de
banco de dados e um sistema sofisticado para gerar declarações de SQL usando
construtores da linguagem python.

* ORM: Introduz uma camada de abstração entre a aplicação python e o banco de dados,
permite muitas operações de banco de dados serem derivadas automaticamente de
ações realizando em objetos python.

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
existente, para isso é necessário utilziar o Alembic. Por conviniência, o MetaData tambpem tem o 
objeto **drop_all()**, usado para apagar todas as tabelas.