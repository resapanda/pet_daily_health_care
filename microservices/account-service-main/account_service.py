import sqlite3
from datetime import datetime, timedelta, timezone
from flask import Flask, jsonify, request
from flask_bcrypt import Bcrypt
from database import init_db, reset_db
import jwt

JWT_SECRET = "SUPER_SECRET_ASDFASDFASDFASDEWQER"
JWT_EXPIRES_IN_MIN = 1000

USERS_DB = "users.db"

def create_app() -> Flask:
    app = Flask(__name__)
    bcrypt = Bcrypt(app)
    init_db()

    # test endpoint
    @app.get("/health")
    def health():
        return jsonify({"ok": True, "service": "health", "time_utc": datetime.now().isoformat()}), 200
    
    # test reset endpoint
    @app.post("/test/reset")
    def test_reset():
        reset_db()
        return jsonify({"ok": True, "message": "Database cleared for testing"}), 200

    # create new account endpoint
    @app.post("/accounts")
    def create_account():
        # parse json request
        data = request.get_json(silent=True) or {}
        username = (data.get("username") or "").strip()
        password = (data.get("password") or "").strip()

        # Validation
        if not username or not password:
            return jsonify({"ok": False, "error": "Username and password are required"}), 400

        # Hash password
        password_hashed =  bcrypt.generate_password_hash(password).decode('utf-8')

        try:
            conn = sqlite3.connect(USERS_DB)
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO Users (user_name, password, created_at)
                VALUES (?, ?, ?)
                """,
                (username, password_hashed, datetime.now().isoformat()),
            )
            conn.commit()
            conn.close()
        
        # catch unique constraint error for username
        except sqlite3.IntegrityError:
            return jsonify({
                "ok": False, "error": {"code": "USER_EXISTS", "message": f"The username '{username}' already exists."}
            }), 400
        except Exception:
            # error response
            return (
                jsonify({"ok": False, "error": {"code": "CREATION_ERROR", "message": "Something went wrong while creating the account."}}),
                500,
            )

        return jsonify(
            {
                "ok": True,
                "username": username,
                "message": "Account created.",
            }
        ), 201
    
    # Returns true if password matches hashed_password
    def check_password(hashed_password, password):
        return bcrypt.check_password_hash(hashed_password, password)


    @app.post("/login") # login
    def login():
        # parse json request
        data = request.get_json(silent=True) or {}
        username = (data.get("username") or "").strip()
        password = (data.get("password") or "").strip()

        if not username or not password:
            return jsonify({
                "ok": False,
                "error": {
                            "code": "INVALID_INPUT",
                            "message": "Username and password are required."
                        }
                }), 400
        
        try:
            # do something
            conn = sqlite3.connect(USERS_DB, timeout = 10)
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * 
                FROM Users 
                WHERE user_name = ?
                """,
                (username,)
            )

            row = cursor.fetchone()
            conn.close()

            if row:
                # if user was found
                user_id = row[0]
                stored_hashed_password = row[2]

                # check the password using bcrypt
                if not check_password(stored_hashed_password, password):
                    return jsonify({
                        "ok": False,
                        "error": {
                            "code": "INVALID_CREDENTIALS",
                            "message": "Invalid credentials."
                        }}), 401
                
                # Password is valid → create JWT
                now = datetime.now(timezone.utc)
                payload = {
                        "sub": username,                 # user name (sub is standard)
                        "uid": user_id,                  # user id (custom)
                        "exp": int((now + timedelta(minutes=JWT_EXPIRES_IN_MIN)).timestamp()), # when it should expire
                        "iat": int(now.timestamp()),     # issued at time ...
                } # JWT attribute names are best if they are short apparently (RFC 7519)

                token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")

                # return the jwt
                return jsonify({
                    "ok": True, 
                    "access_token": token, 
                    "token_type": "Bearer"}), 200
            else:
                # if user wasnt found
                return ( jsonify({
                                    "ok": False, 
                                    "error": 
                                        {
                                            "code": "INVALID_CREDENTIALS", 
                                            "message": "Invalid credentials."
                                        }}), 404)
            
        except Exception:
            # if some unforeseen thing goes wrong
            return (
                        jsonify({
                                    "ok": False, 
                                    "error": 
                                        {  
                                            "code": "LOGIN_ERROR", 
                                            "message": "Something went wrong while logging in."
                                        }}), 500)


    @app.put("/accounts/<username>/change_password")
    def change_pw(username):
        # get JWT token by accessing the HTTP authorization header
        auth_header = request.headers.get("Authorization")
        # return error if there is no header or the header is not in JWT format
        if not auth_header or auth_header[:7] != "Bearer ":
            return jsonify(
                {
                    "ok": False,
                    "message": "Unauthorized. Please log in."
                }
            ), 401

        token = auth_header[7:].strip()

        # check if the user is properly logged into their account using JWT
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            if payload["sub"] != username:
                return jsonify(
                    {
                        "ok": False,
                        "message": "Username does not match the current account. You are not allowed to modify this account's password."
                    }
                ), 403
        # return error if the JWT token is expired
        except jwt.ExpiredSignatureError:
            return jsonify(
                {
                    "ok": False,
                    "message": "The token is expired. Please log in again."
                }
            ), 401
        # return error if the JWT token is invalid
        except jwt.InvalidTokenError:
            return jsonify(
                {
                    "ok": False,
                    "message": "The token is invalid."
                }
            ), 401
        
        
        # parse json request
        data = request.get_json(silent=True) or {}
        old_password = (data.get("old_password") or "").strip()
        new_password = (data.get("new_password") or "").strip()

        # return error if the old password or the new password value is missing
        if not old_password or not new_password:
            return jsonify(
                {
                    "ok": False,
                    "error": "Old and new passwords are required."
                }
            ), 400
        
        conn = None
        try:
            conn = sqlite3.connect(USERS_DB, timeout = 10)
            cursor = conn.cursor()
            # check if the id exists and its password matches the user input
            cursor.execute(
                """
                SELECT password 
                FROM Users 
                WHERE user_name = ?
                """,
                (username,),
            )
            # check if entry exists, if not means that user not found in db
            user = cursor.fetchone()
            if not user:
                conn.close()
                return jsonify({
                    "ok": False,
                    "error": {"code": "USER_NOT_FOUND", "message": "User not found."}
                }), 404

            hashed_password = user[0]

            # check validity of user input for old password
            is_valid_old_password = check_password(hashed_password, old_password)
            if not is_valid_old_password:
                conn.close()
                return jsonify({
                    "ok": False,
                    "error": {"code": "INVALID_CREDENTIALS", "message": "Invalid credentials."}
                }), 401

            # if credentials are valid, update new password with hashed password
            new_password_hashed = bcrypt.generate_password_hash(new_password).decode("utf-8")
            print("old password is valid, changing password...")
            cursor.execute(
                """
                UPDATE 
                Users SET password = ? 
                WHERE user_name = ?
                """,
                (new_password_hashed, username),
            )

            conn.commit()
            conn.close()
        except Exception:
            # error response
            return(
                jsonify({"ok": False, "error": {"code": "UPDATE_ERROR", "message": "Something went wrong while updating the password."}}),
                500,
            )
        
        
        return jsonify(
            {
                "ok": True,
                "username": username,
                "message": "Password updated.",
            }
        ), 200
    
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=6900, debug=True)
