from flask import Flask
from blueprints.file_system_blueprint import fs_bp
from blueprints.search_blueprint import search_bp

app = Flask(__name__)

# Needed to display file names for selection on Frontend
app.register_blueprint(fs_bp, url_prefix='/fs')

# Needed to display file names for selection on Frontend
app.register_blueprint(search_bp, url_prefix='/search')


if __name__ == "__main__":
	app.run()