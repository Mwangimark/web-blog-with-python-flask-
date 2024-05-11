import requests
from flask import Flask, render_template
from bs4 import BeautifulSoup


app = Flask(__name__)


def title_n():
    url = "https://api.npoint.io/db964a16330d99e627cc"
    response = requests.get(url).json()
    return response


@app.route('/')
def start():
    title_name = title_n()
    return render_template("index.html", responses=title_name)


@app.route('/about')
def about_me():
    return render_template('about.html')


@app.route('/contact')
def contact_me():
    return render_template('contact.html')


if __name__ == "__main__":
    app.run(debug=True)
