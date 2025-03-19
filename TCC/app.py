from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'affs_essaminaemuito_feia_ee'  # Troque por uma chave segura!

# Configurações do MySQL
app.config['MYSQL_HOST'] = 'localhost'           # Ou o host do seu servidor
app.config['MYSQL_USER'] = 'root'         # Usuário do MySQL
app.config['MYSQL_PASSWORD'] = 'Feminicare123'       # Senha do MySQL
app.config['MYSQL_DB'] = 'feminicare'


mysql = MySQL(app)

# Página Inicial (Login + Cadastro)
@app.route('/')
def index():
    return render_template('index.html')

# Rota para Login
@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    senha = request.form['senha']

    cur = mysql.connection.cursor()
    cur.execute("SELECT id, nome, email, senha, telefone, numeroCred, especialidade FROM usuarios WHERE email = %s", (email,))
    user = cur.fetchone()
    cur.close()

    if user:
        user_id, nome, email, senha_hash, telefone, numeroCred, especialidade = user
        if check_password_hash(senha_hash, senha):  # Verifica se a senha está correta
            session['usuario_id'] = user_id
            session['nome'] = nome
            session['email'] = email
            session['telefone'] = telefone
            session['numeroCred'] = numeroCred
            session['especialidade'] = especialidade

            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('meu_perfil'))  #  Redireciona para a tela de perfil
        else:
            flash('Senha incorreta.', 'error')
    else:
        flash('Usuário não encontrado.', 'error')

    return redirect(url_for('index'))

# Rota para Cadastro
@app.route('/cadastro', methods=['POST'])
def cadastro():
    nome = request.form['nome']
    email = request.form['emailCadastro']
    senha = request.form['senhaCadastro']
    conf_senha = request.form['confSenha']
    especialidade = request.form['especialidade']
    telefone = request.form['telefone']
    numeroCred = request.form['numeroCred']

    if senha != conf_senha:
        flash('As senhas não conferem!', 'error')
        return redirect(url_for('index'))

    senha_hash = generate_password_hash(senha)  # Criptografa a senha antes de salvar no banco

    cur = mysql.connection.cursor()
    cur.execute(
        """INSERT INTO usuarios (nome, email, senha, especialidade, telefone, numeroCred)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (nome, email, senha_hash, especialidade, telefone, numeroCred)
    )
    mysql.connection.commit()
    cur.close()

    flash('Cadastro realizado com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/meu_perfil')
def meu_perfil():
    if 'usuario_id' not in session:
        flash('Você precisa estar logado para acessar essa página.', 'error')
        return redirect(url_for('index'))

    return render_template(
        'meu_perfil.html',
        nome=session.get('nome'),
        email=session.get('email'),
        telefone=session.get('telefone'),
        numeroCred=session.get('numeroCred'),
        especialidade=session.get('especialidade')
    )

@app.route('/esqueci_senha', methods=['GET', 'POST'])
def esqueci_senha():
    if request.method == 'POST':
        email = request.form['email']
        flash('Se este e-mail estiver cadastrado, enviaremos instruções de recuperação.', 'info')
        return redirect(url_for('index'))
    return render_template('esqueci_senha.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
