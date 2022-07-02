from flask import Flask, render_template
from flask import jsonify
app = Flask(__name__,static_folder = 'static')

@app.route("/")
def home():
    return render_template("index.html")
    # return "Hello world!"

if(__name__ == "__main__"):
    app.run()
