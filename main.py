import yaml

with open('data.yaml') as f:
    
    data = yaml.load(f, Loader=yaml.FullLoader)
    print(data)