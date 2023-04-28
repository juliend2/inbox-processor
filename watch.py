import json
import os
import requests
import sys
import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

JSONL_FILE = "/var/www/julien/uploads/received.jsonl"

def get_json(file_path):
    file = open(file_path)
    lines = file.readlines()
    jsons = [json.loads(s) for s in lines]
    file.close()
    return jsons

def download_image(url, to_file_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(to_file_path, 'w') as f:
            print("Saving file %s" % (to_file_path))
            f.write(response.text)
    else:
        print('Error:', response.status_code)


def process(file_path):
    jsons = get_json(file_path)
    for js in jsons:
        filename = js['fileName']
        filepath = os.path.join(os.path.dirname(JSONL_FILE), filename)
        if os.path.isfile(filepath):
            print("File '%s' already exists" % (filename))
        else:
            photo_url = ''
            try:
                photo_url = js['photoUrl']
            except KeyError:
                print('key error')
                print(js)
            download_image(photo_url, filepath)

class MyHandler(FileSystemEventHandler):

    def on_modified(self, event):
        # Use debounce to ignore events that occur within 0.5 seconds of each other
        if event.src_path == JSONL_FILE:
            self.debounced_process(event.src_path)

    def debounced_process(self, src_path):
        now = time.time()
        if hasattr(self, 'last_event_time') and now - self.last_event_time < 0.5:
            return
        self.last_event_time = now
        # Process the event here...
        print("Processing the file...")
        process(JSONL_FILE)

# Initial run:
process(JSONL_FILE)

# Then watch for changes:
observer = Observer()
observer.schedule(MyHandler(), path=JSONL_FILE)
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()

observer.join()
