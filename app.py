from flask import Flask, render_template
from flask_pymongo import PyMongo
import main

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb+srv://icydenev:iU61v1ZTrOs1Q6Ur@excalibur.dqizetn.mongodb.net/eventDB"
mongo = PyMongo(app)


@app.route('/')
def home():
    # Suggest New Events based on the criteria
    main.main()

    # Fetch data from MongoDB
    data = mongo.db['events'].find()

    print("Data: " + str(data))

    for document in data:
        print(document)

    # Render the data in a Flask template
    return render_template('index.html', data=data)
