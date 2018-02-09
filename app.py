import os
import random
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash, _app_ctx_stack

app = Flask(__name__)
app.config.from_object(__name__)#Load config from this file.

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'hskall.db'),
    DEBUG=True,
    SECRET_KEY=b'seCre7'
))
app.config.from_envvar('HSKVIEW_SETTINGS', silent=True)


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    top = _app_ctx_stack.top
    if not hasattr(top, 'sqlite_db'):
        top.sqlite_db = sqlite3.connect(app.config['DATABASE'])
        top.sqlite_db.row_factory = sqlite3.Row
    return top.sqlite_db


@app.teardown_appcontext
def close_database(exception):
    """Closes the database again at the end of the request."""
    top = _app_ctx_stack.top
    if hasattr(top, 'sqlite_db'):
        top.sqlite_db.close()


def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    populate_db()


def populate_db():
    for hskx in range(1, 7):

        db = get_db()

        insert_sql = '''
             INSERT INTO hskvocab(simplified, traditional, pinyinnumbers, pinyintones, definition, hsklevel)
             VALUES (?,?,?,?,?,?)'''

        filename = 'HSK%d.txt' % hskx

        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))

        with open(os.path.join(__location__, filename), encoding='utf-8') as f:
            raw = f.read()
        lines = raw.split('\n')

        words = []
        for line in lines:
            sections = line.split('\t')
            sections.append(hskx)
            words.append(sections)

        db.executemany(insert_sql, words)
        db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


def query_db(query, args=(), one=False):
    """Queries the database and returns a list of dictionaries."""
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    return (rv[0] if rv else None) if one else rv


@app.route('/')
def home():
    random_word = random.randint(1, 5000)
    query = '''
            SELECT * FROM hskvocab
            WHERE ID = %d''' % random_word
    level_query = query_db('select hsklevel from hskvocab where id=%d' % random_word, one=True)
    return render_template('home.html', hsk=level_query, word=query_db(query, one=True))


@app.route('/<word_id>')
def word(word_id):
    query = "select * from hskvocab where id=%s" % word_id
    return render_template('word.html', word=query_db(query, one=True))


@app.route('/hsk1')
def hsk1():
    return render_template('vocab.html', words=query_db('''
        select * from hskvocab
        where hsklevel=1'''))


@app.route('/hsk2')
def hsk2():
    return render_template('vocab.html', words=query_db('''
        select * from hskvocab
        where hsklevel=2'''))


@app.route('/hsk3')
def hsk3():
    return render_template('vocab.html', words=query_db('''
        select * from hskvocab
        where hsklevel=3'''))


@app.route('/hsk4')
def hsk4():
    return render_template('vocab.html', words=query_db('''
        select * from hskvocab
        where hsklevel=4'''))


@app.route('/hsk5')
def hsk5():
    return render_template('vocab.html', words=query_db('''
        select * from hskvocab
        where hsklevel=5'''))


@app.route('/hsk6')
def hsk6():
    return render_template('vocab.html', words=query_db('''
        select * from hskvocab
        where hsklevel=6'''))