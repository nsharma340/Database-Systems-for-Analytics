from mysql.connector import MySQLConnection, Error

def make_connection():
    """
    Make a connection to the school database.
    """
    try:
        conn = MySQLConnection(host='localhost',
                               database='school',
                               user='root',
                               password='password')
        
        if conn.is_connected():
            print('Connected to the MySQL database!')
            
            return conn
                
    except Error as e:
        print('Connection failed.')
        print(e)
        
        return None
    
def do_queries(conn):
    """
    Use database connection conn to perform queries.
    """
    cursor = conn.cursor()

    sql = "SELECT * FROM class"

    cursor.execute(sql)
    rows = cursor.fetchall()

    for row in rows:
        print(row)

    print('-'*50)

    sql = ( """
            SELECT student.first, student.last, subject 
            FROM student, teacher, class, takes 
            WHERE teacher.last = 'Flynn' 
            AND teacher.first = 'Mabel' 
            AND teacher_id = teacher.id 
            AND code = class_code 
            AND student_id = student.id 
            ORDER BY subject, student.last
            """
          )

    cursor.execute(sql)
    rows = cursor.fetchall()

    for row in rows:
        print(row)

    cursor.close()
    
if __name__ == '__main__':
    conn = make_connection()
    print()
    
    if conn != None:
        do_queries(conn)
        conn.close()
        
        print()
        print('Database connection closed.')
