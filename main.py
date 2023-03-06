from flask import Flask, request , render_template,jsonify, Response,send_file
import sys
import mainfile
import time
import os
import csv
import pandas as pd
import io
from io import StringIO
app = Flask(__name__)


@app.route('/',methods=['POST','GET'])
def home():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit_form():
    if request.method=='POST':
        retry_limit=int(request.form['retry'])
        record_count=int(request.form['record'])
        options = request.form.getlist('option')
        old= request.form['old']
        output = ''
        #print("Hey Buddy")
    # Redirect standard output to a buffer
        oldfinal=(int(old[old.index("/")+1:])*100)+int(old[old.index("/")-2:old.index("/")])
        #print(oldfinal)
        if "1" in options:
            mainfile.first_site(oldfinal,record_count,retry_limit)
        if "2" in options:
            mainfile.second_site(oldfinal,record_count,retry_limit)
        if "3" in options:
            mainfile.third_site(oldfinal,record_count,retry_limit)
        #print(retry_limit)
        #print(record_count)
        #print(options)
        while(True):
            time.sleep(500)
@app.route('/data')
def data():
    def generate():
        # Redirect stdout to a custom stream
        class Stream:
            def __init__(self):
                self.data = []
            def write(self, s):
                self.data.append(s)
        stream = Stream()
        sys.stdout = stream
        
        # Start a loop to continuously check for new data to send to the client
        while True:
            # Yield any new data
            if len(stream.data) > 0:
                yield f"data: {stream.data.pop(0)}\n\n"
            else:
                yield "data: \n\n"
            time.sleep(0.1)
    return Response(generate(), mimetype='text/event-stream')

@app.route('/download')
def download():
    # Read the CSV file data
    caldf = mainfile.global_var.to_csv(index=False, header=True)
    buf_str = io.StringIO(caldf)
    return send_file (io.BytesIO(buf_str.read().encode("utf-8")), mimetype="text/csv", download_name="data.csv" )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
