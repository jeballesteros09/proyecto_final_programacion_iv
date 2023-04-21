from flask import Flask, request, jsonify, make_response, render_template, session, redirect, url_for
import jwt
from datetime import datetime, timedelta
from functools import wraps


app = Flask(__name__)

app.config['SECRET_KEY'] = 'c09ff01bce9e4f2faafe266e5f638a39'


def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.cookies.get('token')
        if not token:
            return jsonify({'Alert': 'No se encuentra el token!'})
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = payload['username']
            expiration = datetime.fromisoformat(payload['expiration'])
            if expiration < datetime.utcnow():
                return jsonify({'Alert': 'El token ha expirado!'})
        except jwt.exceptions.DecodeError:
            return jsonify({'Alert': 'Token no válido'})
        return func(current_user, *args, **kwargs)
    return decorated


@app.route('/public')
def public():
    return 'For public'


@app.route('/auth')
@token_required
def auth(current_user):
    return 'Listo io, tu JWT fue verificado.'


@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('internal_page.html')


@app.route('/login', methods=['POST'])
def login():

    if request.form['username'] == 'usuario@gmail.com' and request.form['password'] == '123456':
        session['logged_in'] = True
        token = jwt.encode({'username': request.form['username'],
                            'expiration': str(datetime.utcnow() + timedelta(seconds=2))}, app.config['SECRET_KEY'])
        response = make_response(redirect(url_for('home')))
        response.set_cookie('token', value=token, httponly=True)
        return response
    else:
        return make_response('No se pudo verificar; Usuario o contrasena incorrectos.', 403,
                             {'WWW-Authenticate': 'Basic realm: Authentication failed!'})


if __name__ == "__main__":
    app.run(debug=True)
