import multiprocessing
import numpy as np
import threading
from multiprocessing.dummy import Process
import os,time
from datetime import datetime, timedelta
import sys
from tkinter import CURRENT
import datetime
from datetime import date, datetime, timedelta
# import pandas as pd
# from fpdf import FPDF
import matplotlib.pyplot as plt
import subprocess
import math
import time
import datetime 
 # import login
import pymysql
from subprocess import Popen, PIPE
import logging
import traceback
import shutil
from pypylon import genicam
from pypylon import pylon
import cv2
#DB credentials
db_user = 'root'
db_pass = 'insightzz123'
db_host = 'localhost'
db_name = 'piston_arrow_inspection_db'

from PyQt5.QtWidgets import * 
from PyQt5 import QtCore, QtGui ,QtWidgets, uic
from PyQt5.QtGui import * 
from PyQt5.QtCore import * 

#from mainwindow import Ui_MainWindow
# from login import Login
from login11 import Ui_Login
# from details import Ui_details_window
# from reportParam import Ui_ReportConfig
# from reportparameter import Ui_reportparameter_window
from download_popup import Ui_download_window
from InspectTypeWindow import Ui_Inspection_type_Window
# from version_window import Ui_VersionWindow

logger = None
log_format=logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger=logging.getLogger("spring_UI")
logger.setLevel(logging.DEBUG)
logger_fh=logging.FileHandler("piston_arrow_UI.log",mode='a')
logger_fh.setFormatter(log_format)
logger_fh.setLevel(logging.DEBUG)
logger.addHandler(logger_fh)

UI_CODE_PATH = os.getcwd()+"/"
PDF_TEMP_PATH = UI_CODE_PATH

DEFAULT_PDF_PATH = f"/home/{os.getlogin()}/Desktop/"

NO_IMAGE_PATH = UI_CODE_PATH+"logo/No_image_found.png"
DOWNLOAD_PATH = os.path.join(os.getcwd(),"Download_Data")
Download_data_is=DOWNLOAD_PATH.replace("\\","/")
DOWNLOAD_PATH=Download_data_is
if not os.path.exists(DOWNLOAD_PATH):
    os.mkdir(DOWNLOAD_PATH)
ui_code = "C:/Insightzz/Arrow_model_and_code_23/final_ui_28_03_23/new_ui/"
#SAVE_IMG_FILE_PATH="C:/Insightzz/Arrow_model_and_code_23/Process_Images/"


not_detected_var = "Needs Review"

