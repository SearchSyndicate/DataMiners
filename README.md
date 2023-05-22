# DataMiners
### **Global Data Search Engine**<br>
pip install -r requirements.txt

#### Deployment Instructions
With Docker: <br>
* Ensure docker engine is running then in a terminal, go to DataMiners directory and run:<br>
`docker compose up` <br>
Then the app will be live at: http://localhost:5000/ <br>

With Flask Locally:  <br>
* Go to DataMiners directory in a terminal and run:<br>
`Python FlaskAPI.py`     <br>
Then the app will be live at: http://127.0.0.1:5000/

In both the above cases, to get the response without UI, run below given code in a python terminal or simply put the endpoint like below in any browser (customise your endpoint with your specific input):<br>
"http://127.0.0.1:5000/predict?company=Amazon&country=USA&url=https://www.amazon.com/&image=y"<br>
Code:
````
import requests
response = requests.get("http://127.0.0.1:5000/predict?company=Amazon&country=USA&url=https://www.amazon.com/&image=")
````

>Note : the endpoint without an url input will look like this: "http://127.0.0.1:5000/predict?company=Amazon&country=USA&url=&image="

For Multiple inputs:<br>
If more than one inputs at once are needed to be called then `BatchAPICall.py` can be used which takes a dataframe of inputs as its input. Sample input data is present at `data/unicorn-company-list-with_URLs.csv`
