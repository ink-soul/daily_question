import asyncio
import datetime
from distutils.command.config import config
import toml
import json
import re
import time
import aiohttp
from bilibili_api import user



def get_config(configFilePath):
    with open(configFilePath,'r') as cfg:
        content = cfg.read()
    config = toml.loads(content)
    cfg.close()
    return config
    
def configCheck(userId,updateMode):
    if len(str(userId)) == 1:
        print("请检查配置文件，确保UID已经正确配置\n")
        exit(1)
    if type(updateMode) !=bool:
        print("运行模式配置错误，请检查配置文件")
        exit(1)
    if  updateMode == True :
        print("uid已正确配置，当前为更新模式，如非第一次运行，请检查配置文件")
        return user.User(uid=int(userId))
    if updateMode == False :
        print("uid已正确配置，当前为初始化模式，将获取所有历史每日一题，如不满足需求，请检查配置文件")
        return user.User(uid=userId)
    
    
        

async def fetch(session: aiohttp.ClientSession, url: str, path: str):
    try:
        async with session.get(url) as resp:
            with open(path, 'wb') as fd:
                while 1:
                    chunk = await resp.content.read(1024)  # 每次获取1024字节
                    if not chunk:
                        break
                    fd.write(chunk)
        # print("downloaded " + url)
    except:
        print("failed " + url)


def copyKeys(src, keys):
    res = {}
    for k in keys:
        if k in src:
            res[k] = src[k]
    return res


def getItem(input):
    if "item" in input:
        return getItem(input["item"])
    if "videos" in input:
        return getVideoItem(input)
    else:
        return getNormal(input)


def timestampCompare(updateMode):
    
    today = datetime.datetime.now()
    
    # 2022-7-12 00:00:00 的时间戳
    firstTimestamp = time.mktime(time.strptime('2022-07-12 00:00:00','%Y-%m-%d %H:%M:%S'))
    
    yesterdayTime = (today-datetime.timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')
    yesterdayTimestamp = time.mktime(time.strptime(yesterdayTime, '%Y-%m-%d %H:%M:%S'))
    if  updateMode == False:
        
        return firstTimestamp  #初次运行获取所有大于此时间戳的动态
    else :

        return yesterdayTimestamp #后续更新获取大于昨日时间戳的动态



def getNormal(input):
    res = copyKeys(input, ['description', 'pictures', 'content'])
    if "pictures" in res:
        res["pictures"] = [pic["img_src"] for pic in res["pictures"]]
    return res


def getVideoItem(input):
    res = copyKeys(input, ['title', 'desc', 'dynamic', 'short_link', 'stat', 'tname'])
    res["av"] = input["aid"]
    res["pictures"] = [input["pic"]]
    return res


def is_in(full_str, sub_str):
    if re.findall(sub_str, full_str):
        return True
    else:
        return False


def writeTomd(f,dynamictime,contentstr):

    # 移除【王道计算机考研】 
    contentstr=re.sub("\u3010\u738b\u9053\u8ba1\u7b97\u673a\u8003\u7814\u3011"," ",contentstr)
    # 移除发起投票文本
    contentstr=re.sub("\u6211\u53d1\u8d77\u4e86\u4e00\u4e2a\u6295\u7968.*$"," ",contentstr)
    # 移除第二天公布答案文本
    contentstr=re.sub("\u6ce8\u610f\uff1a\u7b2c\u4e8c\u5929\u53d1\u5e03\u9898\u76ee\u540c\u4e00\u65f6\u95f4\u8bc4\u8bba\u533a\u516c\u5e03\u7b54\u6848\u54e6\uff01\u0020"," ",contentstr)
    # 补充换行符，使文本可读性更高
    contentstr = re.sub("\n",str('\n \n'),contentstr,count=0,flags=re.DOTALL)

    f.write("\n该题更新于：" + dynamictime + "\n\n")
    f.write(contentstr)
    f.write("\n\n" + "---------" + "\n")
    print("该题更新于：" + dynamictime + "\n\n")
    print(contentstr)
    print("\n\n" + "---------" + "\n")



def cardToObj(input):
    res = {
        "dynamic_id": input["desc"]["dynamic_id"],
        "timestamp": input["desc"]["timestamp"],
        "type": input["desc"]["type"],
        "item": getItem(input["card"])
    }
    if "origin" in input["card"]:
        originObj = json.loads(input["card"]["origin"])
        res["origin"] = getItem(originObj)
        if "user" in originObj and "name" in originObj["user"]:
            res["origin_user"] = originObj["user"]["name"]
    return res


async def getDailyQuestion(uid,updateMode,resultFilePath):
    if updateMode == False:
        print("\n--------------------初始化模式-------------------")
        print("-----获取所有自2022-07-12 00:00:00以来的每日一题-----\n")
        print("-----------------------------------------------------\n")
    elif updateMode == True:
        print("\n-------------更新模式---------")
        print("-----获取前一天的每日一题-----\n")
        print("-----------------------------\n")
    with open(resultFilePath, "a+", encoding="UTF-8") as f:
        offset = 0
        count = 0
        while True:
            # if offset != 0:
                # f.write(",")
            res = await uid.get_dynamics(offset)
            if res["has_more"] != 1:
                break
            offset = res["next_offset"]
            for card in res["cards"]:
                # f.write(",\n" if count > 0 else "[\n")
                cardObj = cardToObj(card)
                flag = False
                timestamp = cardObj["timestamp"]
                timeLocal = time.localtime(timestamp)
                dynamictime = time.strftime("%Y-%m-%d %H:%M:%S",timeLocal)
                if (float(timestamp) >= timestampCompare(updateMode)):
                    #在此处筛选type=4，content中有每日一题字符串的动态
                    if str(cardObj["type"]) == str(4):
                        contentstr = str(cardObj["item"]['content'])
                        noticestr = str("每日一题")
                        if is_in(contentstr,noticestr) == False:
                            
                            await asyncio.sleep(4)
                        else:
                            
                            writeTomd(f,dynamictime,contentstr)
                            
                            count += 1
                            f.flush()
                            await asyncio.sleep(4)
                      
                    else:
                        await asyncio.sleep(4)
                        print("type dismarch")
                        continue
                else:
                    await asyncio.sleep(4)
                    flag = True
                    print("out of time")
                    break
            if flag == True:
                break        
    
    
            
                   
    print()
    print("--------已完成！---------")


if __name__ == '__main__':

    configFilePath = "config.toml"
    

    config = get_config(configFilePath)
    userId = config['UID']
    updateMode = config['UPDATEMODE']
    resultFilePath = config['RESULTFILEPATH']
    uid = configCheck(userId,updateMode)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(getDailyQuestion(uid,updateMode,resultFilePath))
    

