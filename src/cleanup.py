import os
import xml.etree.ElementTree as ET


path = input('url? >> ')

# /home/peter/Downloads/subscriptions.xml

check = os.path.exists(path)

with open(path, 'r') as file:
    tree = ET.parse(file)
    root = tree.getroot()
    for outline in root.findall('.//outline'):
        if 'xmlUrl' in outline.attrib and 'title' in outline.attrib:
            title = outline.attrib['title'].strip()
            url = outline.attrib['xmlUrl'].strip()
            print(title, ' : ', url)
print(check)