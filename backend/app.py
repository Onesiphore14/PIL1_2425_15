from flask import Flask

app = Flask(_name_)

@app.route('/')
def home():
    return "Bienvenue dans le backend !"

if _name_ == '_main_':
    app.run(debug=True)