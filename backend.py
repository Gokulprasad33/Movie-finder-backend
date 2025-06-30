from flask import Flask,request,jsonify
from flask_cors import CORS
import pandas as pd
import re # Regex
import numpy as np 

app = Flask(__name__)
CORS(app)

# Loading csv
df=pd.read_csv('Recommended_movies_v1.csv')

@app.route("/api/suggest-a-movie", methods=["POST"])
def suggest_a_movies():
    data = request.json
    genre = data["genre"]
    language = data["language"]
    year = data["releaseyear"]
    nsfw = data["nsfw"]
    toprated = data["toprated"]
    blockList=data.get('blockedMovie',[]) + data.get('watchLists',[])

    # Processing data 

    # Time
    timePeriod=re.split(r'[-]+',year)
    if(timePeriod[0]=="2000's"):
        timePeriod[0]="2000"
        timePeriod.append("2010")    
    timePeriod = [int(timePeriod[0]), int(timePeriod[1])] # Turn into int before searching

    print(timePeriod)

    # Language
    language_map={ 'Tamil':'ta','English':'en','Korean':'ko','Japanese':'ja','Hindi':'hi','Italian':'it','Portuguese':'pt','Spanish':'es','Chinese':'zh','Latvian':'lv','French':'fr','Turkish':'tr','Russian':'ru','Arabic':'ar','Swedish':'sv','German':'de','Danish':'da','Persian':'fa','Thai':'th','Hungarian':'hu','Bengali':'bn','Polish':'pl','Dutch':'nl','Estonian':'el','Serbian':'sr','Telugu':'te','Ukrainian':'uk','Serbo-Croatian':'sr','Indonesian':'id','Greek':'el','Romanian':'ro','Norwegian':'no','Galician':'cs','Czech':'ga','Irish Gaelic':'ga','Bosnian':'bs','Finnish':'fi','Icelandic':'is','Malayalam':'ml','Latin':'la','Tswana':'tn','Khmer':'km','Hebrew':'he','Basque':'eu','Lithuanian':'lt'}
    language_preference=language_map.get(language)
    print(language_preference)

    # Nsfw and Top rated
    if(nsfw=="Yes"):
        nsfw="True" 
    else:
        nsfw="False"

    if(toprated=="Yes"):
        toprated="True" 
    else:
        toprated="False"
    print(nsfw)
    print(toprated)
    
    if(language_preference=="ta"):
        ratingLimit=6
        ratingCountLimit=10
    else:
        ratingLimit=7.5
        ratingCountLimit=100

    filtered = df[
        df["genres"].str.contains(genre, na=False) &
        (df["original_language"] == language_preference) &
        (df["release_year"] > timePeriod[0]) & (df["release_year"] < timePeriod[1])&
        df["adult"].astype(str).str.contains(nsfw, na=False) & 
        (df["vote_average"]> ratingLimit) & (df["vote_count"]>=ratingCountLimit) & # TopRaing filter avg vote >8 and Vote count > 1000
        ~df["id"].isin(blockList) # Not in the blockecMovieList
    ]


    # Debug
    print("Filtered type:", type(filtered)) # Make sure filtered is a dataframe
    print("Filtered shape:", filtered.shape)

    if filtered.empty:
        return jsonify([])
    # NaN fix
    filtered = filtered.replace({np.nan: None}) 
    result = filtered.sample(min(10, len(filtered))).to_dict(orient="records")
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)