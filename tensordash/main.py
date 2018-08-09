
from warrant import Cognito
import configparser
import os
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
import mimetypes

class Tensordash():
    def __init__(self):
        self.poolId = 'us-east-1_LfXdV62Vn'
        self.clientId = '6deesjtjflk6aphp4dmt9pl8d9'
        self.graphqlApiUrl = 'https://jgyool6savhb3lyvsxcmdivcw4.appsync-api.us-east-1.amazonaws.com/graphql'
        # Load user config
        self.config = configparser.ConfigParser()
        self.configpath = '.tensordash.cfg'
        if os.path.exists(self.configpath):
            self.config.read(self.configpath)
            if 'AUTH' in self.config.sections():
                self._refresh_auth()

    def push(self, project, filepaths, user=None, password=None):
        if user is not None:
            self._authenticate(user, password)
        # TODO: Create new experiment
        # Get signed URLs for all files
        assets = map(lambda asset: {
            'localUri': asset,
            'mimeType': mimetypes.guess_type(asset)
        }, filepaths)
        query = gql('''
            query requestAssets($assetsInput: AssetsInput!) {
                requestAssetsUpload(input: $assetsInput)
            }
        ''')
        params = {'assetsInput': {'assets': assets}}
        res = self.client.execute(query, variable_values=params)
        print(res)
        # TODO: Upload files to S3 directly
        # TODO: Update DB with outputs

    def _refresh_auth(self):
        # TODO: Check if the credentials are set
        auth = self.config['AUTH']
        u = Cognito(self.poolId, self.clientId, id_token=auth['id_token'],
                    access_token=auth['access_token'], refresh_token=auth['refresh_token'])
        u.check_token()
        # save config in memory
        self.config['AUTH'] = {'id_token': u.id_token,
                               'access_token': u.access_token,
                               'refresh_token': u.refresh_token}
        # Reauth GraphQL client
        self._update_graphql_client(u.access_token)

    def _authenticate(self, user, password):
        try:
            u = Cognito(self.poolId, self.clientId, username=user)
            u.authenticate(password=password)
            # save config in memory
            self.config['AUTH'] = {'id_token': u.id_token,
                               'access_token': u.access_token,
                               'refresh_token': u.refresh_token}
            # Setup GraphQL client
            self._update_graphql_client(u.access_token)
        except:
            print('Not authorized. Incorrect username or password.')
            exit(1)

    def _update_graphql_client(self, access_token):
        self.client = Client(transport=RequestsHTTPTransport(
            url=self.graphqlApiUrl,
            headers={'Authorization': access_token},
            use_json=True
        ))

    def login(self, user, password):
        self._authenticate(user, password)
        # write auth to file
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
