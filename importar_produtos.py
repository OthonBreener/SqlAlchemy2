import csv
from db import Session, Modelo, engine
from models import Produto


def inicar_mapeamento():
    #Modelo.metadata.drop_all(engine)
    Modelo.metadata.create_all(engine)


def main():
    inicar_mapeamento()

    with Session() as session:
        with session.begin():
            with open('products.csv') as f:
                reader = csv.DictReader(f)
                for linha in reader:
                    linha['year'] = int(linha['year'])
                    produto = Produto(
                        nome=linha.get('name'),
                        fabricado=linha.get('manufacturer'),
                        ano=linha.get('year'),
                        pais=linha.get('contry'),
                        cpu=linha.get('cpu'),
                    )
                    session.add(produto)

if __name__ == '__main__':
    main()