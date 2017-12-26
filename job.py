import os
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QAction,QApplication,QFileDialog
from pprint import pprint
import csv
from collections import Counter
import matplotlib
import  numpy as np
from bs4 import BeautifulSoup
import requests
import matplotlib.pyplot as plt
import jieba
from wordcloud import WordCloud
from scipy import interpolate
import webbrowser
#指定默认字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['font.family']='sans-serif'
#解决负号'-'显示为方块的问题
matplotlib.rcParams['axes.unicode_minus'] = False

class Ui_jobui(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)
    def setupUi(self, jobui):
        jobui.setObjectName("jobui")
        jobui.resize(640, 500)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("images/logo.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        jobui.setWindowIcon(icon)
        jobui.setToolTipDuration(-1)
        self.label = QtWidgets.QLabel(jobui)
        self.label.setGeometry(QtCore.QRect(60, 110, 91, 16))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(jobui)
        self.label_2.setGeometry(QtCore.QRect(130, 10, 381, 71))
        font = QtGui.QFont()
        font.setFamily("Adobe 黑体 Std R")
        font.setPointSize(20)
        self.label_2.setFont(font)
        self.label_2.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(jobui)
        self.label_3.setGeometry(QtCore.QRect(160, 220, 351, 201))
        font = QtGui.QFont()
        font.setFamily("黑体")
        font.setPointSize(11)
        self.label_3.setFont(font)
        self.label_3.setText("")
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.lineEdit = QtWidgets.QLineEdit(jobui)
        self.lineEdit.setGeometry(QtCore.QRect(60, 130, 371, 41))
        font = QtGui.QFont()
        font.setFamily("Adobe 宋体 Std L")
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.lineEdit.setFont(font)
        self.lineEdit.setText("")
        self.lineEdit.setObjectName("lineEdit")
        self.pushButton = QtWidgets.QPushButton(jobui)
        self.pushButton.setGeometry(QtCore.QRect(460, 130, 121, 41))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.key)
        self.pushButton_2 = QtWidgets.QPushButton(jobui)
        self.pushButton_2.setGeometry(QtCore.QRect(270, 440, 0, 0))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.clicked.connect(self.report)
        self.retranslateUi(jobui)
        QtCore.QMetaObject.connectSlotsByName(jobui)

    def retranslateUi(self, jobui):
        _translate = QtCore.QCoreApplication.translate
        jobui.setWindowTitle(_translate("jobui", "招聘系统数据分析平台"))
        self.label.setText(_translate("jobui", "请输入关键词："))
        self.label_2.setText(_translate("jobui", "招聘系统数据分析平台 V1.0"))
        self.pushButton.setText(_translate("jobui", "立 即 分 析"))
        self.pushButton_2.setText(_translate("jobui", "点击查看报告"))

    def key(self, jobui):
        self.keywd=self.lineEdit.text()
        spider.run()
        self.pushButton_2.setGeometry(QtCore.QRect(270, 440, 110, 40))
        app.processEvents()

    def report(self,jobui):
        webbrowser.open_new("index.html")

