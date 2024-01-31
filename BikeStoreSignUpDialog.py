'''
This module contains the BikeStoreSignUp class, which represents the sign-up dialog for the bike store application.
File: BikeStoreSignUpDialog.py
Author: SQLWeavers
Project: TerraBikes GUI
Course: Data 225
'''
import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtCore import QRegExp   
from BikeStoreUtils import popupMessage, create_connection


class BikeStoreSignUp(QDialog):
    """
    Represents the sign-up dialog for the bike store application.
    """

    def __init__(self, conn, cursor, parent=None):
        """
        Initializes the BikeStoreSignUp dialog.

        Args:
            parent: The parent widget (default: None).
        """
        super(BikeStoreSignUp, self).__init__(parent)
        
        self.ui = uic.loadUi("BikeStoreSignUpDialog.ui")
        self._BikeStoreMainWin = None
        self.conn = conn
        self.cursor = cursor
        
        validator = QRegExpValidator(QRegExp("[0-9]{3}-[0-9]{3}-[0-9]{4}"))
        self.ui.txtPhone.setValidator(validator)

        # Handle the Cancel Button
        self.ui.btnCancel.clicked.self.connect(self._cancel)
        self.ui.txtState.currentIndexChanged.self.connect(self._txtState_currentIndexChanged)
        # Handle the Submit Button
        self.ui.btnSubmit.clicked.self.connect(self._submit)
        self._setStateSelection()
            
    def set_main_dialog(self, main_dialog):
        """
        Sets the main dialog.

        Args:
            main_dialog: The main dialog.
        """
        self._BikeStoreMainWin = main_dialog

    def show_dialog(self):
        """
        Shows the sign-up dialog.
        """
        self.ui.show()

    def _cancel(self):
        """
        Handles the cancel button click event.
        """
        self.ui.hide()
        if self._BikeStoreMainWin:
            self._BikeStoreMainWin.show_dialog() 
    
    
    '''
    Populate the State and City Dropdowns
    '''
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

    def _txtState_currentIndexChanged(self, index):
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

    
    '''
    Validate the Customer Details
    '''
    def _checkCustomerRequired(self):
        """
        Check if all required customer details are filled in the GUI form.
        If any required field is missing or if the username already exists in the database,
        display a warning message and set the validation status accordingly.
        """
        self._CustValidation = "Success"
        if (self.ui.txtFName.text() == "" or 
            self.ui.txtLName.text() == "" or 
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
    
    '''
    Submit the Customer Details for new Customer Creation
    '''
    def _submit(self):
        """
        Handles the submit button click event.
        """
        self._checkCustomerRequired()
        if self._CustValidation == "Success":
            self.conn.autocommit = True
            customerArgs = [self.ui.txtFName.text()
                        , self.ui.txtLName.text()
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
                self.ui.hide()
                if self._BikeStoreMainWin:
                    self._BikeStoreMainWin.show_dialog()  
