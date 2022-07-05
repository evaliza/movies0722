from cgitb import html
import mysql.connector  # pip install mysql-connector-python
import pickle
from numpy import imag
import requests

from flask import Flask, render_template, request, redirect, url_for
from bs4 import BeautifulSoup


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
        

        film = []
        print(type(movieSelected))
        for detail in moviesSelected:
            print("detail[17] :", detail[17])
            image = findPicture(detail[17])
            print(image)
            details = [
                detail[1],
                detail[6],
                detail[10],
                detail[11],
                detail[17],
                image
            ]
            film.append(details)

        return render_template("index.html", movies=film)
        

    return render_template('index.html')


def findPicture(url):
    headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '3600',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }

    req = requests.get(url, headers)
    soup = BeautifulSoup(req.content, 'html.parser')
    description = soup.find("a", {"class":"ipc-lockup-overlay ipc-focusable"}).get_text()
    image = soup.find_all('div',
                            {'class':"ipc-media ipc-media--poster-27x40 ipc-image-media-ratio--poster-27x40 ipc-media--baseAlt ipc-media--poster-l ipc-poster__poster-image ipc-media__img"})[-1].extract()
    child = 'src'

    for child in image:
        child

    return child['src']



if __name__ == "__main__": 
    app.debug = True
    app.run()
        





