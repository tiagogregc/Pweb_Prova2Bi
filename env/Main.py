from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(host='201.23.3.86', user='usr_aluno', password='E$tud@_m@1$', port=5000, database='aula_fatec')

#Rota base
@app.route('/')
def home():
    return render_template('index.html')


#Rotas para disciplinas
@app.route('/disciplinas')
def listar_disciplinas():
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Tiago_Carvalho_tbdisciplinas")
    disciplinas = cursor.fetchall()
    db.close()
    return render_template('listar_disciplinas.html', disciplinas=disciplinas)

@app.route('/disciplinas/cadastro', methods=['GET', 'POST'])
def cadastrar_disciplina():
    if request.method == 'POST':
        nome = request.form['nome']
        carga_horaria = request.form['carga_horaria']
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("INSERT INTO Tiago_Carvalho_tbdisciplinas (nome, carga_horaria) VALUES (%s, %s)", (nome, carga_horaria))
        db.commit()
        db.close()
        return redirect(url_for('listar_disciplinas'))
    return render_template('cadastrar_disciplina.html')

@app.route('/disciplinas/editar/<int:id>', methods=['GET', 'POST'])
def editar_disciplina(id):
    db = get_db_connection()
    cursor = db.cursor()
    if request.method == 'POST':
        nome = request.form['nome']
        carga_horaria = request.form['carga_horaria']
        cursor.execute("UPDATE Tiago_Carvalho_tbdisciplinas SET nome=%s, carga_horaria=%s WHERE id=%s", (nome, carga_horaria, id))
        db.commit()
        db.close()
        return redirect(url_for('listar_disciplinas'))
    cursor.execute("SELECT * FROM Tiago_Carvalho_tbdisciplinas WHERE id=%s", (id,))
    disciplina = cursor.fetchone()
    db.close()
    return render_template('editar_disciplina.html', disciplina=disciplina)

@app.route('/disciplinas/excluir/<int:id>', methods=['POST'])
def excluir_disciplina(id):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM Tiago_Carvalho_tbdisciplinas WHERE id=%s", (id,))
    db.commit()
    db.close()
    return redirect(url_for('listar_disciplinas'))

# Rotas para cursos
@app.route('/cursos')
def listar_cursos():
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("""
        SELECT c.id, c.nome, GROUP_CONCAT(d.nome) AS disciplinas
        FROM Tiago_Carvalho_tb_cursos c
        LEFT JOIN Tiago_Carvalho_tb_curso_disciplinas cd ON c.id = cd.curso_id
        LEFT JOIN Tiago_Carvalho_tbdisciplinas d ON cd.disciplina_id = d.id
        GROUP BY c.id
    """)
    cursos = cursor.fetchall()
    db.close()
    return render_template('listar_cursos.html', cursos=cursos)

@app.route('/cursos/novo', methods=['GET', 'POST'])
def novo_curso():
    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM Tiago_Carvalho_tbdisciplinas")
    disciplinas = cursor.fetchall()

    if request.method == 'POST':
        nome = request.form['nome']
        disciplinas_selecionadas = request.form.getlist('disciplinas')

        cursor.execute("INSERT INTO Tiago_Carvalho_tb_cursos (nome) VALUES (%s)", (nome,))
        curso_id = cursor.lastrowid  

        for disciplina_id in disciplinas_selecionadas:
            cursor.execute("INSERT INTO Tiago_Carvalho_tb_curso_disciplinas (curso_id, disciplina_id) VALUES (%s, %s)", (curso_id, disciplina_id))

        db.commit()  
        db.close() 
        return redirect(url_for('listar_cursos'))

    db.close()  
    return render_template('cadastrar_curso.html', disciplinas=disciplinas)  

@app.route('/cursos/editar/<int:id>', methods=['GET', 'POST'])
def editar_curso(id):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Tiago_Carvalho_tbdisciplinas")
    todas_disciplinas = cursor.fetchall()
    if request.method == 'POST':
        nome = request.form['nome']
        disciplinas_selecionadas = request.form.getlist('disciplinas')
        cursor.execute("UPDATE Tiago_Carvalho_tb_cursos SET nome=%s WHERE id=%s", (nome, id))
        cursor.execute("DELETE FROM Tiago_Carvalho_tb_curso_disciplinas WHERE curso_id=%s", (id,))
        for disciplina_id in disciplinas_selecionadas:
            cursor.execute("INSERT INTO Tiago_Carvalho_tb_curso_disciplinas (curso_id, disciplina_id) VALUES (%s, %s)", (id, disciplina_id))
        db.commit()
        db.close()
        return redirect(url_for('listar_cursos'))
    cursor.execute("SELECT * FROM Tiago_Carvalho_tb_cursos WHERE id=%s", (id,))
    curso = cursor.fetchone()
    cursor.execute("SELECT disciplina_id FROM Tiago_Carvalho_tb_curso_disciplinas WHERE curso_id=%s", (id,))
    disciplinas_curso = [row[0] for row in cursor.fetchall()]
    db.close()
    return render_template('editar_curso.html', curso=curso, todas_disciplinas=todas_disciplinas, disciplinas_curso=disciplinas_curso)

@app.route('/cursos/excluir/<int:id>', methods=['POST'])
def excluir_curso(id):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM Tiago_Carvalho_tb_cursos WHERE id=%s", (id,))
    db.commit()
    db.close()
    return redirect(url_for('listar_cursos'))

