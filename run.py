from app import app
from manage import migrate_up

if __name__ == '__main__':
    migrate_up()
    app.run(host='0.0.0.0', debug=True)
