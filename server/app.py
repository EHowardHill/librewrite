from flask import Flask, request, render_template
from os import listdir, path, makedirs, system
from json import loads, dumps
import random
import string
from requests import post
from datetime import datetime

app = Flask(__name__)
date_format = "%Y-%m-%d %H:%M:%S"


def random_combo(length=5):
    characters = string.ascii_letters + string.digits
    random_combination = "".join(random.choice(characters) for _ in range(length))
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


def devices(code):
    data = {}
    with open("devices.json", "r") as f:
        data = loads("\n".join(f.readlines()))
    for d in data.keys():
        if data[d] == code:
            return d.replace("\n","")
    return None


@app.route("/", methods=["GET"])
def main():
    return render_template("index.html")


@app.route("/", methods=["POST"])
def api():
    if request.form.get("method") == "back":
        code = request.form.get("code")
        return {
            "success": 1,
            "results": [[t, decode(t)] for t in listdir("stories/" + devices(code))],
        }

    elif request.form.get("method") == "load":
        content = ""
        name = request.form.get("name")
        code = devices(request.form.get("code")) + "/"
        file = "stories/" + code + resolve(name)
        if path.exists(file):
            with open(file, "r") as f:
                content = "\n".join(f.readlines())
        print(name)
        return {"success": 1, "content": content, "name": clean(name)}

    elif request.form.get("method") == "save":
        code = devices(request.form.get("code")) + "/"
        system("mkdir -p stories/" + code)
        with open("stories/" + code + encode(request.form.get("name")), "w") as f:
            f.writelines(request.form.get("content").split("\n"))
        return {"success": 1}

    elif request.form.get("method") == "retrieve_id":
        mac = request.form.get("mac_address")

        data = {}
        with open("devices.json", "r") as f:
            data = loads("\n".join(f.readlines()))

        if mac not in data.keys():
            makedirs("stories/" + mac)

        code = random_combo()
        data[mac] = code
        with open("devices.json", "w") as f:
            f.writelines(dumps(data).split("\n"))

        return {"success": 1, "code": code}

    elif request.form.get("method") == "code":
        code = request.form.get("code")
        d = devices(code)
        if d != None:
            return {"success": 1}

    elif request.form.get("method") == "sync":
        code = request.form.get("code")
        stories = loads(request.form.get("stories"))
        print(stories)
        response = {}
        d = devices(code)
        for f in listdir("stories/" + d):
            if f not in stories.keys():
                url = "stories/" + d + "/" + f
                with open(url, "r") as r:
                    response[f] = {
                        "datetime": str(path.getmtime(url)),
                        "contents": "\n".join(r.readlines())
                    }
        for f in stories.keys():
            url = "stories/" + d + "/" + f
            if path.exists(url):
                if str(path.getmtime(url)) > stories[f]["datetime"]:
                    with open(url, "r") as r:
                        response[f] = {
                            "datetime": str(path.getmtime(url)),
                            "contents": "\n".join(r.readlines())
                        }
                else:
                    system("mkdir -p stories/" + d)
                    with open(url, "w") as w:
                        w.write(stories[f]["contents"])
            else:
                system("mkdir -p stories/" + d)
                with open(url, "w") as w:
                    w.write(stories[f]["contents"])
        return {"success": 1, "stories": response}

    return {"success": 0}
