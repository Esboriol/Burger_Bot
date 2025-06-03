import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()


def criar_banco_dados():
    # Conectar ao banco de dados (será criado se não existir)
    conn = sqlite3.connect('burger_mania.db')
    cursor = conn.cursor()

    # Criar tabelas
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categorias (
        id INTEGER PRIMARY KEY,
        nome TEXT NOT NULL
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY,
        categoria_id INTEGER,
        nome TEXT NOT NULL,
        descricao TEXT,
        preco REAL NOT NULL,
        FOREIGN KEY (categoria_id) REFERENCES categorias(id)
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS adicionais (
        id INTEGER PRIMARY KEY,
        nome TEXT NOT NULL,
        preco_adicional REAL NOT NULL
    )''')

    # Inserir categorias
    categorias = [
        (1, 'Hambúrgueres Especiais'),
        (2, 'Acompanhamentos'),
        (3, 'Bebidas')
    ]
    cursor.executemany('INSERT OR IGNORE INTO categorias (id, nome) VALUES (?, ?)', categorias)

    # Inserir produtos
    produtos = [
        # Hambúrgueres
        (1, 1, 'Clássico Mania',
         'Pão brioche, hambúrguer de 180g, queijo cheddar, alface americana, tomate, cebola roxa e maionese especial',
         28.00),
        (2, 1, 'Burger Duplo Sabor',
         'Pão brioche, 2 hambúrgueres de 120g, queijo prato duplo, bacon crocante e molho barbecue da casa', 35.00),
        (3, 1, 'Veggie Delícia',
         'Pão australiano, hambúrguer de grão de bico, queijo mussarela, rúcula, tomate seco e maionese de manjericão',
         30.00),
        (4, 1, 'Frango Crocante',
         'Pão de gergelim, filé de frango empanado, queijo provolone, alface americana e molho honey mustard', 29.00),
        (5, 1, 'Picanha Supreme',
         'Pão de cerveja, hambúrguer de picanha 200g, queijo coalho grelhado, cebola caramelizada e molho de pimenta suave',
         42.00),
        (6, 1, 'Mega Bacon Blast',
         'Pão de brioche tostado, hambúrguer de 180g, muito bacon em tiras, queijo prato, picles e maionese de alho',
         38.00),
        (7, 1, 'Chef’s Especial',
         'Pão preto, blend de carnes da casa 200g, gorgonzola, pera caramelizada e geleia de pimenta', 40.00),
        (8, 1, 'Kids Burger', 'Pão mini brioche, mini hambúrguer 80g, queijo cheddar e batata frita pequena', 20.00),
        (9, 1, 'Monte o Seu Burger', 'Pão brioche e hambúrguer de 180g (base) + ingredientes escolhidos', 25.00),

        # Acompanhamentos
        (10, 2, 'Batata Frita Tradicional', 'Porção individual', 12.00),
        (11, 2, 'Batata Frita com Cheddar e Bacon', 'Porção individual', 18.00),
        (12, 2, 'Anéis de Cebola', 'Porção individual com molho da casa', 15.00),

        # Bebidas
        (13, 3, 'Refrigerantes (Lata)', 'Coca-Cola, Guaraná, Sprite, Fanta Laranja', 7.00),
        (14, 3, 'Sucos Naturais', 'Laranja, Abacaxi com Hortelã', 10.00)
    ]
    cursor.executemany('''
    INSERT OR IGNORE INTO produtos (id, categoria_id, nome, descricao, preco)
    VALUES (?, ?, ?, ?, ?)
    ''', produtos)

    # Inserir adicionais
    adicionais = [
        (1, 'Queijo Extra', 3.00),
        (2, 'Bacon', 5.00),
        (3, 'Molho Especial', 2.50),
        (4, 'Vegetais Premium', 4.00)
    ]
    cursor.executemany('''
    INSERT OR IGNORE INTO adicionais (id, nome, preco_adicional)
    VALUES (?, ?, ?)
    ''', adicionais)

    # Salvar (commit) as mudanças
    conn.commit()
    conn.close()

    print("Banco de dados criado com sucesso!")


if __name__ == '__main__':
    criar_banco_dados()