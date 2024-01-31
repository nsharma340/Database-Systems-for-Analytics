'''
This file contains the code for the Reset Password Dialog in the Bike Store Application.
File: BikeStoreResetPwdDialog.py
Author: SQLWeavers
Project: TerraBikes GUI
Course: Data 225
'''
import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QApplication
import random
from BikeStoreUtils import create_connection, send_email, popupMessage

verificationCode = random.randint(100000, 999999)

class BikeStoreResetPwd(QDialog):
    """
    A dialog window for resetting the password in a bike store application.
    """

    def __init__(self, _username, conn, cursor, parent=None):
        """
        Initializes the BikeStoreResetPwd dialog.

        Args:
            _username (str): The username for which the password is being reset.
            parent (QWidget): The parent widget. Defaults to None.
        """
        super(BikeStoreResetPwd, self).__init__(parent)

        self.ui = uic.loadUi("BikeStoreResetPwdDialog.ui")
        self.conn = conn
        self.cursor = cursor

        self._initTxtFields(_username)
        # Set the Stacked Widget to the First Page
        self.ui.resetPassStacked.setCurrentIndex(0)
        # Handle the Cancel Button
        self.ui.btnCancel.clicked.connect(self._cancel)
        # Handle the Submit Button
        self.ui.btnSubmit.clicked.connect(self._submit)
        # Handle the Validate Button
        self.ui.btnValidate.clicked.connect(self._validate)
        # Handle the Reset Button
        self.ui.btnReset.clicked.connect(self._reset)

        self._BikeStoreMainWin = None

    '''
    Helper Methods, to be used by the main application
    '''
    def set_main_dialog(self, main_dialog):
        """
        Sets the main dialog window.

        Args:
            main_dialog (QWidget): The main dialog window.
        """
        self._BikeStoreMainWin = main_dialog

    def show_dialog(self):
        """
        Shows the dialog window.
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
    Auto Populate Username and Email if available from Previous Screen
    '''
    def _initTxtFields(self, _username):
        """
        Initializes the text fields in the dialog.

        Args:
            _username (str): The username for which the password is being reset.
        """
        # Auto Populate Username and Email if available from Previous Screen
        current_state = self.ui.txtUserName.isReadOnly()
        if _username != '':
            self.ui.txtUserName.setText(_username)
            sql = """select username, c.email_id, e.employee_id
                    from users u
                    left join customer c
                    on c.customer_id = u.customer_id
                    left join employee e
                    on e.employee_id = u.employee_id
                    where upper(u.username) = upper(%s)"""
            self.cursor.execute(sql, (self.ui.txtUserName.toPlainText(),))
            result = self.cursor.fetchall()
            if len(result) != 0:
                # if the Customer Email is available, populate the Email field
                if result[0][1] != '':
                    self.ui.txtEmail.setText(result[0][1])
                # If the Employee Email is available, populate the Email field
                elif result[0][2] != '':
                    self.ui.txtEmail.setText(result[0][2])
                else:
                    self.ui.txtEmail.setText('')
        else:
            # If Username is not available, make the field editable
            self.ui.txtUserName.setReadOnly(not current_state)

    '''
    Handle the Submit, Validate and Reset Buttons
    '''
    def _validate(self):
        """
        Handles the validate button click event.
        """
        if self.ui.txtVerCode.toPlainText() == '':
            popupMessage("Please enter the Verification Code", "Error")
        elif self.ui.txtVerCode.toPlainText() != str(verificationCode):
            popupMessage("Invalid Verification Code", "Error")
        else:
            popupMessage("Verification Successful", "Success")
            self.ui.resetPassStacked.setCurrentIndex(2)

    def _reset(self):
        """
        Handles the reset button click event.
        """
        if self.ui.txtNewPass.text() == '':
            popupMessage("Please enter the New Password", "Error")
        elif self.ui.txtConfirmPass.text() == '':
            popupMessage("Please Confirm the New Password", "Error")
        elif self.ui.txtNewPass.text() != self.ui.txtConfirmPass.text():
            popupMessage("Password Validation Failed", "Error")
        else:
            sql = """update users
                        set pwd = md5(%s)
                      where upper(username) = upper(%s)"""
            self.cursor.execute(sql, (self.ui.txtNewPass.text(), self.ui.txtUserName.toPlainText()))
            self.conn.commit()
            popupMessage("Password Reset Successful", "Success")

            # Navigate to the Login Screen
            self.ui.hide()
            if self._BikeStoreMainWin:
                self._BikeStoreMainWin.show_dialog()

    def _submit(self):
        """
        Handles the submit button click event.
        """
        if self.ui.txtUserName.toPlainText() == '':
            popupMessage("Please enter the Username", "Error")
        elif self.ui.txtEmail.toPlainText() == '':
            popupMessage("Please enter the Email", "Error")
        else:

            sql = """ select t.role 
                    from users u, type t
                   where upper(u.username) = upper(%s)
                     and t.user_role_id = u.user_role_id 
                  """
            # Execute the query
            self.cursor.execute(sql, (self.ui.txtUserName.toPlainText(),))
            result = self.cursor.fetchall()
            # Check the result
            if len(result) == 0:
                popupMessage("Username does not exist", "Error")
            else:
                send_email(str(verificationCode), self.ui.txtEmail.toPlainText())
                self.ui.resetPassStacked.setCurrentIndex(1)
