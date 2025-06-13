from flask import Flask, redirect, render_template, request, session, url_for, Response, Blueprint, jsonify 
# Import pour SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.serving import run_simple
from werkzeug.middleware.proxy_fix import ProxyFix


# Déterminer les chemins en fonction de l'environnement
if "SNAP" in os.environ:
    # Dans le snap
    STATIC_FOLDER = os.path.join(os.environ['SNAP'], 'bin', 'Flask', 'static')
    TEMPLATE_FOLDER = os.path.join(os.environ['SNAP'], 'bin', 'Flask', 'templates')
    DATABASE_PATH = os.path.join(os.environ['SNAP_DATA'], 'db', 'persondb.db')
else:
    # En développement local
    dir_path = os.path.dirname(os.path.realpath(__file__))
    STATIC_FOLDER = os.path.join(dir_path, 'static')
    TEMPLATE_FOLDER = os.path.join(dir_path, 'templates')
    DATABASE_PATH = os.path.join(dir_path, 'persondb.db')

# Création de l'application Flask avec les bons chemins
app = Flask(__name__,
           static_folder=STATIC_FOLDER,
           template_folder=TEMPLATE_FOLDER,
           static_url_path='/sample-web/static')

# Configuration de SQLAlchemy (SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Initialisation de SQLAlchemy avec notre application Flask
db = SQLAlchemy(app)

app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

#~~~~~~~~~~~~~~~~~~~~~~~~~~
######## DATABASE ###########


# Définition du modèle Person (nom et âge uniquement)
class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Person {self.name}, {self.age} ans>'

    # Méthode pour convertir l'objet en dictionnaire
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age
        }

# Création de la table dans la base de données
with app.app_context():
    db.create_all()
    # Ajouter quelques personnes de test si la table est vide
    if Person.query.count() == 0:
        db.session.add(Person(name="Alice", age=25))
        db.session.add(Person(name="Bob", age=30))
        db.session.commit()
        print("Données de test ajoutées.")


#~~~~~~~~~~~~~~~~~~~~~~~~~~
########## serving functions #######

@app.route('/sample-web')
def index():
    return render_template('index.html')

@app.route('/sample-web/page1')
def page1():
    return render_template('page1.html')

@app.route('/sample-web/graphique')
def page2():
    return render_template('graphique.html')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
######## API simple pour les personnes ###########

@app.route('/sample-web/api/people', methods=['GET'])
def get_people():
    """Récupérer toutes les personnes"""
    people = Person.query.all()
    return jsonify([person.to_dict() for person in people])

@app.route('/sample-web/api/people/<int:person_id>', methods=['GET'])
def get_person(person_id):
    """Récupérer une personne par son ID"""
    person = Person.query.get_or_404(person_id)
    return jsonify(person.to_dict())

@app.route('/sample-web/api/people', methods=['POST'])
def create_person():
    """Créer une nouvelle personne"""
    data = request.json
    
    # Vérification simple des données
    if not data or 'name' not in data or 'age' not in data:
        return jsonify({'error': 'Les champs nom et âge sont requis'}), 400
    
    # Créer une nouvelle personne
    new_person = Person(
        name=data['name'],
        age=data['age']
    )
    
    db.session.add(new_person)
    db.session.commit()
    
    return jsonify(new_person.to_dict()), 201

@app.route('/sample-web/api/people/<int:person_id>', methods=['DELETE'])
def delete_person(person_id):
    """Supprimer une personne"""
    person = Person.query.get_or_404(person_id)
    db.session.delete(person)
    db.session.commit()
    return jsonify({'result': True})

# Page simple pour afficher et gérer les personnes
@app.route('/sample-web/people')
def people_page():
    """Page pour afficher et gérer les personnes"""
    people = Person.query.all()
    return render_template('people.html', people=people)

##server start

if __name__ == '__main__':
  

    if "SNAP_DATA" in os.environ:
        run_simple('unix://'+os.environ['SNAP_DATA']+'/package-run/sample-web/example.sock', 0, app)
        #app.run(host='0.0.0.0',debug = False, port=3125)
    else:
        app.run(host='0.0.0.0',debug = False, port=12121)

