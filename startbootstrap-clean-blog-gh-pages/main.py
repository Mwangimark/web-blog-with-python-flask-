import smtplib

import requests
from flask import Flask, render_template, request

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


@app.route('/contact', methods=['GET', 'POST'])
def contact_me():
    if request.method == "POST":
        data = request.form
        print(data['name'])
        print(data['email'])
        print(data['phone'])
        print(data['message'])

        name = data['name']
        email = data['email']
        phone = data['phone']
        message = data['message']

        send_message(name, email, phone, message)

        return render_template('contact.html', msg=True)
    return render_template('contact.html', msg=False)


def send_message(name, email, phone, message):
    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login("marshamark2020@gmail.com", "czck gvhv juvn uajz")
        connection.sendmail(
            from_addr="marshamark2020@gmail.com",
            to_addrs="marshamark2020@gmail.com",
            msg=f"Subject:New message\n\nName:{name}\nPhone NO:{phone}\nEmail:{email}\nMessage:{message}"
        )


if __name__ == "__main__":
    app.run(debug=True, port=3000)
