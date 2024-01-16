# -*- coding: utf-8 -*-
import os
import csv
import sqlite3
from datetime import datetime
from alibabacloud_alimt20181012.client import Client as alimt20181012Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_alimt20181012 import models as alimt_20181012_models

# 创建数据库连接和表
db_connection = sqlite3.connect('translations.db')
db_cursor = db_connection.cursor()
db_cursor.execute('''
CREATE TABLE IF NOT EXISTS translations (
    english TEXT PRIMARY KEY,
    chinese TEXT,
    last_updated DATE
)
''')

# 创建阿里云翻译客户端
def create_alimt_client(access_key_id: str, access_key_secret: str) -> alimt20181012Client:
    config = open_api_models.Config(
        access_key_id=access_key_id,
        access_key_secret=access_key_secret
    )
    config.endpoint = 'mt.cn-hangzhou.aliyuncs.com'
    return alimt20181012Client(config)

# 初始化统计变量
total_translations = 0
saved_to_db = 0

# 风险等级映射
risk_mapping = {
    'Critical': '严重',
    'High': '高危',
    'Medium': '中危',
    'Low': '低危',
    'None': '信息'
}

# 表头翻译映射
header_mapping = {
    'Host': '主机',
    'Protocol': '协议',
    'Port': '端口',
    'Name': '漏洞名称',
    'Synopsis': '描述',
    'Description': '漏洞描述',
    'Solution': '修复建议',
    'See Also': '参考',
    'Risk': '风险等级'
}

# 检测阿里云翻译API key是否正常
def check_alimt_api_key(client: alimt20181012Client) -> bool:
    try:
        # 尝试调用API的一个简单请求来检测key是否有效
        test_request = alimt_20181012_models.TranslateGeneralRequest(
            format_type='text',
            source_language='en',
            target_language='zh',
            source_text='test',
            scene='general'
        )
        client.translate_general(test_request)
        return True
    except Exception as e:
        #print(f"Error checking API key: {e}")
        return False

# 询问用户是否启用伪翻译功能
def prompt_fake_translation() -> bool:
    response = input("API key 测试无效或未设置，要仅启用本地翻译吗（本地未查到的数据将保持不变）? (yes): ")
    return response.strip().lower() == 'yes'

# 从数据库获取翻译或调用阿里云API，或执行伪翻译
def get_translation(client: alimt20181012Client, text: str, use_fake_translation: bool) -> str:
    global saved_to_db
    db_cursor.execute('SELECT chinese FROM translations WHERE english=?', (text,))
    result = db_cursor.fetchone()
    if result:
        return result[0]
    
    if use_fake_translation:
        return text
    
    translate_request = alimt_20181012_models.TranslateGeneralRequest(
        format_type='text',
        source_language='en',
        target_language='zh',
        source_text=text.replace("\n", " "),
        scene='general'
    )
    try:
        response = client.translate_general(translate_request)
        translation = response.body.data.translated
        db_cursor.execute('INSERT INTO translations (english, chinese, last_updated) VALUES (?, ?, ?)',
                          (text, translation, datetime.now().date()))
        db_connection.commit()
        saved_to_db += 1
        return translation
    except Exception as e:
        print(e)
        return text

# 尝试检测API key
alimt_client = create_alimt_client('LTAI5.......', '2AHhuZWhqnQ.......')
api_key_valid = check_alimt_api_key(alimt_client)

# 如果API key无效，询问用户是否启用伪翻译
use_fake_translation = False
if not api_key_valid:
    use_fake_translation = prompt_fake_translation()

# 读取CSV文件
with open('input.csv', 'r', encoding='utf-8') as infile:
    reader = csv.DictReader(infile)
    data = list(reader)

# 翻译表头
translated_headers = [header_mapping.get(col, col) for col in reader.fieldnames]

# 翻译数据和显示进度
data_length = len(data)
for index, row in enumerate(data):
    # 翻译风险等级
    if 'Risk' in row and row['Risk'] in risk_mapping:
        row['Risk'] = risk_mapping[row['Risk']]
    
    # 翻译指定的列
    for column in ['Name', 'Synopsis', 'Description', 'Solution']:
        if column in row and row[column] and not row[column].isspace():
            original_text = row[column]
            translated_text = get_translation(alimt_client, original_text, use_fake_translation)
            if original_text != translated_text:
                total_translations += 1
            row[column] = translated_text
    # 显示进度
    print(f"Progress: {index+1}/{data_length} rows processed.", end='\r')

# 根据风险等级排序
risk_order = {'严重': 0, '高危': 1, '中危': 2, '低危': 3, '信息': 4}
data.sort(key=lambda x: risk_order.get(x['Risk'], 5))

# 写入新的CSV文件
with open('output.csv', 'w', encoding='utf-8', newline='') as outfile:
    writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)  # 使用原始列名
    writer.writeheader()
    writer.writerows(data)

# 显示统计信息
print(f"\n总行数: {data_length}")
print(f"共处理单元格: {total_translations}")
print(f"通过云翻译并保存的新数据: {saved_to_db}")

# 关闭数据库连接
db_connection.close()
