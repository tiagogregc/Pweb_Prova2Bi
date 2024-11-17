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

# Rota para confirmar a exclusão da disciplina
@app.route('/disciplinas/confirmar_exclusao/<int:id>', methods=['GET', 'POST'])
def confirmar_exclusao_disciplina(id):
    db = get_db_connection()
    cursor = db.cursor()

    # Buscar o nome da disciplina para exibir na modal
    cursor.execute("SELECT nome FROM Tiago_Carvalho_tbdisciplinas WHERE id=%s", (id,))
    disciplina = cursor.fetchone()

    if not disciplina:
        db.close()
        return redirect(url_for('listar_disciplinas'))

    disciplina_nome = disciplina[0]
    
    # Verificar se a requisição é POST (excluir)
    if request.method == 'POST':
        # Excluir a disciplina
        cursor.execute("DELETE FROM Tiago_Carvalho_tbdisciplinas WHERE id=%s", (id,))
        db.commit()
        db.close()
        return redirect(url_for('listar_disciplinas'))

    # Exibir a modal com o nome da disciplina
    db.close()
    return render_template('listar_disciplinas.html', disciplina_id_excluir=id, disciplina_nome=disciplina_nome)

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
    
    # Buscando todas as disciplinas
    cursor.execute("SELECT * FROM Tiago_Carvalho_tbdisciplinas")
    todas_disciplinas = cursor.fetchall()

    if request.method == 'POST':
        nome = request.form['nome']
        disciplinas_selecionadas = request.form.getlist('disciplinas')
        
        # Atualizando o nome do curso
        cursor.execute("UPDATE Tiago_Carvalho_tb_cursos SET nome=%s WHERE id=%s", (nome, id))
        
        # Removendo as disciplinas antigas associadas ao curso
        cursor.execute("DELETE FROM Tiago_Carvalho_tb_curso_disciplinas WHERE curso_id=%s", (id,))
        
        # Adicionando as disciplinas selecionadas
        for disciplina_id in disciplinas_selecionadas:
            cursor.execute("INSERT INTO Tiago_Carvalho_tb_curso_disciplinas (curso_id, disciplina_id) VALUES (%s, %s)", (id, disciplina_id))
        
        db.commit()
        db.close()
        return redirect(url_for('listar_cursos'))
    
    # Buscando o curso atual
    cursor.execute("SELECT * FROM Tiago_Carvalho_tb_cursos WHERE id=%s", (id,))
    curso = cursor.fetchone()

    # Buscando as disciplinas associadas ao curso
    cursor.execute("SELECT disciplina_id FROM Tiago_Carvalho_tb_curso_disciplinas WHERE curso_id=%s", (id,))
    disciplinas_curso = [row[0] for row in cursor.fetchall()]
    
    db.close()
    
    return render_template('editar_curso.html', curso=curso, todas_disciplinas=todas_disciplinas, disciplinas_curso=disciplinas_curso)

# Rota para confirmar a exclusão do curso
@app.route('/cursos/confirmar_exclusao/<int:id>', methods=['GET', 'POST'])
def confirmar_exclusao_curso(id):
    db = get_db_connection()
    cursor = db.cursor()

    # Buscar o nome do curso para exibir na modal
    cursor.execute("SELECT nome FROM Tiago_Carvalho_tb_cursos WHERE id=%s", (id,))
    curso = cursor.fetchone()

    if not curso:
        db.close()
        return redirect(url_for('listar_cursos'))

    curso_nome = curso[0]
    
    # Verificar se a requisição é POST (excluir)
    if request.method == 'POST':
        # Excluir o curso
        cursor.execute("DELETE FROM Tiago_Carvalho_tb_cursos WHERE id=%s", (id,))
        db.commit()
        db.close()
        return redirect(url_for('listar_cursos'))

    # Exibir a modal com o nome do curso
    db.close()
    return render_template('listar_cursos.html', curso_id_excluir=id, curso_nome=curso_nome)

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

@app.route('/professores/confirmar_exclusao/<int:id>', methods=['GET', 'POST'])
def confirmar_exclusao_professor(id):
    db = get_db_connection()
    cursor = db.cursor()

    # Buscar o nome do professor para exibir na modal
    cursor.execute("SELECT nome FROM Tiago_Carvalho_tb_professores WHERE id=%s", (id,))
    professor = cursor.fetchone()

    if not professor:
        db.close()
        return redirect(url_for('listar_professores'))

    professor_nome = professor[0]
    
    # Verificar se a requisição é POST (excluir)
    if request.method == 'POST':
        # Excluir o professor
        cursor.execute("DELETE FROM Tiago_Carvalho_tb_professores WHERE id=%s", (id,))
        db.commit()
        db.close()
        return redirect(url_for('listar_professores'))

    # Exibir a modal com o nome do professor
    db.close()
    return render_template('listar_professores.html', professor_id_excluir=id, professor_nome=professor_nome)

