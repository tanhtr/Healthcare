import firebase_admin
from firebase_admin import credentials, db

from cortex import Cortex

class LiveMode():
    def __init__(self, app_client_id, app_client_secret, **kwargs):
        self.c = Cortex(app_client_id, app_client_secret, debug_mode = False, **kwargs)

        self.c.bind(create_session_done = self.on_create_session_done)
        self.c.bind(query_profile_done = self.on_query_profile_done)
        self.c.bind(load_unload_profile_done = self.on_load_unload_profile_done)
        self.c.bind(save_profile_done = self.on_save_profile_done)

        self.c.bind(new_com_data = self.on_new_com_data)
        self.c.bind(new_met_data = self.on_new_met_data)

    def start(self, profile_name, headsetId = ''):
        if profile_name == '':
            raise ValueError('Empty profile_name. The profile_name cannot be empty.')

        self.profile_name = profile_name
        self.c.set_wanted_profile(profile_name)

        if headsetId != '':
            self.c.set_wanted_headset(headsetId)

        self.c.open()

    def load_profile(self, profile_name):
        self.c.setup_profile(profile_name, 'load')

    def unload_profile(self, profile_name):
        self.c.setup_profile(profile_name, 'unload')

    def save_profile(self, profile_name):
        self.c.setup_profile(profile_name, 'save')

    # Callbacks functions
    def on_create_session_done(self, *args, **kwargs):
        self.c.query_profile()

    def on_query_profile_done(self, *args, **kwargs):
        self.profile_lists = kwargs.get('data')

        if self.profile_name in self.profile_lists:
            self.c.get_current_profile()
        else:
            self.c.setup_profile(self.profile_name, 'create')

    def on_load_unload_profile_done(self, *args, **kwargs):
        is_loaded = kwargs.get('isLoaded')
        print("on_load_unload_profile_done: " + str(is_loaded))
        
        if is_loaded == True:
            self.save_profile(self.profile_name)
        else:
            print('The profile ' + self.profile_name + ' is unloaded')
            self.profile_name = ''

    def on_save_profile_done (self, *args, **kwargs):
        print('Save profile ' + self.profile_name + " successfully")

        stream = ['com', 'met']
        self.c.subscribe_request(stream)

    def on_new_met_data(self, *args, **kwargs):
        data = kwargs.get('data')

        if data['met'][11] == True:
            state = "focus"
        elif data['met'][7] == True:
            state = "relaxation"
        elif data['met'][5] == True:
            state = "stress"
        
        ref = db.reference('/')
        ref.update({
            'met/state': state
        })
        
    def on_new_com_data(self, *args, **kwargs):
        data = kwargs.get('data')
        action = data['action']

        ref = db.reference('/')
        ref.update({
            'com/action': action
        })

def main():
    Firebase_credentials = credentials.Certificate('Firebase_credentials.json')

    firebase_admin.initialize_app(Firebase_credentials, {
        'databaseURL': "https://raspberrypi-health-default-rtdb.asia-southeast1.firebasedatabase.app/"
    })

    your_app_client_id = 'TT5dWgW0bgYlQgZ6UKWFUbePXsQQ05p4v5ydoWl1'
    your_app_client_secret = 'XPTyv26CgjTcVSBGJJBiVsj3hY1xAvsZK48GkVFgIuZp5WpuuR4S0reujyvLKkKDYDTz4gOSLHNejhXHV4sxnFptPBvdKfyzsNKlUk54p0HMWqMveIPSLBcDjZV4GZfk'
    
    trained_profile_name = 'BCI'

    l = LiveMode(your_app_client_id, your_app_client_secret)
    l.start(trained_profile_name)

if __name__ == '__main__':
    main()
