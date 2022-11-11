from conf.dbconfig import pg_config
import psycopg2


class UserDAO:
    def __init__(self):

        connection_url = "dbname=%s user=%s password=%s host=%s" % (pg_config['dbname'],
                                                            pg_config['user'],
                                                            pg_config['passwd'],
                                                            pg_config['host'])
        self.conn = psycopg2._connect(connection_url)

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




