import sqlite3
from PyQt5 import QtWidgets
from PyQt5.uic import loadUi
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from flight_manager import FlightsManager

flight_manager = FlightsManager()


def add_to_widget(main_widget, window):
    main_widget.addWidget(window)
    main_widget.setCurrentIndex(main_widget.currentIndex() + 1)


class Starting(QDialog):
    def __init__(self, main_widget):
        super(Starting, self).__init__()
        self.main_widget = main_widget

        loadUi("view/starting_page.ui", self)
        self.starting_login.clicked.connect(self.login_button_clicked_from_starting_page)
        self.starting_create_acc.clicked.connect(self.create_acc_button_clicked_from_starting_page)

    def login_button_clicked_from_starting_page(self):
        login_window = Login(self.main_widget)
        add_to_widget(self.main_widget, login_window)

    def create_acc_button_clicked_from_starting_page(self):
        create_account_window = CreateAccount(self.main_widget)
        add_to_widget(self.main_widget, create_account_window)


class Login(QDialog):
    def __init__(self, main_widget):
        super().__init__()
        self.main_widget = main_widget
        loadUi("view/login_page.ui", self)
        self.login_pass.setEchoMode(QtWidgets.QLineEdit.Password)
        self.login_sign_up_button.clicked.connect(self.create_account_button_from_login_page)
        self.login_button.clicked.connect(self.login_button_clicked)

    def login_button_clicked(self):
        user_name = self.login_username.text()
        user_password = self.login_pass.text()

        if user_name == "" or user_password == "":
            msg = "Please fill all the fields*"
            self.error.setText(msg)
        else:
            # creating connection with sqlite database
            connection = sqlite3.connect("data/users.db")
            cursor = connection.cursor()
            query = 'SELECT password FROM login_accounts WHERE username =\'' + user_name + "\'"
            cursor.execute(query)
            result_from_db = cursor.fetchone()

            if result_from_db is None or result_from_db[0] != user_password:
                msg = "No such account exist!"
                self.error.setText(msg)
            else:
                flights_search = FlightsUi(self.main_widget)
                add_to_widget(self.main_widget, flights_search)

    def create_account_button_from_login_page(self):
        create_account_window = CreateAccount(self.main_widget)
        add_to_widget(self.main_widget, create_account_window)


class CreateAccount(QDialog):
    def __init__(self, main_widget):
        super().__init__()
        self.main_widget = main_widget
        loadUi("view/create_account_page.ui", self)
        self.create_acc_pass.setEchoMode(QtWidgets.QLineEdit.Password)
        self.create_acc_confirm_pass.setEchoMode(QtWidgets.QLineEdit.Password)
        self.create_acc_button.clicked.connect(self.login_button_clicked)
        self.login_button.clicked.connect(self.go_to_login_page)

    def go_to_login_page(self):
        login_page = Login(self.main_widget)
        add_to_widget(self.main_widget, login_page)

    def login_button_clicked(self):
        user_name = self.create_acc_username.text()
        user_password = self.create_acc_pass.text()
        user_confirm_password = self.create_acc_confirm_pass.text()
        if user_name == "" or user_password == "" or user_confirm_password == "":
            msg = "Please fill all the fields*"
            self.error.setText(msg)
        elif user_password != user_confirm_password:
            msg = "The passwords do not match"
            self.error.setText(msg)
        else:
            personal_info = PersonalInfo(self.main_widget, user_name, user_password)
            add_to_widget(self.main_widget, personal_info)


class PersonalInfo(QDialog):
    def __init__(self, main_widget, user_name, user_password):
        super(PersonalInfo, self).__init__()
        self.main_widget = main_widget
        self.all_details = [user_name, user_password]
        loadUi("view/personal_info.ui", self)
        self.register_button.clicked.connect(self.register_button_clicked)

    def register_button_clicked(self):
        self.all_details.extend([
            self.first_name.text(),
            self.second_name.text(),
            self.email.text(),
            self.mobile_num.text(),
            self.dob.text(),
            self.address.document().toPlainText()
        ])
        if "" in self.all_details:
            msg = "Please Fill all the details*"
            self.error.setText(msg)
        else:
            connection = sqlite3.connect("data/users.db")
            cursor = connection.cursor()
            query = 'INSERT INTO login_accounts (username, password, first_name, last_name, email,' \
                    'mobile_number, date_of_birth, address) VALUES (?,?,?,?,?,?,?,?)'
            cursor.execute(query, self.all_details)

            connection.commit()
            connection.close()

            self.open_login_portal()

    def open_login_portal(self):
        login_window = Login(self.main_widget)
        add_to_widget(self.main_widget, login_window)

    def get_details(self):
        return self.all_details


