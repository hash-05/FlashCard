from flask import Flask
from application import config
from application.config import LocalDevelopmentConfig
from application.database import db
from flask_restful import Resource, Api

app = None
api = None


def create_app():
    app = Flask(__name__, template_folder="templates")
    app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    api = Api(app)
    app.app_context().push()
    return app, api


app, api = create_app()  # Create APP

# Controllers
from application.controllers import *

# API
from application.api import *

# Restful controllers
api.add_resource(UserAPI, "/api/user", "/api/user/<int:user_id>")
api.add_resource(ScoreAPI, "/api/deck/<int:d_id>/score")
api.add_resource(ReviewAPI, "/api/deck/<int:d_id>/review")
api.add_resource(RatingAPI, "/api/card/<int:c_id>/rating")
api.add_resource(CardAPI, "/api/user/<int:user_id>/deck/<int:d_id>/card/<int:c_id>",
                 "/api/user/<int:user_id>/deck/<int:d_id>/card")
api.add_resource(DeckAPI, "/api/user/<int:user_id>/deck/<int:d_id>", "/api/user/<int:user_id>/deck")

if __name__ == '__main__':
    app.run(debug=True)
