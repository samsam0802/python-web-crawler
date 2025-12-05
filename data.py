import  requests
from bs4 import BeautifulSoup
import pandas as pd
data = requests.get("https://www.naver.com/")
soup = BeautifulSoup(data.text, 'html.parser')
# Find all <a> tags with an href attribute
links = soup.find_all('a', href=True)
list2=[]
list3=[]


for i in links:
    list2.append(i.find('span').text)
    list3.append(i.find('span').text+str("사랑합니다"))
obj = {"a": list2, "b": list3}
print(obj)
df = pd.DataFrame(obj)
df.to_csv("a.csv", index=False)
print(df)