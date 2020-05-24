import flask

app = flask.Flask(__name__)


@app.route('/')
def main():
    return flask.render_template('login.html')


@app.route('/dashboard')
def dash():
    login = flask.request.args.get('login', None)
    password = flask.request.args.get('password', None)
    
    if login != 'pozltoit' or password != 'zapolarie2019aitivistavka':
        return flask.redirect('/')
    
    return flask.render_template('dashboard.html', args=flask.request.args)

@app.route('/list')
def list():
    login = flask.request.args.get('login', None)
    password = flask.request.args.get('password', None)
    
    if login != 'pozltoit' or password != 'zapolarie2019aitivistavka':
        return flask.redirect('/')
    
    return flask.render_template('list.html', args=flask.request.args)
    

if __name__ == "__main__":
    app.run(port=37777)
