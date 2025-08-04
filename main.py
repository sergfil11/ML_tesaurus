from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
db_path = os.path.join(basedir, 'thesaurus.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

db = SQLAlchemy(app)

# Тематический раздел (например: "Обучение с учителем", "Градиентный спуск")
class Section(db.Model):
    id   = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    terms = db.relationship(
        'Term',
        backref='section',
        lazy=True,
        cascade='all, delete-orphan'   # <- вот он, каскад
    )


class Term(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(100), unique=True, nullable=False)
    definition = db.Column(db.Text, nullable=False)
    comment = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=False)

# Создаём БД
with app.app_context():
    db.create_all()

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        term = request.form['term']
        definition = request.form['definition']
        comment = request.form['comment']
        section_id = request.form['section_id']
        if Term.query.filter_by(term=term).first():
            return "Термин уже существует", 400
        new = Term(term=term, definition=definition, comment=comment,
                   section_id=section_id, updated_at=datetime.utcnow())
        db.session.add(new)
        db.session.commit()
        return redirect(url_for('index'))

    sections = Section.query.order_by(Section.name).all()
    return render_template('add.html', sections=sections)

@app.route('/')
def index():
    sections = Section.query.order_by(Section.name).all()
    return render_template('index.html', sections=sections)

@app.route('/term/<int:term_id>')
def term_detail(term_id):
    entry = Term.query.get_or_404(term_id)
    return render_template('detail.html', entry=entry)

@app.route('/add_section', methods=['GET', 'POST'])
def add_section():
    if request.method == 'POST':
        name = request.form['name']
        if Section.query.filter_by(name=name).first():
            return "Раздел с таким названием уже существует", 400
        new_section = Section(name=name)
        db.session.add(new_section)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_section.html')


@app.route('/edit/<int:term_id>', methods=['GET', 'POST'])
def edit_term(term_id):
    term = Term.query.get_or_404(term_id)
    if request.method == 'POST':
        term.term = request.form['term']
        term.definition = request.form['definition']
        term.comment = request.form['comment']
        term.section_id = request.form['section_id']
        term.updated_at = datetime.utcnow()
        db.session.commit()
        return redirect(url_for('index'))
    sections = Section.query.order_by(Section.name).all()
    return render_template('edit_term.html', term=term, sections=sections)


@app.route('/delete/<int:term_id>', methods=['POST'])
def delete_term(term_id):
    term = Term.query.get_or_404(term_id)
    db.session.delete(term)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete_section/<int:section_id>', methods=['POST'])
def delete_section(section_id):
    section = Section.query.get_or_404(section_id)
    db.session.delete(section)
    db.session.commit()
    return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(debug=True)
