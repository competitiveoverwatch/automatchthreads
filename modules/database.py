import sqlite3, pickle, time

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('automatchthreads.db')
    
    def __del__(self):
        self.conn.close()

    ### Event Database
    def new_event(self, event):
        # prepare data
        event['status'] = 'upcoming'
        event['timestamp'] = None
        event['update_timestamp'] = time.time()
        data = pickle.dumps(event)
        insert = (event['status'], event['timestamp'], event['duration'], event['update_timestamp'], data)
        # insert into database
        c = self.conn.cursor()
        c.execute('INSERT INTO events (status, timestamp, duration, update_timestamp, data) VALUES (?, ?, ?, ?, ?)', insert)
        self.conn.commit()
        c.close()

    def update_event(self, event):
        data = pickle.dumps(event)
        insert = (event['status'], event['timestamp'], event['duration'], event['update_timestamp'], data, event['id'])
        c = self.conn.cursor()
        c.execute('UPDATE events SET status = ? ,timestamp = ? ,duration = ?, update_timestamp = ? ,data = ? WHERE id = ?', insert)
        self.conn.commit()
        c.close()
    
    def make_event_dict(self, input):
        ret = []
        for event in input:
            new_event = {'id': event[0]} # make sure id is set
            if event[5]:
                new_event.update(pickle.loads(event[5])) # update with pickled data
            ret.append(new_event)
        return ret

    def get_upcoming_events(self):
        return self.get_events("upcoming")
    def get_live_events(self):
        return self.get_events("live")
    def get_done_events(self):
        return self.get_events("done")
    def get_events(self, status=None):
        c = self.conn.cursor()
        if status:
            c.execute('SELECT * FROM events WHERE status="%s"' % status)
        else:
            c.execute('SELECT * FROM events')
        ret = self.make_event_dict(c.fetchall())        
        c.close()
        return ret


    ### Match Database
    def new_match(self, match):
        # prepare data
        match['status'] = 'upcoming'
        match['timestamp'] = None
        match['update_timestamp'] = time.time()
        data = pickle.dumps(match)
        insert = (match['status'], match['timestamp'], match['update_timestamp'], data)
        # insert into database
        c = self.conn.cursor()
        c.execute('INSERT INTO matches (status, timestamp, update_timestamp, data) VALUES (?, ?, ?, ?)', insert)
        self.conn.commit()
        c.close()

    def update_match(self, match):
        data = pickle.dumps(match)
        insert = (match['status'], match['timestamp'], match['update_timestamp'], data, match['id'])
        c = self.conn.cursor()
        c.execute('UPDATE matches SET status = ? ,timestamp = ?, update_timestamp = ? ,data = ? WHERE id = ?', insert)
        self.conn.commit()
        c.close()

    def make_match_dict(self, input):
        ret = []
        for match in input:
            new_match = {'id': match[0]} # make sure id is set
            if match[4]:
                new_match.update(pickle.loads(match[4])) # update with pickled data
            ret.append(new_match)
        return ret

    def get_upcoming_matches(self):
        return self.get_matches("upcoming")
    def get_live_matches(self):
        return self.get_matches("live")
    def get_done_matches(self):
        return self.get_matches("done")
    def get_matches(self, status=None):
        c = self.conn.cursor()
        if status:
            c.execute('SELECT * FROM matches WHERE status="%s"' % status)
        else:
            c.execute('SELECT * FROM matches')
        ret = self.make_match_dict(c.fetchall())        
        c.close()
        return ret