
import setuptools

setuptools.setup(
    name = 'tensordash',
    version = '0.1.0',
    author = 'tensordash',
    author_email = 'info@tensordash.ai',
    description = 'A dashboard for your AI experiments',
    url = 'https://github.com/tensordash/tensordash',
    packages = ['tensordash'],
    install_requires = [
        'six',
        'warrant',
        'gql',
        'requests'
    ],
    entry_points = {
        'console_scripts': ['tensordash = tensordash.main:cli']
    }
)