class FlightsUi(QDialog):
    def __init__(self, main_widget):
        super(FlightsUi, self).__init__()
        self.main_widget = main_widget
        loadUi("view/flight_bookings.ui", self)
        self.search_button.clicked.connect(self.load_flights_list_page)

    def load_flights_list_page(self):
        from_user_input = self.from_input.text()
        to_user_input = self.to_input.text()
        if not len(from_user_input) or not len(to_user_input):
            msg = "Please don't leave any field empty"
            self.error_msg.setText(msg)
            msg = ""
            self.help_msg.setText(msg)
        elif len(from_user_input) < 3 or len(to_user_input) < 3:
            msg = "Not enough characters in search box"
            self.error_msg.setText(msg)
            msg = ""
            self.help_msg.setText(msg)
        else:
            from_relevant_data = flight_manager.get_relevant_airports(from_user_input)
            to_relevant_data = flight_manager.get_relevant_airports(to_user_input)

            if not from_relevant_data or not to_relevant_data:
                msg = "Yo! Search something that exist"
                self.error_msg.setText(msg)
                msg = "Anything can do! airport name, country, state, city, iata code or similar*"
                self.help_msg.setText(msg)
            else:
                flights_list_page = FlightList(self.main_widget, from_relevant_data, to_relevant_data)
                add_to_widget(self.main_widget, flights_list_page)


class FlightList(QDialog):
    def __init__(self, main_widget, from_relevant_data, to_relevant_data):
        super(FlightList, self).__init__()
        self.main_widget = main_widget
        loadUi("view/flights_list_page.ui", self)

        self.from_model = QStandardItemModel()
        self.from_list.setModel(self.from_model)
        self.relevant_data_setter(self.from_model, from_relevant_data)

        self.to_model = QStandardItemModel()
        self.to_list.setModel(self.to_model)
        self.relevant_data_setter(self.to_model, to_relevant_data)

        self.search_again_button.clicked.connect(self.go_back_search_again_button_clicked)
        self.show_details_button.clicked.connect(self.show_flight_details_button_clicked)

    def show_flight_details_button_clicked(self):
        if not self.from_list.selectedIndexes() or not self.to_list.selectedIndexes():
            msg = "Please select all the fields*"
            self.error.setText(msg)
        else:
            index_of_from = self.from_list.selectedIndexes()[0]
            from_data = self.from_model.data(index_of_from, Qt.DisplayRole)
            index_of_to = self.to_list.selectedIndexes()[0]
            to_data = self.to_model.data(index_of_to, Qt.DisplayRole)

            flights_full_details = FullDetails(from_data, to_data, self.main_widget)
            add_to_widget(self.main_widget, flights_full_details)

    def go_back_search_again_button_clicked(self):
        search_window = FlightsUi(self.main_widget)
        add_to_widget(self.main_widget, search_window)

    def relevant_data_setter(self, model, relevant_data):
        for airport in relevant_data:
            data = airport['name'] + ', ' + airport['iata'] + ", " + \
                   airport['city'] + ", " + airport['country']['name'] \
                   + ", " + airport['country']['iso']
            model.appendRow(QStandardItem(data))


