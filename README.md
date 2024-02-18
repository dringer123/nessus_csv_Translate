# nessus_csv_Translate
Nessus漏扫结果翻译：.csv在线翻译+本地翻译工具（全程gpt4.0完成）
优先调用本地库的翻译结果，如果没查到就会调用阿里云在线翻译（需配置自己的api key等信息，没填就只有原文），在线翻译的结果存储至translations.db方便下次使用或修改

## 环境
pip3 install alibabacloud_alimt20181012
（这主要是阿里云翻译的依赖）

## 用法
translations.db中存储的一对一翻译原文和结果，加强了准确性，方便后续修改（翻译库修改后再次执行翻译即可）
脚本翻译处理逻辑跟github其他人写的不一样，这个翻译库在后续使用中可以新增没有的数据、自定义更新等，高可维护

1.修改你自己的阿里翻译api key，(申请阿里云翻译api key教程:https://www.zhihu.com/question/622754555/answer/3217852896)
<img width="804" alt="image" src="https://github.com/dringer123/nessus_csv_Translate/assets/47192426/6a643384-65bc-40c0-ac56-45c77f726630">

2.将需要翻译的文件复制到当前目录，改名为input.csv，运行以下命令将自动生成翻译后的output.csv

python3 nessus_csv_Translate.py

<img width="441" alt="image" src="https://github.com/dringer123/nessus_csv_Translate/assets/47192426/cdb7a65a-4da6-4312-ad69-786cebe61ecd">


## translations.db
有精力的小伙伴可以分享自己的translations.db：3090550370@qq.com，作者确认后将会更新在此库




## 错误处理
UnicodeDecodeError: 'utf-8' codec can't decode bytes in position

出现以上错误是因为Plugin Output列的数据存在不认识的字符，建议删掉这一列再翻译
