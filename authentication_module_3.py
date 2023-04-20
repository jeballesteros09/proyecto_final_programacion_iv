from flask import Flask, request, jsonify, make_response, render_template, session
import jwt
from datetime import datetime, timedelta
from functools import wraps

#  http://localhost:5000

app = Flask(__name__)

app.config['SECRET_KEY'] = 'c09ff01bce9e4f2faafe266e5f638a39'


def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'Alert': 'Token is missing!'})
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify({'Alert': 'Invalid token'})
        return func(*args, **kwargs)
    return decorated


@app.route('/public')
def public():
    return 'For public'


@app.route('/auth')
@token_required
def auth():
    return 'JWT is verified.'


@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return 'Tas loggeado pa!'


@app.route('/login', methods=['POST'])
def login():

    if request.form['username'] == 'usuario@gmail.com' and request.form['password'] == '123456':
        session['logged_in'] = True
        token = jwt.encode({'user': request.form['username'],
                            'expiration': str(datetime.utcnow() + timedelta(seconds=600))}, app.config['SECRET_KEY'])
        return jsonify({'token': token})
    else:
        return make_response('Unable to verify; Wrong username or password.', 403,
                             {'WWW-Authenticate': 'Basic realm: Authentication failed!'})


if __name__ == "__main__":
    app.run(debug=True)