# Rotas para professores
@app.route('/professores')
def listar_professores():
    db = get_db_connection()
    cursor = db.cursor()
    
    cursor.execute("SELECT * FROM Tiago_Carvalho_tb_professores")
    professores = cursor.fetchall()
    
    professores_com_disciplinas = []
    for professor in professores:
        cursor.execute("""
            SELECT d.nome FROM Tiago_Carvalho_tbdisciplinas d
            JOIN Tiago_Carvalho_tb_professor_disciplinas pd ON d.id = pd.disciplina_id
            WHERE pd.professor_id = %s
        """, (professor[0],))
        disciplinas = cursor.fetchall()
        disciplinas = [disciplina[0] for disciplina in disciplinas]
        professores_com_disciplinas.append((professor, disciplinas))
    
    db.close()
    return render_template('listar_professores.html', professores_com_disciplinas=professores_com_disciplinas)

@app.route('/professores/novo', methods=['GET', 'POST'])
def novo_professor():
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Tiago_Carvalho_tbdisciplinas")
    disciplinas = cursor.fetchall()
    if request.method == 'POST':
        nome = request.form['nome']
        telefone = request.form['telefone']
        usuario = request.form['usuario']
        senha = request.form['senha']
        disciplinas_selecionadas = request.form.getlist('disciplinas')
        cursor.execute("INSERT INTO Tiago_Carvalho_tb_professores (nome, telefone, usuario, senha) VALUES (%s, %s, %s, %s)", (nome, telefone, usuario, senha))
        professor_id = cursor.lastrowid
        for disciplina_id in disciplinas_selecionadas:
            cursor.execute("INSERT INTO Tiago_Carvalho_tb_professor_disciplinas (professor_id, disciplina_id) VALUES (%s, %s)", (professor_id, disciplina_id))
        db.commit()
        db.close()
        return redirect(url_for('listar_professores'))
    db.close()
    return render_template('cadastrar_professor.html', disciplinas=disciplinas)

@app.route('/professores/editar/<int:id>', methods=['GET', 'POST'])
def editar_professor(id):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Tiago_Carvalho_tbdisciplinas")
    todas_disciplinas = cursor.fetchall()
    if request.method == 'POST':
        nome = request.form['nome']
        telefone = request.form['telefone']
        usuario = request.form['usuario']
        senha = request.form['senha']
        disciplinas_selecionadas = request.form.getlist('disciplinas')
        cursor.execute("UPDATE Tiago_Carvalho_tb_professores SET nome=%s, telefone=%s, usuario=%s, senha=%s WHERE id=%s", (nome, telefone, usuario, senha, id))
        cursor.execute("DELETE FROM Tiago_Carvalho_tb_professor_disciplinas WHERE professor_id=%s", (id,))
        for disciplina_id in disciplinas_selecionadas:
            cursor.execute("INSERT INTO Tiago_Carvalho_tb_professor_disciplinas (professor_id, disciplina_id) VALUES (%s, %s)", (id, disciplina_id))
        db.commit()
        db.close()
        return redirect(url_for('listar_professores'))
    cursor.execute("SELECT * FROM Tiago_Carvalho_tb_professores WHERE id=%s", (id,))
    professor = cursor.fetchone()
    cursor.execute("SELECT disciplina_id FROM Tiago_Carvalho_tb_professor_disciplinas WHERE professor_id=%s", (id,))
    disciplinas_professor = [row[0] for row in cursor.fetchall()]
    db.close()
    return render_template('editar_professor.html', professor=professor, todas_disciplinas=todas_disciplinas, disciplinas_professor=disciplinas_professor)

@app.route('/professores/excluir/<int:id>', methods=['POST'])
def excluir_professor(id):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM Tiago_Carvalho_tb_professores WHERE id=%s", (id,))
    db.commit()
    db.close()
    return redirect(url_for('listar_professores'))

# Rotas para alunos
@app.route('/alunos')
def listar_alunos():
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Pedro_Mota_tb_alunos")
    alunos = cursor.fetchall()
    db.close()
    return render_template('listar_alunos.html', alunos=alunos)

@app.route('/alunos/novo', methods=['GET', 'POST'])
def novo_aluno():
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Tiago_Carvalho_tb_cursos")
    cursos = cursor.fetchall()
    if request.method == 'POST':
        nome = request.form['nome']
        cpf = request.form['cpf']
        endereco = request.form['endereco']
        senha = request.form['senha']
        curso_id = request.form['curso_id']
        cursor.execute("INSERT INTO Pedro_Mota_tb_alunos (nome, cpf, endereco, senha, curso_id) VALUES (%s, %s, %s, %s, %s)", (nome, cpf, endereco, senha, curso_id))
        db.commit()
        db.close()
        return redirect(url_for('listar_alunos'))
    db.close()
    return render_template('novo_aluno.html', cursos=cursos)

@app.route('/alunos/editar/<int:id>', methods=['GET', 'POST'])
def editar_aluno(id):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Tiago_Carvalho_tb_cursos")
    cursos = cursor.fetchall()
    if request.method == 'POST':
        nome = request.form['nome']
        cpf = request.form['cpf']
        endereco = request.form['endereco']
        senha = request.form['senha']
        curso_id = request.form['curso_id']
        cursor.execute("UPDATE Pedro_Mota_tb_alunos SET nome=%s, cpf=%s, endereco=%s, senha=%s, curso_id=%s WHERE id=%s", (nome, cpf, endereco, senha, curso_id, id))
        db.commit()
        db.close()
        return redirect(url_for('listar_alunos'))
    cursor.execute("SELECT * FROM Pedro_Mota_tb_alunos WHERE id=%s", (id,))
    aluno = cursor.fetchone()
    db.close()
    return render_template('editar_aluno.html', aluno=aluno, cursos=cursos)

@app.route('/alunos/excluir/<int:id>', methods=['POST'])
def excluir_aluno(id):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM Pedro_Mota_tb_alunos WHERE id=%s", (id,))
    db.commit()
    db.close()
    return redirect(url_for('listar_alunos'))

if __name__ == '__main__':
    app.run(debug=True)