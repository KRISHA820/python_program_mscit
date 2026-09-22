from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


@app.route("/")
def root():
    return render_template("home.html")


@app.route("/search", methods=["POST"])
def search():

    print(request.method)

    if request.method == "POST":
        taskname = request.form.get("taskname")
        finishdate = request.form.get("finishdate")
        status = request.form.get("status")

        print("Task Name:", taskname)
        print("Finish Date:", finishdate)
        print("Status:", status)

        return jsonify({
            "taskname": taskname,
            "finishdate": finishdate,
            "status": status
        })

    return "Invalid Request"


if __name__ == "__main__":
    app.run(port=5001, debug=True)