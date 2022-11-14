from flask import jsonify
from dao.user import UserDAO;
from marshmallow import Schema, fields, ValidationError


class UserSchema(Schema):
    first_name = fields.String(required=True)
    last_name = fields.String(required=True)
    password = fields.String(required=True)
    is_premium = fields.Boolean(required=True)
    email = fields.String(required=True)

class FriendSchemaEmail(Schema):
    email = fields.String(required=True)


class UserHandler:

    def build_user_dict(self, row):
        result = {}
        result['id_user'] = row[0]
        result['first_name'] = row[1]
        result['last_name'] = row[2]
        result['is_premium'] = row[3]
        result['email'] = row[4]
        return result

    def insertUser(self,json):
        schema = UserSchema()
        try:
            result = schema.load(json)
        except ValidationError as err:
            return jsonify(err.messages), 400

        first_name = json['first_name']
        last_name = json['last_name']
        password = json['password']
        is_premium = json['is_premium']
        email = json['email']
        dao = UserDAO()
        try:
            id_user = dao.insert(first_name, last_name, password, is_premium,email)
            result = self.build_user_dict((id_user, first_name, last_name, is_premium, email))
            return jsonify(User=result), 201
        except ValueError as err:
            return jsonify(str(err)), 409
    def build_userdata_dict(self, row):
        result = {}
        result['id_user'] = row[0]
        result['first_name'] = row[1]
        result['last_name'] = row[2]
        result['password'] = row[3]
        result['is_premium'] = row[4]
        result['email'] = row[5]
        return result

    #Gets all users in the table
    def getAllUsers(self):
        dao = UserDAO()
        result_tuples = dao.getAllUsers()
        result = []
        for row in result_tuples:
            dict = self.build_userdata_dict(row)
            result.append(dict)
        return jsonify(result)

    #Gets user with id given
    def getUserbyId(self, u_id):
        dao = UserDAO()
        result = dao.getUserbyId(u_id)
        if not result:
            return jsonify("Not Found"), 404
        else:
            dict = self.build_userdata_dict(result)
            return jsonify(dict), 200

    def addFriend(self,id_user, json):
        schema = FriendSchemaEmail()
        try:
            # Validate request body against schema data types
            result = schema.load(json)
        except ValidationError as err:
            # Return a nice message if validation fails
            return jsonify(err.messages), 400

        email = json['email']
        dao = UserDAO()
        try:
            dao.addUserFriendByEmail(id_user,email)
            return jsonify("Friend added"), 201
        except ValueError as err:
            return jsonify(str(err)), 400

    def removeFriend(self, id_user, json):
        schema = FriendSchemaEmail()
        try:
            # Validate request body against schema data types
            result = schema.load(json)
        except ValidationError as err:
            # Return a nice message if validation fails
            return jsonify(err.messages), 400

        email = json['email']
        dao = UserDAO()
        try:
            dao.removeUserFriendByEmail(id_user, email)
            return jsonify("Friend removed"), 204
        except ValueError as err:
            return jsonify(str(err)), 400





