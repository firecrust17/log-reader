from flask import Flask
from file_system_blueprint import fs_bp

app = Flask(__name__)

# Needed to display file names for selection on Frontend
app.register_blueprint(fs_bp, url_prefix='/fs')


if __name__ == "__main__":
	app.run()