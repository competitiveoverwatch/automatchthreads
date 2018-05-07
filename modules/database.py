import sqlite3, pickle, time

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('automatchthreads.db')
    
    ### Event Database
    def new_event(self, duration, data):
        # prepare data
        if data:
            data = pickle.dumps(data)
        insert = ('upcoming', None, duration, time.time(), data)
        # insert into database
        c = self.conn.cursor()
        c.execute('INSERT INTO events (status, timestamp, duration, update_timestamp, data) VALUES (?, ?, ?, ?, ?)', insert)
        self.conn.commit()
        c.close()
    
    def update_event(self, event_data):
        data = pickle.dumps(event_data['data'])
        insert = (event_data['status'], event_data['timestamp'], event_data['duration'], event_data['update_timestamp'], data, event_data['id'])
        c = self.conn.cursor()
        c.execute('UPDATE events SET status = ? ,timestamp = ? ,duration = ?, update_timestamp = ? ,data = ? WHERE id = ?', insert)
        self.conn.commit()
        c.close()
    
    def make_event_dict(self, input):
        ret = []
        for event in input:
            new_event = {'id': event[0], 'status': event[1], 'timestamp': event[2], 'duration': event[3], 'update_timestamp': event[4]}
            if event[5]:
                new_event['data'] = pickle.loads(event[5])
            else:
                new_event['data'] = None
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
    def new_match(self, data):
        # prepare data
        if data:
            data = pickle.dumps(data)
        insert = ('upcoming', None, time.time(), data)
        # insert into database
        c = self.conn.cursor()
        c.execute('INSERT INTO matches (status, timestamp, update_timestamp, data) VALUES (?, ?, ?, ?)', insert)
        self.conn.commit()
        c.close()

    def update_match(self, match_data):
        data = pickle.dumps(match_data['data'])
        insert = (match_data['status'], match_data['timestamp'], match_data['update_timestamp'], data, match_data['id'])
        c = self.conn.cursor()
        c.execute('UPDATE matches SET status = ? ,timestamp = ?, update_timestamp = ? ,data = ? WHERE id = ?', insert)
        self.conn.commit()
        c.close()

    def make_match_dict(self, input):
        ret = []
        for match in input:
            new_match = {'id': match[0], 'status': match[1], 'timestamp': match[2], 'update_timestamp': match[3]}
            if match[4]:
                new_match['data'] = pickle.loads(match[4])
            else:
                new_match['data'] = None
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