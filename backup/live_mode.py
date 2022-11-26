from cortex import Cortex
import time

class LiveMode():
    def __init__(self, app_client_id, app_client_secret, **kwargs):
        self.c = Cortex(app_client_id, app_client_secret, debug_mode = False, **kwargs)

        self.c.bind(create_session_done = self.on_create_session_done)
        self.c.bind(query_profile_done = self.on_query_profile_done)
        self.c.bind(load_unload_profile_done = self.on_load_unload_profile_done)
        self.c.bind(save_profile_done = self.on_save_profile_done)

        self.c.bind(new_com_data = self.on_new_com_data)
        self.c.bind(new_met_data = self.on_new_met_data)
        '''
        Facial Expression for thesis
        self.c.bind(new_fe_data = self.on_new_fe_data)
        '''

        self.c.bind(inform_error = self.on_inform_error)

    def start(self, profile_name, headsetId = ''):
        """
        To start live process as below workflow
        1. Check access right -> authorize -> connect headset-> create session
        2. Query profile -> get current profile -> load/create profile -> save profile
        3. Subscribe stream data to show live mode
        """
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
        print('on_create_session_done')
        self.c.query_profile()

    def on_query_profile_done(self, *args, **kwargs):
        print('on_query_profile_done')
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

        stream = ['fac', 'com', 'met']
        self.c.subscribe_request(stream)

    def on_new_com_data(self, *args, **kwargs):
        """
        To handle mental command data emitted from Cortex
        
        Returns
        -------
        data: dictionary
            For example:
            {'action': 'neutral', 'power': 0.0, 'time': 1590736942.8479}
            
        """
        data = kwargs.get('data')
        print('Mental command data: {}'.format(data))
        time.sleep(1)

        '''
        Facial Expression for thesis
        
        def on_new_fe_data(self, *args, **kwargs):
        """
        To handle facical expression data emitted from Cortex
        
        Returns
        -------
        data: dictionary
            For example:
            {'eyeAct': 'blink', 'uAct': 'surprise', 'uPow': 0.0, 'lAct': 'laugh', 'lPow': 0.748513, 'time': 1668497031.389}
            
        """
        data = kwargs.get('data')
        print('Facial expression data: {}'.format(data))
        time.sleep(1)
        '''

    def on_new_met_data(self, *args, **kwargs):
        """
        To handle mental command data emitted from Cortex
        
        Returns
        -------
        data: dictionary
            For example:
            {'action': 'neutral', 'power': 0.0, 'time': 1590736942.8479}
            
        """
        data = kwargs.get('data')
        print('MET data: {}'.format(data))

    def on_inform_error(self, *args, **kwargs):
        error_data = kwargs.get('error_data')
        error_code = error_data['code']
        error_message = error_data['message']

        print(error_data)

        if error_code == ERR_PROFILE_ACCESS_DENIED:
            print('Get error ' + error_message + ". Disconnect headset to fix this issue for next use.")
            self.c.disconnect_headset()

'''
-----------------------------------------------------------
FACIAL EXPRESSIONS
    Eye action: neutral, blink, winkL, winkR
    Upper action: neutral, surprise, frown
    lower action: neutral, smile, clenched teeth, laugh
-----------------------------------------------------------
'''

def main():
    your_app_client_id = 'TT5dWgW0bgYlQgZ6UKWFUbePXsQQ05p4v5ydoWl1'
    your_app_client_secret = 'XPTyv26CgjTcVSBGJJBiVsj3hY1xAvsZK48GkVFgIuZp5WpuuR4S0reujyvLKkKDYDTz4gOSLHNejhXHV4sxnFptPBvdKfyzsNKlUk54p0HMWqMveIPSLBcDjZV4GZfk'
    
    trained_profile_name = 'BCI'

    l = LiveMode(your_app_client_id, your_app_client_secret)
    l.start(trained_profile_name)

if __name__ == '__main__':
    main()