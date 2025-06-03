import os
import sqlite3
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify
from datetime import datetime
from dotenv import load_dotenv
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)

# Configuração do Gemini
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    logger.error("Chave API Gemini não encontrada. Verifique seu arquivo .env")
    raise ValueError("Chave API Gemini não encontrada. Verifique seu arquivo .env")

genai.configure(api_key=api_key)


# Banco de dados
def get_db_connection():
    conn = sqlite3.connect('burger_mania.db')
    conn.row_factory = sqlite3.Row
    return conn


# Rota principal
@app.route('/')
def index():
    try:
        conn = get_db_connection()
        categorias = conn.execute('SELECT * FROM categorias').fetchall()

        menu = {}
        for categoria in categorias:
            produtos = conn.execute(
                'SELECT * FROM produtos WHERE categoria_id = ?',
                (categoria['id'],)
            ).fetchall()
            menu[categoria['nome']] = produtos

        conn.close()
        return render_template('index.html', menu=menu)
    except Exception as e:
        logger.error(f"Erro ao carregar cardápio: {str(e)}")
        return render_template('error.html', message="Erro ao carregar o cardápio")


# Função para tentar diferentes modelos
def try_generate_content(prompt):
    model_names = [
        'gemini-1.5-flash',  # Modelo mais recente e rápido
        'gemini-1.5-pro',
        'gemini-pro',
        'models/gemini-pro'
    ]

    for model_name in model_names:
        try:
            logger.info(f"Tentando modelo: {model_name}")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)

            # Extrair resposta de forma segura
            if response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate.content, 'parts') and candidate.content.parts:
                    return candidate.content.parts[0].text
                elif hasattr(candidate.content, 'text'):
                    return candidate.content.text

            # Fallback para método antigo
            return response.text

        except Exception as e:
            logger.warning(f"Falha com modelo {model_name}: {str(e)}")
            continue

    raise Exception("Todos os modelos falharam")


# Respostas de fallback
FALLBACK_RESPONSES = [
    "Desculpe, estou tendo dificuldades técnicas. Enquanto isso, aqui estão algumas sugestões:",
    "Nosso sistema de atendimento está temporariamente indisponível. Você pode:",
    "Estou enfrentando problemas técnicos. Enquanto resolvemos, você pode:"
]

SUGGESTIONS = [
    "Verificar nosso cardápio à esquerda",
    "Ligar para (11) 9999-8888 para fazer seu pedido",
    "Visitar nosso restaurante na Rua das Hamburguerias, 123"
]


# Rota do chatbot
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.form['message']
    logger.info(f"Cliente: {user_message}")

    try:
        # Buscar cardápio do banco de dados para contexto
        conn = get_db_connection()
        produtos = conn.execute('SELECT nome, descricao, preco FROM produtos').fetchall()
        cardapio_text = "\n".join([f"{p['nome']}: {p['descricao']} - R${p['preco']:.2f}" for p in produtos])
        conn.close()

        # Prompt com contexto do cardápio
        prompt = f"""
        Você é um atendente virtual da lanchonete Burger Mania. 
        Hoje é {datetime.now().strftime('%d/%m/%Y')}.

        Cardápio disponível:
        {cardapio_text}

        Regras importantes:
        1. Responda como um atendente simpático e prestativo
        2. Forneça apenas informações do cardápio acima
        3. Para 'Monte o Seu Burger', explique que o preço base é R$25,00 + adicionais
        4. Incentive o pedido com sugestões
        5. Mantenha as respostas curtas e objetivas
        6. Não invente produtos que não estão no cardápio

        Cliente: {user_message}
        Atendente: 
        """

        # Tentar gerar resposta com diferentes modelos
        response_text = try_generate_content(prompt)
        logger.info(f"Resposta Gemini: {response_text}")
        return jsonify({'response': response_text})

    except Exception as e:
        logger.error(f"Erro grave no chatbot: {str(e)}")

        # Resposta de fallback personalizada
        fallback_idx = hash(user_message) % len(FALLBACK_RESPONSES)
        fallback = FALLBACK_RESPONSES[fallback_idx]
        suggestions = "\n- ".join(SUGGESTIONS)

        return jsonify({
            'response': f"{fallback}\n- {suggestions}"
        })


if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Usar porta diferente para evitar conflitos