class FullDetails(QDialog):
    def __init__(self, from_data, to_data, main_widget):
        super(FullDetails, self).__init__()
        self.main_widget = main_widget
        loadUi("view/all_details.ui", self)
        self.flight_type.addItems(['round', 'oneway'])

        self.adults.setValue(1)

        self.main_user_data = {
            'fly_from': from_data.split(', ')[1],
            'fly_to': to_data.split(', ')[1],
            'curr': "INR",
            'limit': "10",
            'flight_type': 'round'
        }
        date = QDate.currentDate()
        self.from_date.setDate(date)
        self.to_date.setDate(date)

        self.show_flight_details_button.clicked.connect(self.set_all_user_data)
        self.search_again_button.clicked.connect(self.go_back_search_again_button_clicked)

        self.flight_type.currentIndexChanged.connect(self.currentIndexChanged)

    def currentIndexChanged(self, index):
        if str(self.flight_type.itemText(index)) == 'oneway':
            self.min_days.setDisabled(True)
            self.max_days.setDisabled(True)
            self.return_to.setDisabled(True)
            self.return_from.setDisabled(True)
            self.main_user_data['flight_type'] = 'oneway'
        else:
            self.min_days.setDisabled(False)
            self.max_days.setDisabled(False)
            self.return_to.setDisabled(False)
            self.return_from.setDisabled(False)
            self.main_user_data['flight_type'] = 'round'

    def date_organizer(self, date):
        date = date.split('-')
        return '/'.join(date[::-1])

    def set_all_user_data(self):
        self.main_user_data['date_from'] = self.date_organizer(str(self.from_date.date().toPyDate()))
        self.main_user_data['date_to'] = self.date_organizer(str(self.to_date.date().toPyDate()))
        self.main_user_data['price_to'] = self.price.text()
        self.main_user_data['adults'] = self.adults.text()
        self.main_user_data['children'] = self.childrens.text()

        self.details_evaluator()

    def dates_checker(self):
        if str(self.return_from.date().toPyDate()) != "2000-01-01" \
                or str(self.return_to.date().toPyDate()) != "2000-01-01":
            if self.from_date.date() > self.to_date.date() or self.from_date.date() > self.return_from.date() \
                    or self.return_from.date() > self.to_date.date() or self.to_date.date() > self.return_to.date():
                return False
        else:
            self.main_user_data.pop('return_from')
            self.main_user_data.pop('return_to')
            self.main_user_data.pop('nights_in_dst_from')
            self.main_user_data.pop('nights_in_dst_to')
            if self.from_date.date() > self.to_date.date():
                return False
        return True

    def go_back_search_again_button_clicked(self):
        search_window = FlightsUi(self.main_widget)
        add_to_widget(self.main_widget, search_window)

    def details_evaluator(self):
        if self.main_user_data['price_to'] == '':
            msg = "Fill all the required fields*"
            self.error.setText(msg)
        elif self.main_user_data['adults'] == '0':
            msg = "At least one adult is necessary*"
            self.error.setText(msg)
        elif int(self.price.text()) < 1000:
            msg = "Price has to be more than 1000*"
            self.error.setText(msg)
        elif int(self.main_user_data['adults']) <= 0:
            msg = "Invalid Adults number"
            self.error.setText(msg)
        elif int(self.main_user_data['children']) < 0:
            msg = "Invalid Children number"
            self.error.setText(msg)
        elif str(self.flight_type.itemText(self.flight_type.currentIndex())) != 'oneway':
            self.main_user_data['return_from'] = self.date_organizer(str(self.return_from.date().toPyDate()))
            self.main_user_data['return_to'] = self.date_organizer(str(self.return_to.date().toPyDate()))
            self.main_user_data['nights_in_dst_from'] = self.min_days.text()
            self.main_user_data['nights_in_dst_to'] = self.max_days.text()
            if not self.dates_checker():
                msg = "The given dates are invalid, Please check again*"
                self.error.setText(msg)
            else:
                self.error.setText("")
                flight_manager.get_user_flight_details(self.main_user_data)
                flights_full_details = FlightsDetails(self.main_widget, self.main_user_data)
                add_to_widget(self.main_widget, flights_full_details)
        else:
            self.error.setText("")
            flight_manager.get_user_flight_details(self.main_user_data)
            flights_full_details = FlightsDetails(self.main_widget, self.main_user_data)
            add_to_widget(self.main_widget, flights_full_details)


class FlightsDetails(QDialog):
    def __init__(self, main_widget, main_user_data):
        super(FlightsDetails, self).__init__()
        self.main_widget = main_widget
        loadUi("view/flights_details.ui", self)

        response = flight_manager.get_user_flight_details(main_user_data)

        if response[0] == '-1':
            self.list.addItems(["We've faced an Unusual Error!"])
        elif response[0] == '0':
            self.list.addItems(["Sorry! No airplanes Found!"])
        else:
            self.list.addItems(response)

        self.search_again.clicked.connect(self.go_back_search_again_button_clicked)

    def go_back_search_again_button_clicked(self):
        search_window = FlightsUi(self.main_widget)
        add_to_widget(self.main_widget, search_window)
