import xml.etree.ElementTree as ET


# https://docs.python.org/3/library/xml.etree.elementtree.html
# https://zhuanlan.zhihu.com/p/502584681


def main():
    tree = ET.parse('./country_data.xml')

    # 获取根元素
    root = tree.getroot()
    print("{} {}".format(type(root), root))

    # 获取指定元素
    print("root[0][1]: tag={},text={}".format(root[0][1].tag, root[0][1].text))

    # 遍历root元素下的所有一级子元素
    for child in root:
        print("---tag:{}, attr:{}, txt:{} ---".format(child.tag, child.attrib, child.text))

    # 遍历root元素及其所有子元素
    for child in root.iter():
        print("---tag:{}, attr:{}, txt:{} ---".format(child.tag, child.attrib, child.text))

    # 遍历root下指定标签的所有子元素
    for neighbor in root.iter('neighbor'):
        print("neighbor: {}".format(neighbor.attrib))

    # 遍历root下 country 标签的所有一级子元素。
    for country in root.findall('country'):
        name = country.get('name')
        # 获取country下第一个 rank 标签的子元素
        rank = country.find('rank').text
        print("country name: {}, rank: {}".format(name, rank))

    # 更新xml
    for rank in root.iter('rank'):
        new_rank = int(rank.text) + 1
        # 直接修改字段
        rank.text = str(new_rank)
        # 添加或修改属性
        rank.set('updated', 'yes')
        print("rank:{}".format(rank.text))

    tree.write('output.xml')


if __name__ == '__main__':
    main()
