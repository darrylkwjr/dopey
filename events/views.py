from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.views import View
import requests
import pandas as pd

API_KEY = "wrFFyND6lLARzANikXAxbWjVbWhWHQuM"


def extract_event_data(events):
    event_data = []
    for event in events:
        name = event["name"]
        date = event["dates"]["start"]["localDate"]
        venue = event["_embedded"]["venues"][0]["name"]
        state = event["_embedded"]["venues"][0]["state"]["stateCode"]
        city = event["_embedded"]["venues"][0]["city"]["name"]
        url = event["url"]

        event_data.append({"Name": name, "Date": date, "Venue": venue, "State": state, "City": city, "URL": url})
    return pd.DataFrame(event_data)


class ComedyEventsView(View):
    def get(self, request, state_code):
        url = "https://app.ticketmaster.com/discovery/v2/events.json"
        params = {
            "apikey": API_KEY,
            "classificationName": "Comedy",
            "size": 40,
            "page": 0,
            "stateCode": state_code
        }

        df = pd.DataFrame()

        while True:
            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()
            except requests.exceptions.RequestException as e:
                return JsonResponse({"error": f"Unable to fetch data from API. Reason: {e}"}, status=400)

            if "_links" in data and "next" in data["_links"]:
                params["page"] += 1
            else:
                break

            try:
                events = data["_embedded"]["events"]
                temp_df = extract_event_data(events)
                df = pd.concat([df, temp_df], ignore_index=True)
            except KeyError:
                return JsonResponse({"error": "Unable to extract information from event"}, status=400)

            context = {
                    "state_code": state_code,
                    "events": df.to_dict(orient="records"),
                }
            return render(request, 'theme/room.html', context)
