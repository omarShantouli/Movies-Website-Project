from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired
import requests
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

# TODO: Connecting the database
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movie-database.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    title = db.Column(db.String, nullable= False, unique= True)
    year = db.Column(db.Integer, nullable= False)
    description = db.Column(db.String, nullable= False)
    rating = db.Column(db.Float, nullable= False)
    ranking = db.Column(db.String)
    review = db.Column(db.String)
    img_url = db.Column(db.String, nullable= False)

    def __repr__(self):
        return f"<Movie {self.title}>"

# db.create_all()
#=========================================================================================================

# TODO: Adding a movie to the database

new_movie = Movie(
    title="Phone Booth",
    year=2002,
    description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
    rating=7.3,
    ranking=10,
    review="My favourite character was the caller.",
    img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
)
# db.session.add(new_movie)
# db.session.commit()

#=========================================================================================================

# TODO: Creating the update form class
class Update(FlaskForm):
    rating = FloatField(label= 'Your Rating Out of 10 e.g 7.5', validators=[DataRequired()])
    review = StringField(label= 'Your Review', validators=[DataRequired()])
    submit = SubmitField(label='Done')

#=========================================================================================================

# TODO: Home

@app.route("/")
def home():
    all_movies = Movie.query.all()
    temp = {}
    for movie in all_movies:
        temp[movie] = movie.rating
    temp = dict(sorted(temp.items(), key=lambda item: item[1], reverse= True))
    all_movies = []
    for key, val in temp.items():
        all_movies.append(key)
    for i in range(len(all_movies)):
        # This line gives each movie a new ranking reversed from their order in all_movies
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()

    return render_template("index.html", movies= all_movies, movie_cnt= len(all_movies))

#=========================================================================================================

# TODO: editing the rating and the review of the movie
@app.route('/edit/<int:id>', methods= ['GET', 'POST'])
def edit(id):
    form = Update()
    movie_to_edit = Movie.query.get(id)
    if request.method == 'POST':
        movie_to_edit.rating = form.rating.data
        movie_to_edit.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', form= form)

#=========================================================================================================

# TODO: Deleting a Movie
@app.route('/delete/<int:id>')
def delete(id):
    movie_to_delete = Movie.query.get(id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))

#=========================================================================================================

# TODO: Creating the add form class

class Add(FlaskForm):
    title = StringField(label= 'Movie Title', validators=[DataRequired()])
    submit = SubmitField(label= 'Add Movie')

API_KEY = os.environ['API_KEY']



@app.route('/add', methods= ['GET', 'POST'])
def add():
    form = Add()
    movie = form.title.data
    if form.validate_on_submit():
        url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={movie}"
        movies = requests.get(url).json()['results']
        return render_template('select.html', movies= movies)

    return render_template('add.html', form= form)
#=========================================================================================================

# TODO: add a movie card

@app.route('/add_new/<int:id>', methods= ['GET', 'POST'])
def add_new(id):
    response = requests.get(f"https://api.themoviedb.org/3/movie/{id}?api_key={API_KEY}&language=en-US")
    movie = response.json()
    print(movie)
    new_movie = Movie(
        title=movie['title'],
        year=movie['release_date'].split('-')[0],
        description= movie['overview'],
        rating=7.3,
        ranking=None,
        review="My favourite character was the caller.",
        img_url=f"https://image.tmdb.org/t/p/original/{movie['poster_path']}"
    )
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for('edit', id= Movie.query.all()[-1].id))


#=========================================================================================================

# TODO Running the server

if __name__ == '__main__':
    app.run(debug=True)