#============================main window class===========================#
class mainwindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(mainwindow,self).__init__()
        uic.loadUi(ui_code + 'mainwindow_piston_arrow.ui',self)

        # self.setupUi(self)        

        #subprocess.run(['python','C:\Users\mahindra\Insightzz\code\UI\main_piston_v3.py'])
        #p1=subprocess.run(['python','C:/Insightzz/Arrow_model_and_code_23/piston_arrow_algo_final_apr_3.py'])
        
        # self.showMaximized()
        self.setWindowTitle("Drishti - Machine Vision Plateform")
        self.fetch_details_button.clicked.connect(self.first_shift_data)
        self.pushButton_search.clicked.connect(self.search)

        # self.fetch_details_button.clicked.connect(self.fetch_details1)
        self.download_details_button_2.clicked.connect(self.logout_clicked)
        self.download_details_button.clicked.connect(self.Download_report)
        self.Graph_btn.clicked.connect(self.Graph)
        self.cam_Health()
        self.main_tab.tabBarClicked.connect(self.handle_tabbar_clicked)
        self.Print_Engine_number()
        self.Count_all_Engine()

        self.Total_Ok_Engine()
        self.Total_Notok_Engine()

        self.Start_process()
        
        self.main_tab_home=QTimer(self)
        self.main_tab_camhealth=QTimer(self)
        self.main_tab_home.timeout.connect(self.Start_process)
        self.main_tab_home.start(500)
        
        #====================Getting current date time====================#
        current_date = date.today()
        d = QDate(current_date.year, current_date.month, current_date.day) 
        dd = QDate(current_date.year, current_date.month, current_date.day)
        # self.summary_from_date.setDate(d)
        # self.summary_to_date.setDate(dd)
        
        self.details_from_date.setDate(d)
        self.details_to_date.setDate(dd)
                
        #======================Graph presentation func start====================#
        # layout = QVBoxLayout()
        
        # self.exception_lineedit_dict = {}   

    def handle_tabbar_clicked(self, index):
        if index == 0:
            self.main_tab_home=QTimer(self)
            self.main_tab_home.timeout.connect(self.Start_process)
            self.Start_process()
            self.main_tab_home.start(500)
        else:
            self.main_tab_home.stop()
    def Print_Engine_number(self):
        db_fetch = pymysql.connect(host = db_host,
                                    user = db_user,
                                    password = db_pass,
                                    db = db_name)
        cur = db_fetch.cursor()
        current_time = datetime.datetime.now()
        toDate=current_time.strftime("%Y-%m-%d")
        first_date=toDate+" 00:00:00"
        second_date=toDate+" 23:59:59"       
        query="SELECT * FROM piston_arrow_inspection_db.engine_number_table ORDER BY ID desc limit 1;"       
        # query = "select count(ID) as TOTAL_COUNT, date(DATE_TIME) as DATE_TIME from PISTON_PROCESSING_TABLE group by date(DATE_TIME)"
       
        cur.execute(query)
        values=cur.fetchall()
        # print(values)
        Engine_number = values[0][1]
        print(Engine_number)
        self.Total_label_5.setText(str(Engine_number))

    
    def Count_all_Engine(self):
        db_fetch = pymysql.connect(host = db_host,
                                    user = db_user,
                                    password = db_pass,
                                    db = db_name)
        cur = db_fetch.cursor()
        current_time = datetime.datetime.now()
        toDate=current_time.strftime("%Y-%m-%d")
        first_date=toDate+" 00:00:00"
        second_date=toDate+" 23:59:59"       
        query="SELECT COUNT(*) FROM piston_arrow_inspection_db.piston_arrow_processing_table where DATE_TIME between "+'"'+first_date+'"'+" and "+'"'+second_date+'"'+";"
        # query = "select count(ID) as TOTAL_COUNT, date(DATE_TIME) as DATE_TIME from PISTON_PROCESSING_TABLE group by date(DATE_TIME)"
       
        cur.execute(query)
        values=cur.fetchall()
        # print(values)
        Total_img_count = values[0][0]
        # print(Total_img_count)
        self.label_7.setText(str(Total_img_count))

    def Total_Ok_Engine(self):
        global Total_ok_count
        db_fetch = pymysql.connect(host = db_host,
                                    user = db_user,
                                    password = db_pass,
                                    db = db_name)
        cur = db_fetch.cursor()
        current_time = datetime.datetime.now()
        toDate=current_time.strftime("%Y-%m-%d")
        first_date=toDate+" 00:00:00"
        second_date=toDate+" 23:59:59"  
        
        # if PISTON_1_STATUS_OK==None:
        query="SELECT COUNT(*) FROM piston_arrow_inspection_db.piston_arrow_processing_table where PISTON_1_STATUS LIKE 'OK' and DATE_TIME between "+'"'+first_date+'"'+" and "+'"'+second_date+'"'+" ;"
   
        cur.execute(query)
        values=cur.fetchall()
        # print(values)
        Total_ok_count = values[0][0]
        print(Total_ok_count)
        self.label_5.setText(str(Total_ok_count))

    def Total_Notok_Engine(self):
        global Total_Notok_count
        db_fetch = pymysql.connect(host = db_host,
                                    user = db_user,
                                    password = db_pass,
                                    db = db_name)
        cur = db_fetch.cursor()
        current_time = datetime.datetime.now()
        toDate=current_time.strftime("%Y-%m-%d")
        first_date=toDate+" 00:00:00"
        second_date=toDate+" 23:59:59"    
        # query="SELECT COUNT(IS_OK) FROM PISTON_PROCESSING_TABLE;" 
        query="SELECT COUNT(*) FROM piston_arrow_inspection_db.piston_arrow_processing_table where PISTON_1_STATUS LIKE 'NOT OK' and DATE_TIME between "+'"'+first_date+'"'+" and "+'"'+second_date+'"'+" ;"
            
        # query="SELECT COUNT(IS_OK) FROM PISTON_PROCESSING_TABLE WHERE IS_OK LIKE 'NOT OK' ;"        
        cur.execute(query)
        values=cur.fetchall()
        # print(values)
        Total_Notok_count = values[0][0]
        # print(Total_img_count)
        self.label_3.setText(str(Total_Notok_count))



    def Start_process(self):
        try:
            current_time = datetime.datetime.now()
            logger.debug("Start time : "+str(current_time))
            db_fetch = pymysql.connect(host = db_host,user = db_user,password = db_pass, db = db_name)
            cur = db_fetch.cursor()
            query="SELECT * FROM piston_arrow_inspection_db.piston_arrow_processing_table ORDER BY ID desc limit 1;"       
            cur.execute(query)
            values=cur.fetchall()
            triggeredDate = values[0][2]
            status = values[0][6]
            image_link_1 = values[0][4]
            image_link_2 = values[0][5]
            status1 = values[0][6]
            status2 = values[0][7]
            status3 = values[0][8]
            status4 = values[0][9]
            if status1=='OK' and status2=='OK':
                status_piston_1="OK"
            else:
                status_piston_1="NOT OK"
            
            if status3=='OK' and status4=='OK':
                status_piston_2="OK"
            else:
                status_piston_2="NOT OK"

            current_time = datetime.datetime.now() 
    
            secDiff = datetime.timedelta(seconds=50)
    
            if current_time - triggeredDate > secDiff:
                
                self.Home_frame.show()
                # self.frame_2.hide()
            else:
                logger.debug("Head is Visible")
                self.Home_frame.hide()
                self.frame_3.show()
                self.frame.show()
                self.label_2.setPixmap(QPixmap(image_link_1))
                self.label_4.setPixmap(QPixmap(image_link_2))
                self.label_8.setText(status_piston_1)
                self.label_8.setAlignment(QtCore.Qt.AlignCenter)
                # self.label_8.setText(status_piston_1) 
                self.label_17.setText(status_piston_2)
                self.label_17.setAlignment(QtCore.Qt.AlignCenter)
                # self.label_17.setText(status_piston_2)
                if status_piston_1=="OK":                     
                    self.label_8.setStyleSheet("background-color: rgb(0, 255, 0);border: 5px solid black; font: 75 15pt Ubuntu Condensed;")
                elif status_piston_1 == "NOT OK":
                    self.label_8.setStyleSheet("background-color: rgb(255, 0, 0);border: 5px solid black; font: 75 15pt Ubuntu Condensed;")
                if status_piston_2=="OK":                     
                    self.label_17.setStyleSheet("background-color: rgb(0, 255, 0);border: 5px solid black; font: 75 15pt Ubuntu Condensed;")
                elif status_piston_2 == "NOT OK":
                    self.label_17.setStyleSheet("background-color: rgb(255, 0, 0);border: 5px solid black; font: 75 15pt Ubuntu Condensed;")
            
            self.Count_all_Engine()
            self.Total_Ok_Engine()
            self.Total_Notok_Engine()
            self.Print_Engine_number()
            plc_status = self.getPLCDBStatus()
            self.first_shift_data()

            if plc_status == 2:
                QtWidgets.QMessageBox.information(self,"PLC STATUS","Unable to stablish connection with PLC, Kindly check PLC connection.")
            logger.debug("Total time in Start_process : "+str(datetime.datetime.now() - current_time))
        except Exception as e:
            logger.critical(f"Start_process() Exception is : {e}")    
    
    def getPLCDBStatus(self):
        PLC_STATUS = 0
        try:
            db_object = pymysql.connect(host = db_host,user = db_user,password = db_pass, db = db_name)
            cur = db_object.cursor()
            query="SELECT PLC_STATUS FROM plc_status_table"
            cur.execute(query)
            data_set = cur.fetchall()
             
            for i in range(0, len(data_set)):
                PLC_STATUS = int(data_set[i][0]) 
    
        except Exception as e:
            logger.critical(f"getPLCDBStatus() Exception is : {e}")
        finally:
            cur.close()
            db_object.close()
        return PLC_STATUS

    def logout_clicked(self):
        dlg = QMessageBox(self)
        dlg.setWindowTitle(" ")
        dlg.setText("Are you sure want to exit ?")
        dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dlg.setIcon(QMessageBox.Question)
        button = dlg.exec_()

        if button == QMessageBox.Yes:
            print("Yes!")
            self.close()
        else:
            print("No!")

    def Download_report(self):

            from datetime import date, datetime

            if not os.path.exists(DOWNLOAD_PATH+"/"+str(date.today())):
                # os.makedirs(DOWNLOAD_PATH+str(date.today()))
                os.mkdir(DOWNLOAD_PATH+"/"+str(date.today()))
            csv_path = DOWNLOAD_PATH+"/"+str(date.today())+"/"+str(datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))
            if not os.path.exists(csv_path):
                # os.makedirs(DOWNLOAD_PATH+str(date.today()))
                os.mkdir(csv_path)
            # csv_path = DOWNLOAD_PATH+"/"+str(date.today())+"/"+str(datetime.now())
            image_path = csv_path+"/Images"
            if not os.path.exists(image_path):
                # os.makedirs(image_path)   
                os.mkdir(image_path)         
            f = open(csv_path+"/"+'CSV_DATA.csv','w')
            dataStr = "ID"+','+"Head_TYPE"+','+"DATE_TIME"+','+"Head_NO"+','+"IMAGE_LINK"+','+"IS_OK"
            f.write(dataStr + '\n')

            row=self.details_tableWidget.rowCount()
            column=self.details_tableWidget.columnCount()
            
            for i in range(row):   
                dataitem1=self.details_tableWidget.item(i,0)
                dataitem2=self.details_tableWidget.item(i,1)
                dataitem3=self.details_tableWidget.item(i,2)
                dataitem4=self.details_tableWidget.item(i,3)
                dataitem5=self.details_tableWidget.item(i,4)
                dataitem6=self.details_tableWidget.item(i,5)

                # dataitem6=self.Report_table.item(i,5)
                ID=dataitem1.text()
                ENGINE_TYPE=dataitem2.text()
                DATE_TIME=dataitem3.text()
                ENGINE_NUMBER=dataitem4.text()
                IS_OK=dataitem5.text()
                # IMAGE_LINK=dataitem6.text()

                
                IMAGE_LINK=self.getImageLink(ID)
                # self.getImageLink(ID)
                # IMAGE_LINK1 = os.path.basename(IMAGELINK)
                rowData=[ID,ENGINE_TYPE,DATE_TIME,ENGINE_NUMBER,IS_OK,IMAGE_LINK]
                try:
                    shutil.copyfile(IMAGE_LINK,image_path+"/"+os.path.basename(os.path.normpath(IMAGE_LINK)))
                except Exception as e:
                    print('Exception in copying image: ',e)

                dataStr = ID+','+ENGINE_TYPE+','+DATE_TIME+','+ENGINE_NUMBER+','+IS_OK+',' + os.path.basename(IMAGE_LINK)
                f.write(dataStr + '\n')
                # print(f)
                # print(dataStr)
                
            f.close()
            QtWidgets.QMessageBox.information(self,"Data Downloded","Data downloded in reports folder.")
    def getImageLink(self,ID):
        db_fetch = pymysql.connect(host ="localhost",
                                        user = "root",
                                        password = "insightzz123",
                                        db = "piston_arrow_inspection_db") 
        cur = db_fetch.cursor()
        query="select IMG_LINK from piston_arrow_inspection_db.piston_arrow_processing_table WHERE ID="+ID+";"
        cur.execute(query)
        data=cur.fetchall()
        return data[0][0] 
       
        cur.execute(query)
        values=cur.fetchall()
        # print(values)
        Total_img_count = values[0][0]
        # print(Total_img_count)
        self.label_11.setText(str(Total_img_count))
    def search(self):
        
        x=self.search_input.toPlainText()
        db_fetch = pymysql.connect(host = db_host,
                                user = db_user,
                                password = db_pass,
                                db = db_name)
        cur = db_fetch.cursor()
        # fromDate = str(self.de_fromDate.date().toPyDate())+ " 00:00:00"
        # toDate = str(self.de_toDate.date().toPyDate())+ " 23:59:00"
        # today = datetime.date.today()
        # self.fromDate.setDate(today)
        # self.todate_2.setDate(today)
        fromDate=self.details_from_date.date()
        fromDate = fromDate.toString("yyyy-MM-dd")
        fromDate =fromDate+" 00:00:00"
        toDate=self.details_to_date.date()
        toDate = toDate.toString("yyyy-MM-dd")
        toDate = toDate+" 23:59:59"

        query="SELECT * FROM piston_arrow_inspection_db.piston_arrow_processing_table where ENGINE_NUMBER = "+'"'+x+'"'+" and DATE_TIME between "+'"'+fromDate+'"'+" and "+'"'+toDate+'"'+";"
        try:
                cur.execute(query)
                values=cur.fetchall()
                # print(values)
                
                cur.close() 
                i=0
                self.details_tableWidget.setRowCount(0)
                for row_number, row_data in enumerate(values):
                    self.details_tableWidget.insertRow(row_number)
                    ID=row_data[0]
                    ENGINE_TYPE=row_data[1]
                    DATE_TIEM=row_data[2]
                    ENGINE_NUMBER=row_data[3]                
                    IS_OK=str(row_data[5])
                    IMG_LINK=str(row_data[4])
                    CAMERA_TYPE=str(row_data[5])


                    # self.details_tableWidget.setRowHeight(0,80)
                    # self.details_tableWidget.setRowHeight(1,80)
                    # self.details_tableWidget.setRowHeight(2,80)
                    self.details_tableWidget.setItem(row_number,0, QtWidgets.QTableWidgetItem(str(ID)))
                    self.details_tableWidget.setItem(row_number,1, QtWidgets.QTableWidgetItem(str(ENGINE_TYPE)))
                    self.details_tableWidget.setItem(row_number,2, QtWidgets.QTableWidgetItem(str(DATE_TIEM)))
                    self.details_tableWidget.setItem(row_number,3, QtWidgets.QTableWidgetItem(str(ENGINE_NUMBER)))
                    self.details_tableWidget.setItem(row_number,5, QtWidgets.QTableWidgetItem(str(IMG_LINK)))
                    if IS_OK=="OK":
                        self.details_tableWidget.setItem(row_number,4, QtWidgets.QTableWidgetItem(str(IS_OK)))
                    else:
                        IS_OK=="NOT OK"
                        self.details_tableWidget.setItem(row_number,4, QtWidgets.QTableWidgetItem(str(IS_OK)))


                    qSelectButton = QtWidgets.QPushButton("VIEW_Image")
                    qSelectButton.clicked.connect(lambda checked, arg2=IMG_LINK: self.showIMAGE(arg2))                              
                            
                    self.details_tableWidget.setCellWidget(row_number,5, qSelectButton) 
        except Exception as e:
                QtWidgets.QMessageBox.about(self.frame,"Error Occured", str(e))       


    def first_shift_data(self):
        global Total_img_count,Total_ok_img_count,Total_NOT_ok_img_count
        db_fetch = pymysql.connect(host = db_host,
                                        user = db_user,
                                        password = db_pass,
                                        db = db_name)
        cur = db_fetch.cursor()
        fromDate=self.details_from_date.date()
        fromDate = fromDate.toString("yyyy-MM-dd")
        fromDate= fromDate+" 00:00:00"
        toDate=self.details_to_date.date()
        toDate = toDate.toString("yyyy-MM-dd")
        toDate = toDate+" 23:59:59"
        query="SELECT * FROM piston_arrow_inspection_db.piston_arrow_processing_table where DATE_TIME between "+'"'+fromDate+'"'+" and "+'"'+toDate+'"'+";"
        
        try:
            cur.execute(query)
            values=cur.fetchall()
            # print(values)
            
            cur.close() 
            i=0
            self.details_tableWidget.setRowCount(0)
            for row_number, row_data in enumerate(values):
                self.details_tableWidget.insertRow(row_number)
                ID=row_data[0]
                ENGINE_TYPE=row_data[1]
                DATE_TIME=row_data[2]
                ENGINE_NUMBER=row_data[3]                
                IMG_LINK=str(row_data[4])
                IMG_LINK_2=str(row_data[5])
                PISTON_1_STATUS=str(row_data[6])
                # CAMERA_TYPE=str(row_data[5])


                
                self.details_tableWidget.setItem(row_number,0, QtWidgets.QTableWidgetItem(str(ID)))
                self.details_tableWidget.setItem(row_number,1, QtWidgets.QTableWidgetItem(str(ENGINE_TYPE)))
                self.details_tableWidget.setItem(row_number,2, QtWidgets.QTableWidgetItem(str(DATE_TIME)))
                self.details_tableWidget.setItem(row_number,3, QtWidgets.QTableWidgetItem(str(ENGINE_NUMBER)))
                self.details_tableWidget.setItem(row_number,4, QtWidgets.QTableWidgetItem(str(PISTON_1_STATUS)))

                self.details_tableWidget.setItem(row_number,5, QtWidgets.QTableWidgetItem(str(IMG_LINK)))
                qSelectButton = QtWidgets.QPushButton("VIEW_Image_cam_1")
                qSelectButton.clicked.connect(lambda checked, arg1=IMG_LINK: self.showIMAGE(arg1))                              
                        
                self.details_tableWidget.setCellWidget(row_number,5, qSelectButton) 


                self.details_tableWidget.setItem(row_number,6, QtWidgets.QTableWidgetItem(str(IMG_LINK_2)))
                qSelectButton = QtWidgets.QPushButton("VIEW_Image_cam_2")               

                qSelectButton.clicked.connect(lambda checked, arg2=IMG_LINK_2: self.showIMAGE_1(arg2))                              
                        
                self.details_tableWidget.setCellWidget(row_number,6, qSelectButton) 
        except Exception as e:
            print(e)
        
 
    def Graph(self):
      

                # Creating dataset
            cars = ['OK spring', 'Retried spring']
            ENG_No=['Head_number']
        
            # data = [23, 17, 35, 29, 12, 41]
            data = [Total_ok_img_count, Total_NOT_ok_img_count]

        
        
            # Creating explode data
            explode = (0.1, 0.0)
        
            # Creating color parameters
            colors = ( "orange", "cyan")
        
            # Wedge properties
            wp = { 'linewidth' : 1, 'edgecolor' : "green" }
        
            # Creating autocpt arguments
            def func(pct, allvalues):
                # return "{:1.1f}%".format(pct)
                absolute = int(pct / 100.*np.sum(allvalues))
                return "{:.1f}".format(pct, absolute)
        
            # Creating plot
            fig, ax = plt.subplots(figsize =(10, 7))
            wedges, texts, autotexts = ax.pie(data,
                                            autopct = lambda pct: func(pct, data),
                                            explode = explode,
                                            labels = cars,
                                            shadow = True,
                                            colors = colors,
                                            startangle = 90,
                                            wedgeprops = wp,
                                            textprops = dict(color ="magenta"))
        
            # Adding legend
            ax.legend(wedges, cars,
                    title ="INDEX",
                    loc ="center left",
                    bbox_to_anchor =(1, 0, 0.5, 1))
        
            plt.setp(autotexts, size = 8, weight ="bold")
            ax.set_title("GASOLINE PISTON RING INSPECTION GRAPH")
        
            # show plot
            plt.show()
        
    def fetch_details1(self):
        
        db_fetch = pymysql.connect(host = db_host,
                                       user = db_user,
                                       password = db_pass,
                                       db = db_name)
        cur = db_fetch.cursor()
        fromDate=self.details_from_date.date()
        fromDate = fromDate.toString("yyyy-MM-dd")
        fromDate= fromDate+" 00:00:00"
        toDate=self.details_to_date.date()
        toDate = toDate.toString("yyyy-MM-dd")
        toDate = toDate+" 23:59:59"
        query="SELECT * FROM piston_arrow_inspection_db.piston_arrow_processing_table where DATE_TIME between "+'"'+fromDate+'"'+" and "+'"'+toDate+'"'+";"
        
        try:
            cur.execute(query)
            values=cur.fetchall()
            # print(values)
            
            cur.close() 
            i=0
            self.details_tableWidget.setRowCount(0)
            for row_number, row_data in enumerate(values):
                self.details_tableWidget.insertRow(row_number)
                ID=row_data[0]
                ENGINE_TYPE=row_data[1]
                DATE_TIME=row_data[2]
                ENGINE_NUMBER=row_data[3]                
                IMG_LINK=str(row_data[4])
                IS_OK=str(row_data[5])
                # CAMERA_TYPE=str(row_data[5])


                # self.details_tableWidget.setRowHeight(0,80)
                # self.details_tableWidget.setRowHeight(1,80)
                # self.details_tableWidget.setRowHeight(2,80)
                self.details_tableWidget.setItem(row_number,0, QtWidgets.QTableWidgetItem(str(ID)))
                self.details_tableWidget.setItem(row_number,1, QtWidgets.QTableWidgetItem(str(ENGINE_TYPE)))
                self.details_tableWidget.setItem(row_number,2, QtWidgets.QTableWidgetItem(str(DATE_TIME)))
                self.details_tableWidget.setItem(row_number,3, QtWidgets.QTableWidgetItem(str(ENGINE_NUMBER)))
                self.details_tableWidget.setItem(row_number,4, QtWidgets.QTableWidgetItem(str(IS_OK)))


                self.details_tableWidget.setItem(row_number,5, QtWidgets.QTableWidgetItem(str(IMG_LINK)))
                qSelectButton = QtWidgets.QPushButton("VIEW_Image")
                qSelectButton.clicked.connect(lambda checked, arg2=IMG_LINK: self.showIMAGE(arg2))                              
                        
                self.details_tableWidget.setCellWidget(row_number,5, qSelectButton) 
        except Exception as e:
                QtWidgets.QMessageBox.about(self.frame,"Error Occured", str(e))  

    
    def cam_Health(self):
        device_info_list = pylon.TlFactory.GetInstance().EnumerateDevices()
        # print(len(device_info_list))
        if len(device_info_list) > 0:
            db_update = pymysql.connect(host = db_host,
                                       user = db_user,
                                       password = db_pass,
                                       db = db_name)
            cur = db_update.cursor()
            query = "UPDATE cam_health set HEALTH = 'CONNECTED';"
            cur.execute(query)
            db_update.commit()
            cur.close()
        else:
            db_update = pymysql.connect(host = db_host,
                                       user = db_user,
                                       password = db_pass,
                                       db = db_name)
            cur = db_update.cursor()
            query = "UPDATE cam_health set HEALTH = 'NOT CONNECTED';"
            cur.execute(query)
            db_update.commit()
            cur.close()

        db_fetch = pymysql.connect(host = db_host,
                                       user = db_user,
                                       password = db_pass,
                                       db = db_name)
        cur = db_fetch.cursor()        
        query="SELECT * FROM piston_arrow_inspection_db.cam_health;"
        try:
            cur.execute(query)
            values=cur.fetchall()
            # print(values)
            cur.close()             
            self.details_tableWidget_cam_health.setRowCount(0)
            for row_number, row_data in enumerate(values):
                self.details_tableWidget_cam_health.insertRow(row_number)
                cam=row_data[1]
                status=row_data[2]  
                
                self.details_tableWidget_cam_health.setRowHeight(0,80)
                self.details_tableWidget_cam_health.setRowHeight(1,80)
                # self.details_tableWidget_cam_health.setRowHeight(2,80)
                # self.details_tableWidget_cam_health.setRowHeight(3,80)


                self.details_tableWidget_cam_health.setItem(row_number,0, QtWidgets.QTableWidgetItem(str(cam)))
                self.details_tableWidget_cam_health.setItem(row_number,1, QtWidgets.QTableWidgetItem(str(status)))
                if "CONNECTED" != status:
                    self.details_tableWidget_cam_health.item(row_number,1).setBackground(QtGui.QColor(255,0,0))
                else:
                    self.details_tableWidget_cam_health.item(row_number,1).setBackground(QtGui.QColor(0,255,0))
                      
                        
        except Exception as e:
                QtWidgets.QMessageBox.about(self.inf_frame,"Error Occured", str(e))  

        
    def showIMAGE(self,arg1):
        global imagewindow_object
        # print("Inside showIMAGE")
        imagewindow_object.loadImage(arg1)
    
    def showIMAGE_1(self,arg2):
        global imagewindow_object
        # print("Inside showIMAGE")
        imagewindow_object.loadImage_cam1(arg2)


    

  