class JobSpider:

    def __init__(self):
        self.company = []
        self.text = ""
        self.headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36'
                          '(KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
        }

    def job_spider(self):
        """ 爬虫入口
        """
        url = "http://search.51job.com/jobsearch/search_result.php?fromJs=1&jobarea=&keyword="+ui.keywd+"&keywordtype=2&lang=c&stype=2&postchannel=0000&fromType=1&confirmdate=9"
        urls = [url.format(p) for p in range(1, 15)]
        for url in urls:
            r = requests.get(url, headers=self.headers).content.decode('gbk')
            bs = BeautifulSoup(r, 'lxml').find(
                "div", class_="dw_table").find_all("div", class_="el")
            for b in bs:
                try:
                    href, post = b.find('a')['href'], b.find('a')['title']
                    locate = b.find('span', class_='t3').text
                    salary = b.find('span', class_='t4').text
                    d = {
                        'href': href,
                        'post': post,
                        'locate': locate,
                        'salary': salary
                    }
                    self.company.append(d)
                except Exception:
                    pass

    def post_require(self):
        """ 爬取职位描述
        """
        for c in self.company:
            try:
                r = requests.get(c.get('href'), headers=self.headers).content.decode('gbk')
            except requests.RequestException as e:
                continue
            if (BeautifulSoup(r, 'lxml').find('div', class_="bmsg job_msg inbox")!=None):
                bs = BeautifulSoup(r, 'lxml').find('div', class_="bmsg job_msg inbox").text
            else:
                continue
            s = bs.replace("举报", "").replace("分享", "").replace("\t", "").replace("addjob", "").strip()
            self.text += s
        # print(self.text)
        with open(os.path.join("data", "post_require.txt"),"w+", encoding="utf-8" ,newline='') as f:
            f.write(self.text)

    @staticmethod
    def post_desc_counter():
        """ 职位描述统计
        """
        # import thulac
        post = open(os.path.join("data", "post_require.txt"),
                    "r", encoding="utf-8").read()
        # 使用 thulac 分词
        # thu = thulac.thulac(seg_only=True)
        # thu.cut(post, text=True)

        # 使用 jieba 分词
        file_path = os.path.join("data", "user_dict.txt")
        jieba.load_userdict(file_path)
        r = '[’!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~]+。：；、【】等的和1234567890及中并，有对能与各可 \n（）'
        seg_list = jieba.cut(post, cut_all=False)
        counter = dict()
        for seg in seg_list:
            counter[seg] = counter.get(seg, 1) + 1
        for d in r:
            if d in counter:
                del counter[d]
        counter_sort = sorted(
            counter.items(), key=lambda value: value[1], reverse=True)
        #pprint(counter_sort)
        with open(os.path.join("data", "post_pre_desc_counter.csv"),"w+", encoding="utf-8",newline='') as f:
            f_csv = csv.writer(f)
            f_csv.writerows(counter_sort)

    def post_counter(self):
        """ 职位统计
        """
        lst = [c.get('post') for c in self.company]
        counter = Counter(lst)
        counter_most = counter.most_common()
        #pprint(counter_most)
        with open(os.path.join("data", "post_pre_counter.csv"),
                  "w+", encoding="utf-8",newline='') as f:
            f_csv = csv.writer(f)
            f_csv.writerows(counter_most)

    def post_salary_locate(self):
        """ 招聘大概信息，职位，薪酬以及工作地点
        """
        lst = []
        for c in self.company:
            lst.append((c.get('salary'), c.get('post'), c.get('locate')))
        #pprint(lst)

        file_path = os.path.join("data", "post_salary_locate.csv")
        with open(file_path, "w+", encoding="utf-8",newline='') as f:
            f_csv = csv.writer(f)
            f_csv.writerows(lst)

    @staticmethod
    def post_salary():
        """ 薪酬统一处理
        """
        mouth = []
        year = []
        thousand = []
        with open(os.path.join("data", "post_salary_locate.csv"),
                  "r", encoding="utf-8") as f:
            f_csv = csv.reader(f)
            for row in f_csv:
                if "万/月" in row[0]:
                    mouth.append((row[0][:-3], row[2], row[1]))
                elif "万/年" in row[0]:
                    year.append((row[0][:-3], row[2], row[1]))
                elif "千/月" in row[0]:
                    thousand.append((row[0][:-3], row[2], row[1]))
        # pprint(mouth)

        calc = []
        for m in mouth:
            s = m[0].split("-")
            calc.append(
                (round(
                    (float(s[1]) - float(s[0])) * 0.4 + float(s[0]), 1),
                 m[1], m[2]))
        for y in year:
            s = y[0].split("-")
            calc.append(
                (round(
                    ((float(s[1]) - float(s[0])) * 0.4 + float(s[0])) / 12, 1),
                 y[1], y[2]))
        for t in thousand:
            s = t[0].split("-")
            calc.append(
                (round(
                    ((float(s[1]) - float(s[0])) * 0.4 + float(s[0])) / 10, 1),
                 t[1], t[2]))
        #pprint(calc)
        with open(os.path.join("data", "post_salary.csv"),
                  "w+", encoding="utf-8",newline='') as f:
            f_csv = csv.writer(f)
            f_csv.writerows(calc)

    @staticmethod
    def post_salary_localcounter():
        """ 地点统计
        """
        with open(os.path.join("data", "post_salary_locate.csv"),
                  "r", encoding="utf-8") as f:
            f_csv = csv.reader(f)
            lst=[]
            for row in f_csv:
                row[2]=row[2].split("-")[0]
                lst.append(row[2])
        counter = Counter(lst).most_common()
        x=[0]*len(counter)
        y=[0]*len(counter)
        i=0
        counter.sort()
        for c in counter:
            x[i] = c[0]
            y[i] = c[1]
            i=i+1
        plt.xlabel('\n地点')
        plt.ylabel('岗位数')
        # 添加标题
        plt.title('【工作地点统计】')
        plt.figure(figsize=(15, 6))
        plt.bar(np.arange(0,len(counter),1), y , color='rgb', tick_label= x)
        #plt.show()
        plt.savefig(os.path.join("images", "locate.png"))
        with open(os.path.join("data", "post_local.csv"),
                  "w+", encoding="utf-8",newline='') as f:
            f_csv = csv.writer(f)
            f_csv.writerows(counter)
    @staticmethod
    def post_salary_counter():
        """ 薪酬统计
        """
        with open(os.path.join("data", "post_salary.csv"),
                  "r", encoding="utf-8") as f:
            f_csv = csv.reader(f)
            lst = [row[0] for row in f_csv]
        counter = Counter(lst).most_common()
        #pprint(counter)
        x=[0]*len(counter)
        y=[0]*len(counter)
        i=0
        counter.sort()
        for c in counter:
            x[i] = float(c[0])*10000
            y[i] = c[1]
            i=i+1
        func = interpolate.interp1d(x, y, kind='cubic')
        x=np.arange(x[0]+1, x[-1]-1, 10)
        y = func(x)
        plt.xlabel('月薪')
        plt.ylabel('岗位数')
        # 添加标题
        plt.title('【薪资统计】')
        plt.figure(figsize=(15, 6))
        plt.plot(x,y, color="red", linewidth=2.0)
        plt.savefig(os.path.join("images", "money.png"))
        with open(os.path.join("data", "post_salary_counter1.csv"),
                  "w+", encoding="utf-8",newline='') as f:
            f_csv = csv.writer(f)
            f_csv.writerows(counter)

    @staticmethod
    def world_cloud():
        """ 生成词云
        """
        counter = {}
        with open(os.path.join("data", "post_pre_desc_counter.csv"),
                  "r", encoding="utf-8") as f:
            f_csv = csv.reader(f)
            for row in f_csv:
                counter[row[0]] = counter.get(row[0], int(row[1]))
            #pprint(counter)
        file_path = os.path.join("font", "msyh.ttf")
        wc = WordCloud(font_path=file_path,
                       max_words=500,
                       height=1000,
                       width=2000).generate_from_frequencies(counter)
        plt.imshow(wc)
        plt.axis('off')
        #plt.show()
        wc.to_file(os.path.join("images", "wc.jpg"))

    @staticmethod
    def insert_into_db():
        """ 插入数据到数据库
            create table jobpost(
                j_salary float(3, 1),
                j_locate text,
                j_post text
            );
        """
        import pymysql
        conn = pymysql.connect(host="localhost",
                               port=3306,
                               user="root",
                               passwd="0303",
                               db="chenx",
                               charset="utf8")
        cur = conn.cursor()
        with open(os.path.join("data", "post_salary.csv"),
                  "r", encoding="utf-8") as f:
            f_csv = csv.reader(f)
            sql = "insert into jobpost(j_salary, j_locate, j_post) values(%s, %s, %s)"
            for row in f_csv:
                value = (row[0], row[1], row[2])
                try:
                    cur.execute(sql, value)
                    conn.commit()
                except Exception as e:
                    print(e)
        cur.close()
    def run(self):
        ui.label_3.setText("正在搜索职位......请稍等！")
        app.processEvents()
        spider.job_spider()
        ui.label_3.setText("职位基本信息搜索完毕！")
        app.processEvents()
        print("职位基本信息搜索完毕！正在搜索详细信息......请稍等！")
        # 按需启动
        spider.post_require()
        ui.label_3.setText("职位基本信息搜索完毕！\n职位详情爬取完毕！")
        app.processEvents()
        print("职位详情爬取完毕！")
        spider.post_counter()
        ui.label_3.setText("职位基本信息搜索完毕！\n职位详情爬取完毕！\n职位预统计完毕！")
        app.processEvents()
        print("职位预统计完毕！")
        spider.post_salary_locate()
        ui.label_3.setText("职位基本信息搜索完毕！\n职位详情爬取完毕！\n职位预统计完毕！\n职位分职位薪资地点统计完毕！")
        app.processEvents()
        print("职位分职位薪资地点统计完毕！")
        spider.post_salary()
        ui.label_3.setText("职位基本信息搜索完毕！\n职位详情爬取完毕！\n职位预统计完毕！\n职位分职位薪资地点统计完毕！\n薪酬统一处理完毕！")
        app.processEvents()
        print("薪酬统一处理完毕！")
        spider.post_salary_counter()
        ui.label_3.setText("职位基本信息搜索完毕！\n职位详情爬取完毕！\n职位预统计完毕！\n职位分职位薪资地点统计完毕！\n薪酬统一处理完毕！\n薪酬统计展示完毕！")
        app.processEvents()
        print("薪酬统计展示完毕！")
        spider.post_salary_localcounter()
        ui.label_3.setText("职位基本信息搜索完毕！\n职位详情爬取完毕！\n职位预统计完毕！\n职位分职位薪资地点统计完毕！\n薪酬统一处理完毕！\n薪酬统计展示完毕！\n工作地点统计完毕！")
        app.processEvents()
        print("工作地点统计完毕！")
        #spider.post_desc_counter()
        ui.label_3.setText(
            "职位基本信息搜索完毕！\n职位详情爬取完毕！\n职位预统计完毕！\n职位分职位薪资地点统计完毕！\n薪酬统一处理完毕！\n薪酬统计展示完毕！\n工作地点统计完毕！\n词云数据预处理完毕！")
        app.processEvents()
        print("词云数据预处理完毕！")
        #spider.world_cloud()
        ui.label_3.setText(
            "职位基本信息搜索完毕！\n职位详情爬取完毕！\n职位预统计完毕！\n职位分职位薪资地点统计完毕！\n薪酬统一处理完毕！\n薪酬统计展示完毕！\n工作地点统计完毕！\n词云数据预处理完毕！\n词云生成完毕！")
        app.processEvents()
        print("词云生成完毕！")
        # spider.insert_into_db()
        # print("数据导入数据库完毕！")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = Ui_jobui()
    ui.show()
    spider = JobSpider()
    sys.exit(app.exec_())