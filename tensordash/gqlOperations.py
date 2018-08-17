
from gql import gql

createExperiment = gql('''
    mutation CreateExperiment($input: ExperimentInput) {
        createExperiment(input: $input) {
            id
        }
    }
''')

requestUpload = gql('''
    query RequestUpload($input: AssetsInput!) {
        requestUpload(input: $input) {
            localUri
            putUrl
            mimeType
            acl
            key
        }
    }
''')