#===========================Login Window===================================#
class login(QtWidgets.QMainWindow, Ui_Login):
    def __init__(self, *args, obj=None, **kwargs):
        super(login, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowTitle("Drishti - Machine Vision Plateform")
        self.Enter_pushButton.clicked.connect(self.login)
        self.password_lineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        
    #=====================Enter key press event============================#
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            self.login()    
    
    #===================== Login func start===============================#    
    def login(self):
        username = str(self.username_lineEdit.text())
        print(username)
        password = str(self.password_lineEdit.text())
        print(password)
        if username == "MHEL" and password == "mhel@123":
            # mainwindow_object.show()
            # login_object.close()
            pass
        
        elif username == "" and password == "":
            self.wrong_cred_label.setText(QtCore.QCoreApplication.translate("Login", "Username or Password can not be empty!"))
        elif username != "MHEL":
            self.wrong_cred_label.setText(QtCore.QCoreApplication.translate("Login", "Username wrong!"))
        elif password != "":
            self.wrong_cred_label.setText(QtCore.QCoreApplication.translate("Login", "Password wrong!"))
        else:
            try:
                db_fetch = pymysql.connect(host = db_host,
                                           user = db_user,
                                           passwd = db_pass,
                                           db = db_name)
                cur = db_fetch.cursor()
                query = "select USER_NAME, PASSWORD from login"
                cur.execute(query)
                data_set = cur.fetchall()
                # print(data_set)
                cur.close()
                for row in range (0, len(data_set)):
                    if username == data_set[row][1] and password == data_set[row][2]:
                        
                        self.username_label.clear()
                        self.password_label.clear()
                        self.wrong_cred_label.clear()
                    elif username == data_set[row][0] and password != data_set[row][1]:
                        self.wrong_cred_label.setText(QtCore.QCoreApplication.translate("Please, enter valid password"))
                    elif username != data_set[row][0] and password == data_set[row][1]:
                        self.wrong_cred_label.setText(QtCore.QCoreApplication.translate("Please, enter valid username"))
                        
                    #mainwindow_object.update_cam_health()
                    #mainwindow_object.timer_cam_health.start(5000)                    
                        
            except Exception as e:
                print('Exception in Login:', e)
                

#============================Image window class=============================#
class PhotoViewer(QtWidgets.QGraphicsView):
    photoClicked = QtCore.pyqtSignal(QtCore.QPoint)

    def __init__(self, parent):
        super(PhotoViewer, self).__init__(parent)
        self._zoom = 0
        self._empty = True
        self._scene = QtWidgets.QGraphicsScene(self)
        self._photo = QtWidgets.QGraphicsPixmapItem()
        self._scene.addItem(self._photo)
        self.setScene(self._scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(30, 30, 30)))
        self.setFrameShape(QtWidgets.QFrame.NoFrame)

    def hasPhoto(self):
        return not self._empty

    def fitInView(self, scale=True):
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            if self.hasPhoto():
                unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())
                self.scale(factor, factor)
            self._zoom = 0

    def setPhoto(self, pixmap=None):
        self._zoom = 0
        if pixmap and not pixmap.isNull():
            self._empty = False
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
            self._photo.setPixmap(pixmap)
        else:
            self._empty = True
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self._photo.setPixmap(QtGui.QPixmap())
        self.fitInView()

    def wheelEvent(self, event):
        if self.hasPhoto():
            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1
            if self._zoom > 0:
                self.scale(factor, factor)
            elif self._zoom == 0:
                self.fitInView()
            else:
                self._zoom = 0

    def toggleDragMode(self):
        if self.dragMode() == QtWidgets.QGraphicsView.ScrollHandDrag:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        elif not self._photo.pixmap().isNull():
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

    def mousePressEvent(self, event):
        if self._photo.isUnderMouse():
            self.photoClicked.emit(self.mapToScene(event.pos()).toPoint())
        super(PhotoViewer, self).mousePressEvent(event)      

