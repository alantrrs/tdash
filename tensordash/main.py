
from warrant import Cognito
import configparser
import os

class Tensordash():
    def __init__(self):
        self.poolId = 'us-east-1_fc6CHd37U'
        self.clientId = '62hrpekqtvh8v5u3u1bipos574'
        # Load user config
        self.config = configparser.ConfigParser()
        self.configpath = '.tensordash.cfg'
        if os.path.exists(self.configpath):
            self.config.read(self.configpath)

    def push(self, project, filepaths, user=None, password=None):
        self._authenticate(user, password)
        # TODO: Get signed URLs for all files
        print('PUSH:', project, filepaths)
        # TODO: Upload files from directory to S3 directly
        # TODO: Update DB with outputs
        print("pushing..")

    def _authenticate(self, user, password):
        try:
            u = Cognito(self.poolId, self.clientId, username=user)
            u.authenticate(password=password)
        except:
            print('Not authorized. Incorrect username or password.')
            return (None, None, None)
        return (u.id_token, u.access_token, u.refresh_token)

    def login(self, user, password):
        id_token, access_token, refresh_token = self._authenticate(user, password)
        if id_token is None:
            exit(1)
        # save the config
        self.config['AUTH'] = {'id_token': id_token,
                               'access_token': access_token,
                               'refresh_token': refresh_token}
        self.config.write(open(self.configpath, 'w'))
        print('You\'re logged in. Credentials stored.')

    def logout(self):
        if not ('AUTH' in self.config.sections()):
            print('You\'re not logged in. All good.')
            exit(0)
        # Logout
        auth = self.config['AUTH']
        u = Cognito(self.poolId, self.clientId, id_token=auth['id_token'],
                    access_token=auth['access_token'], refresh_token=auth['refresh_token'])
        try:
            u.logout()
        except:
            pass
        # Remove credentials
        self.config.remove_section('AUTH')
        self.config.write(open(self.configpath, 'w'))
        print('Credentials successfully removed.')

if __name__ == '__main__':
    # Get arguments
    import argparse
    parser = argparse.ArgumentParser(prog='tensordash', description=('Tensordash client.'))
    subparsers = parser.add_subparsers(dest='action')
    # parser for 'push' command
    push_parser = subparsers.add_parser('push', help='Upload files to the dashboard.')
    push_parser.add_argument('--project', type=str, help='project')
    push_parser.add_argument('filepaths', nargs='*', type=str, help='files & directories to upload')
    push_parser.add_argument('--user', type=str, help='username')
    push_parser.add_argument('--password', type=str, help='password')
    # parser for 'login' command
    login_parser = subparsers.add_parser('login', help='Authenticate and store your credentials.')
    login_parser.add_argument('--user', type=str, help='username')
    login_parser.add_argument('--password', type=str, help='password')
    # parser for 'logout' command
    logout_parser = subparsers.add_parser('logout', help='Remove your credantials from local storage.')
    # parse
    args = parser.parse_args()
    action = args.action

    # execute commands
    tensordash = Tensordash()
    if action == 'login':
        tensordash.login(args.user, args.password)
    elif action == 'logout':
        tensordash.logout()
    elif action == 'push':
        tensordash.push(args.project, args.filepaths, user=args.user, password=args.password)
