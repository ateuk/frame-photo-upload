## Intro 
Web app to upload files to a local directory.

- This project is a Flask web application designed to manage and display images. 
- This is used to enable users to upload pictures to be displayed on an eink frame.
- This is vibe coded.
- Lightweight, can run on a raspberry pi zero

## Run

```
pip install -r requirements.txt
gunicorn  --bind 0.0.0.0:8000 app:app
```


