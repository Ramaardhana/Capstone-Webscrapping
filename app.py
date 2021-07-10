from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.coingecko.com/en/coins/ethereum/historical_data/usd?start_date=2020-01-01&end_date=2021-06-30#panel')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
table = soup.find('table', attrs={'class':'table table-striped text-sm text-lg-normal'})
body = table.find_all("tr")

body_length=len(body)

temp = [] #initiating a tuple

for i in range(1, len(body)): 

    #scrapping process
    
    #scrape date
    Date = body[i].th.text #Column "Date" is uniquely marked by 'th'.
          
    #scrape Volume
    Volume = body[i].find_all('td')[1].text  #Column "Volume" is marked by 'td' in column #1 (#0 is "Market cap") .
    Volume = Volume.strip('\n') #to remove excess white space
    

    
    temp.append((Date, Volume,))

#change into dataframe
df = pd.DataFrame(temp, columns = ('Date', 'Volume'))

#insert data wrangling here
df['Volume']=df['Volume'].str.replace('$','')
df['Volume']=df['Volume'].str.replace(',','')
df['Volume']=df['Volume'].astype('int64')
df['Date']=pd.to_datetime(df['Date'],format='%Y-%m-%d')
df['Quarter']=df['Date'].dt.to_period('Q')
df=df.set_index('Date')


#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'{round(df["Volume"].mean(), 2)}' #be careful with the " and ' 

	# generate plot
	ax = df.plot(figsize = (20,9)) 
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)