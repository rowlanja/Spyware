from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def main():
    return render_template("Jan-01-23BTCUSDT.html")

@app.route('/stat/') # EDIT
def stat():
    print(" is equal to ")
    return render_template("screen.html")

@app.route('/all/') # EDIT
def all():
    print("all")
    return render_template("all_charts.html")
            
if __name__ == "__main__":
    app.run(debug=True)