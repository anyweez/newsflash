package shared

import (
    "labix.org/v2/mgo"
)

type DBSession struct {
    session    *mgo.Session
}

func NewDBSession(connUrl string) (DBSession, error) {
    dbs := DBSession{}
    session, err := mgo.Dial(connUrl)
    
    if err == nil {
        dbs.session = session
        return dbs, nil
    } else {
        return dbs, err
    }
}

/**
 *
 * Note that forked sessions must be closed independently!
 */
func (dbs *DBSession) Fork() *mgo.Session {
    return dbs.session.Copy()
}