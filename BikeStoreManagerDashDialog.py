'''
This file contains the BikeStoreManagerDash class, which is a QDialog that represents the Bike Store Manager Dashboard.
The dashboard contains charts and tables that display various sales and employee data.
The dashboard also contains a sidebar that allows the user to navigate to other pages in the application.

Author: SQLWeavers
File: BikeStoreManagerDashDialog.py
Course: Data 225
Project: TerraBikes
'''

import sys
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox, QTableWidgetItem, QLabel
from PyQt5.QtCore import QDate, Qt, pyqtSlot
from PyQt5.QtGui import QFont, QColor
from BikeStoreManagerDashDialog_ui import Ui_BikeStoreManagerDashDialog
from BikeStoreUtils import create_connection
from datetime import datetime
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Connect to the database
conn = create_connection(config_file='terrabikes_bi.ini')
cursor = conn.cursor()

conn2 = create_connection(config_file='terrabikes.ini')
cursor2 = conn2.cursor()

def _close_db_connections():
    """
    Closes the database connections.
    """
    cursor.close()
    conn.close()
    cursor2.close()
    conn2.close()

class BikeStoreManagerDash(QDialog):
    """
    A class representing the Bike Store Manager Dashboard.
    """
        
    def __init__(self, _username, parent=None):
        """
        Initializes the BikeStoreManagerDash object.

        Parameters:
        - _username (str): The username of the manager.
        - parent (QWidget): The parent widget (default is None).
        """
        super(BikeStoreManagerDash, self).__init__(parent)
        self.ui = Ui_BikeStoreManagerDashDialog()
        self.ui.setupUi(self)
        self._BikeStoreMainWin = None
        
        self.username = _username
        self.ui.wdgtShortSidebar.hide()
        self.ui.ManagerDashboardStacked.setCurrentIndex(0)
        self.setDefaults()

    def set_main_dialog(self, main_dialog):
        """
        Sets the main dialog.

        Args:
            main_dialog: The main dialog.
        """
        self._BikeStoreMainWin = main_dialog

    '''
    ***********  SALES DASHBOARD  ***********
    =========================================
    Heirarchy:
    - setDefaults()
    - setCharts()
        - setSummaryLabels()
        - setRegionOrdersBarChart()
        - setOrderCountsStatusChart()
        - setOrderCountsByYearChart()
        - setQuantitiesByCategoryChart()
        - populateTopProducts()   
    =========================================    
    '''
    def setDefaults(self):
        """
        Sets the default values and configurations for the dashboard.
        """
        self.fromDate = None
        self.toDate = None
        self.RadioYear = None
        self.RadioYear2 = None
        self.RadioMonth = None
        sql = """select concat(first_name,' ', last_name)
                    from users u, employee e
                    where u.username = %s
                    and e.employee_id = u.employee_id"""
        cursor2.execute(sql, (self.username,))
        result = cursor2.fetchall()
        if len(result) > 0:
            ManagerName = result[0][0]
            currDate = datetime.now().date()
            mgrtext = "Manager Name: "+ManagerName +'\n'+'Date: '+str(currDate)
            self.ui.lblManagerName.setText(mgrtext)

        currentDate = QDate.currentDate()
        self.ui.txtRangeFrom.setDate(currentDate)  
        self.ui.txtRangeTo.setDate(currentDate)

        
        self.ui.SelectYear.blockSignals(True)
        sql = """select distinct year from calendar order by 1"""
        cursor.execute(sql)
        result = cursor.fetchall()
        self.ui.SelectYear.clear()
        if len(result) > 0:
            self.ui.SelectYear.addItem("All")
            for row_number, row_data in enumerate(result):
                self.ui.SelectYear.addItem(str(row_data[0]))
        
        self.ui.SelectYear.blockSignals(False)

        
        sql = """select distinct region from region where region!= 'Online' order by 1"""
        self.ui.SelectRegion.blockSignals(True)
        cursor.execute(sql)
        result = cursor.fetchall()
        self.ui.SelectRegion.clear()
        if len(result) > 0:
            self.ui.SelectRegion.addItem("All")
            for row_number, row_data in enumerate(result):
                self.ui.SelectRegion.addItem(str(row_data[0]))        
        
        self.ui.SelectRegion.blockSignals(False)
        self.setCharts()

    def setCharts(self, Year='All', Region='All'):
        """
        Sets the charts and data based on the selected year and region.

        Parameters:
        - Year (str): The selected year (default is 'All').
        - Region (str): The selected region (default is 'All').
        """
        self.setSummaryLabels(Year, Region)
        self.setRegionOrdersBarChart(Year, Region)
        self.setOrderCountsStatusChart(Year, Region)
        self.setOrderCountsByYearChart(Year, Region)
        self.setQuantitiesByCategoryChart(Year, Region)
        self.populateTopProducts(Year, Region)

    '''
    ***********  EVENT HANDLERS  ***********
    =========================================
    '''    
    def handleRadioElse(self):
        """
        Handles the radio buttons when 'All' option is selected.
        """
        self.RadioYear = None
        self.RadioYear2 = None
        self.RadioMonth = None
    
    def handleRadioButtons(self):
        """
        Handles the radio buttons selection and sets the corresponding values.
        """
        self.fromDate = None
        self.toDate = None
        if self.ui.chkAll.isChecked():
            self.handleRadioElse()
        if self.ui.chk2Year.isChecked():
            self.RadioYear = datetime.now().year
            self.RadioYear2 = self.RadioYear - 1
            self.RadioMonth = None

        if self.ui.chkLastYear.isChecked():
            self.RadioYear = datetime.now().year - 1
            self.RadioYear2 = None
            self.RadioMonth = None

        if self.ui.chkYear.isChecked():
            self.RadioYear = datetime.now().year
            self.RadioYear2 = None
            self.RadioMonth = None  

        if self.ui.chk6Months.isChecked():
            self.RadioYear = datetime.now().year
            self.RadioYear2 = None
            self.RadioMonth = datetime.now().month - 5

        if self.ui.chkQuarter.isChecked():
            self.RadioYear = datetime.now().year
            self.RadioYear2 = None
            self.RadioMonth = datetime.now().month - 2

        if self.ui.chkMonth.isChecked():
            self.RadioYear = datetime.now().year
            self.RadioYear2 = None
            self.RadioMonth = datetime.now().month - 1

        self.setCharts()

    @pyqtSlot()
    def on_chkAll_clicked(self):
        """
        Slot function called when 'All' checkbox is clicked.
        """
        self.handleRadioButtons()
    
    @pyqtSlot()
    def on_chk2Year_clicked(self):
        """
        Slot function called when '2 Year' checkbox is clicked.
        """
        self.handleRadioButtons()
    
    @pyqtSlot()
    def on_chkLastYear_clicked(self):
        """
        Slot function called when 'Last Year' checkbox is clicked.
        """
        self.handleRadioButtons()
    
    @pyqtSlot()
    def on_chkYear_clicked(self):
        """
        Slot function called when 'Year' checkbox is clicked.
        """
        self.handleRadioButtons()
    
    @pyqtSlot()
    def on_chk6Months_clicked(self):
        """
        Slot function called when '6 Months' checkbox is clicked.
        """
        self.handleRadioButtons()
    
    @pyqtSlot()
    def on_chkQuarter_clicked(self):
        """
        Slot function called when 'Quarter' checkbox is clicked.
        """
        self.handleRadioButtons()
    
    @pyqtSlot()
    def on_chkMonth_clicked(self):
        """
        Slot function called when 'Month' checkbox is clicked.
        """
        self.handleRadioButtons()

    @pyqtSlot(int)
    def on_SelectYear_currentIndexChanged(self):
        """
        Slot function called when the year selection is changed.
        """
        self.fromDate = None
        self.toDate = None
        if self.ui.SelectRegion.currentText() != 'All':
            region = self.ui.SelectRegion.currentText()
        else:
            region = 'All'

        if self.ui.SelectYear.currentText() != 'All':
            self.setCharts(self.ui.SelectYear.currentText(), region)
        else:
            self.ui.SelectRegion.setCurrentText('All')
            self.setCharts()

    @pyqtSlot(int)
    def on_SelectRegion_currentIndexChanged(self):
        """
        Event handler for the currentIndexChanged signal of the SelectRegion combo box.
        Updates the charts based on the selected region and year.

        Returns:
            None
        """
        self.fromDate = None
        self.toDate = None
        year = 'All'
        if self.ui.SelectYear.currentText() != 'All':
            year = self.ui.SelectYear.currentText()
        else:
            if self.ui.SelectRegion.currentText() != 'All':
                QMessageBox.warning(self, "Error", "Please select a year")
                self.ui.SelectRegion.setCurrentText('All')
                return

        if self.ui.SelectRegion.currentText() != 'All':
            self.setCharts(year, self.ui.SelectRegion.currentText())
        else:
            self.setCharts(year)

    @pyqtSlot()
    def on_btnGenerate_clicked(self):
        """
        Event handler for the 'Generate' button click event.
        Retrieves the selected date range from the UI and sets the charts accordingly.
        """
        self.fromDate = self.ui.txtRangeFrom.date().toPyDate()
        self.toDate = self.ui.txtRangeTo.date().toPyDate()
        self.setCharts()

    '''
    ***********  CHARTS  ***********
    =========================================
    Methods:
    - setSummaryLabels()
    - setRegionOrdersBarChart()
    - setOrderCountsStatusChart()
    - setOrderCountsByYearChart()
    - setQuantitiesByCategoryChart()
    - populateTopProducts()
    ========================================='''

    def setSummaryLabels(self, Year='All', Region='All'):
        """
        Sets the summary labels in the GUI based on the specified filters.

        Args:
            Year (str): The year to filter the data by. Default is 'All'.
            Region (str): The region to filter the data by. Default is 'All'.
        """
        sql = """SELECT 
                    COUNT(DISTINCT od.order_id) order_count,
                    COUNT(DISTINCT s.customer_key) customer_count,
                    SUM(s.qty) total_items,
                    ROUND(SUM(s.price), 2) total_sales,
                    ROUND(AVG(od.rating), 2) average_rating,
                    ROUND((COUNT(DISTINCT od.order_id) / ((DATEDIFF(MAX(order_date), MIN(order_date)) / 365) * 12)),
                            2) avg_orders
                FROM
                    sales s,
                    order_details od
                WHERE
                    s.order_detail_key = od.order_detail_key"""
        if Year != 'All':
            sql = sql + " and s.calendar_key in (select calendar_key from calendar where year = "+Year+")"
        if Region != 'All':
            sql = sql + " and s.region_key in (select region_key from region where region = '"+Region+"')"
        if self.fromDate != None and self.toDate != None:
            sql = sql + " and s.calendar_key in (select calendar_key from calendar where full_date between '"+str(self.fromDate)+"' and '"+str(self.toDate)+"')"

        if self.RadioYear != None and self.RadioYear2 == None:
            sql = sql + " and s.calendar_key in (select calendar_key from calendar where year = "+str(self.RadioYear)+")"
        if self.RadioYear2 != None and self.RadioYear != None:
            sql = sql + " and s.calendar_key in (select calendar_key from calendar where year in ("+str(self.RadioYear2)+","+str(self.RadioYear)+"))"
        if self.RadioMonth != None:
            sql = sql + " and s.calendar_key in (select calendar_key from calendar where month >= "+str(self.RadioMonth)+")"

        cursor.execute(sql)
        result = cursor.fetchall()
        if len(result) > 0:
            font = QFont()
            font.setPointSize(24)
            css = 'color: white; background-color: DodgerBlue;'
            self.ui.txtTotOrders.setText(str(result[0][0]))
            self.ui.txtTotOrders.setFont(font)
            self.ui.txtTotOrders.setStyleSheet(css)
            self.ui.txtTotOrders.setAlignment(Qt.AlignCenter)
            self.ui.txtTotCustomers.setText(str(result[0][1]))
            self.ui.txtTotCustomers.setFont(font)
            self.ui.txtTotCustomers.setStyleSheet(css)
            self.ui.txtTotCustomers.setAlignment(Qt.AlignCenter)
            self.ui.txtTotItems.setText(str(result[0][2]))
            self.ui.txtTotItems.setFont(font)
            self.ui.txtTotItems.setStyleSheet(css)
            self.ui.txtTotItems.setAlignment(Qt.AlignCenter)
            self.ui.txtTotSales.setText(str(result[0][3]))
            self.ui.txtTotSales.setFont(font)
            self.ui.txtTotSales.setStyleSheet(css)
            self.ui.txtTotSales.setAlignment(Qt.AlignCenter)
            self.ui.txtAvgRating.setText(str(result[0][4]))
            self.ui.txtAvgRating.setFont(font)
            self.ui.txtAvgRating.setStyleSheet(css)
            self.ui.txtAvgRating.setAlignment(Qt.AlignCenter)
            self.ui.txtAvgOrders.setText(str(result[0][5]))
            self.ui.txtAvgOrders.setFont(font)
            self.ui.txtAvgOrders.setStyleSheet(css)
            self.ui.txtAvgOrders.setAlignment(Qt.AlignCenter)
        else:
            font = QFont()
            font.setPointSize(24)
            css = 'color: white; background-color: DodgerBlue;'
            self.ui.txtTotOrders.setText("0")
            self.ui.txtTotOrders.setFont(font)
            self.ui.txtTotOrders.setStyleSheet(css)
            self.ui.txtTotOrders.setAlignment(Qt.AlignCenter)
            self.ui.txtTotCustomers.setText("0")
            self.ui.txtTotCustomers.setFont(font)
            self.ui.txtTotCustomers.setStyleSheet(css)
            self.ui.txtTotCustomers.setAlignment(Qt.AlignCenter)
            self.ui.txtTotItems.setText("0")
            self.ui.txtTotItems.setFont(font)
            self.ui.txtTotItems.setStyleSheet(css)
            self.ui.txtTotItems.setAlignment(Qt.AlignCenter)
            self.ui.txtTotSales.setText("0")
            self.ui.txtTotSales.setFont(font)
            self.ui.txtTotSales.setStyleSheet(css)
            self.ui.txtTotSales.setAlignment(Qt.AlignCenter)
            self.ui.txtAvgRating.setText("0")
            self.ui.txtAvgRating.setFont(font)
            self.ui.txtAvgRating.setStyleSheet(css)
            self.ui.txtAvgRating.setAlignment(Qt.AlignCenter)
            self.ui.txtAvgOrders.setText("0")
            self.ui.txtAvgOrders.setFont(font)
            self.ui.txtAvgOrders.setStyleSheet(css)
            self.ui.txtAvgOrders.setAlignment(Qt.AlignCenter)

    def setRegionOrdersBarChart(self, Year='All', Region='All'):
        """
        Sets the region orders bar chart based on the specified year and region.

        Args:
            Year (str): The year for which the orders are to be displayed. Defaults to 'All'.
            Region (str): The region for which the orders are to be displayed. Defaults to 'All'.

        Returns:
            None
        """
        select = """ select r.region, count(distinct od.order_id)
                    from sales s, region r, order_details od
                    where s.region_key = r.region_key
                    and od.order_detail_key = s.order_detail_key"""

        group = """ group by r.region
                    order by 1"""
        if Year != 'All':
            select = select + " and s.calendar_key in (select calendar_key from calendar where year = "+Year+")"
        if Region != 'All':
            select = select + " and r.region = '"+Region+"'"
        if self.fromDate != None and self.toDate != None:
            select = select + " and s.calendar_key in (select calendar_key from calendar where full_date between '"+str(self.fromDate)+"' and '"+str(self.toDate)+"')"

        if self.RadioYear != None and self.RadioYear2 == None:
            select = select + " and s.calendar_key in (select calendar_key from calendar where year = "+str(self.RadioYear)+")"
        if self.RadioYear2 != None and self.RadioYear != None:
            select = select + " and s.calendar_key in (select calendar_key from calendar where year in ("+str(self.RadioYear2)+","+str(self.RadioYear)+"))"
        if self.RadioMonth != None:
            select = select + " and s.calendar_key in (select calendar_key from calendar where month >= "+str(self.RadioMonth)+")"

        sql = select+group
        cursor.execute(sql)
        orderData = cursor.fetchall()
        if len(orderData) > 0:
            labels = [region_name for region_name, _ in orderData]
            values = [order_count for _, order_count in orderData]

            bar_colors = ['skyblue', 'lightgreen', 'lightcoral', 'lightsalmon', 'aquamarine']

            fig, ax = plt.subplots(figsize=(5.5, 2.5))
            bars = ax.bar(labels, values, color=bar_colors)
            ax.set_xlabel('Region', fontsize=10)
            ax.set_ylabel('Order Count', fontsize=10)
            ax.set_title('Total Orders by Region', fontsize=10)

            for bar, value in zip(bars, values):
                yval = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2, yval, round(value, 2), ha='center', va='bottom', fontsize=8)
            ax.tick_params(axis='x', labelsize=8)
            ax.tick_params(axis='y', labelsize=8)
            canvas = FigureCanvas(fig)
            while self.ui.barChartLayout.count():
                item = self.ui.barChartLayout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            self.ui.barChartLayout.addWidget(canvas)
            plt.close(fig)
        else:
            while self.ui.barChartLayout.count():
                item = self.ui.barChartLayout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            noData = QLabel("No Data")
            noData.setStyleSheet("color: white; background-color: DodgerBlue;")
            noData.setAlignment(Qt.AlignCenter)
            self.ui.barChartLayout.addWidget(noData)

    def setOrderCountsStatusChart(self, Year='All', Region='All'):
        """
        Sets the order counts status chart based on the specified Year and Region.

        Args:
            Year (str): The year for filtering the order dates. Default is 'All'.
            Region (str): The region for filtering the order details. Default is 'All'.

        Returns:
            None
        """
        select = """select count(*), order_status from order_details where 1=1 """
                
        group = """ group by order_status
                order by 1"""
        
        if Year != 'All':
            select = select + " and order_date in (select full_date from calendar where year = "+Year+")"
        if Region != 'All':
            select = select + " and order_detail_key in (select order_detail_key from sales s, region r where s.region_key = r.region_key and r.region = '"+Region+"') "
        if self.fromDate != None and self.toDate != None:
            select = select + " and order_date between '"+str(self.fromDate)+"' and '"+str(self.toDate)+"'"
        
        if self.RadioYear != None and self.RadioYear2 == None:
            select = select + " and order_date in (select full_date from calendar where year = "+str(self.RadioYear)+")"
        if self.RadioYear2 != None and self.RadioYear != None:
            select = select + " and order_date in (select full_date from calendar where year in ("+str(self.RadioYear2)+","+str(self.RadioYear)+"))"
        if self.RadioMonth != None:
            select = select + " and order_date in (select full_date from calendar where month >= "+str(self.RadioMonth)+")"

        sql = select+group
        cursor.execute(sql)
        orderData = cursor.fetchall()
        if len(orderData) > 0:
            labels = [order_status for _, order_status in orderData]
            values = [order_count for order_count, _ in orderData]

            colors = ['gold', 'lightskyblue', 'lightcoral', 'lightgreen']
            fig, ax = plt.subplots(figsize=(3, 3))
            label_fontsize = 8
            ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors, textprops={'fontsize': label_fontsize})
            ax.set_title('Order Counts by Status', fontsize=10)
            canvas = FigureCanvas(fig)
            while self.ui.PieChartLayout.count():
                item = self.ui.PieChartLayout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            self.ui.PieChartLayout.addWidget(canvas)
            plt.close(fig)
        else:
            while self.ui.PieChartLayout.count():
                item = self.ui.PieChartLayout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            noData = QLabel("No Data")
            noData.setStyleSheet("color: white; background-color: DodgerBlue;")
            noData.setAlignment(Qt.AlignCenter)
            self.ui.PieChartLayout.addWidget(noData)

    def setOrderCountsByYearChart(self, Year='All', Region='All'):
        """
        Sets the order counts by year chart in the GUI.

        Args:
            Year (str): The year to filter the data by. Default is 'All'.
            Region (str): The region to filter the data by. Default is 'All'.
        """
        select = """select cd.year, monthname(cd.full_date), count(distinct od.order_id), cd.month
        from sales s, calendar cd, order_details od
        where s.calendar_key = cd.calendar_key
        and od.order_detail_key = s.order_detail_key"""

        group = """
         group by cd.year, monthname(cd.full_date), cd.month
        order by 1 desc,4"""
        
        if Year != 'All':
            select = select + " and cd.year = "+Year
        if Region != 'All':
            select = select + " and s.region_key in (select region_key from region where region = '"+Region+"')"
        if self.fromDate != None and self.toDate != None:
            select = select + " and cd.full_date between '"+str(self.fromDate)+"' and '"+str(self.toDate)+"'"

        if self.RadioYear != None and self.RadioYear2 == None:
            select = select + " and cd.year = "+str(self.RadioYear)
        if self.RadioYear2 != None and self.RadioYear != None:
            select = select + " and cd.year in ("+str(self.RadioYear2)+","+str(self.RadioYear)+")"
        if self.RadioMonth != None:
            select = select + " and cd.month >= "+str(self.RadioMonth)

        sql = select+group
        cursor.execute(sql)
        result = cursor.fetchall()
        if len(result) > 0:
            columns = ['year', 'month', 'total_orders','month_number']
            order_data = pd.DataFrame(result, columns=columns)

            fig, ax = plt.subplots(figsize=(6.5, 3))

            for year in order_data['year'].unique():
                data_by_year = order_data[order_data['year'] == year]
                ax.plot(data_by_year['month'], data_by_year['total_orders'], label=str(year))


            ax.set_xlabel('Month', fontsize=8)
            ax.set_ylabel('Total Orders', fontsize=8)
            ax.set_title('Order Trends by Year and Month', fontsize=10)
            ax.legend(loc='lower right', fontsize=8)
            ax.tick_params(axis='x', labelsize=6)
            ax.tick_params(axis='y', labelsize=6)

            canvas = FigureCanvas(fig)
            while self.ui.lineChartLayout.count():
                item = self.ui.lineChartLayout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            self.ui.lineChartLayout.addWidget(canvas)
            plt.close(fig)
        else:
            while self.ui.lineChartLayout.count():
                item = self.ui.lineChartLayout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            noData = QLabel("No Data")
            noData.setStyleSheet("color: white; background-color: DodgerBlue;")
            noData.setAlignment(Qt.AlignCenter)
            self.ui.lineChartLayout.addWidget(noData)

    def setQuantitiesByCategoryChart(self, Year='All', Region='All'):
        """
        Sets the quantities by category chart in the GUI based on the specified year and region.

        Args:
            Year (str, optional): The year to filter the data. Defaults to 'All'.
            Region (str, optional): The region to filter the data. Defaults to 'All'.
        """
        select = """select c.year, p.category_name, count(s.qty)
        from product p, sales s, order_details o, calendar c
        where s.product_key = p.product_key
        and o.order_detail_key = s.order_detail_key
        and c.calendar_key = s.calendar_key"""

        group = """ group by p.category_name, c.year
        order by 1 desc, 2"""

        if Year != 'All':
            select = select + " and c.year = "+Year
        if Region != 'All':
            select = select + " and s.region_key in (select region_key from region where region = '"+Region+"')"

        if self.fromDate != None and self.toDate != None:
            select = select + " and c.full_date between '"+str(self.fromDate)+"' and '"+str(self.toDate)+"'"

        if self.RadioYear != None and self.RadioYear2 == None:
            select = select + " and c.year = "+str(self.RadioYear)
        if self.RadioYear2 != None and self.RadioYear != None:
            select = select + " and c.year in ("+str(self.RadioYear2)+","+str(self.RadioYear)+")"
        if self.RadioMonth != None:
            select = select + " and c.month >= "+str(self.RadioMonth)

        sql = select+group
        cursor.execute(sql)
        result = cursor.fetchall()
        if len(result) > 0:
            df = pd.DataFrame(result, columns=['Year', 'Category', 'Quantity'])
            df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce').fillna(0)

            custom_colors = ['lightgreen', 'lightblue', 'gold', 'lightsalmon', 'lightcoral']

            # Pivot the DataFrame to create a matrix suitable for plotting
            pivot_df = df.pivot(index='Year', columns='Category', values='Quantity').fillna(0)

            fig, ax = plt.subplots(figsize=(4, 2.8))

            # Plotting
            pivot_df.plot(kind='bar', stacked=True, figsize=(4, 2.8), color=custom_colors, ax=ax, width=0.3)

            # Add labels and title
            ax.set_xlabel('Year', fontsize=8)
            ax.set_ylabel('Quantity', fontsize=8)
            ax.set_title('Year-wise Splits of Bike Quantities by Category', fontsize=10)

            # Add legend
            ax.legend(title='Category', loc='upper left',fontsize=6)
            ax.tick_params(axis='x', labelsize=6, rotation=0)
            ax.tick_params(axis='y', labelsize=6)
            # ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
            # Show the plot
            canvas = FigureCanvas(fig)
            while self.ui.StackBarLayout.count():
                item = self.ui.StackBarLayout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            self.ui.StackBarLayout.addWidget(canvas)
            plt.close(fig)
        else:
            while self.ui.StackBarLayout.count():
                item = self.ui.StackBarLayout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            noData = QLabel("No Data")
            noData.setStyleSheet("color: white; background-color: DodgerBlue;")
            noData.setAlignment(Qt.AlignCenter)
            self.ui.StackBarLayout.addWidget(noData)


    def populateTopProducts(self, Year='All', Region='All'):
        """
        Populates the top products table in the GUI based on the specified filters.

        Args:
            Year (str): The year to filter the data by. Default is 'All'.
            Region (str): The region to filter the data by. Default is 'All'.

        Returns:
            None
        """
        select = """select p.product_name, sum(qty) items_sold, count(distinct o.order_id) orders
                    from sales s, product p, calendar cd, order_details o
                    where s.product_key = p.product_key
                    and cd.calendar_key = s.calendar_key
                    and o.order_detail_key = s.order_detail_key
                    """
        group = """ group by p.product_name
                    order by 3 desc
                    limit 10"""
        if Year != 'All':
            select = select + " and cd.year = "+Year
        if Region != 'All':
            select = select + " and s.region_key in (select region_key from region where region = '"+Region+"')"
        if self.fromDate != None and self.toDate != None:
            select = select + " and cd.full_date between '"+str(self.fromDate)+"' and '"+str(self.toDate)+"'"

        if self.RadioYear != None and self.RadioYear2 == None:
            select = select + " and cd.year = "+str(self.RadioYear)
        if self.RadioYear2 != None and self.RadioYear != None:
            select = select + " and cd.year in ("+str(self.RadioYear2)+","+str(self.RadioYear)+")"
        if self.RadioMonth != None:
            select = select + " and cd.month >= "+str(self.RadioMonth)

        sql = select+group
        cursor.execute(sql)
        result = cursor.fetchall()
        self.ui.tblTopProducts.setRowCount(0)
        if len(result) > 0:
            self.ui.tblTopProducts.setRowCount(len(result))
            for row_number, row_data in enumerate(result):
                for column_number, data in enumerate(row_data):
                    item = QTableWidgetItem(str(data))
                    self.ui.tblTopProducts.setItem(row_number, column_number, item)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.ui.tblTopProducts.resizeColumnsToContents()
            
            colorsList = sns.light_palette("lightgreen", 10).as_hex()
            colorsList = colorsList[::-1]
            for rowIndex in range(self.ui.tblTopProducts.rowCount()):
                self.setColortoRow(rowIndex, QColor(colorsList[rowIndex]), self.ui.tblTopProducts)
        
    def setColortoRow(self, rowIndex, color, table):
        """
        Sets the background color of a specific row in the table.

        Args:
            rowIndex (int): The index of the row to set the color for.
            color (QColor): The color to set as the background color.

        Returns:
            None
        """
        # table = self.ui.tblTopProducts
        for j in range(table.columnCount()):
            table.item(rowIndex, j).setBackground(color)
            
    def on_btnEdEmplLarge_toggled(self):
        """
        Slot function called when the 'Sales Dashboard' button is clicked.
        """
        self.ui.ManagerDashboardStacked.setCurrentIndex(0)
    
    '''
    ***********  EMPLOYEE DASHBOARD  ***********
    =========================================
    Heirarchy:
    - emp_defaults()
    - populate_emp_state()
    - prepareFinalSql()
    - Set Charts
        - set_emp_Summary_labels()
        - top_Emp_by_sales_Chart()
        - pie_regions_by_emp_performance()
        - avg_rating_by_empregion()
        - populate_emp_datatable()
    =========================================
    '''
       
    def on_btnEmplDashLarge_toggled(self):
        """
        Slot function called when the 'Employee Dashboard' button is clicked.
        """
        self.ui.ManagerDashboardStacked.setCurrentIndex(1)
        self.emp_defaults()
        self.setupEmpCharts()
        
    def emp_defaults(self):
        """
        Sets the default values for the employee year and region dropdowns.

        Retrieves distinct years from the calendar table and populates the empYear dropdown.
        Retrieves distinct regions from the region table (excluding "Online") and populates the empRegion dropdown.
        """
        sql = """
        select distinct c.year
        from calendar c
        order by 1 desc
        """
        cursor.execute(sql)
        result = cursor.fetchall()
        self.ui.empYear.blockSignals(True)
        self.ui.empYear.clear()
        if len(result) > 0:
            self.ui.empYear.addItem("All")
            for row_number, row_data in enumerate(result):
                self.ui.empYear.addItem(str(row_data[0]))
        self.ui.empYear.blockSignals(False)
        
        sql = """
        select distinct r.region
        from region r
        where r.region != "Online"
        order by 1
        """
        cursor.execute(sql)
        result = cursor.fetchall()
        self.ui.empRegion.blockSignals(True)
        self.ui.empRegion.clear()
        if len(result) > 0:
            self.ui.empRegion.addItem("All")
            for row_number, row_data in enumerate(result):
                self.ui.empRegion.addItem(str(row_data[0]))
        self.ui.empRegion.blockSignals(False)
        
    def populate_emp_state(self):
        """
        Populates the employee state dropdown based on the selected region.

        If the selected region is not 'All', it retrieves distinct states from the database
        for the selected region and adds them to the employee state dropdown.
        If the selected region is 'All', it clears the employee state dropdown.

        Parameters:
        - self: The BikeStoreManagerDashDialog instance.

        Returns:
        None
        """
        if self.ui.empRegion.currentText() != 'All':
            sql = """
            select distinct r.state
            from region r
            where r.region != "Online"
            and r.region = '"""+self.ui.empRegion.currentText()+"""'
            order by 1
            """

            cursor.execute(sql)
            result = cursor.fetchall()
            self.ui.empState.blockSignals(True)
            self.ui.empState.clear()
            if len(result) > 0:
                self.ui.empState.addItem("All")
                for row_number, row_data in enumerate(result):
                    self.ui.empState.addItem(str(row_data[0]))
            self.ui.empState.blockSignals(False)
        else:
            self.ui.empState.clear()
    
    def setupEmpCharts(self):
        """
        Sets up the employee charts based on the selected year, region, and state.

        Retrieves the selected year, region, and state from the UI elements.
        If any of the selections are empty, sets them to "All".
        Calls various methods to generate and populate the employee charts and data table.
        """
        Year = self.ui.empYear.currentText()
        if Year == "":
            Year = "All"
        Region = self.ui.empRegion.currentText()
        if Region == "":
            Region = "All"
        state = self.ui.empState.currentText()
        if state == "":
            state = "All"
        self.top_Emp_by_sales_Chart(Year, Region, state)
        self.pie_regions_by_emp_performance(Year, Region, state)
        self.set_emp_Summary_labels(Year, Region, state)
        self.avg_rating_by_empregion(Year, Region, state)
        self.populate_emp_datatable(Year, Region, state)
    
    @pyqtSlot(int)       
    def on_empYear_currentIndexChanged(self):
        self.setupEmpCharts()
        
    @pyqtSlot(int)
    def on_empRegion_currentIndexChanged(self):
        self.populate_emp_state()
        self.setupEmpCharts()
        
    @pyqtSlot(int)
    def on_empState_currentIndexChanged(self):
        self.setupEmpCharts()
                
    def prepareFinalSql(self, year, region, state, select, group, special="None"):
        """
        Prepare the final SQL query based on the provided parameters.

        Args:
            year (str): The year to filter the data by. If 'All', no year filter will be applied.
            region (str): The region to filter the data by. If 'All', no region filter will be applied.
            state (str): The state to filter the data by. If 'All', no state filter will be applied.
            select (str): The SELECT part of the SQL query.
            group (str): The GROUP BY part of the SQL query.
            special (str, optional): Special flag to indicate a special condition. Defaults to "None".

        Returns:
            str: The final SQL query.

        """
        if year != 'All':
            if special == "special":
                select = select + """ and year <= """+year
            else:
                select = select + """ and year = """+year
        if region != 'All':
            select = select + """ and region = '"""+region+"""' """
        if state != 'All':
            select = select + """ and state = '"""+state+"""' """
        
        sql = select+group
        return sql
    
    def top_Emp_by_sales_Chart(self, year='All', region='All', state='All'):
        """
        Generates a bar chart showing the top 5 employees by revenue generated.

        Args:
            year (str): The year for which the data is to be displayed. Default is 'All'.
            region (str): The region for which the data is to be displayed. Default is 'All'.
            state (str): The state for which the data is to be displayed. Default is 'All'.
        """
        select1 = """
        with top_emp as (select employee_id, round(sum(price),2) 
                        from employee_sales_view 
                        where 1=1 """

        if year == 'All':
            select1 = select1 + """ and year = (select max(year) from calendar) """

        group1 = """ group by employee_id
                order by 2 desc
                limit 5)
                """

        sql_part1 = self.prepareFinalSql(year, region, state, select1, group1)

        select2 = """
            select ev.year, ev.employee_id, ev.employee_name,
            round(sum(ev.price),2) as Revenue_generated, count(distinct ev.order_id) as count_of_orders
            from employee_sales_view ev, top_emp te 
            where ev.employee_id = te.employee_id """

        group2 = """
        group by year, employee_id, employee_name
        order by 1,4 desc;
        """

        sql_part2 = self.prepareFinalSql(year, region, state, select2, group2, "special")

        sql = sql_part1 + sql_part2
        cursor.execute(sql)
        result = cursor.fetchall()
        if len(result) > 0:
            df = pd.DataFrame(result, columns=['Year', 'Employee_ID', 'Employee_Name', 'Revenue_generated', 'count_of_orders'])

            pivot_df = df.pivot(index='Employee_Name', columns='Year', values='Revenue_generated')
            fig, ax = plt.subplots(figsize=(5, 3))
            pivot_df.plot(kind='bar', ax=ax)
            ax.set_title('Top 5 Employees by Revenue Generated', fontsize=10)
            ax.set_xlabel('Employee Name', fontsize=8)
            ax.set_ylabel('Revenue Generated', fontsize=8)
            ax.tick_params(axis='x', rotation=0, labelsize=6, right=True)
            ax.legend(loc='upper left')
            canvas = FigureCanvas(fig)
            while self.ui.EmpChart1.count():
                item = self.ui.EmpChart1.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            self.ui.EmpChart1.addWidget(canvas)
            plt.close(fig)
        else:
            while self.ui.EmpChart1.count():
                item = self.ui.EmpChart1.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            noData = QLabel("No Data")
            noData.setStyleSheet("color: white; background-color: DodgerBlue;")
            noData.setAlignment(Qt.AlignCenter)
            self.ui.EmpChart1.addWidget(noData)
        
    def avg_rating_by_empregion(self, year='All', region='All', state='All'):
        """
        Calculates the average rating by employee region.

        Args:
            year (str): The year to filter the data. Default is 'All'.
            region (str): The region to filter the data. Default is 'All'.
            state (str): The state to filter the data. Default is 'All'.

        Returns:
            None
        """
        select = """select year, region, round(avg(rating),1)
                    from employee_sales_view 
                    where 1=1 """

        group = """ 
            group by year, region
            order by 1,2 desc"""

        sql = self.prepareFinalSql(year, region, state, select, group)

        cursor.execute(sql)
        result = cursor.fetchall()
        if len(result) > 0:
            region_data = pd.DataFrame(result, columns=['Year', 'Region', 'Avg_Rating'])
            region_data['Avg_Rating'] = pd.to_numeric(region_data['Avg_Rating'], errors='coerce')
            if year != 'All' or region != 'All' or state != 'All':
                custom_colors = ['lightgreen', 'lightblue', 'gold', 'lightsalmon', 'lightcoral']
                pivot_df = region_data.pivot(index='Region', columns='Year', values='Avg_Rating').fillna(0)
                fig, ax = plt.subplots(figsize=(5, 3))
                pivot_df.plot(kind='bar', color=custom_colors, ax=ax)
            else:
                fig, ax = plt.subplots(figsize=(5, 3))
                for year in region_data['Year'].unique():
                    data_by_year = region_data[region_data['Year'] == year]
                    ax.plot(data_by_year['Region'], data_by_year['Avg_Rating'], label=str(year))
            ax.set_title('Average Rating by Region', fontsize=10)
            ax.set_xlabel('Region')
            ax.set_ylabel('Average Rating')
            ax.tick_params(axis='x', rotation=0, labelsize=6, right=True)
            ax.legend(loc='lower left')
            canvas = FigureCanvas(fig)
            while self.ui.EmpChart2.count():
                item = self.ui.EmpChart2.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            self.ui.EmpChart2.addWidget(canvas)
            plt.close(fig)
        else:
            while self.ui.EmpChart2.count():
                item = self.ui.EmpChart2.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            noData = QLabel("No Data")
            noData.setStyleSheet("color: white; background-color: DodgerBlue;")
            noData.setAlignment(Qt.AlignCenter)
            self.ui.EmpChart2.addWidget(noData)
    
    def populate_emp_datatable(self, year='All', region='All', state='All'):
        """
        Populates the employee datatable with sales and rating data.

        Args:
            year (str): The year to filter the data by. Default is 'All'.
            region (str): The region to filter the data by. Default is 'All'.
            state (str): The state to filter the data by. Default is 'All'.
        """
        select = """
        select employee_name, round(sum(price),2), count(distinct order_id) from employee_sales_view 
        where 1=1 """

        group = """ group by employee_name
        order by 2 desc
        limit 10
        """

        sql = self.prepareFinalSql(year, region, state, select, group)

        cursor.execute(sql)
        result = cursor.fetchall()
        self.ui.tblEmpSales.setRowCount(0)
        if len(result) > 0:
            self.ui.tblEmpSales.setRowCount(len(result))
            for row_number, row_data in enumerate(result):
                for column_number, data in enumerate(row_data):
                    item = QTableWidgetItem(str(data))
                    self.ui.tblEmpSales.setItem(row_number, column_number, item)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.ui.tblEmpSales.resizeColumnsToContents()

            colorsList = sns.light_palette("xkcd:golden", 10).as_hex()
            colorsList = colorsList[::-1]
            for rowIndex in range(self.ui.tblEmpSales.rowCount()):
                self.setColortoRow(rowIndex, QColor(colorsList[rowIndex]), self.ui.tblEmpSales)

        select = """
        select employee_name, round(avg(rating),2), count(distinct order_id)
        from employee_sales_view
        where 1=1 """

        group = """
        group by employee_name
        order by 3 desc 
        limit 10
        """

        sql = self.prepareFinalSql(year, region, state, select, group)

        cursor.execute(sql)
        result = cursor.fetchall()
        self.ui.tblEmpRating.setRowCount(0)
        if len(result) > 0:
            self.ui.tblEmpRating.setRowCount(len(result))
            for row_number, row_data in enumerate(result):
                for column_number, data in enumerate(row_data):
                    item = QTableWidgetItem(str(data))
                    self.ui.tblEmpRating.setItem(row_number, column_number, item)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.ui.tblEmpRating.resizeColumnsToContents()

            colorsList = sns.light_palette("#29F", 10).as_hex()
            colorsList = colorsList[::-1]
            for rowIndex in range(self.ui.tblEmpRating.rowCount()):
                self.setColortoRow(rowIndex, QColor(colorsList[rowIndex]), self.ui.tblEmpRating)
    
        
    def pie_regions_by_emp_performance(self, year = 'All', region = 'All', state = 'All'):
            """
            Generates pie charts to visualize revenue generated and count of orders by region based on employee performance.

            Parameters:
            - year (str): The year for which the data is to be analyzed. Default is 'All'.
            - region (str): The specific region for which the data is to be analyzed. Default is 'All'.
            - state (str): The specific state for which the data is to be analyzed. Default is 'All'.
            """
            select = """
            select region,
            round(sum(price),2) as Revenue_generated, COUNT(DISTINCT order_id) as count_of_orders
            from employee_sales_view
            where 1=1 """
            
            group = """
            group by region
            order by 1 desc;
            """
            
            sql = self.prepareFinalSql(year, region, state, select, group)
            
            cursor.execute(sql)
            result = cursor.fetchall()
            if len(result) > 0:
                df = pd.DataFrame(result, columns = ['Region', 'Revenue_generated', 'count_of_orders'])
                
                colors = ['gold', 'yellowgreen', 'lightcoral', 'lightskyblue', 'lightgreen', 'paleturquoise', 'peachpuff']
                labels = df['Region']
                values1 = df['Revenue_generated']
                values2 = df['count_of_orders']
                fig, ax = plt.subplots(figsize = (5, 3))
                ax.pie(values1, labels = labels, autopct = '%1.1f%%', startangle = 90, colors = colors, textprops={'fontsize': 6})
                ax.set_title('Revenue Generated by Region', fontsize = 10)
                canvas = FigureCanvas(fig)
                while self.ui.EmpPie1.count():
                    item = self.ui.EmpPie1.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                
                self.ui.EmpPie1.addWidget(canvas)
                plt.close(fig)
                
                fig, ax = plt.subplots(figsize = (5, 3))
                ax.pie(values2, labels = labels, autopct = '%1.1f%%', startangle = 90,colors = colors, textprops={'fontsize': 6})
                ax.set_title('Orders by Region', fontsize = 10)
                canvas = FigureCanvas(fig)  
                while self.ui.EmpPie2.count():
                    item = self.ui.EmpPie2.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                        
                self.ui.EmpPie2.addWidget(canvas)
                plt.close(fig)
            else:
                while self.ui.EmpPie1.count():
                    item = self.ui.EmpPie1.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                while self.ui.EmpPie2.count():
                    item = self.ui.EmpPie2.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                noData = QLabel("No Data")
                noData.setStyleSheet("color: white; background-color: DodgerBlue;")
                noData.setAlignment(Qt.AlignCenter)
                self.ui.EmpPie1.addWidget(noData)
                self.ui.EmpPie2.addWidget(noData)
        
    def format_labels(self):
        font = QFont()
        font.setPointSize(20)
        css = 'color: white; background-color: MediumBlue;'
        self.ui.lblTpRegion.setFont(font)
        self.ui.lblTpRegion.setStyleSheet(css)
        self.ui.lblTpRegion.setAlignment(Qt.AlignCenter)
        self.ui.lblTpState.setFont(font)
        self.ui.lblTpState.setStyleSheet(css)
        self.ui.lblTpState.setAlignment(Qt.AlignCenter)
        self.ui.lblTpEmpBus.setFont(font)
        self.ui.lblTpEmpBus.setStyleSheet(css)
        self.ui.lblTpEmpBus.setAlignment(Qt.AlignCenter)
        self.ui.lblEmpMaxOrders.setFont(font)
        self.ui.lblEmpMaxOrders.setStyleSheet(css)
        self.ui.lblEmpMaxOrders.setAlignment(Qt.AlignCenter)
        self.ui.lblEmpRating.setFont(font)
        self.ui.lblEmpRating.setStyleSheet(css)
        self.ui.lblEmpRating.setAlignment(Qt.AlignCenter)
        self.ui.lblEmpLowSales.setFont(font)
        self.ui.lblEmpLowSales.setStyleSheet(css)
        self.ui.lblEmpLowSales.setAlignment(Qt.AlignCenter)
        
        font = QFont()
        font.setPointSize(15)
        css = 'color: white; background-color: SteelBlue;'
        self.ui.lblTpRegionDets.setFont(font)
        self.ui.lblTpRegionDets.setStyleSheet(css)
        self.ui.lblTpRegionDets.setAlignment(Qt.AlignCenter)
        self.ui.lblTpStateDets.setFont(font)
        self.ui.lblTpStateDets.setStyleSheet(css)
        self.ui.lblTpStateDets.setAlignment(Qt.AlignCenter)
        self.ui.lblTpEmpBusDets.setFont(font)
        self.ui.lblTpEmpBusDets.setStyleSheet(css)
        self.ui.lblTpEmpBusDets.setAlignment(Qt.AlignCenter)
        self.ui.lblEmpMaxOrdDets.setFont(font)
        self.ui.lblEmpMaxOrdDets.setStyleSheet(css)
        self.ui.lblEmpMaxOrdDets.setAlignment(Qt.AlignCenter)
        self.ui.lblEmpRatingDets.setFont(font)
        self.ui.lblEmpRatingDets.setStyleSheet(css)
        self.ui.lblEmpRatingDets.setAlignment(Qt.AlignCenter)
        self.ui.lblEmpLowSalesDets.setFont(font)
        self.ui.lblEmpLowSalesDets.setStyleSheet(css)
        self.ui.lblEmpLowSalesDets.setAlignment(Qt.AlignCenter)
        
        
    def setEmptyEmpLabels(self):
        self.ui.lblTpRegion.setText("")
        self.ui.lblTpRegionDets.setText("")
        self.ui.lblTpState.setText("")
        self.ui.lblTpStateDets.setText("")
        self.ui.lblTpEmpBus.setText("")
        self.ui.lblTpEmpBusDets.setText("")
        self.ui.lblEmpMaxOrders.setText("")
        self.ui.lblEmpMaxOrdDets.setText("")
        self.ui.lblEmpRating.setText("")
        self.ui.lblEmpRatingDets.setText("")
        self.ui.lblEmpLowSales.setText("")
        self.ui.lblEmpLowSalesDets.setText("")
        
    def set_emp_Summary_labels(self, Year='All', Region='All', State='All'):
        """
        Sets the summary labels for employee sales based on the specified filters.

        Args:
            Year (str): The year to filter the sales data. Default is 'All'.
            Region (str): The region to filter the sales data. Default is 'All'.
            State (str): The state to filter the sales data. Default is 'All'.
        """
        self.setEmptyEmpLabels()
        select = """
            select region, count(DISTINCT order_id)  as order_count,
            round(sum(price),2)  as Revenue_generated
            from employee_sales_view
            where 1=1 """
        group = """
            group by region
            order by 3 desc
            limit 1
            """
            
        sql = self.prepareFinalSql(Year, Region, State, select, group)
        cursor.execute(sql)
        result = cursor.fetchall()
        if len(result) > 0:
            self.ui.lblTpRegion.setText(str(result[0][0]))
            self.ui.lblTpRegionDets.setText(str(result[0][2]))
            
        select = """
            select  state, count(DISTINCT order_id) as order_count,
            round(sum(price),2)  as Revenue_generated
            from employee_sales_view
            where 1=1 """
        group = """
            group by state
            order by 3 desc
            limit 1
            """
            
        sql = self.prepareFinalSql(Year, Region, State, select, group)   
        cursor.execute(sql)
        result = cursor.fetchall()
        if len(result) > 0: 
            self.ui.lblTpState.setText(str(result[0][0]))
            self.ui.lblTpStateDets.setText(str(result[0][2]))
            
        select = """
            select employee_name,
            round(sum(price),2) as Revenue_generated
            from employee_sales_view
            where 1=1 """
        group = """
            group by employee_name
            order by 2 desc
            limit 1
        """
        
        sql = self.prepareFinalSql(Year, Region, State, select, group)
        
        cursor.execute(sql)
        result = cursor.fetchall()
        if len(result) > 0:
            self.ui.lblTpEmpBus.setText(str(result[0][0]))
            self.ui.lblTpEmpBusDets.setText(str(result[0][1]))
            
        select = """
            select employee_name,count(distinct order_id) as count_of_orders
            from employee_sales_view
            where 1=1 """
        group = """
            group by employee_name
            order by 2 desc
            limit 1
        """
            
        sql = self.prepareFinalSql(Year, Region, State, select, group)
        
        cursor.execute(sql)
        result = cursor.fetchall()
        if len(result) > 0:
            self.ui.lblEmpMaxOrders.setText(str(result[0][0]))
            self.ui.lblEmpMaxOrdDets.setText(str(result[0][1]))
            
        select = """
            select employee_name, count(distinct order_ID) AS TOTAL_ORDERS 
            from employee_sales_view
            where rating >= 4 """
        group = """
            group by employee_name
            order by 2 desc
            LIMIT 1
            """
        
        sql = self.prepareFinalSql(Year, Region, State, select, group)    
        cursor.execute(sql) 
        result = cursor.fetchall()
        if len(result) > 0:
            self.ui.lblEmpRating.setText(str(result[0][0]))
            self.ui.lblEmpRatingDets.setText(str(result[0][1]))  
            
        select = """
            select employee_name,
            round(sum(price),2) as Revenue_generated
            from employee_sales_view
            where 1=1 """
        group = """
            group by employee_name
            order by 2 asc
            limit 1

            """
            
        sql = self.prepareFinalSql(Year, Region, State, select, group)
        cursor.execute(sql)
        result = cursor.fetchall()
        if len(result) > 0:
            self.ui.lblEmpLowSales.setText(str(result[0][0]))
            self.ui.lblEmpLowSalesDets.setText(str(result[0][1]))
        
        self.format_labels()
    
    @pyqtSlot()
    def on_RefreshDwh_clicked(self):
        """
        Slot function called when the 'Refresh Data' button is clicked.
        """
        sql = """
            call refresh_dwh_prc(@refresh_status);
            """
        cursor.execute(sql)
        sql = """
            select @refresh_status;
            """
        cursor.execute(sql)
        result = cursor.fetchall()
        conn.commit()
        if len(result) > 0:
            if result[0][0] == "Success":
                QMessageBox.information(self, "Refresh Data", "Data Refreshed Successfully")
                self.setDefaults()
                self.emp_defaults()
                # self.setupCharts()
                self.setupEmpCharts()
            else:
                QMessageBox.warning(self, "Refresh Data", "Data Refresh Failed")