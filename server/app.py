from flask import Flask, request, render_template
from os import listdir, path, makedirs, path
from json import loads, dumps
import random
import string

app = Flask(__name__)

def random_combo(length=5):
    characters = string.ascii_letters + string.digits
    random_combination = ''.join(random.choice(characters) for _ in range(length))
    return random_combination

def decode(t):
    return t.replace("_", " ").replace(".md", "")


def encode(t):
    return t.replace(" ", "_") + ".md"


def resolve(t):
    if ".md" in t:
        return t
    return encode(t)

def clean(t):
    if ".md" not in t:
        return t
    return decode(t)


@app.route("/", methods=["GET"])
def main():
    entries = [[t, decode(t)] for t in listdir("stories")]
    print(entries)
    return render_template("index.html", entries=entries)


@app.route("/", methods=["POST"])
def api():

    if request.form.get("method") == "back":
        return {"success": 1, "results": [[t, decode(t)] for t in listdir("stories")]}

    elif request.form.get("method") == "load":
        content = ""
        name = request.form.get("name")
        file = "stories/" + resolve(name)
        if path.exists(file):
            with open(file, "r") as f:
                content = "\n".join(f.readlines())
        print(name)
        return {"success": 1, "content": content, "name": clean(name)}

    elif request.form.get("method") == "save":
        with open("stories/" + encode(request.form.get("name")), "w") as f:
            f.writelines(request.form.get("content").split("\n"))
        return {"success": 1}
    
    elif request.form.get("method") == "retrieve_id":
        mac = request.form.get("mac_address")

        if not path.exists("stories/" + mac):
            makedirs("stories/" + mac)

        data = {}
        with open("devices.json", "r") as f:
            data = loads("\n".join(f.readlines()))
        code = random_combo()
        data[mac] = code
        with open("devices.json", "w") as f:
            f.writelines(dumps(data).split('\n'))

        return {"success": 1, "code": code}

    return {"success": 0}
