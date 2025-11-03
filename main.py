from flask import Flask, render_template, session
from controllers.auth_controller import auth_bp
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.register_blueprint(auth_bp)

@app.route("/")
def index():
    if "user_id" not in session:
        from flask import redirect, url_for
        return redirect(url_for("auth.login"))
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
