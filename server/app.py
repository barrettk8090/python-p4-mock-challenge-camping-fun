#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

##REMEMBER TO INCLUDE THIS IN THE FILE
api = Api(app)


@app.route('/')
def home():
    return ''

class AllCampers(Resource):
    def get(self):
        all_campers = Camper.query.all()
        camper_list = []
        for camper in all_campers:
            camper_list.append(camper.to_dict(rules = ('-signups',)))
        return make_response(camper_list, 200)
    def post(self):
        try:
            data = request.get_json()
            new_camper = Camper(
                name = data.get("name"),
                age = data.get("age"),
            )
            if new_camper:
                db.session.add(new_camper)
                db.session.commit()
                #return the response minus the nested signups. Make sure to have a following comma!
                return make_response(new_camper.to_dict(rules = ('-signups',)), 201)    
        except:
            return make_response({"errors": ["validation errors"]}, 400)

    
class OneCamper(Resource):
    def get(self, id):
        single_camper = Camper.query.filter(Camper.id == id).first()
        if single_camper:
            return make_response(single_camper.to_dict(), 200)
        else:
            return make_response({"error": "Camper not found"}, 404)
    ##CHECK SOLUTION CODE TO UPDATE THE TRY/EXCEPT here
    def patch(self, id):
        single_camper = Camper.query.filter(Camper.id == id).first()
        if single_camper:
            try:
                #using either data.get("something") or data["something"] should be the same and both valid syntax
                data = request.get_json()
                for attr in data:
                    setattr(single_camper, attr, data[attr])
                db.session.add(single_camper)
                db.session.commit()
                return make_response(single_camper.to_dict(rules = ('-signups',)),202)
            except:
                return make_response({ "errors": ["validation errors"] }, 400)
        else:
            return make_response({"error": "Camper not found"}, 404)
        
class AllActivities(Resource):
    def get(self):
        all_activities = Activity.query.all()
        act_list = []
        for activity in all_activities:
            act_list.append(activity.to_dict(rules = ('-signups',)))
        return make_response(act_list, 200)

class OneActivity(Resource):
    def delete(self, id):
        one_activity = Activity.query.filter(Activity.id == id).first()
        if one_activity:
            db.session.delete(one_activity)
            db.session.commit()
            return make_response({}, 204)
        else:
            return make_response({"error": "Activity not found"}, 404)

class CreateSignup(Resource):
    def post(self):
        try:
            data = request.get_json()
            new_signup = Signup(
                camper_id = data["camper_id"],
                activity_id = data["activity_id"],
                time = data["time"]
            )
            if new_signup:
                db.session.add(new_signup)
                db.session.commit()
                return make_response(new_signup.to_dict(), 201)
        except:
            return make_response({ "errors": ["validation errors"] }, 400)
        
    

api.add_resource(AllCampers, '/campers')
api.add_resource(OneCamper, '/campers/<int:id>')
api.add_resource(AllActivities, '/activities')
api.add_resource(OneActivity, '/activities/<int:id>')
api.add_resource(CreateSignup, '/signups')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
