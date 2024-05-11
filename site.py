from project import create_app, db
from project.main.fill_db import build

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # db.create_all()
        # build()
        pass
    app.run(debug=True)
