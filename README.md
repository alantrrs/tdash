
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
tensordash push --project username/my-project /path/to/logs.out.tfevents /path/to/file2
```
