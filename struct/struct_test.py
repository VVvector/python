# -*- coding:utf-8 -*-
from collections import OrderedDict
import struct
import json

'''
二进制文件的写入和读取
'''


def read_file(file_path):
    person = []
    file = open(file_path, "rb")
    name = file.read(8)
    name = struct.unpack('<8s', name)[0]
    male = file.read(1)
    male = struct.unpack('<b', male)[0]
    age = file.read(2)
    age = struct.unpack('<H', age)[0]
    height = file.read(4)
    height = int.from_bytes(height, byteorder='little')
    weight = file.read(4)
    weight = struct.unpack('<f', weight)[0]
    feature_size = file.read(4)
    feature_size = int.from_bytes(feature_size, byteorder='little')
    features = []
    for i in range(feature_size // 4):
        feature_value = file.read(4)
        feature_value = struct.unpack('<f', feature_value)[0]
        features.append(feature_value)
    person.append({
        "name": name,
        "male": male,
        "age": age,
        "height": height,
        "weight": weight,
        "feature_size": feature_size,
        "features": features,
    })
    return person


def write_file(file_path, person, features):
    file = open(file_path, "wb")
    # file.seek(0, 2)
    # 把字符串的地方转为字节类型,还要先转成utf-8的编码(否则报错string argument without an encoding)
    name = struct.pack('<8s', person['name'].encode('utf-8'))
    file.write(name)
    male = struct.pack('<?', person['male'])
    file.write(male)
    age = struct.pack('<H', person['age'])
    file.write(age)
    height = struct.pack('<I', person['height'])
    file.write(height)
    weight = struct.pack('<f', person['weight'])
    file.write(weight)
    features_size = struct.pack('<I', 5 * 4)
    file.write(features_size)
    for key, value in features.items():
        feature_value = struct.pack('<f', value)
        file.write(feature_value)
    file.close()


def parse_person_bin(person_bin, person_json):
    with open(person_json, "r") as f:
        # Starting with Python 3.7, the regular dict became order preserving, so it is no longer necessary
        # to specify collections.OrderedDict for JSON generation and parsing.
        person_info_format_dict = json.load(f)
        print("person info format: {}".format(person_info_format_dict))

    format_byte_order = person_info_format_dict["byte_order"]
    person_info_format = "{}".format(format_byte_order)
    person_info_keys = []
    for k, v in person_info_format_dict["person_info"].items():
        if k == "feature":
            break
        if v is None:
            continue
        person_info_format = "{}{}".format(person_info_format, v)
        person_info_keys.append(k)
    person_info_format_size = struct.calcsize(person_info_format)
    print("person_info_format: {}, size: {}".format(person_info_format, person_info_format_size))

    # just for test
    person_info_format_dict["person_info"]["test"] = "8s"
    print("person info: {}".format(person_info_format_dict["person_info"]))

    person_feature_format = "{}".format(format_byte_order)
    person_feature_keys = []
    for k, v in person_info_format_dict["person_info"]["feature"].items():
        person_feature_format = "{}{}".format(person_feature_format, v)
        person_feature_keys.append(k)
    person_feature_format_size = struct.calcsize(person_feature_format)
    print("person_feature_format: {}, size: {}".format(person_feature_format, person_feature_format_size))

    with open(person_bin, "rb") as f:
        f.seek(0, 0)
        person_info_value_tuple = struct.unpack(person_info_format, f.read(person_info_format_size))
        person_info_values = list(person_info_value_tuple)
        print("person info: {}".format(person_info_values))
        person_info_dict = dict(zip(person_info_keys, person_info_values))
        print("person info dict: {}".format(person_info_dict))

        f.seek(person_info_format_size, 0)
        person_feature_value_tuple = struct.unpack(person_feature_format, f.read(person_feature_format_size))
        person_feature_values = list(person_feature_value_tuple)
        print("person feature info: {}".format(person_feature_values))
        person_feature_dict = dict(zip(person_feature_keys, person_feature_values))
        print("person feature dict: {}".format(person_feature_dict))


def main():
    person = OrderedDict()
    person.update({'name': 'Jame'})
    person.update({'male': True})
    person.update({'age': 25})
    person.update({'height': 178})
    person.update({'weight': 64.0})
    features = {'Strength': 54.0,  # 力量
                'Intelligence': 78.0,  # 智力
                'Constitution': 32.0,  # 体力
                'Dexterity': 78.0,  # 敏捷
                'Mentality': 53.0  # 精神
                }
    file_path = "./person_info.bin"
    write_file(file_path, person, features)
    person_info = read_file(file_path)
    print(person_info)

    parse_person_bin(file_path, "./person.json")


if __name__ == '__main__':
    main()
