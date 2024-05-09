from config import app, db, request, make_response, api, Resource, jsonify, jwt, create_access_token, jwt_required, current_user, get_jwt, set_access_cookies
from models import User
import datetime
from datetime import timedelta

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(username=identity).one_or_none()

@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        return response

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    jti = jwt_payload["jti"]
    token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()
    return token is not None

class Home (Resource):
    @jwt_required()
    def get(self):
        print(current_user.username, current_user.email, current_user._password_hash, current_user.id)
        response = (
            {
                "Message": "Welcome to my Home Page"
            }
        )
        return make_response(
            response,
            200
        )
api.add_resource(Home, "/")

class AddUser(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        role = data.get('role')
        password = data.get('password')

        if not username or not email or not role or not password:
            return jsonify({"error": "Username, email, role and password are required."}), 400

        new_user = User(username=username, email=email, role=role)
        new_user.password_hash = password
        db.session.add(new_user)
        db.session.commit()
        
        return make_response({"message": "The user has been created successfully"}, 201)

api.add_resource(AddUser, "/adduser")

class LoginUser(Resource):
    def post(self):
        data = request.get_json()

        new_user = User.query.filter_by(email=data['email']).first()
        if not new_user:
            return jsonify({"error": "email is incorrect."}), 400

        if new_user.validates(data['password']):
            given_token = create_access_token(identity=new_user.username)
            return make_response(
                jsonify(
                    {"message": "The user has been logged in successfully", "token": given_token}
                    ),
                    200
            )
        else:
            return make_response(
                jsonify(
                    {"error": "You have entered the Incorrect password"}
                ),
                400
            )

api.add_resource(LoginUser, "/login")

class LogoutUser(Resource):
    @jwt_required
    def delete(self):
        jti = get_jwt()["jti"]
        now = datetime.now(timezone.utc)
        token = TokenBlocklist(jti=jti, created_at=now)
        db.session.add(token)
        db.session.commit()
        return make_response(
            jsonify(
                {"message": "Successfully logged out"}
            ),
            200
        )
api.add_resource(LogoutUser, "/logout")


if __name__ == '__main__':
    app.run(port=5555, debug=True)