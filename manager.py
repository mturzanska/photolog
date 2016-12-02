from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

from photolog import db, photolog

migrate = Migrate(photolog, db)
manager = Manager(photolog)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
