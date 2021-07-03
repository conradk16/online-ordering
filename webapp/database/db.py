


#####          #####
##### DATABASE #####
#####          #####

DATABASE = './databases/database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row # return rows as Row objects instead of tuples for easier handling
    return db

@application.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cursor = get_db().execute(query, args)
    return_value = cursor.fetchall()
    cursor.close()
    return (return_value[0] if return_value else None) if one else return_value

def init_db():
    with application.app_context():
        db = get_db()
        with application.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

#####          #####        
##### DATABASE #####
#####          #####
