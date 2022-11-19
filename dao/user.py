from conf.dbconfig import pg_config
import psycopg2


class UserDAO:
    def __init__(self):

        connection_url = "dbname=%s user=%s password=%s host=%s" % (pg_config['dbname'],
                                                            pg_config['user'],
                                                            pg_config['passwd'],
                                                            pg_config['host'])
        self.conn = psycopg2._connect(connection_url)

    #get all user in the table
    def getAllUsers(self):
        query = 'select * from "user" WHERE is_deleted = FALSE ORDER BY id_user ASC;'
        cursor = self.conn.cursor()
        cursor.execute(query)
        result = []
        for row in cursor:
            print(row)
            result.append(row)
        cursor.close()
        return result

    #get user by id given
    def getUserbyId(self, id_user):
        query = 'select * from "user" where id_user = %s AND is_deleted = FALSE;'
        cursor = self.conn.cursor()
        cursor.execute(query, (id_user,))
        return cursor.fetchone()

    def insert(self, first_name, last_name, password, is_premium,email):
        try:
            cursor = self.conn.cursor()
            query = "insert into \"user\"(first_name, last_name, password, is_premium,email) values (%s, %s, %s, %s, %s) returning id_user;"
            cursor.execute(query, (first_name, last_name, password, is_premium,email))
            id_user = cursor.fetchone()[0]
            self.conn.commit()
            return id_user

        except psycopg2.errors.lookup("23505"):
            raise ValueError('The email is already taken')

    def updateUser (self, id_user, first_name, last_name, password, is_premium, email):
        cursor = self.conn.cursor()
        try:
            query = "update \"user\" set first_name=%s, last_name=%s, password=%s, is_premium=%s, email=%s where id_user=%s"
            cursor.execute(query, (first_name, last_name, password, is_premium, email, id_user))
            self.conn.commit()
        except psycopg2.errors.lookup("23505"):
            raise ValueError('The email is already taken')

        return id_user

    def deleteUser (self, id_user):
        cursor  = self.conn.cursor()
        query = "update \"user\" set is_deleted = True where id_user=%s"
        cursor.execute(query, (id_user,))
        self.conn.commit()
        return id_user

    def addUserFriendByEmail(self,id_user,email):
       cursor = self.conn.cursor()
       query = "select id_user from \"user\" where email = %s;"
       cursor.execute(query, (email,))
       row = cursor.fetchone()
       if row is None:
           raise ValueError('The email doesn´t exits')
       id_user_friend = row[0]
       try:
           query = "insert into tags_friends(id_user_tagged,id_user_who_tag) values (%s,%s)"
           cursor.execute(query, (id_user_friend,id_user))
           self.conn.commit()
       except psycopg2.errors.lookup("23503"):
           raise ValueError('The id user doesn´t exits')
       except psycopg2.errors.lookup("23505"):
           raise ValueError('You are already friends')

    def removeUserFriendByEmail(self,id_user,email):
       cursor = self.conn.cursor()
       query = "select id_user from \"user\" where email = %s;"
       cursor.execute(query, (email,))
       row = cursor.fetchone()
       if row is None:
           raise ValueError('The email doesn´t exits')
       id_user_friend = row[0]
       query = "delete from tags_friends where id_user_tagged = %s and id_user_who_tag = %s;"
       cursor.execute(query, (id_user_friend,id_user))
       self.conn.commit()

    def viewTop10UsersWithMoreEmailsOnInbox(self):
        query = "SELECT U.id_user, U.first_name, U.last_name, count(R.id_email) AS Inbox_Emails" \
                " FROM \"user\" AS U " \
                " INNER JOIN \"receive\" R on R.id_user = U.id_user" \
                " INNER JOIN \"email\" E on E.id_email = R.id_email" \
                " WHERE U.is_deleted = FALSE AND E.is_deleted_outbox = FALSE" \
                " GROUP BY U.id_user,U.first_name, U.last_name" \
                " order by count(R.id_email) Desc"\
                " LIMIT 10"
        cursor = self.conn.cursor()
        cursor.execute(query)
        result = []
        for row in cursor:
            print(row)
            result.append(row)
        cursor.close()
        return result

    def viewTop10UsersWithMoreEmailsOnOutbox(self):
        query = "SELECT U.id_user, U.first_name, U.last_name, count(E.id_user_from) AS Outbox_Emails" \
                " FROM \"user\" AS U " \
                " INNER JOIN \"email\" E on E.id_user_from = U.id_user" \
                " WHERE U.is_deleted = FALSE AND E.is_deleted_outbox = FALSE" \
                " GROUP BY U.id_user,U.first_name, U.last_name" \
                " order by count(E.id_user_from) Desc"\
                " LIMIT 10"
        cursor = self.conn.cursor()
        cursor.execute(query)
        result = []
        for row in cursor:
            print(row)
            result.append(row)
        cursor.close()
        return result

    def viewEmailMostRecepientsOfUser(self, id_user):
        query = "select R.id_email, count(R.id_email) as recipients " \
                "from receive R " \
                "inner join email E on R.id_email = E.id_email " \
                "where E.id_user_from = %s AND E.is_deleted_outbox = FALSE " \
                "group by R.id_email " \
                "having count(R.id_email) = "\
                "( "\
                    "select max(cR.recipients) from "\
                        "(select  count(R.id_email) as recipients " \
                        "from receive R " \
                        "inner join email E on R.id_email = E.id_email " \
                        "where E.id_user_from = %s AND E.is_deleted_outbox = FALSE " \
                        "group by R.id_email ) as cR" \
                ")"\

        cursor = self.conn.cursor()
        cursor.execute(query, (id_user, id_user))
        result = []
        for row in cursor:
            result.append(row)
        cursor.close()
        return result

    def viewEmailMostRepliesOfUser(self, id_user):
        query = "with replyCount " \
                "as (" \
                "select R.id_email_reply_to as id_email, count(R.id_email_reply_to) as replies " \
                "from replies R inner join email E on R.id_email = E.id_email WHERE E.is_deleted_outbox = FALSE " \
                "group by R.id_email_reply_to " \
                "order by count(R.id_email_reply_to) desc " \
                ") " \
                "select RC.id_email, RC.replies " \
                "from replyCount as RC inner join email E on RC.id_email = E.id_email " \
                "where id_user_from = %s AND E.is_deleted_outbox = FALSE " \
                "AND RC.replies =  "\
                "( "\
                    "select max(cR.replies) from " \
                        "(select RC.id_email, RC.replies " \
                        "from replyCount as RC inner join email E on RC.id_email = E.id_email " \
                        "where id_user_from = %s AND E.is_deleted_outbox = FALSE ) as cR" \
                ") "

        cursor = self.conn.cursor()
        cursor.execute(query, (id_user, id_user))
        result = []
        for row in cursor:
            result.append(row)
        cursor.close()
        return result

    def viewTop5RecipientsOfUser(self, id_user):
        query = "select receive.id_user, count(receive.id_user) as sent " \
                "from receive " \
                "inner join email E on receive.id_email = E.id_email " \
                "where E.id_user_from = %s AND E.is_deleted_outbox = FALSE " \
                "group by receive.id_user " \
                "order by count(receive.id_user) desc " \
                "limit 5 "

        cursor = self.conn.cursor()
        cursor.execute(query, (id_user,))
        result = []
        for row in cursor:
            result.append(row)
        cursor.close()
        return result

    def viewTop5SendersOfUser(self, id_user):
        query = "select id_user_from, count(id_user_from) as recieved " \
                "from receive R " \
                "inner join email E on R.id_email = E.id_email " \
                "where R.id_user = %s AND E.is_deleted_outbox = FALSE " \
                "group by id_user_from " \
                "order by count(E.id_user_from) desc " \
                "limit 5 "

        cursor = self.conn.cursor()
        cursor.execute(query, (id_user,))
        result = []
        for row in cursor:
            result.append(row)
        cursor.close()
        return result