# Rotas para alunos
@app.route('/alunos')
def listar_alunos():
    db = get_db_connection()
    cursor = db.cursor()
    
    # Buscar alunos e seus cursos
    cursor.execute("""
        SELECT a.id, a.nome, a.cpf, a.endereco, a.senha, GROUP_CONCAT(c.nome) AS cursos
        FROM Tiago_Carvalho_tb_alunos a
        LEFT JOIN Tiago_Carvalho_tb_alunos_cursos ac ON a.id = ac.aluno_id
        LEFT JOIN Tiago_Carvalho_tb_cursos c ON ac.curso_id = c.id
        GROUP BY a.id
    """)
    
    alunos = cursor.fetchall()
    db.close()
    
    return render_template('listar_alunos.html', alunos=alunos)

@app.route('/alunos/novo', methods=['GET', 'POST'])
def cadastrar_aluno():
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Tiago_Carvalho_tb_cursos")
    cursos = cursor.fetchall()
    
    if request.method == 'POST':
        nome = request.form['nome']
        cpf = request.form['cpf']
        endereco = request.form['endereco']
        senha = request.form['senha']
        cursos_selecionados = request.form.getlist('curso_id')
        
        cursor.execute("INSERT INTO Tiago_Carvalho_tb_alunos (nome, cpf, endereco, senha) VALUES (%s, %s, %s, %s)", (nome, cpf, endereco, senha))
        aluno_id = cursor.lastrowid
        
        for curso_id in cursos_selecionados:
            cursor.execute("INSERT INTO Tiago_Carvalho_tb_alunos_cursos (aluno_id, curso_id) VALUES (%s, %s)", (aluno_id, curso_id))
        
        db.commit()
        db.close()
        return redirect(url_for('listar_alunos'))
    
    db.close()
    return render_template('cadastrar_aluno.html', cursos=cursos)

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
        cursos_selecionados = request.form.getlist('curso_id')  # Obter múltiplos cursos
        
        # Atualizar os dados do aluno na tabela Tiago_Carvalho_tb_alunos
        cursor.execute("UPDATE Tiago_Carvalho_tb_alunos SET nome=%s, cpf=%s, endereco=%s, senha=%s WHERE id=%s", (nome, cpf, endereco, senha, id))
        
        # Remover cursos antigos associados ao aluno
        cursor.execute("DELETE FROM Tiago_Carvalho_tb_alunos_cursos WHERE aluno_id=%s", (id,))
        
        # Adicionar os cursos selecionados
        for curso_id in cursos_selecionados:
            cursor.execute("INSERT INTO Tiago_Carvalho_tb_alunos_cursos (aluno_id, curso_id) VALUES (%s, %s)", (id, curso_id))
        
        db.commit()
        db.close()
        return redirect(url_for('listar_alunos'))
    
    cursor.execute("SELECT * FROM Tiago_Carvalho_tb_alunos WHERE id=%s", (id,))
    aluno = cursor.fetchone()
    
    # Carregar cursos do aluno (selecionados previamente)
    cursor.execute("SELECT curso_id FROM Tiago_Carvalho_tb_alunos_cursos WHERE aluno_id=%s", (id,))
    cursos_aluno = [curso[0] for curso in cursor.fetchall()]
    
    db.close()
    return render_template('editar_aluno.html', aluno=aluno, cursos=cursos, cursos_aluno=cursos_aluno)

@app.route('/alunos/confirmar_exclusao/<int:id>', methods=['GET', 'POST'])
def confirmar_exclusao(id):
    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM Tiago_Carvalho_tb_alunos WHERE id=%s", (id,))
    aluno = cursor.fetchone()

    aluno_id = aluno[0]
    aluno_nome = aluno[1]

    if request.method == 'POST':
        # Remover os registros da tabela de relacionamento entre aluno e cursos
        cursor.execute("DELETE FROM Tiago_Carvalho_tb_alunos_cursos WHERE aluno_id=%s", (id,))
        
        # Remover o aluno da tabela Tiago_Carvalho_tb_alunos
        cursor.execute("DELETE FROM Tiago_Carvalho_tb_alunos WHERE id=%s", (id,))
        
        db.commit()
        db.close()
        return redirect(url_for('listar_alunos'))

    db.close()

    # Passar os dados para o template da modal
    return render_template('listar_alunos.html', aluno_id_excluir=id, aluno_nome=aluno_nome)

if __name__ == '__main__':
    app.run(debug=True)