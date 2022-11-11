from conf.dbconfig import pg_config
import psycopg2


class EmailDAO:
    def __init__(self):

        connection_url = "dbname=%s user=%s password=%s host=%s" % (pg_config['dbname'],
                                                                    pg_config['user'],
                                                                    pg_config['passwd'],
                                                                    pg_config['host'])
        self.conn = psycopg2._connect(connection_url)

    def createEmail(self, subject, raw_content, to, id_user):
        try:

            cursor = self.conn.cursor()
            query = "select id_user from \"user\" where email = %s;"
            cursor.execute(query, (to,))
            row = cursor.fetchone()
            if row is None:
                raise ValueError('The email doesn´t exits')
            id_user_to = row[0];
            cursor = self.conn.cursor()
            try:
                query = "insert into \"email\"(subject, raw_content, date_sended,id_user_from)" \
                        " values (%s, %s,current_timestamp, %s) returning id_email;"
                cursor.execute(query, (subject, raw_content, id_user))
            except psycopg2.errors.lookup("23503"):
                raise ValueError('The id user doesn´t exits')

            id_email = cursor.fetchone()[0]

            query = "insert into \"receive\"(id_user, id_email)" \
                    " values (%s, %s);"
            cursor.execute(query, (id_user_to, id_email))


            self.conn.commit()
            return (id_email,id_user_to)

        except psycopg2.errors.lookup("23505"):
            raise ValueError('The email is already taken')

    def retreiveInbox(self, id_user):
        cursor = self.conn.cursor()
        query = "select e.id_email,subject,date_sended,e.id_user_from,u.email," \
                "(case when friends.id_user_tagged is null then 'Not friend' else 'Friends!' end) as friendship" \
                " from receive inner join email e on receive.id_email = e.id_email" \
                " inner join \"user\" u on u.id_user = e.id_user_from" \
                " left join tags_friends friends on receive.id_user = friends.id_user_who_tag and e.id_user_from = friends.id_user_tagged" \
                " where receive.id_user = %s" \
                " and is_deleted is false" \
                " order by receive.id_email desc;"
        cursor.execute(query, (id_user,))
        result = []
        for row in cursor:
            result.append(row)
        return result;








