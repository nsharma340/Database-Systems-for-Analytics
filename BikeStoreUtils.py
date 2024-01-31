import os
from configparser import ConfigParser
from mysql.connector import MySQLConnection, Error
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from PyQt5.QtWidgets import QMessageBox


def read_config(config_file='config.ini', section='mysql'):
    """
    Reads the configuration file and returns the configuration parameters as a dictionary.

    Args:
        config_file (str): The path to the configuration file. Default is 'config.ini'.
        section (str): The section name in the configuration file. Default is 'mysql'.

    Returns:
        dict: A dictionary containing the configuration parameters.

    Raises:
        Exception: If the configuration file doesn't exist or the section is missing in the file.
    """
    parser = ConfigParser()
    if os.path.isfile(config_file):
        parser.read(config_file)
    else:
        raise Exception(f"Configuration file '{config_file}' doesn't exist.")

    config = {}

    if parser.has_section(section):
        items = parser.items(section)

        for item in items:
            config[item[0]] = item[1]

    else:
        raise Exception(f'Section [{section}] missing in config file {config_file}')

    return config

def create_connection(config_file='config.ini', section='mysql'):
    """
    Creates a connection to the MySQL database using the configuration parameters.

    Args:
        config_file (str): The path to the configuration file. Default is 'config.ini'.
        section (str): The section name in the configuration file. Default is 'mysql'.

    Returns:
        MySQLConnection: The connection object.

    Raises:
        Exception: If the connection fails.
    """
    try:
        db_config = read_config(config_file, section)
        conn = MySQLConnection(**db_config)

        if conn.is_connected():
            return conn

    except Error as e:
        raise Exception(f'Connection failed: {e}')
    
def DecisionBox(message, parent=None): 
    """
    Displays a confirmation message box with the given message and returns the user's reply.

    Parameters:
    - message (str): The message to be displayed in the confirmation box.
    - parent (QWidget): The parent widget for the message box. Defaults to None.

    Returns:
    - int: The user's reply. Returns QMessageBox.Ok if the user clicks the Ok button, and QMessageBox.Cancel if the user clicks the Cancel button.
    """
    msg_box = QMessageBox()
    reply = msg_box.question(parent, 'Confirmation', message, QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
    
    msg_box_width = 639
    msg_box_height = 479
    x = 600
    y = 350

    # Set the geometry of the QMessageBox
    msg_box.setGeometry(x, y, msg_box_width, msg_box_height)

    return reply


def popupMessage(message, type):
    """
    Displays a popup message box with the specified message and type.

    Args:
        message (str): The message to be displayed.
        type (str): The type of the message box. Possible values are 'Error', 'Success', or 'Warning'.
    """
    # Create QMessageBox
    msg_box = QMessageBox()
    if type == "Error":
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Error")
    elif type == "Success":
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Success")
    else:
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("Warning")

    msg_box.setText(message)

    msg_box_width = 639
    msg_box_height = 479
    x = 600
    y = 350

    # Set the geometry of the QMessageBox
    msg_box.setGeometry(x, y, msg_box_width, msg_box_height)

    # Show the QMessageBox
    msg_box.exec_()

def _show_custom_message(title, message, parent=None):
    """
    Displays a custom message box with the specified title and message.
    
    Args:
        title (str): The title of the message box.
        message (str): The message to be displayed in the message box.
        parent (QWidget, optional): The parent widget of the message box. Defaults to None.
    
    Returns:
        str: The button clicked by the user. Possible values are "Ok" or "Cancel".
    """
    message_box = QMessageBox()
    message_box.setParent(parent)
    message_box.setIcon(QMessageBox.Question)
    message_box.setWindowTitle(title)
    message_box.setText(message)
    message_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    
    result = message_box.exec_()

    if result == QMessageBox.Ok:
        return "Ok"
    elif result == QMessageBox.Cancel:
        return "Cancel"

def send_email(verificationCode, emailId):
    """
    Sends an email with the verification code to the specified email address.

    Args:
        verificationCode (str): The verification code to be sent.
        emailId (str): The email address of the recipient.

    Raises:
        Exception: If unable to send the email.
    """
    try:
        # Email configuration
        sender_email = "sqlweavers@gmail.com"
        receiver_email = emailId
        subject = "TerraBikes Reset Password - Verification Code"
        body = "This is your verification code: " + verificationCode

        # Create the email message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject

        # Attach the body to the message
        message.attach(MIMEText(body, "plain"))

        # Establish a connection with the SMTP server
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, "dfju nqvw ygil vslg")
            server.sendmail(sender_email, receiver_email, message.as_string())
    except Error as e:
        raise Exception(f'Unable to send Email: {e}')