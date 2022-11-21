
from sqlalchemy import Column, Date, exc, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import create_database, database_exists, drop_database


def create_db(engine_url):
    """

    Args:
        engine_url:

    Returns:

    """
    try:
        if not database_exists(engine_url):
            create_database(engine_url)
            print('Database {} was created.'.format(str(engine_url).split('/')[-1:]))
        else:
            print('Database {} already exists.'.format(str(engine_url).split('/')[-1:]))
    except (exc.SQLAlchemyError, Exception) as error:
        print('Database {} was not created.'.format(str(engine_url).split('/')[-1:]), error)

    return


def db_exists(engine_url):
    if database_exists(engine_url):
        print('Database {} exists.'.format(str(engine_url).split('/')[-1:]))
    else:
        print('Database {} does not exist.'.format(str(engine_url).split('/')[-1:]))

    return database_exists(engine_url)


def drop_db(engine_url):
    try:
        if database_exists(engine_url):
            drop_database(engine_url)
            print('Database {} was dropped.'.format(str(engine_url).split('/')[-1:]))
    except (exc.SQLAlchemyError, Exception) as error:
        print('Database {} was not dropped.'.format(str(engine_url).split('/')[-1:]), error)

    return


Base = declarative_base()


class Set(Base):
    __tablename__ = 'set'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    realease_date = Column(Date, nullable=False)


class Card(Base):
    __tablename__ = 'card'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    card_set = Column(ForeignKey(Set.id), nullable=False)
    pitch_value = Column(Integer, nullable=False)
    card_type = Column(String, nullable=False)
    talent = Column(String, nullable=False)
    color = Column(String, nullable=False)



