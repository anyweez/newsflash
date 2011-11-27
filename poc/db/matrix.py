import db

class MatrixStore(object):
    def __init__(self):
        self.db = db.RecordStore('localhost')
    
    # Used to set (x, y) = value.  The store currently assumes that
    #   the matrix is symmetric, so (x, y) and (y, x) will always
    #   return the same value.  They actually result in the same 
    #   query.
    def set_val(self, x, y, value):
        small = min(x, y)
        large = max(x, y)
        sql = 'SELECT COUNT(val) FROM matrix WHERE x = %s AND y = %s'
        num_rows = self.db.execute( sql, (small, large) )
        
        if int(num_rows[0][0]) > 0:
            sql = 'UPDATE matrix SET val = %s WHERE x = %s AND y = %s'
            self.db.execute( sql, (value, small, large) )
        else:
            sql = 'INSERT INTO matrix (x, y, val) VALUES (%s, %s, %s)'
            self.db.execute( sql, (small, large, value) )
    
    def get_val(self, x, y):
        small = min(x, y)
        large = max(x, y)
        sql = 'SELECT val FROM matrix WHERE x = %s AND y = %s'
        return self.db.execute( sql, (small, large) )[0][0]
    
    # Returns a dictionary mapping rid => similarity values.
    def getrow(self, x):
        sql = 'SELECT x, y, val FROM matrix WHERE x = %s OR y = %s'
        vals = self.db.execute( sql, (x, x) )

        row = {}
        for val in vals:
            if int(val[0]) != int(x):
                row[int(val[0])] = float(val[2])
            else:
                row[int(val[1])] = float(val[2])
            
        return row