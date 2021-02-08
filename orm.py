from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

class Magiclink(Base):
    __tablename__ = 'magiclink'
    
    id = Column(Integer, primary_key=True)
    create_time = Column(DateTime)
    email = Column(String)
    token = Column(String)
    route = Column(String)
    counter = Column(Integer)
    revoked = Column(Boolean)

    def __repr__(self):
        return ('<Magiclink('
            'id={}, create_time="{}", email="{}", token="{}", counter={}, revoked={})>').format(
                self.id, self.create_time, self.email, 
                self.token, self.counter, self.revoked)


ENGINE = create_engine('sqlite:///magiclink.db', 
    echo=False, 
    connect_args={'check_same_thread': False})
Base.metadata.create_all(ENGINE)


class MagiclinkDB():

    def __init__(self):
        self.session = sessionmaker(bind=ENGINE)()

    def add_magiclink(self, email, token, route):
        record = Magiclink(
            create_time=datetime.now(),
            email=email,
            token=token,
            route=route,
            counter=0,
            revoked=False)
        self.session.add(record)
        self.session.commit()
        return record

    def find_by_token(self, token):
        return self.session.query(Magiclink).\
            filter(Magiclink.token == token).\
            first()

    def verify_token(self, token):
        record = self.find_by_token(token)

        if (record is not None) and (not record.revoked):
            return True
        return False

    def verify_token_and_route(self, token, route):
        record = self.find_by_token(token)

        if (record is not None) and (not record.revoked) and token.route == route:
            return True
        return False

    def increment_counter(self, token):
        record = self.find_by_token(token)
        record.counter += 1
        self.session.commit()

    def revoke(self, token):
        record = self.find_by_token(token)
        record.revoked = True
        session.commit()