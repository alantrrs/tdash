

class Tensordash():
    def __init__(self):
        # TODO: load config
        print('load-config')

    def push(self, project, filepaths, user=None, password=None):
        self._authenticate(user, password)
        # TODO: Get signed URLs for all files
        print 'PUSH:', project, filepaths
        # TODO: Upload files from directory to S3 directly
        # TODO: Update DB with outputs
        print("pushing..")

    def _authenticate(self, user, password):
        # TODO: authenticate with server
        print("Authenticating with server..")

    def login(self, user, password):
        isAuth, token = self._authenticate(user, password)


    def logout(self):
        # TODO: Remove auth
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
