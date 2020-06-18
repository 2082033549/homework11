from urllib import request
import re
import chardet
from bs4 import BeautifulSoup

import sys

print('-----Packages and Version-----')
print('Python '+sys.version)
print('BeautifulSoup4 '+'4.9.1')
print('chardet '+ chardet.version.__version__)
#判断字符串是否为数值型
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False

# 51job搜索结果页面
url1 ='https://search.51job.com/list/010000,000000,0000,00,9,99,Python%25E5%25BC%2580%25E5%258F%2591%25E5%25B7%25A5%25E7%25A8%258B%25E5%25B8%2588,2,1.html?lang=c&stype=&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&providesalary=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=&dibiaoid=0&address=&line=&specialarea=00&from=&welfare='
r=request.Request(url1)
res = request.urlopen(r)
html=res.read()
res.close()
code = chardet.detect(html)['encoding']
html=html.decode(code)
soup = BeautifulSoup(html, 'html.parser')
##获取职位总页数
the_total_page = soup.select('.p_in .td')[0].string.strip()
the_total_page = int(re.sub(r"\D", "", the_total_page))

##获取职位总数
the_total_job = soup.select('.rt ')[0].string.strip()
the_total_job = int(re.sub(r"\D", "", the_total_job))


total_salary_min = 0.0
total_salary_max = 0.0
mean_salary_min = 0.0
mean_salary_max = 0.0


#爬取所有搜索结果页面
for index in range(the_total_page+1):
    #index = i + 1
    url = 'https://search.51job.com/list/010000,000000,0000,00,9,99,Python%25E5%25BC%2580%25E5%258F%2' \
          '591%25E5%25B7%25A5%25E7%25A8%258B%25E5%25B8%2588,2,{}.html?lang=c&stype=&postchannel=0000&workyea' \
          'r=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&providesalary=99&lonlat=0%2C0&radius=-1&ord_field=' \
          '0&confirmdate=9&fromType=&dibiaoid=0&address=&line=&specialarea=00&from=&welfare='.format(index)
    r=request.Request(url)
    res = request.urlopen(r)
    #读取网页编码格式
    html=res.read()
    res.close()
    html=html.decode(code)
    scale = 1.0

    #你需要留下的用（.*?）,它的前后一定要有一个原来的存在内容，被你删掉的，用.*?表示
    reg = re.compile('<div class="el">.*?<a target="_blank" title="(.*?)".*?<a target="_blank" title="(.*?)".*?<span class="t3">(.*?)</span>.*?<span class="t4">(.*?)</span>.*?<span class="t5">(.*?)</span>',re.S)
    # 得到结果，是一个列表
    data = re.findall(reg,html)

    with open('51job.txt', 'a', encoding='utf-8') as file:
        # 读取的每一个 each 都是 一个tuple
        for each in data:
            row =list(each)
            salary = str(each[3])
            #统一薪资单位
            if(salary[-3:] == "千/月"):
                scale = 0.1
            elif(salary[-3:] == "万/年"):
                scale = 1/12
            else:
                scale = 1
            salary = salary[0:-3]
            #根据'-'分割薪资下限和上限
            b = salary.find("-")
            min_salary = salary[0:b]
            max_salary = salary[b+1:]
            # 统计总下限和总上限
            if(is_number(min_salary) and is_number(max_salary)):
                c = (float(min_salary)*scale)
                d = (float(max_salary)*scale)
                total_salary_min = total_salary_min + c
                total_salary_max = total_salary_max + d
            else:
                the_total_job = the_total_job - 1
                continue
            row[3] = str('%.2f' % c) + "-" + str('%.2f' % d) + "万/月"
            for i in row:
                file.write(i + '  ')
            file.write('\n')
#统计薪资的上下限均值
mean_salary_min = total_salary_min/the_total_job
mean_salary_max = total_salary_max/the_total_job

print("Python工程师职位平均薪资为:"+str('%.2f'%mean_salary_min ) + "-" +str('%.2f'%mean_salary_max)+"万/月")