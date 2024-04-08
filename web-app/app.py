"""
Simple Flask application to serve the front end of the Speech to Text project.
"""

from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index():
    """
    Render the main page of the web application.
    """
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=3000)
