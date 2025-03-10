from flask import Flask,request,jsonify
import os
import requests
from flask_cors import CORS
import base64

app=Flask(__name__)
CORS(app)
global urls

@app.route("/")
def welcome():
    print(os.getenv("ACCESS_KEY"))
    return "hello flask"


@app.route("/get-images",methods=["GET"])
def get_images():
    page=request.args.get('page')

    url = "https://api.unsplash.com/photos/random"
    params = {
        'client_id':os.getenv('ACCESS_KEY'),
        'count': 20  ,
        'page ':page
    }
    try:
        response=requests.get(url=url,params=params)
        response.raise_for_status()
        data=response.json()
        if not response:
            return "no data found"
        
        
        urls_list=[]
      

        for photo in data:
            urls_list.append({"id":photo["id"],"urls":photo["urls"],"height":photo["height"]})

        print (len(urls_list))
        return urls_list,200
    
    except Exception as e:
        print(f"An error occurred !{e}")
        return jsonify({"error":str(e)}),500


@app.route("/search/<query>",methods=["GET"])
def search_images(query):
    try:
        query=query.strip().replace(" ","+")
        page=request.args.get('page')
        url = f"https://api.unsplash.com/search/photos"
        params = {
        'client_id':os.getenv('ACCESS_KEY'),
         'count':20,
          'page':page,
          'query':query
        }
        data=requests.get(url=url,params=params)
        response=data.json()
        if not response:
            return "no results found"
        urls_list=[]
      

        for photo in response["results"]:
            urls_list.append({"id":photo["id"],"urls":photo["urls"],"height":photo["height"]})
        
        print (len(urls_list))
        return urls_list,200
        
     
    except Exception as e:
        print("error occured while searching",e)
        return jsonify({"error":str(e)}),500



@app.route("/get-topic/<topic>",methods=["GET"])
def get_topic(topic):
    page=request.args.get('page')

    try:
        url = f"https://api.unsplash.com/topics/{topic}/photos"
        params = {
        'client_id':os.getenv('ACCESS_KEY'),
        'count':20,
        'page':page,
        }
        data=requests.get(url=url,params=params)
        response=data.json()
        if not data:
            return "no results found"
        urls_list=[]
        for photo in response:
            urls_list.append({"id":photo["id"],"urls":photo["urls"],"height":photo["height"]})
        
        print(len(urls_list))
        return urls_list


    except Exception as e:
        print("error occured while getting topic",e)
        return jsonify({"error":str(e)}),500
    

@app.route("/generate-ai-image",methods=["POST"])
def generate_image():
    API_BASE_URL = "https://api.cloudflare.com/client/v4/accounts/a57a418d002a3c48dcc1f7ef8f69d4c8/ai/run/"
    headers = {"Authorization": f"Bearer {os.getenv('BEARER_TOKEN')}"}
    try:
     
        prompt=str(request.form["prompt"])
        if not prompt:
            return jsonify({"error": "Please enter a prompt"}), 400
        input={"prompt":prompt}
        response = requests.post(f"{API_BASE_URL}@cf/stabilityai/stable-diffusion-xl-base-1.0", headers=headers, json=input)
        if response.status_code == 200:
            image_base64 = base64.b64encode(response.content).decode('utf-8')
            image_uri = f"data:image/png;base64,{image_base64}"
            
            return jsonify({"image_uri": image_uri}), 200
            
        else:
            return jsonify({
                "error": "Image generation failed",
                "details": response.text
            }), 500



    
    except Exception as e:
        print("error occured while generating image",e)
        return jsonify({"error":str(e)}),500








if __name__=="__main__":
    app.run()