import xml.etree.ElementTree as ET


# https://docs.python.org/3/library/xml.etree.elementtree.html

def main():
    tree = ET.parse('./country_data.xml')
    root = tree.getroot()
    print("{} {}".format(type(root), root))
    for child in root:
        print(child.tag, child.attrib)

    print("root[0][1].text: {}".format(root[0][1].text))

    for neighbor in root.iter('neighbor'):
        print("neighbor: {}".format(neighbor.attrib))

    for country in root.findall('country'):
        rank = country.find('rank').text
        name = country.get('name')
        print(name, rank)

    for rank in root.iter('rank'):
        new_rank = int(rank.text) + 1
        rank.text = str(new_rank)
        rank.set('updated', 'yes')

    tree.write('output.xml')


if __name__ == '__main__':
    main()
