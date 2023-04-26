import json
import os
import requests
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

def process(file_path):
    jsons = get_json(file_path)
    for js in jsons:
        filename = './data/photo-%s.jpg' % (js['timestamp'])
        if os.path.isfile(filename):
            print("File %s already exists" % (filename))
        else:
            response = requests.get(js['photoUrl'])
            if response.status_code == 200:
                with open(filename, 'w') as f:
                    print("Saving file %s" % (filename))
                    f.write(response.text)
            else:
                print('Error:', response.status_code)

class MyHandler(FileSystemEventHandler):

    def __init__(self, filepath):
        self.filepath = filepath

    def on_modified(self, event):
        # Use debounce to ignore events that occur within 0.5 seconds of each other
        if event.src_path == self.filepath:
            print('[on modidied]', event.src_path)
            self.debounced_process(event.src_path)

    def debounced_process(self, src_path):
        now = time.time()
        if hasattr(self, 'last_event_time') and now - self.last_event_time < 0.5:
            return
        self.last_event_time = now
        # Process the event here...
        print("Processing the file...")
        process(JSONL_FILE)

process(JSONL_FILE)

observer = Observer()
observer.schedule(MyHandler(JSONL_FILE), path=os.getcwd())
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()