#============================Image window class=============================#
class ImageWindow(QtWidgets.QWidget):
    def __init__(self):
        super(ImageWindow, self).__init__()
        self.viewer = PhotoViewer(self)
        self.imagepath = "" 
        self.update_button = QtWidgets.QPushButton(self)
        self.update_button.setGeometry(QtCore.QRect(200, 0, 130, 40))
        font = QtGui.QFont()
        font.setPointSize(15)
        self.update_button.setFont(font)
        self.update_button.setObjectName("update_button")
        self.update_button.setText(QtCore.QCoreApplication.translate("ImageviewWindow", ""))
        # self.update_button.clicked.connect(self.update_table)

        font = QtGui.QFont()
        font.setPointSize(15)
        self.notdefect_checkbox = QtWidgets.QCheckBox(self)
        self.notdefect_checkbox.setFont(font)
        self.notdefect_checkbox.setAutoFillBackground(True)
        self.notdefect_checkbox.setIconSize(QtCore.QSize(30, 30))
        # self.notdefect_checkbox.setObjectName("notdefect_checkbox")
        # self.notdefect_checkbox.setText(QtCore.QCoreApplication.translate("ImageviewWindow", "Not a deftect"))        
       
        self.viewer.photoClicked.connect(self.photoClicked)
        # Arrange layout
        VBlayout = QtWidgets.QVBoxLayout(self)
        VBlayout.addWidget(self.viewer)
        HBlayout = QtWidgets.QHBoxLayout()
        HBlayout.setAlignment(QtCore.Qt.AlignLeft)
        HBlayout.addWidget(self.update_button)                
        HBlayout.addWidget(self.notdefect_checkbox)        
        VBlayout.addLayout(HBlayout)
        self.imagepath = ""        

    def loadImage(self, imagelink):
        self.close()        
        self.setGeometry(100, 100, 800, 600)
        self.show()
        self.notdefect_checkbox.setChecked(False)        
        self.imagepath = imagelink        
        self.viewer.setPhoto(QtGui.QPixmap(imagelink))

    def loadImage_cam1(self, imagelink):
        self.close()        
        self.setGeometry(100, 100, 800, 600)
        self.show()
        self.notdefect_checkbox.setChecked(False)        
        self.imagepath = imagelink        
        self.viewer.setPhoto(QtGui.QPixmap(imagelink))

    def pixInfo(self):
        self.viewer.toggleDragMode()

    def photoClicked(self, pos):
        if self.viewer.dragMode()  == QtWidgets.QGraphicsView.NoDrag:
            self.editPixInfo.setText('%d, %d' % (pos.x(), pos.y()))
 
        
    def show_message(self, message):
        choice = QMessageBox.information(self, 'Message!',message)

 
  
