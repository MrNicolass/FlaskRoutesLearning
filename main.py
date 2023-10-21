from flask import Flask, flash, redirect, render_template, request, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy #Biblioteca responsável pelo banco de dados
import ujson #Biblioteca "estilziada" para trabalhar com dados em JSON
import time #Biblioteca utilizada para calcular o tempo das execuções
import heapq #Biblioteca para implementar uma fila de prioridades

#Variável/instância para acessar o Flask de forma mais fácil
app = Flask(__name__, template_folder='Pages')
#Conexão com o banco de dados e sua chave de segurança
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Persons.db'
app.config["SECRET_KEY"] = "random string"
#Instância do banco
db = SQLAlchemy(app)

#---<Rotas de navegação>---

#Rota padrão/inicial
@app.route("/")
def home():
    return render_template('index.html') #Carrega arquivo index/home html com as rotas e demais envios de dados

#Rota de execução da tarefa dois -> Criação de dez mil registros no SQLite
@app.route("/crud")
def crud():
    #Função try para tentar criar e retornar os registros no banco e calcular o tempo de execução
    try:
        #Calcula o tempo de execuação da função de criação de pessoas e da query de busca
        begin = time.time()
        Persons.new_persons()
        queryPersons = Persons.toJSON()
        end = time.time()
        execution_time = (end - begin) * 1000
        return f"{execution_time} {queryPersons}"
    #Função except para caso aconteça algum erro, apresenta mensagem na página home
    except:
        flash(f"Erro na execução", "Error")
        return render_template('index.html')

#Rota de execução da tarefa um -> Ordenação do array ordenação utilizando Merge Sort
@app.route("/order", methods=['GET', 'POST'])
def order():
    #Servidor verifica se está recebendo algo com o método POST
    if request.method == "POST":
        textareaData = request.form["vetor"]
        #Verifica se foi recebido algo, se não for apresenta um erro
        if not textareaData:
            flash("Vetor não digitado!", "Error")
        else:
            #Transforma os números digitados em uma lista, depois aplica a função map para transformar cada número da string que for divido por vírgula pela função split em números inteiros
            vetor = list(map(int, textareaData.split(",")))
            #Ordena os números com a função Merge Sort e calcula o tempo de execução
            begin = time.time()
            inOrder = merge_sort(vetor)
            end = time.time()
            #Transforma vetor ordenado em um JSON
            success_json = ujson.dumps(inOrder)
            execution_time = (end - begin) * 1000 #Cálcula o tempo de execução e transforma em microsegundos
            flash(f"{success_json} Tempo de execução: {execution_time}", "Sucesso")
    return render_template("order.html")

#Rota de execução da tarefa três -> Encontrar o menor caminho dentro de um graph
@app.route("/graph", methods=['GET', 'POST'])
def graph():
    #Servidor verifica se está recebendo algo com o método POST
    if request.method == "POST":
        textareaData = request.form["graph"]
        #Verifica se foi recebido algo, se não for apresenta um erro
        if not textareaData:
            flash("Grafo não digitado!", "Error")
        else:
            #Transforma os valores digitados de String para JSON
            graph = ujson.loads(textareaData)
            #Executado o algoritmo de dijkstra para encontrar o menor caminho no grafo, passando o grafo e o inicio e calcula o tempo de execução
            begin = time.time()
            shortestWay = dijkstra(graph, "A")
            end = time.time()
            #Transforma resultado do grafo em JSON
            success_json = ujson.dumps(shortestWay)
            execution_time = (end - begin) * 1000
            flash(f"{success_json} Tempo de execução: {execution_time}", "Sucesso")
    return render_template("graph.html")

#---</Rotas de navegação>---

#---<Classes e funções do programa>---

class Persons(db.Model):
    #Campos Globais da classe -> Colunas da tabela
    id = db.Column('person_id', db.Integer, primary_key = True)
    nome = db.Column(db.String(50))
    email = db.Column(db.String(40))
    phone = db.Column(db.Integer)
    notes = db.Column(db.String(100))

    #Função construtora da classe
    def __init__(self, nome, phone, email, notes):
        self.nome = nome
        self.phone = phone
        self.email = email
        self.notes = notes

    #Função para realizar criação das pessoas/popular banco de dados
    def new_persons():
        for i in range(10000):
            persun = Persons(
                nome=f"Nicolas{i+1}", #Adiciona uma numeração nos nomes para diferenciação
                email="nicolas@catolica.com",
                phone="4799101520",
                notes="observacao"
            )
            db.session.add(persun)
        db.session.commit()
    
    #Função para transformar os dados da classe/tabela persons em JSON
    def toJSON():
        person_to_dict = [] 
        for e in db.session.query(Persons).all(): 
            person_to_dict.append(e.to_dict())
        success_json = ujson.dumps(person_to_dict)
        return success_json
    
    #Função que corrigi a não possibilidade de serialização dos dados, 
    #converte os dados da instância do objeto da classe para um dicionário/array
    def to_dict(self): 
        return { 
            'nome': self.nome, 
            'email': self.email, 
            'phone': self.phone, 
            'notes': self.notes
            }

def merge_sort(lista):
    if len(lista) <= 1:
        return lista
    
    meio = len(lista) // 2
    esquerda = merge_sort(lista[:meio])
    direita = merge_sort(lista[meio:])
    
    return merge(esquerda, direita)

def merge(esquerda, direita):
    resultado = []
    i = j = 0
    
    while i < len(esquerda) and j < len(direita):
        if esquerda[i] < direita[j]:
            resultado.append(esquerda[i])
            i += 1
        else:
            resultado.append(direita[j])
            j += 1
    
    resultado.extend(esquerda[i:])
    resultado.extend(direita[j:])
    
    return resultado

def dijkstra(graph, begin):
    distance = {v: float('infinity') for v in graph}
    distance[begin] = 0
    pq = [(0, begin)]
    
    while len(pq) > 0:
        current_distance, current_vertex = heapq.heappop(pq)
        
        if current_distance > distance[current_vertex]:
            continue
        
        for neighbor, weight in graph[current_vertex].items():
            dist = current_distance + weight
            
            if dist < distance[neighbor]:
                distance[neighbor] = dist
                heapq.heappush(pq, (dist, neighbor))
    
    return distance

#---</Classes e funções do programa>---

if __name__ == '__main__':
    app.app_context().push()
    db.create_all()
    app.run(host='0.0.0.0', port='5000', debug=True)