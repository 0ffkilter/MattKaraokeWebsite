import requests
import re
from flask import Flask
from flask import render_template
from flask import request
import json

app = Flask(__name__)

# strCond
# 1 = single search, 0 = multi search
strCond = 0

import re

# as per recommendation from @freylis, compile once only
CLEANR = re.compile("<.*?>")


def cleanhtml(raw_html):
    cleantext = re.sub(CLEANR, "", raw_html)
    return cleantext


# natType
country_options = {
    "All Countries": "",
    "US": "ENG",
    "Korea": "KOR",
    "Japan": "JPN",
    "China": "CHN",
    "Indonesia": "PHL",
    "Phillipines": "INS",
}

# strType
search_options = {
    "Any": "",
    "Song Title": "1",
    "Artist": "2",
    "Song Id": "5",
    "Lyricist": "3",
    "Composer": "4",
    "Lyrics": "6",
}

pat = re.compile(
    '<td class="youtube_auto_search" data-pro="(\\d+)" data-title="(.*)" data-singer="(.*)"'
)


@app.route("/", methods=["POST", "GET"])
def base():
    payload = {}

    payload["SearchOrderItem"] = ""
    payload["SearchOrderType"] = ""
    payload["strCond"] = strCond
    payload["natType"] = "ENG"
    payload["strType"] = "2"
    payload["strText"] = "one republic"

    nat_select = "All Countries"
    search_select = "Any"
    formatted_matches = []

    if request.args is not None:
        if "country" in request.args and request.args["country"] != "":
            payload["natType"] = country_options[request.args["country"]]
            nat_select = request.args["country"]

        if "search" in request.args and request.args["search"] != "":
            option_number = search_options[request.args["search"]]
            payload["strType"] = option_number
            if option_number == "":
                for i in range(5):
                    payload["strSize0%i" % (i)] = 100
            else:
                payload["strSize0%s" % (option_number)] = 100

            search_select = request.args["search"]

        if "song_search" in request.args and request.args["song_search"] != "":
            payload["strText"] = request.args["song_search"]
            page = requests.post(
                "https://www.tjmedia.com/tjsong/song_search_list.asp",
                payload,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded; charset=euc-kr"
                },
            )

            page.encoding = "euc-kr"

            matches = pat.findall(page.content.decode("utf-8", errors="ignore"))

            ids = set()
            for m in matches:
                song_id = cleanhtml(m[0])

                if song_id not in ids:
                    ids.add(song_id)
                    formatted_matches.append(
                        {
                            "song": cleanhtml(m[1]),
                            "artist": cleanhtml(m[2]),
                            "id": song_id,
                        }
                    )

    content = {
        "songs": formatted_matches,
        "count": len(formatted_matches),
        "country_options": country_options.keys(),
        "search_options": search_options.keys(),
        "nat_select": nat_select,
        "search_select": search_select,
    }
    print(content)

    return render_template("index.html", **content)
