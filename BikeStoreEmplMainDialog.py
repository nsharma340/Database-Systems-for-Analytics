'''
This module contains the class for the Employee Portal.
The Employee Portal has the following functionalities:
    1. View Orders
    2. View Inventory
    3. View Grievances
    4. View Customers
    5. Place Order
    6. Update Order Status
    7. Update Inventory
    8. Update Grievance Status
    9. Disable Customer
    10. Delete Customer
File: BikeStoreEmplMainDialog.py
Project: Terrabikes
Author: SQLWeavers
Course: DATA 225    
'''
import sys
from PyQt5.QtWidgets import QDialog, QApplication, QLabel, QTableWidgetItem
from PyQt5.QtWidgets import QMessageBox, QWidget, QComboBox, QSpinBox, QLineEdit, QInputDialog
from BikeStoreEmplMainDialog_ui import Ui_BikeStoreEmplMainDialog
from BikeStoreUtils import create_connection, _show_custom_message
from datetime import datetime
from PyQt5.QtCore import QDate, pyqtSlot, QRegExp,Qt
from PyQt5.QtGui import QRegExpValidator

class BikeStoreEmplMain(QDialog):
    """
    Represents the main dialog for the employee portal in the Bike Store application.

    Args:
        _username (str): The username of the employee.
        parent (QWidget): The parent widget. Defaults to None.
    """

    def __init__(self, _username, conn, cursor, parent=None):
        super(BikeStoreEmplMain, self).__init__(parent)
        self.ui = Ui_BikeStoreEmplMainDialog()
        self.ui.setupUi(self)
        self.conn = conn
        self.cursor = cursor

        self._BikeStoreMainWin = None

        self.ui.wdgtShortSidebar.hide()
        self.ui.EmployeePortalStacked.setCurrentIndex(0)
        self._username = _username
        self._showWelcome = "Yes"

        # EmployeePortalStacked = self.ui.widget.findChild(QStackedWidget, 'EmployeePortalStacked')

        self._setOrders(_username)
        self._setHeaderLabel(_username)

    '''
    Helper function to be used by the main dialog
    '''

    def set_main_dialog(self, main_dialog):
        """
        Sets the main dialog.

        Args:
            main_dialog: The main dialog.
        """
        self._BikeStoreMainWin = main_dialog

    def _setHeaderLabel(self, _username):
        """
        Sets the header label with the employee name and current date.

        Args:
            _username (str): The username of the employee.
        """
        lblEmployeeName = self.ui.widget.findChild(QLabel, 'lblEmployeeName')
        current_date = QDate.currentDate()
        currDate = datetime.now().date()
        sql = """select concat(e.first_name,' ',e.last_name)
                from users u, employee e
                where e.employee_id = u.employee_id
                and upper(u.username) = upper(%s)"""
        self.cursor.execute(sql, (self._username,))
        result = self.cursor.fetchall()

        if len(result) > 0:
            self.emplName = result[0][0]
            lblEmployeeName.setText("Employee Name: " + self.emplName + '\n' + 'Date: ' + str(currDate))
        else:
            lblEmployeeName.setText("Employee Name: " + _username + '\n' + 'Date: ' + str(currDate))

    @pyqtSlot()
    def on_btnSignOut_clicked(self):
        """
        Handles the sign out button click event.
        """
        self.close()
        if self._BikeStoreMainWin:
            self._BikeStoreMainWin.show_dialog()

    '''
    Functions for Orders Page
    =========================
    Stack Index = 0
    '''

    def on_btnOrdersLarge_toggled(self):
        self.ui.EmployeePortalStacked.setCurrentIndex(0)
        self._setOrders(self._username)

    def _setOrders(self, username):
        """
        Sets the orders table with the orders of the employee.

        Args:
            username (str): The username of the employee.
        """
        if self.ui.EmployeePortalStacked.currentIndex() == 0:
            sql = """
                    select o.order_id, o.order_status, o.ordered_date, o.shipped_date, 
                    concat(c.first_name,' ',c.last_name) as customer_name, c.contact, c.address delivery_address, o.delivered_date
                    from orders o, employee e, customer c, users u
                    where upper(u.username) = upper(%s)
                    AND u.employee_id = e.employee_id
                    AND o.employee_id = e.employee_id
                    AND o.customer_id = c.customer_id;
                    """

            self.cursor.execute(sql, (username,))
            result = self.cursor.fetchall()

            if len(result) == 0:
                QMessageBox.warning(self, "Warning", "No Orders Found")
            else:
                if self._showWelcome == "Yes":
                    QMessageBox.information(self, "Success", "Number of Orders Found - " + str(len(result)))
                    self._showWelcome = "No"

                self.ui.tblPg1Orders.setRowCount(len(result))
                for i, row in enumerate(result):
                    for j, col in enumerate(row):
                        item = QTableWidgetItem(str(col))
                        self.ui.tblPg1Orders.setItem(i, j, item)
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.ui.tblPg1Orders.resizeColumnsToContents()
                self.ui.tblPg1Orders.setSortingEnabled(True)

    def on_tblPg1Orders_cellClicked(self, row, column):
        """
        Sets the order details table with the order details of the selected order.
        """
        if self.ui.EmployeePortalStacked.currentIndex() == 0:

            order_id = self.ui.tblPg1Orders.item(row, 0).text()
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
            self.cursor.execute(sql, (order_id,))
            result = self.cursor.fetchall()
            self.ui.tblPg1OrderDetails.clearContents()
            self.ui.tblPg1OrderDetails.setRowCount(len(result))
            for i, row in enumerate(result):
                for j, col in enumerate(row):
                    item = QTableWidgetItem(str(col))
                    self.ui.tblPg1OrderDetails.setItem(i, j, item)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.ui.tblPg1OrderDetails.resizeColumnsToContents()
            self.ui.tblPg1OrderDetails.setSortingEnabled(True)

    def _updateOrderStatus(self, action):
        """
        Update the status of an order based on the specified action.

        Args:
            action (str): The action to perform on the order. Possible values are "Shipped", "Delayed", or "Delivered".

        Returns:
            None
        """
        if self.ui.tblPg1Orders.rowCount() == 0:
            QMessageBox.warning(self, "Warning", "Please select an order")
        if self.ui.tblPg1Orders.rowCount() > 0:
            if (action == "Shipped" or action == "Delayed"):
                if self.ui.tblPg1Orders.item(self.ui.tblPg1Orders.currentRow(),1).text() == "New":
                    decision = _show_custom_message("Confirmation","Do you want to proceed?",self)
                    if decision == "Ok":
                        if action == "Shipped":
                            dateParam = 0
                        if action == "Delayed":
                            dateParam = 10
                        sql = """update orders set order_status = %s , shipped_date = now()+%s where order_id = %s"""
                        self.cursor.execute(sql,(action, dateParam, self.ui.tblPg1Orders.item(self.ui.tblPg1Orders.currentRow(),0).text(),))
                        self.conn.commit()
                        QMessageBox.information(self, "Success", "Order Updated")
                        self._setOrders(self._username)
                    if decision == "Cancel":
                        return
                else:
                    QMessageBox.warning(self, "Warning", "Order is already shipped or delivered")
                    return
            if action == "Delivered":
                if self.ui.tblPg1Orders.item(self.ui.tblPg1Orders.currentRow(),1).text() == "New":
                    QMessageBox.warning(self, "Warning", "Order is not shipped, it cannot be delivered")
                    return
                if self.ui.tblPg1Orders.item(self.ui.tblPg1Orders.currentRow(),1).text() == "Delivered":
                    QMessageBox.warning(self, "Warning", "Order is already delivered")
                    return
                if (self.ui.tblPg1Orders.item(self.ui.tblPg1Orders.currentRow(),1).text() == "Delayed" or
                    self.ui.tblPg1Orders.item(self.ui.tblPg1Orders.currentRow(),1).text() == "Shipped"):
                    decision = _show_custom_message("Confirmation","Do you want to proceed?",self)
                    if decision == "Ok":
                        sql = """update orders set order_status = %s , delivered_date = now() where order_id = %s"""
                        self.cursor.execute(sql,(action, self.ui.tblPg1Orders.item(self.ui.tblPg1Orders.currentRow(),0).text(),))
                        self.conn.commit()
                        QMessageBox.information(self, "Success", "Order Updated")
                        self._setOrders(self._username)
                    if decision == "Cancel":
                        return
    
    @pyqtSlot()
    def on_btnShipOrder_clicked(self):
        self._updateOrderStatus("Shipped")
    
    @pyqtSlot()
    def on_btnOrderDelay_clicked(self):
        self._updateOrderStatus("Delayed")
    
    @pyqtSlot()
    def on_btnOrderDelivered_clicked(self):
        self._updateOrderStatus("Delivered")

    '''
    Functions for Inventory Page
    ============================
    Stack Index = 1
    '''
    def on_btnInventoryLarge_toggled(self):
        self.ui.EmployeePortalStacked.setCurrentIndex(1)
        self._loadSelectionMenus()

    def _loadSelectionMenus(self):
        """
        Loads the menus for Search Bar.

        This method retrieves distinct values from the 'products', 'category', and 'warehouse' tables
        and populates the corresponding dropdown menus in the GUI with these values.
        """
        sql = """ select distinct product_id from products """
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        if len(result) > 0:
            self.ui.selectProd.clear()
            self.ui.selectProd.addItem("All")
            for i in range(len(result)):
                self.ui.selectProd.addItem(result[i][0])

        sql = """ select distinct category_name from category """
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        if len(result) > 0:
            self.ui.selectCat.clear()
            self.ui.selectCat.addItem("All")
            for i in range(len(result)):
                self.ui.selectCat.addItem(result[i][0])

        sql = """ select distinct warehouse_name from warehouse """
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        if len(result) > 0:
            self.ui.selectWarehouse.clear()
            self.ui.selectWarehouse.addItem("All")
            for i in range(len(result)):
                self.ui.selectWarehouse.addItem(result[i][0])

    @pyqtSlot()
    def on_btnSearch_clicked(self):
        """
        Sets the inventory details table with the inventory details.
        """
        if self.ui.EmployeePortalStacked.currentIndex() == 1:
            product_id = self.ui.selectProd.currentText()
            category_name = self.ui.selectCat.currentText()
            warehouse_name = self.ui.selectWarehouse.currentText()
            self._populateInventoryDetails(product_id,warehouse_name,category_name)
    
    def _populateInventoryDetails(self,product_id,warehouse_name,category_name):
        """
        Sets the inventory details table with the inventory details.
        """
        if self.ui.EmployeePortalStacked.currentIndex() == 1:
            sql = """
                    select p.product_id, p.product_name, c.category_name, b.brand_name, p.model_year, p.price, p.discount_percent, p.quantity, p.inventory_status
                    from products p, category c, brand b
                    where p.brand_id = b.brand_id
                    and c.category_id = p.category_id
                    """
            sql_params = ()
            if product_id != "All":
                sql += " and p.product_id = %s"
                sql_params = (product_id,)
            if category_name != "All":
                sql += " and c.category_name = %s"
                sql_params = sql_params + (category_name,)
            if warehouse_name != "All":
                sql += " and p.product_id in (select wi.product_id from warehouse_inventory wi, warehouse w where wi.warehouse_id = w.warehouse_id and w.warehouse_name = %s)"
                sql_params = sql_params + (warehouse_name,)
            if len(sql_params) > 0:
                self.cursor.execute(sql,sql_params)
            else:  
                self.cursor.execute(sql)
            result = self.cursor.fetchall()

            self.ui.tblProdList.clearContents()
            self.ui.tblWarehouse.clearContents()
            self.ui.tblWarehouse.setRowCount(0)
            self.ui.tblWarehouseOrders.clearContents()
            self.ui.tblWarehouseOrders.setRowCount(0)
            self.ui.tblProdList.setRowCount(len(result))
            for i, row in enumerate(result):
                for j, col in enumerate(row):
                    item = QTableWidgetItem(str(col))
                    self.ui.tblProdList.setItem(i, j, item)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.ui.tblProdList.resizeColumnsToContents()
            self.ui.tblProdList.setSortingEnabled(True)

    def on_tblProdList_cellClicked(self, row, column):
        """
        Sets the inventory details table with the inventory details.
        """
        if self.ui.EmployeePortalStacked.currentIndex() == 1:

            product_id = self.ui.tblProdList.item(row,0).text()
            sql = """
                    select wi.product_id, w.warehouse_id, w.warehouse_name, wi.quantity, w.address, w.contact, wi.status, wi.warehouse_inv_id
                    from warehouse w, warehouse_inventory wi
                    where w.warehouse_id = wi.warehouse_id
                    and wi.product_id = %s
                    """
            self.cursor.execute(sql,(product_id,))
            result = self.cursor.fetchall()

            self.ui.tblWarehouse.setRowCount(len(result))
            for i, row in enumerate(result):
                for j, col in enumerate(row):
                    item = QTableWidgetItem(str(col))
                    self.ui.tblWarehouse.setItem(i, j, item)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.ui.tblWarehouse.resizeColumnsToContents()
            self.ui.tblWarehouse.setSortingEnabled(True)
            self.on_tblWarehouse_cellClicked(0, 0)

    def on_tblWarehouse_cellClicked(self, row, column):
        """
        Sets the inventory details table with the inventory details.
        """
        if self.ui.EmployeePortalStacked.currentIndex() == 1:

            product_id = self.ui.tblWarehouse.item(row,0).text()
            warehouse_id = self.ui.tblWarehouse.item(row,1).text()
            sql = """
                    select ws.supply_order_id, wi.product_id, w.warehouse_name, ws.need_by_date, ws.qty_ordered, ws.shipment_status,
                    ws.creation_date
                    from warehouse w, warehouse_inventory wi, warehouse_supply ws
                    where w.warehouse_id = wi.warehouse_id
                    and wi.warehouse_inv_id = ws.warehouse_inv_id
                    and wi.product_id = %s
                    and w.warehouse_id = %s
                    """
            self.cursor.execute(sql,(product_id,warehouse_id))
            result = self.cursor.fetchall()

            self.ui.tblWarehouseOrders.setRowCount(len(result))
            for i, row in enumerate(result):
                for j, col in enumerate(row):
                    item = QTableWidgetItem(str(col))
                    self.ui.tblWarehouseOrders.setItem(i, j, item) 
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.ui.tblWarehouseOrders.resizeColumnsToContents()
            self.ui.tblWarehouseOrders.setSortingEnabled(True)

    @pyqtSlot()
    def on_btnWarehouseInv_clicked(self):
        """
        Handle the button click event for updating warehouse inventory.

        This method is triggered when the 'Warehouse Inventory' button is clicked.
        It checks if a product and a warehouse are selected, and prompts the user to enter a quantity.
        If a valid quantity is entered, it updates the inventory in the database and displays a success message.
        """
        if self.ui.tblProdList.rowCount() == 0:
            QMessageBox.warning(self, "Warning", "Please select a product")
        if self.ui.tblProdList.rowCount() > 0:
            if self.ui.tblWarehouse.rowCount() == 0:
                QMessageBox.warning(self, "Warning", "Please select a warehouse")
            if self.ui.tblWarehouse.rowCount() > 0:
                if not self.ui.tblWarehouse.selectedItems():
                    QMessageBox.warning(self, "Warning", "Please select a warehouse")
                    return
                else:
                    prodct_id = self.ui.tblProdList.item(self.ui.tblProdList.currentRow(),0).text()
                    warehouse_id = self.ui.tblWarehouse.item(self.ui.tblWarehouse.currentRow(),1).text()

                    validator = QRegExpValidator(QRegExp("[0-9]{10}"))
                    txtQuantity = QLineEdit()
                    txtQuantity.setValidator(validator)
                    text, ok = QInputDialog.getText(self, 'Input Dialog', 'Enter Quantity:', txtQuantity.Normal, '0')
                    if ok:
                        if text == "" or text == "0":
                            QMessageBox.warning(self, "Warning", "Please enter a valid quantity")
                            return
                        else:
                            warehouseInvArgs = [warehouse_id, prodct_id, int(text)]
                            self.cursor.execute("SELECT InsertWarehouseInventory(%s,%s,%s)", warehouseInvArgs)
                            _warehouseInvID = self.cursor.fetchone()[0]
                            self.conn.commit()
                            if _warehouseInvID != None:
                                QMessageBox.information(self, "Success", "Inventory Updated")
                                self.ui.tblWarehouse.clearContents()
                                self.ui.tblWarehouse.setRowCount(0)
                                self.ui.tblWarehouseOrders.clearContents()
                                self.ui.tblWarehouseOrders.setRowCount(0)
                                self.on_btnSearch_clicked()

    @pyqtSlot()
    def on_btnOrderInventory_clicked(self):
        """
        Handle the button click event for ordering inventory.

        This method checks if a warehouse is selected and if the selected warehouse has any stock available.
        If there is stock available, a confirmation message is shown to the user.
        If the user confirms the order, the inventory is ordered and the necessary tables are updated.
        If the user cancels the order, the method returns without performing any action.

        Args:
            None

        Returns:
            None
        """
        if self.ui.tblWarehouse.rowCount() == 0:
            QMessageBox.warning(self, "Warning", "Please select a warehouse")
        if self.ui.tblWarehouse.rowCount() > 0:
            if not self.ui.tblWarehouse.selectedItems():
                QMessageBox.warning(self, "Warning", "Please select a warehouse")
                return
            else:
                warehouseInvId = self.ui.tblWarehouse.item(self.ui.tblWarehouse.currentRow(),7).text()
                orderedQuantity = self.ui.tblWarehouse.item(self.ui.tblWarehouse.currentRow(),3).text()
                invStatus = self.ui.tblProdList.item(self.ui.tblProdList.currentRow(),6).text()
                if orderedQuantity == "0" or invStatus == "Out of Stock":
                    QMessageBox.warning(self, "Warning", "No Stock, Unable to Order Inventory")
                    return
                else:
                    decision = _show_custom_message("Confirmation","Do you want to proceed?",self)
                    if decision == "Ok":
                        warehouseSupplyArgs = [warehouseInvId, orderedQuantity]
                        self.cursor.execute("select InsertWarehouseSupply(%s,%s)",warehouseSupplyArgs)
                        _warehouseSupplyID = self.cursor.fetchone()[0]
                        self.conn.commit()
                        if _warehouseSupplyID != None:
                            QMessageBox.information(self, "Success", "Inventory Ordered")
                            self.ui.tblWarehouse.clearContents()
                            self.ui.tblWarehouse.setRowCount(0)
                            self.ui.tblWarehouseOrders.clearContents()
                            self.ui.tblWarehouseOrders.setRowCount(0)
                            self.on_btnSearch_clicked()
                    if decision == "Cancel":
                        return
    
    @pyqtSlot()
    def on_btnRcvdInventory_clicked(self):
        """
        Handle the event when the 'Receive Inventory' button is clicked.

        This method checks if an order is selected in the warehouse orders table.
        If an order is selected and the supply status is not 'Delivered', it prompts for confirmation.
        If confirmed, it updates the product inventory in the database and displays success or failure messages.
        Finally, it clears the contents of the warehouse and warehouse orders tables and triggers a search.

        Returns:
            None
        """
        if self.ui.tblWarehouseOrders.rowCount() == 0:
            QMessageBox.warning(self, "Warning", "Please select an order")
        if self.ui.tblWarehouseOrders.rowCount() > 0:
            if not self.ui.tblWarehouseOrders.selectedItems():
                QMessageBox.warning(self, "Warning", "Please select an order")
                return
            else:
                warehouseSupplyId = self.ui.tblWarehouseOrders.item(self.ui.tblWarehouseOrders.currentRow(),0).text()
                supplyStatus = self.ui.tblWarehouseOrders.item(self.ui.tblWarehouseOrders.currentRow(),5).text()
                if supplyStatus == "Delivered":
                    QMessageBox.warning(self, "Warning", "Inventory is already received")
                    return
                else:
                    decision = _show_custom_message("Confirmation","Do you want to proceed?",self)
                    if decision == "Ok":
                        self.cursor.execute("select UpdateProductInventory(%s)",(warehouseSupplyId,))
                        _returnVal = self.cursor.fetchone()[0]
                        self.conn.commit()
                        if _returnVal == 0:
                            QMessageBox.warning(self, "Warning", "Inventory Update Failed")
                            return
                        else:
                            QMessageBox.information(self, "Success", "Inventory Received")
                            self.ui.tblWarehouse.clearContents()
                            self.ui.tblWarehouse.setRowCount(0)
                            self.ui.tblWarehouseOrders.clearContents()
                            self.ui.tblWarehouseOrders.setRowCount(0)
                            self.on_btnSearch_clicked()
                    if decision == "Cancel":
                        return

    @pyqtSlot()
    def on_btnOutofStock_clicked(self):
        """
        Handle the button click event for marking a product as out of stock.

        If no product is selected, display a warning message.
        If the selected product is already out of stock, display a warning message.
        If the user confirms the action, update the product's quantity and inventory status in the database.
        Display a success message and refresh the product list.

        Returns:
            None
        """
        if self.ui.tblProdList.rowCount() == 0:
            QMessageBox.warning(self, "Warning", "Please select a product")
        if self.ui.tblProdList.rowCount() > 0:
            if (
                self.ui.tblProdList.item(self.ui.tblProdList.currentRow(), 7).text() == "0"
                or self.ui.tblProdList.item(self.ui.tblProdList.currentRow(), 8).text() == "Out of Stock"
            ):
                QMessageBox.warning(self, "Warning", "Product is already out of stock")
            else:
                decision = _show_custom_message("Confirmation", "Do you want to proceed?", self)
                if decision == "Ok":
                    sql = """update products set quantity = 0, inventory_status = 'Out of Stock' where product_id = %s"""
                    self.cursor.execute(sql, (self.ui.tblProdList.item(self.ui.tblProdList.currentRow(), 0).text(),))
                    self.conn.commit()
                    QMessageBox.information(self, "Success", "Product Updated")
                    self.on_btnSearch_clicked()
                if decision == "Cancel":
                    return

    @pyqtSlot()
    def on_btnDiscount_clicked(self):
        """
        Handle the event when the discount button is clicked.

        This method retrieves the discount percentage for a selected product from the database,
        prompts the user to enter a new discount percentage, and updates the database with the new value.
        Finally, it displays a success message and refreshes the product list and customer search.

        Args:
            None

        Returns:
            None
        """
        validator = QRegExpValidator(QRegExp("[0-9]{3}"))
        sql = """select discount_percent from products where product_id = %s"""
        product_id = self.ui.tblProdList.item(self.ui.tblProdList.currentRow(),0).text()
        self.cursor.execute(sql,(product_id,))
        result = self.cursor.fetchall()
        txtDiscount = QLineEdit()
        txtDiscount.setValidator(validator)
        if len(result) > 0:
            default_text = str(result[0][0])
        else:
            default_text = "0.00"
        text, ok = QInputDialog.getText(self, 'Input Dialog', 'Enter Discount %:', txtDiscount.Normal, default_text)
        if ok:
            sql = """update products set discount_percent = %s where product_id = %s"""
            self.cursor.execute(sql,(text,product_id))
            self.conn.commit()
            self.on_btnSearch_clicked()
            QMessageBox.information(self, "Success", "Discount Updated")
            self.on_btnCustSearch_clicked()

    '''
    Functions for Grievances Page
    =============================
    Stack Index = 2
    '''
    def on_btnComplaintsLarge_2_toggled(self):
        self.ui.EmployeePortalStacked.setCurrentIndex(2)
        self._populateComplaints()   

    def _populateComplaints(self):
        """
        Sets the complaints table with the complaints.
        """
        if self.ui.EmployeePortalStacked.currentIndex() == 2:
            sql = """
                    select f.record_type, f.order_id, f.creation_date, f.status, concat(c.first_name,' ',c.last_name) customer_name,
                    c.email_id, c.contact, f.comments, f.emp_comments
                    from feedback f, orders o, customer c
                    where f.record_type = 'GREVIANCE'
                    and o.order_id = f.order_id
                    and c.customer_id = o.customer_id
                    """
            self.cursor.execute(sql)
            result = self.cursor.fetchall()

            self.ui.tblGreviances.setRowCount(len(result))
            for i, row in enumerate(result):
                for j, col in enumerate(row):
                    item = QTableWidgetItem(str(col))
                    self.ui.tblGreviances.setItem(i, j, item)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.ui.tblGreviances.resizeColumnsToContents()
            self.ui.tblGreviances.setSortingEnabled(True)

    def on_tblGreviances_cellClicked(self, row, column):
        self.ui.GrvPgComments.setText(self.ui.tblGreviances.item(row,7).text())
        self.ui.GrvPgComments.setReadOnly(True)
        self.ui.GrvPgEmplComments.setText(self.ui.tblGreviances.item(row,8).text())   

    def _handleGrievance(self, action):
        """
        Handles the grievance based on the selected action.

        Args:
            action (str): The action to be taken on the grievance.

        Returns:
            None
        """
        if self.ui.tblGreviances.rowCount() == 0 or not self.ui.tblGreviances.selectedItems():
            QMessageBox.warning(self, "Warning", "Please select a grievance")
            return
        if self.ui.tblGreviances.rowCount() > 0:
            if (
                self.ui.tblGreviances.item(self.ui.tblGreviances.currentRow(), 3).text() == "Closed"
                or self.ui.tblGreviances.item(self.ui.tblGreviances.currentRow(), 3).text() == "Rejected"
            ):
                QMessageBox.warning(self, "Warning", "Grievance is already resolved")
            if (
                self.ui.tblGreviances.item(self.ui.tblGreviances.currentRow(), 3).text() == "Open"
                or self.ui.tblGreviances.item(self.ui.tblGreviances.currentRow(), 3).text() == "In Progress"
            ):
                if self.ui.GrvPgEmplComments.toPlainText() == "":
                    QMessageBox.warning(self, "Warning", "Please enter employee comments")
                    return

                decision = _show_custom_message("Confirmation", "Do you want to proceed?", self)
                if decision == "Ok":
                    sql = """update feedback set status = %s , emp_comments = %s, updated_date = now() where order_id = %s"""
                    self.cursor.execute(
                        sql,
                        (
                            action,
                            self.ui.GrvPgEmplComments.toPlainText(),
                            self.ui.tblGreviances.item(self.ui.tblGreviances.currentRow(), 1).text(),
                        ),
                    )
                    self.conn.commit()
                    QMessageBox.information(self, "Success", "Grievance Updated")
                    self._populateComplaints()
                if decision == "Cancel":
                    return
    
    @pyqtSlot()
    def on_btnResolveGrv_clicked(self):
        self._handleGrievance("Closed")

    @pyqtSlot()
    def on_btnRejectGrv_clicked(self):
        self._handleGrievance("Rejected")

    '''
    Functions for Customers Page
    ============================
    Stack Index = 3
    '''
    def on_btnCustomersLarge_toggled(self):    
        self.ui.EmployeePortalStacked.setCurrentIndex(3)
        self._loadCustSearchMenus()

    def _loadCustSearchMenus(self):
        """
        Loads the menus for Search Bar
        """
        sql = """ select distinct state_name from regions """
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        if len(result) > 0:
            self.ui.selectState.clear()
            self.ui.selectState.addItem("All")
            for i in range(len(result)):
                self.ui.selectState.addItem(result[i][0])

    @pyqtSlot()
    def on_btnCustSearch_clicked(self):
        """
        Sets the customers table with the customers.
        """
        if self.ui.EmployeePortalStacked.currentIndex() == 3:
            custId = self.ui.txtCustId.text()
            custName = self.ui.txtSrchCustName.text()
            state = self.ui.selectState.currentText()

            sql = """select customer_id, concat(first_name,' ',last_name) customer_name, status, end_date,
                        (select count(order_id) from orders where customer_id = c.customer_id) order_count,
                        contact, email_id, address, city, state_name, region
                        from customer c, regions r
                        where c.region_id = r.region_id"""
            sql_params = ()
            if custId != "":
                sql += " and customer_id = %s"
                sql_params = (custId,)
            if custName != "":
                sql += " and concat(first_name,' ',last_name) like %s"
                sql_params = sql_params + ('%'+custName+'%',)
            if state != "All":
                sql += " and state_name = %s"
                sql_params = sql_params + (state,)
            if len(sql_params) > 0:
                self.cursor.execute(sql,sql_params)
            else:
                self.cursor.execute(sql)
            result = self.cursor.fetchall()


            self.ui.tblCustomers.clearContents()
            self.ui.tblCustOrders.clearContents()
            self.ui.tblCustomers.setRowCount(len(result))
            for i, row in enumerate(result):
                for j, col in enumerate(row):
                    item = QTableWidgetItem(str(col))
                    self.ui.tblCustomers.setItem(i, j, item)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.ui.tblCustomers.resizeColumnsToContents()
            self.ui.tblCustomers.setSortingEnabled(True)

    def on_tblCustomers_cellClicked(self, row, column):
        """
        Sets the orders table with the orders of the customer.
        """
        if self.ui.EmployeePortalStacked.currentIndex() == 3:
            custId = self.ui.tblCustomers.item(row,0).text()
            sql = """select o.order_id, o.order_status, o.ordered_date, o.shipped_date, count(od.product_id) item_count,
                    sum(od.quantity) total_quantity, round(sum(price),2) total_price, sum(discount) total_discount
                    from orders o, order_details od
                    where o.order_id = od.order_id
                    and customer_id = %s
                    group by o.order_id, o.order_status, o.ordered_date, o.shipped_date"""
            self.cursor.execute(sql,(custId,))
            result = self.cursor.fetchall()

            self.ui.tblCustOrders.setRowCount(len(result))
            for i, row in enumerate(result):
                for j, col in enumerate(row):
                    item = QTableWidgetItem(str(col))
                    self.ui.tblCustOrders.setItem(i, j, item)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.ui.tblCustOrders.resizeColumnsToContents()
            self.ui.tblCustOrders.setSortingEnabled(True)

    @pyqtSlot()
    def on_BtnDisableCustomer_clicked(self):
        """
        Handle the click event of the 'Disable Customer' button.

        This method checks if a customer is selected in the table. If a customer is selected,
        it checks the status of the customer. If the customer is already disabled, it displays
        a warning message. If the customer is active, it displays a confirmation message to
        proceed with disabling the customer. If the user confirms, it updates the customer's
        status to 'INACTIVE' and sets the end date to the current date. It also updates the
        user's end date. Finally, it displays a success message and refreshes the customer
        search results.

        Returns:
            None
        """
        if self.ui.tblCustomers.rowCount() == 0:
            QMessageBox.warning(self, "Warning", "Please select a customer")

        if self.ui.tblCustomers.rowCount() > 0:
            if self.ui.tblCustomers.item(self.ui.tblCustomers.currentRow(), 2).text() == "INACTIVE":
                QMessageBox.warning(self, "Warning", "Customer is already disabled")

            if self.ui.tblCustomers.item(self.ui.tblCustomers.currentRow(), 2).text() == "ACTIVE":
                decision = _show_custom_message("Confirmation", "Do you want to proceed?", self)
                if decision == "Ok":
                    sql = """update customer set status = 'INACTIVE' , end_date = now() where customer_id = %s"""
                    self.cursor.execute(sql, (self.ui.tblCustomers.item(self.ui.tblCustomers.currentRow(), 0).text(),))
                    sql = """update users set end_date = now() where customer_id = %s"""
                    self.cursor.execute(sql, (self.ui.tblCustomers.item(self.ui.tblCustomers.currentRow(), 0).text(),))
                    self.conn.commit()
                    QMessageBox.information(self, "Success", "Customer disabled")
                    self.on_btnCustSearch_clicked()
                if decision == "Cancel":
                    return
        
    @pyqtSlot()
    def on_BtnDeleteCustomer_clicked(self):
        """
        Handle the click event of the delete customer button.

        If no customer is selected, display a warning message.
        If the selected customer is inactive, display a warning message.
        If the selected customer has orders, display a warning message.
        If the user confirms the deletion, delete the customer from the database.
        Refresh the customer table after deletion.

        Returns:
            None
        """
        if self.ui.tblCustomers.rowCount() == 0:
            QMessageBox.warning(self, "Warning", "Please select a customer")
        if self.ui.tblCustomers.rowCount() > 0:
            if self.ui.tblCustomers.item(self.ui.tblCustomers.currentRow(),2).text() == "INACTIVE":
                QMessageBox.warning(self, "Warning", "Customer is disabled, unable to Delete")
            if self.ui.tblCustomers.item(self.ui.tblCustomers.currentRow(),2).text() == "ACTIVE":
                sql = """select count(order_id) from orders where customer_id = %s"""
                self.cursor.execute(sql,(self.ui.tblCustomers.item(self.ui.tblCustomers.currentRow(),0).text(),))
                result = self.cursor.fetchall()
                if result[0][0] > 0:
                    QMessageBox.warning(self, "Warning", "Customer has orders, unable to Delete")
                else:
                    decision = _show_custom_message("Confirmation","Do you want to proceed?",self)  
                    if decision == "Ok":
                        sql = """delete from users where customer_id = %s"""
                        self.cursor.execute(sql,(self.ui.tblCustomers.item(self.ui.tblCustomers.currentRow(),0).text(),))
                        sql = """delete from customer where customer_id = %s"""
                        self.cursor.execute(sql,(self.ui.tblCustomers.item(self.ui.tblCustomers.currentRow(),0).text(),))
                        self.conn.commit()
                        QMessageBox.information(self, "Success", "Customer deleted")
                        self.on_btnCustSearch_clicked()
                    if decision == "Cancel":
                        return

    '''
    Functions for Walk-In Order Page
    ==============================
    Stack Index = 4
    '''

    def on_btnNewOrderLarge_toggled(self):    
        """
        Event handler for the 'New Order' button toggled signal.
        Switches the current index of the EmployeePortalStacked widget to display the 'New Order' screen.
        Hides the product widgets in the 'New Order' screen.
        Sets a phone number validator for the txtPhone QLineEdit widget.
        Sets the state selection if it is empty.
        Sets the product selection for the EOrderPgProd1 QComboBox widget if it is empty.
        """
        self.ui.EmployeePortalStacked.setCurrentIndex(4)
        # Hide Product Widgets in New Order Screen
        self.ui.widgetProd2.hide()
        self.ui.widgetProd3.hide()
        self.ui.widgetProd4.hide()
        self.ui.widgetProd5.hide()
        validator = QRegExpValidator(QRegExp("[0-9]{3}-[0-9]{3}-[0-9]{4}"))
        self.ui.txtPhone.setValidator(validator)
        validator = QRegExpValidator(QRegExp("[0-9]{5}"))
        self.ui.txtPostalCode.setValidator(validator)
        if self.ui.txtState.count() == 0:
            self._setStateSelection()
        if self.ui.EOrderPgProd1.count() == 0:
            self._setProductSelection()
    
    def _setStateSelection(self):
        """
        Sets the state selection options in the order page.
        """
        sql = """select DISTINCT state_name from regions order by 1"""
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        self.ui.txtState.clear()
        if len(result) > 0:
            self.ui.txtState.addItem("")
            for i in range(len(result)):
                self.ui.txtState.addItem(result[i][0])

    def on_txtState_currentIndexChanged(self, index):
        """
        Sets the city selection options in the order page.
        """
        if self.ui.txtState.currentText() != "":
            sql = """select DISTINCT city from regions where state_name = %s order by 1"""
            self.cursor.execute(sql,(self.ui.txtState.currentText(),))
            result = self.cursor.fetchall()
            self.ui.txtCity.clear()
            if len(result) > 0:
                self.ui.txtCity.addItem("")
                for i in range(len(result)):
                    self.ui.txtCity.addItem(result[i][0])         

    def _setProductSelection(self):
        """
        Sets the product selection options in the order page.
        """
        if self.ui.EmployeePortalStacked.currentIndex() == 4:
            for index_num in range(1,6):
                widgetProd = self.ui.widget.findChild(QWidget, 'widgetProd'+str(index_num))
                if index_num != 1:
                    widgetProd.hide()
                lblPrice = widgetProd.findChild(QLabel, 'ElblPrice'+str(index_num))
                lblPrice.setText('0.00')
                OrderPgProd = widgetProd.findChild(QComboBox, 'EOrderPgProd'+str(index_num))
                OrderPgProd.clear()
                sbQuantity = widgetProd.findChild(QSpinBox, 'EsbQuantity'+str(index_num))
                sbQuantity.clear()
                sbQuantity.setMinimum(0)
                lblSubtotal = widgetProd.findChild(QLabel, 'ElblSubtotal'+str(index_num))
                lblSubtotal.setText('')
                txtDiscount = widgetProd.findChild(QLabel, 'EtxtDiscount'+str(index_num))
                txtDiscount.setText('0.00')
                lblTotalPrice = self.ui.widget.findChild(QLabel, 'lblTotPrice')
                lblTotalPrice.setText('0.0')

        sql="""select CONCAT(product_id,' - ',product_name) as product from products"""
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        if len(result) > 0:
            for i in range(1, 6):
                widgetProd = self.ui.widget.findChild(QWidget, 'widgetProd'+str(i))
                OrderPgProd = widgetProd.findChild(QComboBox, 'EOrderPgProd'+str(i))
                OrderPgProd.addItems([i[0] for i in result])       

    def populatePriceQuantity(self, index_num):
        """
        Populates the price and quantity information for a selected product.

        Args:
            index_num (int): The index number of the product.

        Returns:
            None
        """
        widgetProd = self.ui.widget.findChild(QWidget, 'widgetProd'+str(index_num))
        OrderPgProd = widgetProd.findChild(QComboBox, 'EOrderPgProd'+str(index_num))
        lblPrice = widgetProd.findChild(QLabel, 'ElblPrice'+str(index_num))
        sbQuantity = widgetProd.findChild(QSpinBox, 'EsbQuantity'+str(index_num))
        txtDiscount = widgetProd.findChild(QLabel, 'EtxtDiscount'+str(index_num))

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
        lblPrice = widgetProd.findChild(QLabel, 'ElblPrice'+str(index_num))
        sbQuantity = widgetProd.findChild(QSpinBox, 'EsbQuantity'+str(index_num))
        lblSubtotal = widgetProd.findChild(QLabel, 'ElblSubtotal'+str(index_num))
        txtDiscount = widgetProd.findChild(QLabel, 'EtxtDiscount'+str(index_num))
        lblTotalPrice = self.ui.widget.findChild(QLabel, 'lblTotPrice')

        quantity = float(sbQuantity.value())
        price = float(lblPrice.text())
        if txtDiscount.text() == '':
            discount = 0
        else:    
            discount = float(txtDiscount.text())

        subtotal = (quantity * price) - (quantity*discount)
        lblSubtotal.setText(str(round(subtotal,2)))
        TotalPrice = 0
        for i in range(1, 6):
            lblSubtotal = self.ui.widget.findChild(QLabel, 'ElblSubtotal'+str(i))
            if lblSubtotal.text() != '':
                TotalPrice += float(lblSubtotal.text())
        lblTotalPrice.setText(str(round(TotalPrice,2)))

    # Handle Signals for Combo Box
    def on_EOrderPgProd1_currentIndexChanged(self, index):
        self.populatePriceQuantity(1)
        self.calculateSubtotals(1)
    
    def on_EOrderPgProd2_currentIndexChanged(self, index):
        self.populatePriceQuantity(2)
        self.calculateSubtotals(2)

    def on_EOrderPgProd3_currentIndexChanged(self, index):
        self.populatePriceQuantity(3)
        self.calculateSubtotals(3)

    def on_EOrderPgProd4_currentIndexChanged(self, index):
        self.populatePriceQuantity(4)
        self.calculateSubtotals(4)

    def on_EOrderPgProd5_currentIndexChanged(self, index):
        self.populatePriceQuantity(5)
        self.calculateSubtotals(5)

    def on_EsbQuantity1_valueChanged(self, value):
        self.calculateSubtotals(1)
    def on_EsbQuantity2_valueChanged(self, value):
        self.calculateSubtotals(2)
    def on_EsbQuantity3_valueChanged(self, value):
        self.calculateSubtotals(3)
    def on_EsbQuantity4_valueChanged(self, value):
        self.calculateSubtotals(4)
    def on_EsbQuantity5_valueChanged(self, value):
        self.calculateSubtotals(5)

    @pyqtSlot()
    def on_BtnSubmitOrder_clicked(self):
        """
        Slot function for the "Submit Order" button clicked event.
        """
        self._checkCustomerRequired()
        if self._CustValidation == "Success":
            if self.ui.lblTotPrice.text() == '0.0':
                QMessageBox.warning(self, "Warning", "Please select a product")
                return 
            else:
                self._createCustomer()
                self._createOrder()

    def _checkCustomerRequired(self):
        """
        Checks if all the required customer details are filled in the GUI form.
        If any required field is missing or if the username already exists in the database,
        it displays a warning message and returns an appropriate validation status.

        Returns:
            str: The validation status, which can be either "Success" or "Error".
        """
        self._CustValidation = "Success"
        if (self.ui.txtCustName.text() == "" or 
            self.ui.txtAddress.text() == "" or 
            self.ui.txtCity.currentText() == "" or 
            self.ui.txtState.currentText() == "" or
            self.ui.txtPostalCode.text() == "" or 
            self.ui.txtPhone.text() == "" or
            self.ui.txtEmail.text() == "" or 
            self.ui.txtUserName.text() == "" or
            self.ui.txtPassword.text() == ""):
            self._CustValidation = "Error"
            QMessageBox.warning(self, "Warning", "Customer Details are Missing")
            return
        
        if self.ui.txtUserName.text() != "":
            sql = """select count(*) from users where username = %s"""
            self.cursor.execute(sql,(self.ui.txtUserName.text(),))
            result = self.cursor.fetchall()
            if result[0][0] > 0:
                self._CustValidation = "Error"
                QMessageBox.warning(self, "Warning", "Username already exists")
                return

    def _createCustomer(self):
        """
        Creates a new customer and inserts their information into the database.

        Returns:
            None

        Raises:
            None
        """
        self.conn.autocommit = True
        fullname = self.ui.txtCustName.text()
        if len(fullname.split(' ')) == 1:
            firstname = fullname
            lastname = ''
        else:
            firstname = fullname.split(' ')[0]
            lastname = fullname.split(' ')[1]
            
        customerArgs = [firstname
                      , lastname
                      , self.ui.txtEmail.text()
                      , self.ui.txtPhone.text()
                      , self.ui.txtAddress.text()
                      , self.ui.txtUserName.text()
                      , self.ui.txtPassword.text()
                      , self.ui.txtState.currentText()
                      , self.ui.txtCity.currentText()
                      , self.ui.txtPostalCode.text()
                      ]
        self.cursor.execute("SELECT InsertCustomerAndUser(%s, %s,%s, %s,%s, %s,%s, %s,%s, %s)", customerArgs)
        self._user_id = self.cursor.fetchone()[0]
        self.conn.commit()
        if self._user_id == None or self._user_id == 0:
            QMessageBox.warning(self, "Warning", "Customer Creation Failed")
            return
        else:
            QMessageBox.information(self, "Success", "Customer Created Successfully")

    def _createOrder(self):
        """
        Creates an order based on the user input and inserts it into the database.

        Returns:
            None

        Raises:
            None
        """
        if self._user_id != None or self._user_id != 0:
            self.conn.autocommit = True
            self.cursor.execute("SELECT InsertOrder(%s, %s)", (self.ui.txtUserName.text(), self._username))
            _order_id = self.cursor.fetchone()[0]
            # self.conn.commit()

            if _order_id != None or _order_id != 0:
                _orderDetailIDs = []
                for i in range(1, 6):
                    widgetProd = self.ui.widget.findChild(QWidget, 'widgetProd'+str(i))
                    if not widgetProd.isVisible():
                        break
                    else:
                        OrderPgProd = widgetProd.findChild(QComboBox, 'EOrderPgProd'+str(i))
                        sbQuantity = widgetProd.findChild(QSpinBox, 'EsbQuantity'+str(i))
                        txtDiscount = widgetProd.findChild(QLabel, 'EtxtDiscount'+str(i))
                        lblSubtotal = widgetProd.findChild(QLabel, 'ElblSubtotal'+str(i))
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