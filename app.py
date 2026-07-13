from flask import Flask, render_template, request
from recommender import search
import re

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search_page():

    requirement = request.form.get("requirement", "").strip()

    results = search(requirement)

    for module in results:

        features = module.get("features") or module.get("Features") or ""

        feature_list = []

        if isinstance(features, str):

            # First try splitting by new lines
            feature_list = [
                f.strip()
                for f in features.split("\n")
                if f.strip()
            ]

            # If only one long paragraph exists, split by feature titles
            if len(feature_list) <= 1:
                feature_list = re.split(
                    r'(?<=[.])\s*(?=[A-Z][A-Za-z0-9 /&()\'-]+:)',
                    features
                )

                feature_list = [
                    f.strip()
                    for f in feature_list
                    if f.strip()
                ]

        module["feature_list"] = feature_list

    return render_template(
        "index.html",
        requirement=requirement,
        results=results
    )


if __name__ == "__main__":
    app.run(debug=True)