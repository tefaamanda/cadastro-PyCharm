import re
from flask import Flask, jsonify, request
from main import app, con
from flask_bcrypt import generate_password_hash, check_password_hash


@app.route('/cadastro', methods=['GET'])
def cadastro():
    cur = con.cursor()
    cur.execute("SELECT id_cadastro, nome, email, senha FROM cadastro")
    cadastro = cur.fetchall()
    cadastro_dic = []
    for cadastro in cadastro:
        cadastro_dic.append({
            'id_cadastro': cadastro[0],
            'nome': cadastro[1],
            'email': cadastro[2],
            'senha': cadastro[3]
        })
    return jsonify(mensagem='Cadastros', cadastro=cadastro_dic)
def validar_senha(senha):
    padrao = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%¨&*])(?=.*\d).{8,}$'

    if re.fullmatch(padrao, senha):
        return True
    else:
        return False

@app.route('/cadastro', methods=['POST'])
def cadastro_post():
    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')

    if not validar_senha(senha):
        return jsonify('A sua senha precisa ter pelo menos 8 caracteres, uma letra maiúscula, uma letra minúscula, um número e um caractere especial.')

    cursor = con.cursor()

    cursor.execute("SELECT 1 FROM cadastro WHERE EMAIL = ?", (email,))

    if cursor.fetchone():
        return jsonify({"error": "E-mail já cadastrado!"}), 400

    senha = generate_password_hash(senha).decode('utf-8')

    cursor.execute("INSERT INTO CADASTRO(NOME, EMAIL, SENHA) VALUES (?, ?, ?)",
                   (nome, email, senha))

    con.commit()
    cursor.close()

    return jsonify({
        'message': "Cadastro registrado com sucesso!",
        'cadastro': {
            'nome': nome,
            'email': email,
            'senha': senha
        }
    })


@app.route('/cadastro/<int:id>', methods=['PUT'])
def cadastro_put(id):
    cursor = con.cursor()
    cursor.execute("select id_cadastro, nome, email, senha from cadastro WHERE id_cadastro = ?", (id,))
    cadastro_data = cursor.fetchone()

    if not cadastro_data:
        cursor.close()
        return jsonify({"Cadastro não encontrado"})

    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')

    cursor.execute("UPDATE cadastro SET NOME = ?, EMAIL = ?, SENHA = ? WHERE ID_CADASTRO = ?",
                   (nome, email, senha, id))
    con.commit()
    cursor.close()

    return jsonify({
        'message': "Cadastro atualizado com sucesso!",
        'cadastro': {
            'id_cadastro': id,
            'nome': nome,
            'email': email,
            'senha': senha
        }
    })

@app.route('/cadastro/<int:id>', methods=['DELETE'])
def deletar_cadastro(id):
    cursor = con.cursor()

    cursor.execute("SELECT 1 FROM cadastro WHERE ID_CADASTRO = ?", (id,))
    if not cursor.fetchone():
        cursor.close()
        return jsonify({"error": "Cadastro não encontrado"}), 404

    cursor.execute("DELETE FROM cadastro WHERE ID_CADASTRO = ?", (id,))
    con.commit()
    cursor.close()

    return jsonify({
        'message': "Cadastro excluído com sucesso!",
        'id_cadastro': id
    })

@app.route('/login/<int:id>', methods=['GET', 'POST'])
def login(id):
    cursor = con.cursor()
    cursor.execute("select id_cadastro, nome, email, senha from cadastro WHERE id_cadastro = ?", (id,))
    login_data = cursor.fetchone()

    if not login_data:
        cursor.close()
        return jsonify({'erro': "Login não encontrado"}), 400

    senha_hash = senha [0]

    if check_password_hash(senha_hash, senha):
        return jsonify({"message": "Login realizado com sucesso"}), 200

    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')

    cursor = con.cursor()

    cursor.execute("SELECT id_cadastro, nome FROM Cadastro WHERE email = ? AND senha = ?", (email, senha,))
    cadastro = cursor.fetchone()

    cursor.execute("SELECT senha FROM Cadastro WHERE email = ?", (email,))
    senha = cursor.fetchone()
    cursor.close()

    if cadastro:
        return jsonify({
            'message': "Login feito com sucesso!"
        })

    else:
        return jsonify({
            'message': "Erro no login!"
        })