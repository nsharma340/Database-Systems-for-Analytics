'''
This file contains the main dialog for the Bike Store Customer Portal.
It contains the logic for the customer portal and the functions for the
different pages in the portal.
    1. Orders Page
    2. New Orders Page
    3. Feedback Page
    4. Complaints Page
File: BikeStoreCustMainDialog.py
Author: SQLWeavers
Project: TerraBikes GUI
Course: Data 225
'''
import sys
from PyQt5.QtWidgets import QDialog, QApplication, QStackedWidget, QLabel, QTableWidgetItem, QComboBox,QSpinBox
from PyQt5.QtWidgets import QWidget, QTextEdit, QMessageBox
from BikeStoreCustMainDialog_ui import Ui_BikeStoreCustMainDialog
from BikeStoreUtils import create_connection
from datetime import datetime
from PyQt5.QtCore import pyqtSlot,Qt

class BikeStoreCustMain(QDialog):
    """
    Main dialog for the Bike Store Customer Portal.
    """

    def __init__(self, _username, conn, cursor, parent=None):
        """
        Initializes the BikeStoreCustMain dialog.

        Args:
            _username (str): The username of the customer.
            parent (QWidget): The parent widget. Defaults to None.
        """
        super(BikeStoreCustMain, self).__init__(parent)

        self.ui = Ui_BikeStoreCustMainDialog()
        self.ui.setupUi(self)
        self.conn = conn
        self.cursor = cursor
        self._BikeStoreMainWin = None
        self.ui.wdgtShortSidebar.hide()
        self.ui.CustomerPortalStacked.setCurrentIndex(0)
        self._username = _username
        self._showWelcome = "Yes"

        CustomerPortalStacked = self.ui.widget.findChild(QStackedWidget, 'CustomerPortalStacked')

        self._setOrders(_username)
        self._setHeaderLabel(_username)

    '''
    Helper functions used by Cust Main Dialog
    -----------------------------------------
    '''
    def set_main_dialog(self, main_dialog):
        """
        Sets the main dialog.

        Args:
            main_dialog: The main dialog.
        """
        self._BikeStoreMainWin = main_dialog

    @pyqtSlot()
    def on_btnSignOut_clicked (self):
        """
        Handles the cancel button click event.
        """
        self.close()
        if self._BikeStoreMainWin:
            self._BikeStoreMainWin.show_dialog() 

    def _setHeaderLabel(self, _username):
        """
        Sets the header label with the customer name and current date.

        Args:
            _username (str): The username of the customer.
        """
        lblCustomerName = self.ui.widget.findChild(QLabel, 'lblCustomerName')
        txtCustomerName = self.ui.widget.findChild(QTextEdit, 'OrderPgCustName')
        currDate = datetime.now().date()
        sql = """select concat(first_name,' ',c.last_name)
                from users u, customer c
                where c.customer_id = u.customer_id
                and upper(u.username) = upper(%s)"""
        self.cursor.execute(sql, (_username,))
        result = self.cursor.fetchall()

        if len(result) > 0:
            self.custName = result[0][0]   
            lblCustomerName.setText("Customer Name: "+self.custName+'\n'+'Date: '+str(currDate))
            txtCustomerName.setText(self.custName)
            txtCustomerName.setReadOnly(True)
        else:
            lblCustomerName.setText("Customer Name: "+_username+'\n'+'Date: '+str(currDate)) 
            txtCustomerName.setText(_username)
            txtCustomerName.setReadOnly(False)  

    '''
    Functions for Customers Orders Page
    ====================================
    Stack Index: 0
    '''
    def _setOrders(self,username):
        """
        Sets the orders table with the orders of the customer.

        Args:
            username (str): The username of the customer.
        """
        if self.ui.CustomerPortalStacked.currentIndex() == 0:
            sql = """
                    select o.order_id, o.order_status, o.ordered_date, o.shipped_date, concat(e.first_name, ' ', e.last_name) as "Sales Rep"
                    from orders o, employee e, customer c, users u
                    where upper(u.username) = upper(%s)
                    AND u.customer_id = c.customer_id
                    AND o.employee_id = e.employee_id
                    AND o.customer_id = c.customer_id;
                    """

            self.cursor.execute(sql,(username,))         
            result = self.cursor.fetchall()      
            self.ui.tblPg1Orders.clearContents()
            self.ui.tblPg1Orders.setRowCount(0)
            if len(result) == 0:
                QMessageBox.warning(self, "Warning", "No Orders Found")
            else:
                if self._showWelcome == "Yes":
                    QMessageBox.information(self, "Success", "Number of Orders Found - "+str(len(result)))
                    self._showWelcome = "No"
                stackCustPortalWidgets = self.ui.CustomerPortalStacked.currentWidget()
                tableOrders = self.ui.tblPg1Orders

                tableOrders.setRowCount(len(result))
                for i, row in enumerate(result):
                    for j, col in enumerate(row):
                        item = QTableWidgetItem(str(col))
                        tableOrders.setItem(i, j, item)
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                tableOrders.resizeColumnsToContents()
                tableOrders.setSortingEnabled(True)
                

    def on_tblPg1Orders_cellClicked(self, row, column):
        """
        Slot function for the tableOrders cell clicked event.
        
        This function is triggered when a cell in the tableOrders widget is clicked. It retrieves the order ID from the clicked cell,
        performs a SQL query to fetch the order details from the database, and populates the tableOrdersDetails widget with the fetched data.
        
        Args:
            row (int): The row index of the clicked cell.
            column (int): The column index of the clicked cell.
        """
        orderID = self.ui.tblPg1Orders.item(row,0).text()

        sql = """
             select p.product_id, p.product_name, p.price as "unit price", od.quantity, (p.price*od.quantity) as "gross price",
                od.discount, CASE WHEN od.discount is not null
                                THEN round(((p.price*od.quantity) - od.discount),2) 
                                ELSE round((p.price*od.quantity),2)
                                END as "net price"
                from orders o, order_details od, products p
                where o.order_id = od.order_id
                and p.product_id = od.product_id
                and o.order_id = %s;
            """
        self.cursor.execute(sql,(orderID,))  
        result = self.cursor.fetchall()
        self.ui.tblPg1OrderDetails.clearContents()
        self.ui.tblPg1OrderDetails.setRowCount(0)
        if len(result) > 0:

            tableOrdersDetails = self.ui.tblPg1OrderDetails

            tableOrdersDetails.setRowCount(len(result))
            for i, row in enumerate(result):
                for j, col in enumerate(row):
                    item = QTableWidgetItem(str(col))
                    tableOrdersDetails.setItem(i, j, item)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            tableOrdersDetails.resizeColumnsToContents()
            tableOrdersDetails.setSortingEnabled(True)

    def on_btnOrdersLarge_toggled(self):
        """
        Slot function for the "Orders" button toggled event.
        Sets the current index of the CustomerPortalStacked widget to 0.
        """
        self.ui.CustomerPortalStacked.setCurrentIndex(0) 
        self._setOrders(self._username)

    def on_btnCrOrderLarge_toggled(self):
        """
        Slot function for the "Create Order" button toggled event.
        Sets the current index of the CustomerPortalStacked widget to 1.
        """
        self.ui.CustomerPortalStacked.setCurrentIndex(1)
        self._setProductSelection()

    '''
    Functions for New Orders Page
    ====================================
    Stack Index: 1
    '''
    def _setProductSelection(self):
        """
        Sets the product selection options in the order page.
        """
        if self.ui.CustomerPortalStacked.currentIndex() == 1:
            for index_num in range(1,6):
                widgetProd = self.ui.widget.findChild(QWidget, 'widgetProd'+str(index_num))
                if index_num != 1:
                    widgetProd.hide()
                lblPrice = widgetProd.findChild(QLabel, 'lblPrice'+str(index_num))
                lblPrice.setText('0.00')
                OrderPgProd = widgetProd.findChild(QComboBox, 'OrderPgProd'+str(index_num))
                OrderPgProd.clear()
                sbQuantity = widgetProd.findChild(QSpinBox, 'sbQuantity'+str(index_num))
                sbQuantity.clear()
                sbQuantity.setMinimum(0)
                lblSubtotal = widgetProd.findChild(QLabel, 'lblSubtotal'+str(index_num))
                lblSubtotal.setText('')
                txtDiscount = widgetProd.findChild(QLabel, 'txtDiscount'+str(index_num))
                txtDiscount.setText('0.00')
                lblTotalPrice = self.ui.widget.findChild(QLabel, 'lblTotPrice')
                lblTotalPrice.setText('0.0')

        sql="""select CONCAT(product_id,' - ',product_name) as product from products"""
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        if len(result) > 0:
            for i in range(1, 6):
                widgetProd = self.ui.widget.findChild(QWidget, 'widgetProd'+str(i))
                OrderPgProd = widgetProd.findChild(QComboBox, 'OrderPgProd'+str(i))
                OrderPgProd.addItems([i[0] for i in result])

    def populatePriceQuantity(self, index_num):
        """
        Populates the price, quantity, and discount information for a selected product.

        Args:
            index_num (int): The index number of the product widget.

        Returns:
            None
        """
        widgetProd = self.ui.widget.findChild(QWidget, 'widgetProd'+str(index_num))
        OrderPgProd = widgetProd.findChild(QComboBox, 'OrderPgProd'+str(index_num))
        lblPrice = widgetProd.findChild(QLabel, 'lblPrice'+str(index_num))
        sbQuantity = widgetProd.findChild(QSpinBox, 'sbQuantity'+str(index_num))
        txtDiscount = widgetProd.findChild(QLabel, 'txtDiscount'+str(index_num))

        product_id = OrderPgProd.currentText().split(' - ')[0]
        
        sql = """select price,quantity,discount_percent from products where product_id = %s"""
        self.cursor.execute(sql,(product_id,))
        result = self.cursor.fetchall()

        if len(result) > 0:
            lblPrice.setText(str(result[0][0]))
            if result[0][2] != None:
                DiscountAmount = round(float((result[0][0] * result[0][2])/100),2)
                txtDiscount.setText(str(DiscountAmount))
            sbQuantity.setMinimum(0)
            sbQuantity.setMaximum(result[0][1])

    def calculateSubtotals(self, index_num):
        """
        Calculate the subtotals and total price for a given product.

        Args:
            index_num (int): The index number of the product.

        Returns:
            None
        """
        widgetProd = self.ui.widget.findChild(QWidget, 'widgetProd'+str(index_num))
        lblPrice = widgetProd.findChild(QLabel, 'lblPrice'+str(index_num))
        sbQuantity = widgetProd.findChild(QSpinBox, 'sbQuantity'+str(index_num))
        lblSubtotal = widgetProd.findChild(QLabel, 'lblSubtotal'+str(index_num))
        txtDiscount = widgetProd.findChild(QLabel, 'txtDiscount'+str(index_num))
        lblTotalPrice = self.ui.widget.findChild(QLabel, 'lblTotPrice')

        quantity = float(sbQuantity.value())
        price = float(lblPrice.text())
        if txtDiscount.text() == '':
            discount = 0
        else:    
            discount = float(txtDiscount.text())

        subtotal = (quantity * price) - (quantity * discount)
        lblSubtotal.setText(str(round(subtotal,2)))
        TotalPrice = 0
        for i in range(1, 6):
            lblSubtotal = self.ui.widget.findChild(QLabel, 'lblSubtotal'+str(i))
            if lblSubtotal.text() != '':
                TotalPrice += float(lblSubtotal.text())
        lblTotalPrice.setText(str(round(TotalPrice,2)))

    @pyqtSlot()
    def on_btnSubmitOrder_clicked(self):
        """
        Slot function for the "Submit Order" button clicked event.
        This function handles the logic for submitting an order in the GUI.
        It retrieves the necessary information from the GUI widgets and inserts the order and order details into the database.
        If the order submission is successful, it displays a success message and updates the GUI accordingly.
        If the order submission fails, it displays a warning message.
        """
        if self.ui.lblTotPrice.text() == '0.0':
            QMessageBox.warning(self, "Warning", "Please select a product to order")
            return
        else: 
            self.conn.autocommit = True
            self.cursor.execute("SELECT InsertOrder(%s, %s)", (self._username, 'ONL_DIRECT'))
            _order_id = self.cursor.fetchone()[0]
            # conn.commit()

            if _order_id != None or _order_id != 0:
                _orderDetailIDs = []
                for i in range(1, 6):
                    widgetProd = self.ui.widget.findChild(QWidget, 'widgetProd'+str(i))
                    if not widgetProd.isVisible():
                        break
                    else:
                        OrderPgProd = widgetProd.findChild(QComboBox, 'OrderPgProd'+str(i))
                        sbQuantity = widgetProd.findChild(QSpinBox, 'sbQuantity'+str(i))
                        txtDiscount = widgetProd.findChild(QLabel, 'txtDiscount'+str(i))
                        lblSubtotal = widgetProd.findChild(QLabel, 'lblSubtotal'+str(i))
                        product_id = OrderPgProd.currentText().split(' - ')[0]
                        quantity = float(sbQuantity.value())
                        if txtDiscount.text() == '':
                            discount = 0
                        else:    
                            discount = float(txtDiscount.text())
                        subtotal = float(lblSubtotal.text())
                        if quantity > 0:
                            orderDetailArgs = [_order_id, product_id, quantity, discount, subtotal]
                            self.cursor.execute("SELECT InsertOrderDetails(%s,%s,%s,%s,%s)", orderDetailArgs)
                            _orderDetailID = self.cursor.fetchone()[0]
                            self.conn.commit()
                            if _orderDetailID != None:
                                _orderDetailIDs.append(_orderDetailID)
                if len(_orderDetailIDs) > 0:
                    QMessageBox.information(self, "Success", "Order Submitted Successfully")
                    self.conn.commit()
                    self._setProductSelection()
                    self.ui.btnOrdersLarge.setChecked(True)
                    self.on_btnOrdersLarge_toggled()
                else:
                    QMessageBox.warning(self, "Warning", "Order Submission Failed")
    
    # Handle Signals for Combo Box
    def on_OrderPgProd1_currentIndexChanged(self, index):
        self.populatePriceQuantity(1)
        self.calculateSubtotals(1)
    
    def on_OrderPgProd2_currentIndexChanged(self, index):
        self.populatePriceQuantity(2)
        self.calculateSubtotals(2)

    def on_OrderPgProd3_currentIndexChanged(self, index):
        self.populatePriceQuantity(3)
        self.calculateSubtotals(3)

    def on_OrderPgProd4_currentIndexChanged(self, index):
        self.populatePriceQuantity(4)
        self.calculateSubtotals(4)

    def on_OrderPgProd5_currentIndexChanged(self, index):
        self.populatePriceQuantity(5)
        self.calculateSubtotals(5)

    def on_sbQuantity1_valueChanged(self, value):
        self.calculateSubtotals(1)
    def on_sbQuantity2_valueChanged(self, value):
        self.calculateSubtotals(2)
    def on_sbQuantity3_valueChanged(self, value):
        self.calculateSubtotals(3)
    def on_sbQuantity4_valueChanged(self, value):
        self.calculateSubtotals(4)
    def on_sbQuantity5_valueChanged(self, value):
        self.calculateSubtotals(5)

    def on_txtDiscount1_textChanged(self, text):
        self.calculateSubtotals(1)
    def on_txtDiscount2_textChanged(self, text):
        self.calculateSubtotals(2)
    def on_txtDiscount3_textChanged(self, text):
        self.calculateSubtotals(3)
    def on_txtDiscount4_textChanged(self, text):
        self.calculateSubtotals(4)
    def on_txtDiscount5_textChanged(self, text):
        self.calculateSubtotals(5)

    '''
    Functions for Customers Feedback Page
    ====================================
    Stack Index: 2
    '''
    def on_btnFeedbackLarge_toggled(self):
        """
        Slot function for the "Feedback" button toggled event.
        Sets the current index of the CustomerPortalStacked widget to 2.
        """
        self.ui.CustomerPortalStacked.setCurrentIndex(2)
        self._setFeedbackDefaults()

    def _setFeedbackDefaults(self):
        """
        Sets the default values for the feedback page.
        """
        self.ui.FdbkPgCustName.setText(self.custName)
        self.ui.FdbkPgCustName.setReadOnly(True)
        self.ui.FdbkPgOrderIds.clear()

        sql = """select concat('Order: ',order_id,' Status: ',order_status, ' Ordered Date: ', ordered_date)
                    from orders o, users u
                    where o.customer_id = u.customer_id
                    and upper(u.username) = upper(%s)"""
        self.cursor.execute(sql, (self._username,))
        resOrder = self.cursor.fetchall()
        if len(resOrder) > 0:
            self.ui.FdbkPgOrderIds.addItems([i[0] for i in resOrder])
    
    @pyqtSlot()
    def on_btnSubmitFeedback_clicked(self):
        """
        Slot function for the "Submit Feedback" button clicked event.
        """
        if self.ui.FdbkPgComments.toPlainText() == '':
            QMessageBox.warning(self, "Warning", "Please enter the feedback comments")
            return
        
        if self.ui.FdbkPgOrderIds.currentText() != '':
            sql = """
                select record_id from feedback where record_type = 'FEEDBACK' and order_id = %s
                """
            self.cursor.execute(sql, (self.ui.FdbkPgOrderIds.currentText().split(' ')[1],))
            result = self.cursor.fetchall()
            if len(result) > 0:
                QMessageBox.warning(self, "Warning", "Feedback already submitted for this order")
                return
            
        self.conn.autocommit = True
        feedbackArgs = [self._username, self.ui.FdbkPgOrderIds.currentText().split(' ')[1], self.ui.FdbkPgRating.text(), self.ui.FdbkPgComments.toPlainText(), None] 
        self.cursor.execute("SELECT InsertFeedback(%s, %s, %s, %s, %s)", feedbackArgs)
        _feedback_id = self.cursor.fetchone()[0]
        self.conn.commit()
        
        if _feedback_id != None or _feedback_id != 0:
            QMessageBox.information(self, "Success", "Thank you, Feedback Submitted Successfully!!")
            self._setFeedbackDefaults()
        else:
            QMessageBox.warning(self, "Warning", "Feedback Submission Failed")
    
    '''
    Functions for Customers Complaints Page
    ====================================
    Stack Index: 3
    '''
    def on_btnComplaintsLarge_toggled(self):    
        """
        Slot function for the "Complaints" button toggled event.
        Sets the current index of the CustomerPortalStacked widget to 3.
        """
        self.ui.CustomerPortalStacked.setCurrentIndex(3)
        self._setGrevianceParams()

    def _setGrevianceParams(self):
        """
        Sets the parameters for the grievance form.

        This method sets the initial values and enables/disables certain UI elements
        for the grievance form. It populates the dropdown menus with relevant data
        from the database and displays existing grievances in a table.

        Returns:
            None
        """
        self.ui.textCustomerName.setText(self.custName)
        self.ui.textCustomerName.setReadOnly(True)
        self.ui.GrvOrderIds.setEnabled(True)
        self.ui.GrvOrderIds.clear()
        self.ui.GrvIssueCat.setEnabled(True)
        self.ui.GrvIssueCat.clear()
        self.ui.grvIssueDetails.setReadOnly(False)
        self.ui.grvIssueDetails.clear()
        self.ui.GrvEmplComments.setReadOnly(True)
        self.ui.GrvEmplComments.clear()
        self.ui.BtnGrvSubmit.setEnabled(True)
        self.ui.lblGrvStatus.setText('New')

        sql = '''select distinct grevience_category 
                from feedback where grevience_category is not null'''
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        if len(result) > 0:
            self.ui.GrvIssueCat.addItems([i[0] for i in result])

        sql = """select concat('Order: ',order_id,' Status: ',order_status, ' Ordered Date: ', ordered_date)
                    from orders o, users u
                    where o.customer_id = u.customer_id
                    and upper(u.username) = upper(%s)"""
        self.cursor.execute(sql, (self._username,))
        resOrder = self.cursor.fetchall()
        if len(resOrder) > 0:
            self.ui.GrvOrderIds.addItems([i[0] for i in resOrder])


        sql = """select f.order_id, f.grevience_category, f.status, f.creation_date,f.comments, f.emp_comments
                    from feedback f, customer c, users u
                    where f.record_type = 'GREVIANCE'
                    and c.customer_id = f.customer_id
                    and c.customer_id = u.customer_id
                    and upper(u.username) = upper(%s)"""
        self.cursor.execute(sql, (self._username,))
        result = self.cursor.fetchall()
        if len(result) > 0:
            self.ui.tblGreviances.setRowCount(len(result))
            for i, row in enumerate(result):
                for j, col in enumerate(row):
                    item = QTableWidgetItem(str(col))
                    self.ui.tblGreviances.setItem(i, j, item)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.ui.tblGreviances.resizeColumnsToContents()
            self.ui.tblGreviances.setSortingEnabled(True)

    def on_tblGreviances_cellClicked(self, row, column):
        """
        Handle the cell click event in the tblGreviances table.

        Args:
            row (int): The row index of the clicked cell.
            column (int): The column index of the clicked cell.
        """
        self.ui.GrvOrderIds.setEnabled(False)
        self.ui.GrvIssueCat.setEnabled(False)
        self.ui.BtnGrvSubmit.setEnabled(False)
        self.ui.grvIssueDetails.setReadOnly(True)
        self.ui.GrvEmplComments.setReadOnly(True)
        self.ui.GrvOrderIds.addItems([self.ui.tblGreviances.item(row,0).text()])
        self.ui.GrvIssueCat.addItems([self.ui.tblGreviances.item(row,1).text()])
        self.ui.grvIssueDetails.setText(self.ui.tblGreviances.item(row,4).text())
        self.ui.GrvEmplComments.setText(self.ui.tblGreviances.item(row,5).text())
        self.ui.lblGrvStatus.setText(self.ui.tblGreviances.item(row,2).text())

    @pyqtSlot()
    def on_BtnNewGreviance_clicked(self):
        self._setGrevianceParams()
    
    @pyqtSlot()
    def on_BtnGrvSubmit_clicked(self):
        """
        Handle the button click event for submitting a grievance.

        This method retrieves the necessary information from the UI elements,
        executes a database query to insert the grievance feedback, and displays
        a success or failure message accordingly.

        Args:
            self: The object instance.

        Returns:
            None
        """
        if self.ui.grvIssueDetails.toPlainText() == '':
            QMessageBox.warning(self, "Warning", "Please enter the grievance details")
            return
        if self.ui.GrvOrderIds.currentText() != '':
            sql = """
                select record_id from feedback where record_type = 'GREVIANCE' and order_id = %s
                """
            self.cursor.execute(sql, (self.ui.GrvOrderIds.currentText().split(' ')[1],))
            result = self.cursor.fetchall()
            if len(result) > 0:
                QMessageBox.warning(self, "Warning", "Greviance already submitted for this order")
                return                
        self.conn.autocommit = True
        grevianceArgs = [self._username, self.ui.GrvOrderIds.currentText().split(' ')[1], None, self.ui.grvIssueDetails.toPlainText(), self.ui.GrvIssueCat.currentText()] 
        self.cursor.execute("SELECT InsertFeedback(%s, %s, %s, %s, %s)", grevianceArgs)
        _greviance_id = self.cursor.fetchone()[0]
        self.conn.commit()
        
        if _greviance_id != None or _greviance_id != 0:
            QMessageBox.information(self, "Success", "Greviance Submitted, We will be in touch!!")
            self._setGrevianceParams()
        else:
            QMessageBox.warning(self, "Warning", "Greviance Submission Failed")
