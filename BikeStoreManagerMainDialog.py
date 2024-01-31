'''
This file contains the main dialog for the Bike Store Manager.
Manager can view the employee details, update the employee details and create new employee.
Manager can also view the dashboard.
File: BikeStoreManagerMainDialog.py
Author: SQLWeavers
Project: Terrabikes
Course: DATA 225
'''
import sys
from PyQt5.QtWidgets import QDialog, QApplication, QLabel
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox
from BikeStoreManagerMainDialog_ui import Ui_BikeStoreManagerMainDialog
from BikeStoreUtils import create_connection
from PyQt5.QtCore import pyqtSlot, QDate, QRegExp, Qt
from PyQt5.QtGui import QRegExpValidator
from datetime import datetime
from BikeStoreManagerDashDialog import BikeStoreManagerDash

class BikeStoreManagerMain(QDialog):
    """
    The main dialog window for the Bike Store Manager application.

    Args:
        _username (str): The username of the manager.
        parent (QWidget): The parent widget. Defaults to None.
    """

    def __init__(self, _username, conn, cursor, parent=None):
        super(BikeStoreManagerMain, self).__init__(parent)
        self.ui = Ui_BikeStoreManagerMainDialog()
        self.ui.setupUi(self)
        self.conn = conn
        self.cursor = cursor

        self._BikeStoreMainWin = None

        self.ui.wdgtShortSidebar.hide()
        self.ui.ManagerPortalStacked.setCurrentIndex(0)
        self.ui.tblEmployee.setColumnCount(6)
        self.username = _username   
        self.populate_empl_details()
        self._setHeaderLabel(self.username)
        

    '''
    Helpers Methods
    '''    
    def _setHeaderLabel(self, _username):
        """
        Sets the header label with the customer name and current date.

        Args:
            _username (str): The username of the customer.
        """
        lblManagerHeader = self.ui.widget.findChild(QLabel, 'lblManagerHeader')
        current_date = QDate.currentDate()
        currDate = datetime.now().date()
        sql = """select concat(e.first_name,' ',e.last_name)
                from users u, employee e
                where e.employee_id = u.employee_id
                and upper(u.username) = upper(%s)"""
        self.cursor.execute(sql, (self.username,))
        result = self.cursor.fetchall()

        if len(result) > 0:
            self.emplName = result[0][0]   
            lblManagerHeader.setText("Manager Name: "+self.emplName+'\n'+'Date: '+str(currDate))
        else:
            lblManagerHeader.setText("Manager Name: "+self.username+'\n'+'Date: '+str(currDate)) 

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

    '''
    Methods for Employee Details
    ============================
    Stack Index: 0
    '''
    def populate_empl_details(self):
        """
        Populates the employee details in the table widget.

        Retrieves employee details from the database based on the logged-in user's username.
        The employee details include employee ID, name, status, end date, region, and order count.
        The retrieved data is then displayed in the table widget.

        Parameters:
        - self: The instance of the class.

        Returns:
        - None
        """
        sql = """
        select e.employee_id, concat(e.first_name, ' ', e.last_name) as Employee_Name, e.status, 
        e.end_date, r.region, (select count(order_id) from orders where employee_id = e.employee_id)as order_count
        from users u,manager m,employee e, regions r
        where u.username = %s
        and u.employee_id = m.manager_emp_id
        and e.region_id = r.region_id
        and e.manager_id = m.manager_id;
        """
        self.cursor.execute(sql, (self.username,))
        result = self.cursor.fetchall()
        self.ui.tblEmployee.setRowCount(0)

        if len(result) > 0:
            self.ui.tblEmployee.setRowCount(len(result))
            for row_number, row_data in enumerate(result):
                for column_number, data in enumerate(row_data):
                    item = QTableWidgetItem(str(data))
                    self.ui.tblEmployee.setItem(row_number, column_number, item)
                    self.ui.tblEmployee.resizeColumnsToContents()
                    self.ui.tblEmployee.setSortingEnabled(True)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)

    def on_tblEmployee_cellClicked(self, row, column):
        """
        Handle the event when a cell in the tblEmployee table is clicked.

        Args:
            row (int): The row index of the clicked cell.
            column (int): The column index of the clicked cell.
        """
        employee_id = self.ui.tblEmployee.item(row, 0).text()
        sql = """
            select e.employee_id, e.email_id, e.contact,e.address, r.state_name, r.city, e.emp_rating,
                    e.bonus, e.salary
            from employee e, regions r
            where e.region_id = r.region_id
            and e.employee_id = %s
            """
        self.cursor.execute(sql, (employee_id,))
        result = self.cursor.fetchall()

        if len(result) > 0:
            self.ui.tblEmployeeDetails.setRowCount(len(result))
            for row_number, row_data in enumerate(result):
                for column_number, data in enumerate(row_data):
                    item = QTableWidgetItem(str(data))
                    self.ui.tblEmployeeDetails.setItem(row_number, column_number, item)
                    self.ui.tblEmployeeDetails.resizeColumnsToContents()
                    self.ui.tblEmployeeDetails.setSortingEnabled(True)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)

    @pyqtSlot()
    def on_btnPg1UpdEmp_clicked(self):
        if self.ui.tblEmployee.selectedItems() == []:
            QMessageBox.warning(self, "Warning", "Please select an employee")
            return
        else:
            self.ui.ManagerPortalStacked.setCurrentIndex(1)
            self.ui.txtEmpId.setText(self.ui.tblEmployee.item(self.ui.tblEmployee.currentRow(), 0).text())
            self.on_btnSearchEmp_clicked()
            
    '''
    Methods for Employee Creation
    ============================
    Stack Index: 1
    '''
    def on_btnEdEmplLarge_toggled(self):
        """
        This method is triggered when the 'btnEdEmplLarge' button is toggled.
        It performs the following actions:
        1. Sets the current index of the ManagerPortalStacked widget to 1.
        2. Sets validators for various input fields.
        3. Clears the input fields.
        4. Sets the end date to '9999-12-31' and the start date to the current date.
        5. Disables the 'btnUpdEmployee' button.
        """
        if self.ui.btnEdEmplLarge.isChecked():
            self.ui.ManagerPortalStacked.setCurrentIndex(1)
            validator = QRegExpValidator(QRegExp("[0-9]{10}"))
            self.ui.EmplPgSalary.setValidator(validator)
            self.ui.EmplPgBonus.setValidator(validator)
            self.ui.EmplPgLeaves.setValidator(validator)
            self.ui.EmplPgPostalCode.setValidator(validator)
            validator = QRegExpValidator(QRegExp("[0-9]{3}-[0-9]{3}-[0-9]{4}"))
            self.ui.EmplPgPhone.setValidator(validator)
            # self.populateState()
            self.clear_fields()
            self.ui.EmplPgEndDate.setDate(QDate.currentDate().addYears(5))
            self.ui.EmplPgEndDate.setDisplayFormat("MM/dd/yyyy")
            self.ui.EmplPgStartDate.setDate(QDate.currentDate())
            self.ui.EmplPgStartDate.setDisplayFormat("MM/dd/yyyy")
            self.ui.btnUpdEmployee.setEnabled(False)

    def on_btnEmployeesLarge_toggled(self):
        if self.ui.btnEmployeesLarge.isChecked():
            self.ui.ManagerPortalStacked.setCurrentIndex(0) 

    def on_txtEmpName_textChanged(self):
        """
        This method is called when the text in the txtEmpName QLineEdit widget is changed.
        It retrieves the entered employee name, performs a database query to search for matching employee names,
        and populates the selectEmpName QComboBox widget with the matching names.

        Returns:
            None
        """
        emp_text = self.ui.txtEmpName.text()  
        if emp_text == '':
            self.ui.selectEmpName.clear()
            return
        sql = """
            select concat(e.first_name, ' ', e.last_name) 
            from employee e
            where upper(concat(e.first_name, ' ', e.last_name)) like upper(%s)
            """
        sqlparam = '%' + emp_text + '%'
        self.cursor.execute(sql, (sqlparam,))
        result = self.cursor.fetchall()
        self.ui.selectEmpName.clear()
        if len(result) > 0:
            self.ui.selectEmpName.addItems([row[0] for row in result])

    def populateState(self):
        """
        Loads the menus for Search Bar
        """
        sql = """ select distinct state_name from regions order by 1"""
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        if len(result) > 0:
            self.ui.EmplPgState.clear()
            for i in range(len(result)):
                self.ui.EmplPgState.addItem(result[i][0])

    def on_EmplPgState_currentTextChanged(self):
        state = self.ui.EmplPgState.currentText()
        self.populateCity(state)

    def populateCity(self, state):
        """
        Loads the menus for Search Bar
        """
        sql = """ select distinct city from regions where state_name = %s order by 1"""
        self.cursor.execute(sql, (state,))
        result = self.cursor.fetchall()
        if len(result) > 0:
            self.ui.EmplPageCity.clear()
            for i in range(len(result)):
                self.ui.EmplPageCity.addItem(result[i][0])

    @pyqtSlot()
    def on_btnSearchEmp_clicked(self):
        """
        Perform a search for an employee based on the provided employee ID or name.
        If the employee ID is provided, search for the employee with that ID.
        If the employee name is provided, search for the employee with that name.
        If neither the ID nor the name is provided, display a warning message.

        If a matching employee is found, populate the UI fields with the employee's information.
        """

        emp_Id = self.ui.txtEmpId.text()
        emp_name = self.ui.selectEmpName.currentText()
        sql = """
                select concat(e.first_name, ' ', e.last_name) as Name ,TRIm(SUBSTRING_INDEX(e.address, ',', 1)) address,r.state_name,r.city, TRIm(SUBSTRING_INDEX(e.address, ' ', -1)) as Postal_code
                ,e.contact,e.start_date,e.end_date,e.Salary,e.email_id,e.emp_rating,e.bonus,e.leaves_taken, u.username
                from employee e, regions r, users u
                where e.region_id = r.region_id
                and e.employee_id = u.employee_id

             """
        if emp_Id != '':
            sql += " and e.employee_id = %s"
            self.cursor.execute(sql, (emp_Id,))
            result = self.cursor.fetchall()
        elif emp_name != '':
            sql += " and concat(e.first_name, ' ', e.last_name) = %s"
            self.cursor.execute(sql, (emp_name,))
            result = self.cursor.fetchall()
        else:
            QMessageBox.warning(self, "Warning", "Please enter Employee Id or Name")
            return
        
        if len(result) > 0:
            self.ui.EmplPgEmplName.setText(result[0][0])
            self.ui.EmplPgEmplName.setReadOnly(True)
            self.ui.EmplPgAddress.setText(result[0][1])
            self.populateState()
            self.ui.EmplPgState.setCurrentText(result[0][2])
            self.populateCity(result[0][2])
            self.ui.EmplPageCity.setCurrentText(result[0][3])
            self.ui.EmplPgPostalCode.setText(result[0][4])
            self.ui.EmplPgPhone.setText(result[0][5])
            strDate = result[0][6].strftime('%Y-%m-%d')
            startDate = QDate.fromString(strDate, 'yyyy-MM-dd')
            self.ui.EmplPgStartDate.setDate(startDate)
            self.ui.EmplPgStartDate.setDisplayFormat("MM/dd/yyyy")
            self.ui.EmplPgStartDate.setReadOnly(True)
            self.ui.btnCreateEmployee.setEnabled(False)
            if result[0][7] == None:
                # endDate = QDate.fromString('0000-00-00', 'yyyy-MM-dd')
                endDate = QDate.currentDate().addYears(5)
            else:
                enDate = result[0][7].strftime('%Y-%m-%d')
                endDate = QDate.fromString(enDate, 'yyyy-MM-dd')
            self.ui.EmplPgEndDate.setDate(endDate)
            self.ui.EmplPgEndDate.setDisplayFormat("MM/dd/yyyy")
            self.ui.EmplPgSalary.setText(str(result[0][8]))
            self.ui.EmplPgEmail.setText(result[0][9])
            self.ui.EmplPgRating.setValue(result[0][10])
            self.ui.EmplPgBonus.setText(str(result[0][11]))
            self.ui.EmplPgLeaves.setText(str(result[0][12]))
            self.ui.EmplPgUsername.setText(result[0][13])
            self.ui.EmplPgUsername.setReadOnly(True)
            self.ui.EmplPgPassword.setReadOnly(True)
            self.ui.btnUpdEmployee.setEnabled(True)

    def validateFields(self, mode = "create"):
        """
        Validates the fields in the employee page.

        Checks if all the required fields are filled in. If any field is missing,
        it displays a warning message and sets the validation status to 'Fail'.
        Otherwise, it sets the validation status to 'Success'.

        Returns:
            None
        """
        self.validationStatus = 'Success'
        pwd = "DONT VALIDATE"
        if mode == "create":
            if self.ui.EmplPgPassword.text() == '':
                pwd = None
        if mode == "update":
            pwd = 'DONT VALIDATE'
               
        if (self.ui.EmplPgEmplName.text() == '' or 
            self.ui.EmplPgAddress.text() == '' or
            self.ui.EmplPgState.currentText() == '' or
            self.ui.EmplPageCity.currentText() == '' or
            self.ui.EmplPgPostalCode.text() == '' or
            self.ui.EmplPgPhone.text() == '' or
            self.ui.EmplPgSalary.text() == '' or
            self.ui.EmplPgEmail.text() == '' or
            self.ui.EmplPgRating.value() == '' or
            self.ui.EmplPgUsername.text() == '' or
            self.ui.EmplPgBonus.text() == '' or 
            self.ui.EmplPgLeaves.text() == '' or 
            pwd == None):
            QMessageBox.warning(self, "Warning", "Employee Details are Missing")
            self.validationStatus = 'Fail'    
        else:
            self.validationStatus = 'Success'

    @pyqtSlot()
    def on_btnUpdEmployee_clicked(self):
        """
        Handle the click event of the 'Update Employee' button.

        This method validates the fields, and if the validation is successful,
        it retrieves the values from the input fields and executes a SQL query
        to update the employee details in the database. If the update is successful,
        a success message is displayed, and the input fields are cleared.

        Args:
            None

        Returns:
            None
        """
        self.validateFields("update")
        if self.validationStatus == 'Success':
            if self.ui.EmplPgEndDate.text() == '12/31/99':
                endDate = None
                fEndDate = None
            else:
                endDate = self.ui.EmplPgEndDate.date()
                pyEndDate = endDate.toPyDate()
                fEndDate = pyEndDate.strftime('%Y-%m-%d')
            
            if self.ui.EmplPgLeaves.text() == '':
                leaves = int(0)
            else:
                leaves = int(self.ui.EmplPgLeaves.text())
            
            if self.ui.EmplPgBonus.text() == '':
                bonus = float(0)
            else:
                bonus = float(self.ui.EmplPgBonus.text())
                
                
            args = [
                self.ui.EmplPgEmplName.text(),
                self.ui.EmplPgAddress.text(),
                self.ui.EmplPgState.currentText(),
                self.ui.EmplPageCity.currentText(),
                self.ui.EmplPgPostalCode.text(),
                self.ui.EmplPgPhone.text(),
                fEndDate,
                self.ui.EmplPgSalary.text(),
                self.ui.EmplPgEmail.text(),
                self.ui.EmplPgRating.value(),
                bonus,
                leaves
            ]
            sql = """
                select update_employee(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """
            self.cursor.execute(sql, args)
            result = self.cursor.fetchall()
            self.conn.commit()
            if len(result) > 0:
                QMessageBox.information(self, "Success", "Employee Updated Successfully")
                self.clear_fields()
                self.ui.btnEmployeesLarge.setChecked(True)
                self.on_btnEmployeesLarge_toggled()
                self.populate_empl_details()

    @pyqtSlot()
    def on_btnCancel_clicked(self):
        self.clear_fields()
        self.ui.btnEmployeesLarge.setChecked(True)
        self.on_btnEmployeesLarge_toggled()
        self.populate_empl_details()

    @pyqtSlot()
    def on_btnClearFields_clicked(self):
        self.clear_fields()
        self.populateState()

    def clear_fields(self):
        """
        Clears all the input fields in the user interface for employee information.
        """
        self.ui.EmplPgEmplName.clear()
        self.ui.EmplPgEmplName.setReadOnly(False)               
        self.ui.EmplPgAddress.clear()
        self.populateState()        
        self.ui.EmplPageCity.clear()    
        self.ui.EmplPgPostalCode.clear()    
        self.ui.EmplPgPhone.clear()
        self.ui.EmplPgStartDate.setDate(QDate.currentDate())
        self.ui.EmplPgStartDate.setDisplayFormat("MM/dd/yyyy")
        self.ui.EmplPgStartDate.setReadOnly(False)
        self.ui.EmplPgEndDate.setDate(QDate.currentDate().addYears(5))
        self.ui.EmplPgEndDate.setDisplayFormat("MM/dd/yyyy")
        self.ui.EmplPgSalary.clear()
        self.ui.EmplPgEmail.clear()
        self.ui.EmplPgRating.clear()
        self.ui.EmplPgBonus.clear()
        self.ui.EmplPgLeaves.clear()
        self.ui.EmplPgUsername.clear()
        self.ui.EmplPgUsername.setReadOnly(False)   
        self.ui.EmplPgPassword.setReadOnly(False)
        self.ui.txtEmpId.clear()
        self.ui.txtEmpName.clear()
        self.ui.selectEmpName.clear()
        self.ui.btnUpdEmployee.setEnabled(False)
        self.ui.btnCreateEmployee.setEnabled(True)

    @pyqtSlot()
    def on_btnCreateEmployee_clicked(self):
        """
        Event handler for the 'Create Employee' button click.

        This method is called when the 'Create Employee' button is clicked in the GUI.
        It validates the input fields, retrieves the values from the GUI elements,
        and calls the database function to create a new employee record.
        If the employee is created successfully, it displays a success message,
        clears the input fields, and updates the employee details in the GUI.

        Args:
            None

        Returns:
            None
        """
        self.validateFields()
        if self.validationStatus == 'Success':
            if (self.ui.EmplPgEndDate.text() == '12/31/9999' or self.ui.EmplPgEndDate.text() == ''
            or self.ui.EmplPgEndDate.text() == '00/00/0000'):
                endDate = None
                fEndDate = None
            else:
                endDate = self.ui.EmplPgEndDate.date()
                pyEndDate = endDate.toPyDate()
                fEndDate = pyEndDate.strftime('%Y-%m-%d')

            startDate = self.ui.EmplPgStartDate.date()
            pyStartDate = startDate.toPyDate()
            fstartdate = pyStartDate.strftime('%Y-%m-%d')
            self.conn.autocommit = True
            args = [self.ui.EmplPgEmplName.text(),
                    self.ui.EmplPgAddress.text(),
                    self.ui.EmplPgState.currentText(),
                    self.ui.EmplPageCity.currentText(),
                    self.ui.EmplPgPostalCode.text(),
                    self.ui.EmplPgPhone.text(),
                    fstartdate,
                    fEndDate,
                    self.ui.EmplPgSalary.text(),
                    self.ui.EmplPgEmail.text(),
                    self.ui.EmplPgRating.value(),
                    self.ui.EmplPgBonus.text(),
                    self.ui.EmplPgLeaves.text(),
                    self.ui.EmplPgUsername.text(),
                    self.ui.EmplPgPassword.text(),
                    self.username
                    ]
            sql = """
                select create_employee(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                 """
            self.cursor.execute(sql, args)
            result = self.cursor.fetchall()
            self.conn.commit()
            if len(result) > 0:
                QMessageBox.information(self, "Success", "Employee Created Successfully")
                self.clear_fields()
                self.ui.btnEmployeesLarge.setChecked(True)
                self.on_btnEmployeesLarge_toggled()
                self.populate_empl_details()

    '''
    Methods for Manager Dashboards
    ============================
    '''
    def on_btnEmplDashLarge_toggled(self):
        if self.ui.btnEmplDashLarge.isChecked():
            self._bikeStoreManagerDashMain = BikeStoreManagerDash(self.username, parent=self)
            self._bikeStoreManagerDashMain.set_main_dialog(self._BikeStoreMainWin)
            self._bikeStoreManagerDashMain.exec_()
