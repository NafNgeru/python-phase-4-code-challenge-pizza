#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


class Restaurants(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return [restaurant.to_dict(only=('id', 'name', 'address')) for restaurant in restaurants]
    
class RestaurantByID(Resource):
    def get(self, id):
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            return {"error": "Restaurant not found"}, 404
        return restaurant.to_dict(rules=("id", "name", "address", "restaurant_pizzas.pizza")), 200

    def delete(self, id):
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            return {"error": "Restaurant not found"}, 404
        db.session.delete(restaurant)
        db.session.commit()
        return "", 204

class Pizzas(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return [p.to_dict(only=("id", "name", "ingredients")) for p in pizzas], 200

class RestaurantPizzas(Resource):
    def post(self):
        data = request.get_json()
        try:
            price = data["price"]
            pizza_id = data["pizza_id"]
            restaurant_id = data["restaurant_id"]

            restaurant = Restaurant.query.get(restaurant_id)
            pizza = Pizza.query.get(pizza_id)

            if not restaurant or not pizza:
                return {"error": "Restaurant or Pizza not found"}, 404

            if not (1 <= price <= 30):
                raise ValueError("Price must be between 1 and 30")

            new_rp = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
            db.session.add(new_rp)
            db.session.commit()

            return new_rp.to_dict(rules=("id", "price", "pizza", "restaurant", "pizza_id", "restaurant_id")), 201

        except Exception:
            return {"errors": ["validation errors"]}, 400

api.add_resource(Restaurants, "/restaurants")
api.add_resource(RestaurantByID, "/restaurants/<int:id>")
api.add_resource(Pizzas, "/pizzas")
api.add_resource(RestaurantPizzas, "/restaurant_pizzas")

if __name__ == "__main__":
    app.run(port=5555, debug=True)