#=============================Report parameters class=========================#
class VersionWindow(QtWidgets.QMainWindow):
    def __init__(self,*args,**kwargs):
        super(VersionWindow,self).__init__(*args,**kwargs)
        self.setupUi(self)
# def location_on_screen(self):
#     ag=QtWidgets.QDesktopWidget().availableGeometry()
#     x=ag.width()
#     y=0
#     mainwindow.move(x,y)

def call_algo():
    p1=subprocess.run(['python','C:/Insightzz/Arrow_model_and_code_23/piston_arrow_algo_final_apr_3.py'])
    print("algo start")

def call_frame_cap():
    print("FRAME CAPTURE")
    p=subprocess.run(['python','C:/Insightzz/Arrow_model_and_code_23/frame_cap_code_28_03_23.py'])
#========================class object defined=============================#    
if __name__=='__main__':
    # app = QtWidgets.QApplication(sys.argv)
    # mainwindow = QtWidgets.QMainWindow()
    # ui=mainwindow()
    # ui.setupUi(mainwindow)
    # ui.location_on_screen()
    # mainwindow.show()
    # p=Process(target=call_algo)
    # p.start()

    # imagewindow_object= ImageWindow()

    # # p2=threading.Thread(target=ui.startLoop)
    # # p2.start()
    # sys.exit(app.exec_())
    global imagewindow_object

    app = QtWidgets.QApplication(sys.argv)   
    # login_object = login()
    
    mainwindow_object = mainwindow()
    # mainwindow_object.location_on_screen()
    mainwindow_object.show()

    p=Process(target=call_frame_cap)
    p.start()
    time.sleep(0.1)
    p1=Process(target=call_algo)
    p1.start()
    imagewindow_object= ImageWindow()
    app.exec()      