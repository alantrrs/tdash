
import setuptools

setuptools.setup(
    name = 'tensordash',
    version = '0.0.4',
    author = 'tensordash',
    author_email = 'info@tensordash.ai',
    description = 'A dashboard for your AI experiments',
    url = 'https://github.com/tensordash/tensordash',
    packages = setuptools.find_packages(),
    scripts = ['tensordash/main.py']
)
