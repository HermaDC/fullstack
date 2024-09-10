from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configuración de la base de datos SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo para la tabla de usuarios
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Crear las tablas en la base de datos
with app.app_context():
    db.create_all()

# Ruta de inicio, redirige al login
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# Ruta de registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='sha256')
        
        # Verificar si el usuario ya existe
        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            flash('El nombre de usuario ya está en uso.')
            return redirect(url_for('register'))
        
        # Crear nuevo usuario
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registro exitoso. ¡Inicia sesión ahora!')
        return redirect(url_for('login'))
    
    return render_template('register.html')

# Ruta de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Buscar el usuario en la base de datos
        user = User.query.filter_by(username=username).first()
        
        # Verificar la contraseña
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Inicio de sesión exitoso.')
            return redirect(url_for('dashboard'))
        else:
            flash('Usuario o contraseña incorrectos.')
    
    return render_template('login.html')

# Ruta del contenido reservado (dashboard)
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Por favor, inicia sesión para acceder al contenido.')
        return redirect(url_for('login'))
    return render_template('dashboard.html')

# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Has cerrado sesión exitosamente.')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
