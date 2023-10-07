from flask import Flask, request, render_template
from os import listdir, path

app = Flask(__name__)


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

    return {"success": 0}
