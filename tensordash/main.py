
from warrant import Cognito
from six.moves import configparser
from six.moves import input
import os
from gql import Client
from gql.transport.requests import RequestsHTTPTransport
from tensordash.gqlOperations import createExperiment, requestUpload
import requests
import getpass

class Tensordash():
    def __init__(self):
        # Load user config
        self.aws_region = 'us-east-1'
        self.config = configparser.ConfigParser()
        self.configpath = os.path.expanduser('~/.tensordash.cfg')
        if os.path.exists(self.configpath):
            self.loadConfigFromFile()
            if 'AUTH' in self.config.sections():
                self._refresh_auth()
        else:
            print('Configuration not found, fetching from server.')
            self.reconfigure()

    def reconfigure(self):
        # Fetch config
        try:
            configEndpoint = os.getenv('TENSORDASH_API', 'https://api.tensordash.ai/config/config')
            r = requests.get(configEndpoint)
            config = r.json()
            # Reset & save config
            self.config.remove_section('AUTH')
            self.config.remove_section('SERVER')
            self.config.add_section('SERVER')
            for key in config:
                self.config.set('SERVER', key, config[key])
            with open(self.configpath, 'w') as f:
                self.config.write(f)
            print('Configuration saved to ' + self.configpath)
        except Exception as e:
            print('Error: ' + str(e))
            print('Failed to save the configuration.')
            exit(1)

    def loadConfigFromFile(self):
        self.config.read(self.configpath)
        if 'SERVER' in self.config.sections():
            self.clientId = self.config.get('SERVER', 'pyclientid')
            self.userPoolId = self.config.get('SERVER', 'userpoolid')
            self.graphqlEndpoint = self.config.get('SERVER', 'graphqlendpoint')
        if 'AUTH' in self.config.sections():
            self.auth = dict(self.config.items('AUTH'))

    def saveConfigToFile(self):
        self.config.remove_section('AUTH')
        self.config.add_section('AUTH')
        for key in ['id_token', 'access_token', 'refresh_token']:
            self.config.set('AUTH', key, self.auth[key])
        with open(self.configpath, 'w') as f:
            self.config.write(f)

    def createExperiment(self, ownerId, projectName, description=None):
        params = {'input': {
            'ownerId': ownerId,
            'projectName': projectName,
            'description': description
        }}
        try:
            res = self.client.execute(createExperiment, variable_values=params)
            return res['createExperiment']['id']
        except Exception as e:
            # TODO: Parse error correctly
            print(str(e))
            print("Failed to create new experiment.")
            exit(1)


    def push(self, project, filepaths, user=None, password=None, description=None):
        if user is not None:
            self._authenticate(user, password)
        if not hasattr(self, 'auth'):
            print('You need to be authenticated to push data. Please login first.')
            exit(1)
        # Create new experiment
        s = project.split('/')
        ownerId = s[0]
        projectName = s[1]
        experimentId = s[2] if len(s) == 3 else self.createExperiment(ownerId, projectName, description=description)
        # Get signed URLs for all files
        assets = map(lambda asset: {'localUri': os.path.abspath(asset)}, filepaths)
        params = {'input': {
            'ownerId': ownerId,
            'projectName': projectName,
            'experimentId': experimentId,
            'assets': assets
        }}
        try:
            res = self.client.execute(requestUpload, variable_values=params)
        except Exception as e:
            print(str(e))
            print('Failed to push to experiment')
            return
        # Upload files to S3 directly
        for asset in res['requestUpload']:
            print('Uploading {}'.format(asset['localUri']))
            requests.put(asset['putUrl'], data=open(asset['localUri'], 'rb'), headers = {
                'Content-Type': asset['mimeType'],
                'x-amz-acl': asset['acl']
            })
        print('Uploaded files to experiment id: {}'.format(experimentId))
        print('Check it out at https://tensordash.ai/u/{}/{}'.format(ownerId, projectName))

    def _refresh_auth(self):
        # TODO: Check if the credentials are set
        auth = self.auth
        u = Cognito(self.userPoolId, self.clientId, id_token=auth['id_token'],
                    access_token=auth['access_token'], refresh_token=auth['refresh_token'],
                    access_key='adasd', secret_key='adas', user_pool_region=self.aws_region)
        u.check_token()
        # save config in memory
        self.auth = {
            'id_token': u.id_token,
            'access_token': u.access_token,
            'refresh_token': u.refresh_token
        }
        # Reauth GraphQL client
        self._update_graphql_client(u.access_token)

    def _authenticate(self, user, password):
        try:
            u = Cognito(self.userPoolId, self.clientId, username=user,
                        access_key='asdas', secret_key='asdas', user_pool_region=self.aws_region)
            u.authenticate(password=password)
            # save config in memory
            self.auth = {
                'id_token': u.id_token,
                'access_token': u.access_token,
                'refresh_token': u.refresh_token
            }
            # Setup GraphQL client
            self._update_graphql_client(u.access_token)
        except: # Exception as e:
            # print(str(e))
            print('Not authorized. Incorrect username or password.')
            exit(1)

    def _update_graphql_client(self, access_token):
        self.client = Client(transport=RequestsHTTPTransport(
            url=self.graphqlEndpoint,
            headers={'Authorization': access_token},
            use_json=True
        ))

    def login(self, user, password):
        if user is None:
            user = input('Username: ')
        if password is None:
            password = getpass.getpass()
        self._authenticate(user, password)
        # write auth to file
        self.saveConfigToFile()
        print('You\'re logged in. Credentials stored.')

    def logout(self):
        if not ('AUTH' in self.config.sections()):
            print('You\'re not logged in. All good.')
            exit(0)
        # Logout
        auth = self.auth
        u = Cognito(self.userPoolId, self.clientId, id_token=auth['id_token'],
                    access_key='adasd', secret_key='asdas', user_pool_region=self.aws_region,
                    access_token=auth['access_token'], refresh_token=auth['refresh_token'])
        try:
            u.logout()
        except:
            pass
        # Remove credentials
        self.config.remove_section('AUTH')
        with open(self.configpath, 'w') as f:
            self.config.write(f)
        print('Credentials successfully removed.')

def cli():
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
    subparsers.add_parser('logout', help='Remove your credantials from local storage.')
    subparsers.add_parser('configure', help='Reconfigure the server settings.')
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
    elif action == 'configure':
        tensordash.reconfigure()
