from flask import jsonify
from dao.email import EmailDAO;
from marshmallow import Schema, fields, ValidationError


class EmailSchema(Schema):
    subject = fields.String(required=True)
    raw_content = fields.String(required=True)
    to = fields.String(required=True)



class EmailHandler:

    def build_email_dict(self, row):
        result = {}
        result['id_email'] = row[0]
        result['subject'] = row[1]
        result['raw_content'] = row[2]
        result['id_used_sended'] = row[3]
        return result

    def build_inbox_dict(self, row):
        result = {}
        result['id_email'] = row[0]
        result['subject'] = row[1]
        result['date_sended'] = row[2]
        result['id_user_from'] = row[3]
        result['email'] = row[4]
        result['friendship'] = row[5]
        return result

    def createEmail(self,json,id_user):
        schema = EmailSchema()
        try:
            result = schema.load(json)
        except ValidationError as err:
            return jsonify(err.messages), 400

        subject = json['subject']
        raw_content = json['raw_content']
        to = json['to']
        dao = EmailDAO()
        try:
            (id_email,id_user_to) = dao.createEmail(subject, raw_content, to, id_user)
            result = self.build_email_dict((id_email, subject, raw_content, id_user_to))
            return jsonify(Email=result), 201
        except ValueError as err:
            return jsonify(str(err)), 409

    def retreiveInbox(self, id_user):
        dao = EmailDAO()
        result_dao = dao.retreiveInbox(id_user)
        result_list = []
        for row in result_dao:
            result = self.build_inbox_dict(row)
            result_list.append(result)
        return jsonify(Inbox=result_list)









