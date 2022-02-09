from flask import Flask, render_template
app = Flask(__name__)

@app.route("/akshat")
def Akshat():
    return "Hello Akshat"

@app.route("/")
def index():
    name = "Akshat"
    return render_template('index.html', name = name)

app.run(debug=True)