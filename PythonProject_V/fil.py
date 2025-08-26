import os
import json
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)
SECRET_KEY = os.environ.get("SECRET_KEY", "default_key")
app.config["SECRET_KEY"] = SECRET_KEY

people_db = {
    1: {"nome": "Maria Silva", "sexo": "Feminino", "idade": 35, "condicao": "Desempregada",
        "observacao": "Precisa de ajuda com alimentação."},
    2: {"nome": "João Santos", "sexo": "Masculino", "idade": 50, "condicao": "Em situação de rua",
        "observacao": "Necessita de roupas e abrigo."},
    3: {"nome": "Ana Souza", "sexo": "Feminino", "idade": 22, "condicao": "Família de baixa renda",
        "observacao": "Procura emprego e apoio para os filhos."}
}
# Contador para gerar novos IDs
next_id = 4


# --- Rotas do Backend ---

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, people_json=json.dumps(people_db))


@app.route('/add', methods=['POST'])
def add_person():
    """
    Adiciona uma nova pessoa à base de dados.
    O ID é gerado automaticamente.
    """
    global next_id
    nome = request.form.get('nome')
    sexo = request.form.get('sexo')
    idade = int(request.form.get('idade', 0))
    condicao = request.form.get('condicao')
    observacao = request.form.get('observacao')

    if nome and idade > 0:
        people_db[next_id] = {
            "nome": nome,
            "sexo": sexo,
            "idade": idade,
            "condicao": condicao,
            "observacao": observacao
        }
        next_id += 1
    return redirect(url_for('index'))


@app.route('/update', methods=['POST'])
def update_person():
    """
    Atualiza os dados de uma pessoa existente.
    """
    person_id = int(request.form.get('id'))
    nome = request.form.get('nome')
    sexo = request.form.get('sexo')
    idade = int(request.form.get('idade', 0))
    condicao = request.form.get('condicao')
    observacao = request.form.get('observacao')

    if person_id in people_db:
        people_db[person_id]["nome"] = nome
        people_db[person_id]["sexo"] = sexo
        people_db[person_id]["idade"] = idade
        people_db[person_id]["condicao"] = condicao
        people_db[person_id]["observacao"] = observacao
    return redirect(url_for('index'))


@app.route('/delete', methods=['POST'])
def delete_person():
    """
    Deleta uma pessoa da base de dados.
    """
    person_id = int(request.form.get('id'))
    if person_id in people_db:
        del people_db[person_id]
    return redirect(url_for('index'))


# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <title>Gestão de Pessoas</title>
    <style>
        body { font-family: sans-serif; margin: 2em; }
        .container { display: flex; gap: 2em; }
        .form-section, .list-section { flex: 1; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #ccc; padding: 0.5em; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h1>Gestão de Pessoas</h1>
    <div class="container">
        <div class="form-section">
            <h2>Adicionar/Atualizar Pessoa</h2>
            <form id="person-form" method="POST">
                <input type="hidden" name="id" id="person-id">
                <label for="nome">Nome:</label><br>
                <input type="text" name="nome" id="nome" required><br><br>
                <label for="sexo">Sexo:</label><br>
                <input type="text" name="sexo" id="sexo"><br><br>
                <label for="idade">Idade:</label><br>
                <input type="number" name="idade" id="idade" required><br><br>
                <label for="condicao">Condição:</label><br>
                <input type="text" name="condicao" id="condicao"><br><br>
                <label for="observacao">Observação:</label><br>
                <textarea name="observacao" id="observacao"></textarea><br><br>
                <button type="submit" id="submit-button">Adicionar</button>
                <button type="button" onclick="clearForm()">Limpar</button>
            </form>
        </div>
        <div class="list-section">
            <h2>Lista de Pessoas Cadastradas</h2>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Nome</th>
                        <th>Sexo</th>
                        <th>Idade</th>
                        <th>Condição</th>
                        <th>Observação</th>
                        <th>Ações</th>
                    </tr>
                </thead>
                <tbody id="person-list">
                </tbody>
            </table>
        </div>
    </div>

    <script>
        const peopleDb = {{ people_json | safe }};
        const personList = document.getElementById('person-list');
        const personForm = document.getElementById('person-form');
        const submitButton = document.getElementById('submit-button');

        function renderList() {
            personList.innerHTML = '';
            for (const id in peopleDb) {
                const person = peopleDb[id];
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${id}</td>
                    <td>${person.nome}</td>
                    <td>${person.sexo}</td>
                    <td>${person.idade}</td>
                    <td>${person.condicao}</td>
                    <td>${person.observacao}</td>
                    <td>
                        <button onclick="editPerson(${id})">Editar</button>
                        <form method="POST" action="{{ url_for('delete_person') }}" style="display:inline;">
                            <input type="hidden" name="id" value="${id}">
                            <button type="submit">Excluir</button>
                        </form>
                    </td>
                `;
                personList.appendChild(row);
            }
        }

        function editPerson(id) {
            const person = peopleDb[id];
            document.getElementById('person-id').value = id;
            document.getElementById('nome').value = person.nome;
            document.getElementById('sexo').value = person.sexo;
            document.getElementById('idade').value = person.idade;
            document.getElementById('condicao').value = person.condicao;
            document.getElementById('observacao').value = person.observacao;
            submitButton.textContent = 'Atualizar';
            personForm.action = "{{ url_for('update_person') }}";
        }

        function clearForm() {
            personForm.reset();
            document.getElementById('person-id').value = '';
            submitButton.textContent = 'Adicionar';
            personForm.action = "{{ url_for('add_person') }}";
        }

        document.addEventListener('DOMContentLoaded', renderList);
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(debug=True)