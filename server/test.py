from requests import get


print(get('http://localhost:3001/tags_to_colors').json())
text = '日本'
print(get(f'http://localhost:3001/tokenize?string1=かちゃ&string2={text}').json())
