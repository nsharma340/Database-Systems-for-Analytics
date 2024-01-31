'''
This file contains the code for the Main Window in the Bike Store Application.
File: BikeStoreMainWin.py
Author: SQLWeavers
Project: TerraBikes GUI
Course: Data 225
'''
import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QApplication
from BikeStoreSignUpDialog import BikeStoreSignUp
from BikeStoreResetPwdDialog import BikeStoreResetPwd
from BikeStoreCustMainDialog import BikeStoreCustMain
from BikeStoreEmplMainDialog import BikeStoreEmplMain
from BikeStoreManagerMainDialog import BikeStoreManagerMain
from BikeStoreUtils import create_connection

# Main Class for TerraBikes Application
class BikeStoreMainWin(QDialog):
    """
    The main window class for the TerraBikes application.

    This class represents the main window of the TerraBikes application. It provides functionality for user login, sign up, and password reset.
    """

    # Initialize the Main Window
    def __init__(self, parent=None):
        """
        Initialize the main window.

        Args:
            parent (QWidget): The parent widget. Defaults to None.
        """
        super(BikeStoreMainWin, self).__init__(parent)
        self.ui = uic.loadUi("BikeStoreMainWin.ui")
        self.ui.show()
        self.create_connection()
        # Capture Button Events
        self.ui.btnSignUp.clicked.connect(self._showBikeStoreNewSignUp)
        self.ui.btnForgetPass.clicked.connect(self._bikeStoreResetPass)
        self.ui.btnLogin.clicked.connect(self._bikeStoreLogin)

    def create_connection(self):
        # Connect to the database
        self.conn = create_connection(config_file='terrabikes.ini')
        self.cursor = self.conn.cursor()

    # Close Db connections
    def _close_db_connections(self):
        """
        Closes the database connections.

        This function closes the cursor and connection to the database.
        """
        self.cursor.close()
        self.conn.close() 

    def show_dialog(self):
        """
        Show the main window dialog.
        """
        self.ui.show()

    # Routine for Sign Up Button
    def _showBikeStoreNewSignUp(self):
        """
        Show the sign up dialog.

        This method is responsible for displaying the sign up dialog in the main window.
        It creates an instance of the `BikeStoreSignUp` class, sets the main dialog as its parent,
        hides the current main window, and shows the sign up dialog.
        """
        self._bikeStoreSignUp = BikeStoreSignUp(self.conn, self.cursor, parent=self)
        self._bikeStoreSignUp.set_main_dialog(self)
        self.ui.hide()
        self._bikeStoreSignUp.show_dialog()

    # Routine for Reset Password Button
    def _bikeStoreResetPass(self):
        """
        Show the password reset dialog.

        This method is called when the user wants to reset their password. It retrieves the username entered in the
        text field, creates an instance of the `BikeStoreResetPwd` class, and sets the main dialog as its parent.
        The main dialog is then hidden, and the password reset dialog is shown to the user.
        """
        _username = self.ui.txtUserName.text()
        self._bikeStoreResetPwd = BikeStoreResetPwd(_username, self.conn, self.cursor, parent=self)
        self._bikeStoreResetPwd.set_main_dialog(self)
        self.ui.hide()
        self._bikeStoreResetPwd.show_dialog()

    # Routine for Login Button
    def _bikeStoreLogin(self):
        """
        Perform user login.

        This method retrieves the username and password entered by the user from the GUI.
        It then executes a SQL query to check if the provided credentials are valid.
        If the credentials are valid, it checks the role of the user and opens the corresponding main window.
        If the role is 'Customer', it opens the Customer Main Window.
        If the role is 'Manager', it opens the Manager Main Window.
        If the role is 'Employee', it opens the Employee Main Window.
        If the role is not defined, it displays an error message.

        Parameters:
        - None

        Returns:
        - None
        """
        if self.conn.is_connected() == False:
            self.create_connection()
        # Get the username and password
        username = self.ui.txtUserName.text()
        password = self.ui.txtPass.text()
        sql = """ select t.role 
                    from users u, type t
                   where upper(u.username) = upper(%s) 
                     and u.pwd = md5(%s)
                     and t.user_role_id = u.user_role_id 
              """
        # Execute the query
        self.cursor.clear_attributes
        self.cursor.execute(sql, (username, password))
        result = self.cursor.fetchall()
        # Check the result
        if len(result) == 0:
            self.ui.lblLoginError.setText("Invalid username or password")
            return
        else:
            # Initialize the dialogs
            # Check the role
            # If the role is Customer, show the Customer Main Window
            if result[0][0] == 'Customer':
                self._bikeStoreCustMain = BikeStoreCustMain(username, self.conn, self.cursor, parent=self)
                self._bikeStoreCustMain.set_main_dialog(self)
                self.ui.hide()
                self._bikeStoreCustMain.exec_()
            # If the role is Manager, show the Manager Main Window
            elif result[0][0] == 'Manager':
                self._bikeStoreManagerMain = BikeStoreManagerMain(username, self.conn, self.cursor, parent=self)
                self._bikeStoreManagerMain.set_main_dialog(self)
                self.ui.hide()
                self._bikeStoreManagerMain.exec_()
            # If the role is Employee, show the Employee Main Window
            elif result[0][0] == 'Employee':
                self._bikeStoreEmplMain = BikeStoreEmplMain(username,self.conn, self.cursor, parent=self)
                self._bikeStoreEmplMain.set_main_dialog(self)
                self.ui.hide()
                self._bikeStoreEmplMain.exec_()
            else:
                # If the role is not defined, show the error message
                self.ui.lblLoginError.setText("System Error, Please contact admin")
                return

if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = BikeStoreMainWin()
    form.show_dialog()
    sys.exit(app.exec_())
