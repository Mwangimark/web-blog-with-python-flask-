import smtplib


class Email:
    def __init__(self):
        pass

    def send_message(name, email, phone, message):
        with smtplib.SMTP("host") as connection:
            connection.starttls()
            connection.login("marshamark2020@gmail.com", "czck gvhv juvn uajz ")
            connection.sendmail(
                from_addr=email,
                to_addrs="marshamark2020@gmail.com",
                msg=f"Name:{name}\nPhone NO:{phone}\nEmail:{email}\nMessage:{message}"
            )

