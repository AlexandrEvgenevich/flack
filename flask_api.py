from flask import Flask, jsonify, request
from sqlalchemy import create_engine, Column, String, Integer, DateTime, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask.views import MethodView

app = Flask('application')
DSN = 'postgresql://postgres:postgres@localhost:5432/rat_data_base'

engine = create_engine(DSN)
Base = declarative_base()
Session = sessionmaker(bind=engine)


class Notifications(Base):
    __tablename__ = 'Notes'

    noti_id = Column(Integer, primary_key=True)
    header = Column(String)
    description = Column(String)
    creation_date = Column(DateTime, server_default=func.now())
    owner = Column(String, nullable=False)


Base.metadata.create_all(engine)


class View(MethodView):
    def get(self, noti_id):
        with Session() as session:
            resp = session.query(Notifications).get(noti_id)
            if resp is None:
                return jsonify({'error': '404'})
            return jsonify({
                'id': resp.noti_id,
                'header': resp.header,
                'description': resp.description,
                'creation_time': resp.creation_date.isoformat(),
                'owner': resp.owner
            })

    def post(self):
        data = request.json
        with Session() as session:
            new_note = Notifications(**data)
            session.add(new_note)
            session.commit()
            return jsonify({'status': 'ok', 'header': new_note.header})

    def patch(self, noti_id):
        data = request.json
        with Session() as session:
            resp = session.query(Notifications).get(noti_id)
            for x, y in data.items():
                setattr(resp, x, y)
            session.commit()
            return jsonify({'status': 'ok'})

    def delete(self, noti_id):
        with Session() as session:
            resp = session.query(Notifications).get(noti_id)
            session.delete(resp)
            session.commit()
            return jsonify({'status': 'ok'})


def main_page():
    return 'rat'


app.add_url_rule('/', view_func=main_page, methods=['GET'])
app.add_url_rule('/notifications', view_func=View.as_view('notes_post'), methods=['POST'])
app.add_url_rule('/notifications/<int:noti_id>',
                 view_func=View.as_view('notes_gpd'),
                 methods=['GET', 'PATCH', 'DELETE'])


app.run()
