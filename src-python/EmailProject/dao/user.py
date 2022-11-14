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
        query = 'select * from "user" ORDER BY id_user ASC;'
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
        query = 'select* from "user" where id_user = %s;'
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
                " WHERE E.is_deleted_outbox = FALSE" \
                " GROUP BY U.id_user" \
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
                " WHERE E.is_deleted_outbox = FALSE" \
                " GROUP BY U.id_user" \
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




