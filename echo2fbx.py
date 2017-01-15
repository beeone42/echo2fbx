import urllib2, os, sys, json
from flask import Flask, jsonify, request

CONFIG_FILE = 'config.json'

app = Flask(__name__)
fbx = ""

cmds = {
    'Volume': { 'up':   { 'cmd': 'vol_inc', 'rep': 'volume up' },
                'down': { 'cmd': 'vol_dec', 'rep': 'volume down' } },
    'Channel': { 'up':   { 'cmd': 'prgm_inc', 'rep': 'channel up' },
                 'down': { 'cmd': 'prgm_dec', 'rep': 'channel down' } },
    'Tv':      { 'cmd': 'tv', 'rep': 'tv' },
    'Ok':      { 'cmd': 'ok', 'rep': 'ok' },
    'GoHome':  { 'cmd': 'home', 'rep': 'i go home' },
    'Mute':    { 'cmd': 'mute', 'rep': 'volume mute' },
    'PowerOn': { 'cmd': 'power', 'rep': 'power' }
    }

def open_and_load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as config_file:
            return json.loads(config_file.read())
    else:
        print "File [%s] doesn't exist, aborting." % (CONFIG_FILE)
        sys.exit(1)

@app.route("/", methods=['GET', 'POST'])
def hello():
    cmd = ""
    rep = ""
    content = request.get_json(silent=True)
    intent = content['request']['intent']['name']
    res = { "version": "1.0", "response": {
            "outputSpeech": { "type": "PlainText", "text": "unknown function" },
            "card": { "type": "Simple", "title": "freebox", "content": "unknown function" },
            "shouldEndSession": True }, "sessionAttributes": {} }


    if (intent in cmds.keys()):
        if (isinstance(cmds[intent], dict) and ('cmd' not in cmds[intent].keys())):
            param = ""
            if ('slots' in content['request']['intent'].keys()):
                param = content['request']['intent']['slots']['Param']['value']
            if (param in cmds[intent].keys()):
                cmd =  cmds[intent][param]['cmd']
                rep =  cmds[intent][param]['rep']
        else:
            cmd = cmds[intent]['cmd']
            rep = cmds[intent]['rep']

    if (cmd != ""):
        print cmd
        req = urllib2.Request('http://hd1.freebox.fr/pub/remote_control?code=' + fbx + '&key=' + cmd + '&long=false')
        response = urllib2.urlopen(req)
        the_page = response.read()
        print the_page

    if (rep != ""):
        res['response']['outputSpeech']['text'] = rep

    return jsonify(res)

if __name__ == "__main__":
    config = open_and_load_config()
    fbx = config['fbx']
    print "Freebox remote controller code: " + fbx
    app.run()
