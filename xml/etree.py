import xml.etree.ElementTree as ET


# https://docs.python.org/3/library/xml.etree.elementtree.html
# https://zhuanlan.zhihu.com/p/502584681


def main():
    tree = ET.parse('./country_data.xml')

    # 获取根元素
    root = tree.getroot()
    print("{} {}".format(type(root), root))

    for child in root:
        print("tag:{}, attr:{}, text:{}".format(child.tag, child.attrib, child.text))
        for tg in child.iter():
            print(tg.text)

    # 获取指定元素
    print("root[0][1]: tag={},text={}".format(root[0][1].tag, root[0][1].text))

    # 遍历root下所有子元素的 neighbor 标签的节点
    for neighbor in root.iter('neighbor'):
        print("neighbor: {}".format(neighbor.attrib))

    # 查找root下所有的 country 元素, 并且获取country的属性和子元素rank的text内容。
    for country in root.findall('country'):
        name = country.get('name')
        rank = country.find('rank').text
        print("country name: {}, rank: {}".format(name, rank))

    # 更新xml
    for rank in root.iter('rank'):
        new_rank = int(rank.text) + 1
        # 直接修改字段
        rank.text = str(new_rank)
        # 添加或修改属性
        rank.set('updated', 'yes')

    tree.write('output.xml')


if __name__ == '__main__':
    main()
