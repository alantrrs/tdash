
# tensordash

The client for [tensordash.ai](https://tensordash.ai)

## Install
```
pip install tensordash
```

## Keep track of your experiment outputs

### 1. Create a project on http://tensordash.ai

### 2. Authenticate
```
tensorboard login
```

### 3. Push your results

After running your experiment, in order to push your output files to a new run in a project 
just specify the project and the file paths:
```
tensordash push --project username/my-project /path/to/file1 /path/to/file2
```

If all your files are in the same directory, you can push the complete directory:
```
tensordash push --project username/my-project /path/to/output_directory
```

That's it, tensordash will return a URL where your outputs are stored and can be visualized.
