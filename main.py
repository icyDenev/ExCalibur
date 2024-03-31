import requests
from icalendar import Calendar
from datetime import datetime
from perplexityai import Perplexity
from pymongo import MongoClient
import re
import json

class Event:
    def __init__(self, name, start_time, end_time, location):
        self.name = name
        self.start_time = start_time
        self.end_time = end_time
        self.location = location

    def __str__(self):
        return f"Event: {self.name}\nStart Time: {self.start_time}\nEnd Time: {self.end_time}\nLocation: {self.location}\n"


def fetch_ical_events( start_time, end_time):
    try:
        ical_text = open("cal.ics", "r").read()
        cal = Calendar.from_ical(ical_text)

        events = []
        for component in cal.walk():
            if component.name == "VEVENT":
                event_start = component.decoded('dtstart')
                event_end = component.decoded('dtend')

                if event_start.isoformat() >= start_time.isoformat() and event_end.isoformat() <= end_time.isoformat():
                    name = str(component.get('summary'))
                    start_time_str = event_start.strftime('%Y-%m-%d %H:%M:%S')
                    end_time_str = event_end.strftime('%Y-%m-%d %H:%M:%S')
                    location = str(component.get('location'))
                    event = Event(name, start_time_str, end_time_str, location)
                    events.append(event)

        return events
    except Exception as e:
        print("An error occurred:", e)
        return []


def main():
    ical_link = r"https://calendar.google.com/calendar/embed?src=bf9c50ce81d2b8f7db69c12ffc8beb7aa41850c059ba69275d10c498fdc9abe6%40group.calendar.google.com&ctz=Europe%2FLondon"
    start_time = datetime(2024, 3, 31)
    end_time = datetime(2024, 4, 30)
    events = fetch_ical_events(start_time, end_time)
    eventsText = ""
    interests = "ANY"
    locationRadius = 100
    location = "Princeton, NJ"
    sources = "https://www.eventbrite.com/"
    outputFormat = "Event: \nStart Time:\nEnd Time:\nLocation:\nLink:\n"
    resp = ""

    for event in events:
        eventsText += str(event) + "\n"

    prompt = "Find events between" + str(start_time) + "and " + str(end_time) +  "based on these interests: " + interests + "\nMake sure these events are at most " + str(locationRadius) + " mi away from " + location + "Find the events that are not in conflict with the following events: " + eventsText + "\nIf there are any events, output them in the following format:\n" + outputFormat + "\nUse these sources: " + sources
    for a in Perplexity().generate_answer(prompt):
        if 'answer' in a:
            resp = a['answer']

    print(resp)

    # The pattern to search for
    pattern = r"Event: (.*?)\nStart Time: (.*?)\nEnd Time: (.*?)\nLocation: (.*?)\nLink: (.*?)\n"

    # Use re.findall() to find all matches of the pattern
    matches = re.findall(pattern, resp)

    # Convert the matches to a list of dictionaries
    events = [{"Event": m[0], "Start Time": m[1], "End Time": m[2], "Location": m[3], "Link": m[4]} for m in matches]

    # Convert the list of dictionaries to a JSON string
    json_data = json.dumps(events, indent=4)

    client = MongoClient('mongodb+srv://icydenev:iU61v1ZTrOs1Q6Ur@excalibur.dqizetn.mongodb.net/')

    # Select or create the database
    db = client['eventDB']

    # Select or create the collection
    collection = db['events']

    try:
        # Open and load the JSON file
        file_data = json.loads(json_data)
    finally:
        file_data = None

    if file_data == None:
        print("No data found.")
    # Check if the JSON data is a list of documents
    elif isinstance(file_data, list):
        # Insert all documents in the list
        collection.insert_many(file_data)
    else:
        # Insert a single document
        collection.insert_one(file_data)

    print("JSON data inserted into MongoDB.")

if __name__ == "__main__":
    main()
