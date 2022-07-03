import mysql.connector  # pip install mysql-connector-python
import pickle

from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


def connector():
    mydb = mysql.connector.connect(
        host = "localhost",
        user= "root",
        passwd="MYsql",
        database= "new_movie"
    )
    return mydb

def get_movies(connect):
    c = connect.cursor()
    c.execute("SELECT * FROM movie LIMIT 10")
    for movie in c:
        print(movie)

def get_movie_titles(connect):
    c = connect.cursor()
    c.execute("SELECT * FROM movie")
    return c

def get_movie_title(connect, title):
    c = connect.cursor()
    requete = 'SELECT * FROM movie WHERE movie_title="'+title+'"'
    
    c.execute(requete)
    result = c.fetchone()
    return result
    
def recommendation(title, model, titlesdb):
    # Get the index of the movie that matches the title
    idx = title[-1]

    # # # Get the pairwsie similarity scores of all movies with that movie
    # # sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = list(enumerate(model[idx]))

    # # # Sort the movies based on the similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # # # Get the scores of the (5) most similar movies
    sim_scores = sim_scores[1:6]

    # Return the top 5 most similar movies
    return [i[0] for i in sim_scores]

def findMovies(connect, idMovies):
    c = connect.cursor()

    str1 = ','.join(str(e) for e in idMovies)
    

    requete = 'SELECT * FROM movie WHERE id IN ('+ str1 +')'
    c.execute(requete)
    result = c.fetchall()
    return result










# The route() function of the Flask class is a decorator,
# which tells the application which URL should call
# the associated function.

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        print("verif")

        movieSelected = request.form['film']
        try:
            filename = 'cosin_sim_model.sav'
            m = pickle.load(open(filename, 'rb'))
        except IOError:
            print("Error: File does not appear to exist.")

        # connexion à la BDD mySql 
        connect = connector()

        # Select all info the movies
        titlesdb = get_movie_titles(connect)

        # Select info of the movie searched 
        myMovie = get_movie_title(connector(), movieSelected)

        # Return the 5 recommended movies'ids
        idMovies = recommendation(myMovie, m, titlesdb)

        # Find the 5 selected movies in DB
        moviesSelected = findMovies(connector(), idMovies)
        for m in moviesSelected:
            print(">>>>>>>>>> ",m, "\n")

        return render_template("index.html", movies=moviesSelected)
        

    return render_template('index.html')

if __name__ == "__main__": 
    app.debug = True
    app.run()
        





