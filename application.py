from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import pymongo

application = Flask(__name__) # initializing a flask app
app=application

@app.route('/',methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")

@app.route('/review',methods=['POST','GET']) # route to show the review comments in a web UI
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            uClient = uReq(flipkart_url)
            flipkartPage = uClient.read()
            uClient.close()
            flipkart_html = bs(flipkartPage, "html.parser")
            bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})
            reviews = []
            client = pymongo.MongoClient("mongodb+srv://atamotia:atamotia@cluster0.av6ep6v.mongodb.net/?retryWrites=true&w=majority")
            db = client['Web_Scrapper']
            db_coll = db[searchString]

            for box in bigboxes:

                try: 
                    productLink = "https://www.flipkart.com" + box.div.div.div.a['href']
                    prodRes = requests.get(productLink)
                    prodRes.encoding='utf-8'    
                    prod_html = bs(prodRes.text, "html.parser")

                    try:
                            prodName = prod_html.find_all('span', {'class': 'B_NuCI'})[0].text
                    
                    except:
                            prodName = 'No Name'

                    commentboxes = prod_html.find_all('div', {'class': "_16PBlm"})
                    for commentbox in commentboxes:

                        try:
                            name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text

                        except:
                            name = 'No Name'

                        try:
                            rating = commentbox.div.div.div.div.text

                        except:
                            rating = 'No Rating'

                        try:
                            commentHead = commentbox.div.div.div.p.text

                        except:
                            commentHead = 'No Comment Heading'
                        
                        try:
                            comtag = commentbox.div.div.find_all('div', {'class': ''})
                            custComment = comtag[0].div.text
                        
                        except Exception as e:
                            comtag = 'No Comment'

                        mydict = {"Product": prodName, "Name": name, "Rating": rating, "CommentHead": commentHead,
                                "Comment": custComment}
                        reviews.append(mydict)
                
                except:
                    continue
                
            db_coll.insert_many(reviews)
            return render_template('results.html', reviews=reviews[0:len(reviews)])
        except Exception as e:
            return 'something is wrong'
    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8000, debug=True)
