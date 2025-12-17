import sys   # to run the app
import json   #to save the events
import os   # check if the same file exist
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QLabel, QCalendarWidget, QStackedWidget, QHBoxLayout, QDialog,
    QLineEdit, QTextEdit, QMessageBox, QListWidget, QListWidgetItem,
    QTableWidget, QTableWidgetItem
)
from PyQt6.QtGui import QPalette, QColor, QFont
from PyQt6.QtCore import QDate, Qt

# how the events are saved
EVENTS_FILE = "events.json"


# Event Dialog when uhen you click a date on the calendar
class EventDialog(QDialog):
    def __init__(self, date, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Event")
        self.date = date
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Event Date: {self.date.toString()}"))
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Event Title")
        layout.addWidget(self.title_input)
        self.details_input = QTextEdit()
        self.details_input.setPlaceholderText("Event Details...")
        layout.addWidget(self.details_input)
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.save_btn)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

#Once the details are typed then the events are saved
    def get_event_data(self):
        return {
            "title": self.title_input.text(),
            "details": self.details_input.toPlainText(),
            "date": self.date
        }


# Travel Planner App main page
class TravelPlanner(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Travel Planner")
        self.setGeometry(200, 100, 1200, 700)

        # Load events
        self.events = self.load_events()

        container = QWidget()
        self.setCentralWidget(container)
        layout = QVBoxLayout()

        # Header
        header = QLabel("✈️ Travel Planner")
        header.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        header.setStyleSheet("color: orange;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # Navigation
        nav_layout = QHBoxLayout()
        self.monthly_btn = QPushButton("Monthly View")
        self.weekly_btn = QPushButton("Weekly View")
        self.yearly_btn = QPushButton("Yearly View")
        for btn in [self.monthly_btn, self.weekly_btn, self.yearly_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: orange;
                    color: white;
                    font-weight: bold;
                    border-radius: 10px;
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: #ff9933;
                }
            """)
            nav_layout.addWidget(btn)
        layout.addLayout(nav_layout)

        # Views
        self.views = QStackedWidget()
        layout.addWidget(self.views)
        self.monthly_view = self.create_monthly_view()
        self.weekly_view = self.create_weekly_view()
        self.yearly_view = self.create_yearly_view()
        self.views.addWidget(self.monthly_view)
        self.views.addWidget(self.weekly_view)
        self.views.addWidget(self.yearly_view)
        #Switch in between views
        self.monthly_btn.clicked.connect(lambda: self.views.setCurrentWidget(self.monthly_view))
        self.weekly_btn.clicked.connect(lambda: self.views.setCurrentWidget(self.weekly_view))
        self.yearly_btn.clicked.connect(lambda: self.views.setCurrentWidget(self.yearly_view))

        container.setLayout(layout)
        self.apply_theme()

        # Update all events to the list
        self.update_all_event_lists()

    # Monthly View Page
    def create_monthly_view(self):
        widget = QWidget()
        layout = QVBoxLayout()
        self.calendar = QCalendarWidget()
        self.calendar.clicked.connect(self.add_event)
        layout.addWidget(self.calendar)
        self.event_list = QListWidget()
        self.event_list.itemClicked.connect(self.show_event_details)
        layout.addWidget(QLabel("All Events:"))
        layout.addWidget(self.event_list)
        widget.setLayout(layout)
        return widget

        #Weekly View Page
    def create_weekly_view(self):
        widget = QWidget()
        layout = QVBoxLayout()

        # Table: 7 columns for days, multiple rows for events
        self.week_table = QTableWidget()
        self.week_table.setColumnCount(7)
        self.week_start = QDate.currentDate()
        self.week_table.cellClicked.connect(self.weekly_cell_single_clicked)
        self.week_table.cellDoubleClicked.connect(self.weekly_cell_double_clicked)
        layout.addWidget(self.week_table)

        #Event list below
        self.weekly_event_list = QListWidget()
        self.weekly_event_list.itemClicked.connect(self.show_event_details)
        layout.addWidget(QLabel("All Events:"))
        layout.addWidget(self.weekly_event_list)

        widget.setLayout(layout)
        self.update_weekly_table()
        return widget

#Updates the event list everytime you add an event
    def update_weekly_table(self):
        max_events = 0
        for col in range(7):
            date = self.week_start.addDays(col)
            date_key = date.toString("yyyy-MM-dd")
            num_events = len(self.events.get(date_key, []))
            if num_events > max_events:
                max_events = num_events
        self.week_table.setRowCount(max_events if max_events > 0 else 1)
#Max number of events in a single day and the format/style of the events
        for col in range(7):
            date = self.week_start.addDays(col)
            date_key = date.toString("yyyy-MM-dd")
            day_events = self.events.get(date_key, [])
            for row in range(max_events):
                if row < len(day_events):
                    item = QTableWidgetItem(day_events[row]["title"])
                    item.setForeground(QColor("black"))
                    self.week_table.setItem(row, col, item)
                else:
                    self.week_table.setItem(row, col, QTableWidgetItem(""))
#Columm headers
        self.week_table.setHorizontalHeaderLabels(
            [(self.week_start.addDays(i)).toString("ddd MMM d") for i in range(7)]
        )
# Single clicking shows all the event details
    def weekly_cell_single_clicked(self, row, column):
        # Show all events (same as other pages)
        self.update_weekly_event_list_all()
#Double clicking adds an event
    def weekly_cell_double_clicked(self, row, column):
        date = self.week_start.addDays(column)
        self.add_event(date)

#Yearly View Page
    def create_yearly_view(self):
        widget = QWidget()
        layout = QVBoxLayout()
        self.year_calendars = []
        self.current_year = QDate.currentDate().year()
        months_layout = QHBoxLayout()
        #Create mini 12 calendars 
        for month in range(1, 13):
            cal = QCalendarWidget()
            cal.setCurrentPage(self.current_year, month)
            cal.setFixedSize(200, 150)
            cal.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
            cal.setNavigationBarVisible(False)
            cal.clicked.connect(self.yearly_cell_clicked)
            self.year_calendars.append(cal)
            months_layout.addWidget(cal)
            if month % 4 == 0:
                layout.addLayout(months_layout)
                months_layout = QHBoxLayout()
        layout.addLayout(months_layout)
        self.yearly_event_list = QListWidget()
        self.yearly_event_list.itemClicked.connect(self.show_event_details)
        layout.addWidget(QLabel("All Events:"))
        layout.addWidget(self.yearly_event_list)
        widget.setLayout(layout)
        return widget


    # Event Handling/Format and Display

    def add_event(self, date):
        dialog = EventDialog(date, self)
        if dialog.exec():
            data = dialog.get_event_data()
            if data["title"].strip():
                date_key = date.toString("yyyy-MM-dd")
                self.events.setdefault(date_key, []).append(data)
                self.update_all_event_lists()
            else:
                QMessageBox.warning(self, "Missing Title", "Please enter an event title.")
#Update the events when you go to a different page
    def update_all_event_lists(self):
        self.update_monthly_event_list_all()
        self.update_weekly_event_list_all()
        self.update_yearly_event_list_all()
        self.update_weekly_table()

    def update_monthly_event_list_all(self):
        self.event_list.clear()
        for date_key, events in sorted(self.events.items()):
            for ev in events:
                item = QListWidgetItem(f"{ev['date'].toString()} — {ev['title']} — {ev['details']}")
                item.setForeground(QColor("black"))
                self.event_list.addItem(item)

    def update_weekly_event_list_all(self):
        self.weekly_event_list.clear()
        for date_key, events in sorted(self.events.items()):
            for ev in events:
                item = QListWidgetItem(f"{ev['date'].toString()} — {ev['title']} — {ev['details']}")
                item.setForeground(QColor("black"))
                self.weekly_event_list.addItem(item)

    def update_yearly_event_list_all(self):
        self.yearly_event_list.clear()
        for date_key, events in sorted(self.events.items()):
            for ev in events:
                item = QListWidgetItem(f"{ev['date'].toString()} — {ev['title']} — {ev['details']}")
                item.setForeground(QColor("black"))
                self.yearly_event_list.addItem(item)

    def yearly_cell_clicked(self, date):
        self.add_event(date)


    # Show Event Details with Delete + Confirmation
    def show_event_details(self, item):
        text = item.text()
        for date_key, event_list in self.events.items():
            for event in event_list:
                display_text = f"{event['date'].toString()} — {event['title']} — {event['details']}"
                if display_text == text:
                    msg_box = QMessageBox(self)
                    msg_box.setWindowTitle(f"Event: {event['title']}")
                    msg_box.setText(f"Title: {event['title']}\nDate: {event['date'].toString()}\nDetails: {event['details']}")
                    delete_button = msg_box.addButton("Delete Event", QMessageBox.ButtonRole.ActionRole)
                    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                    msg_box.exec()

                    if msg_box.clickedButton() == delete_button:
                        confirm = QMessageBox.question(
                            self,
                            "Confirm Delete",
                            f"Are you sure you want to delete '{event['title']}'?",
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                        )
                        if confirm == QMessageBox.StandardButton.Yes:
                            event_list.remove(event)
                            if not event_list:
                                del self.events[date_key]
                            self.update_all_event_lists()
                    return

    # Save & Load Events/ what pops up when you click the event
    def save_events(self):
        data = {}
        for date_key, events in self.events.items():
            data[date_key] = []
            for ev in events:
                data[date_key].append({
                    "title": ev["title"],
                    "details": ev["details"],
                    "date": ev["date"].toString("yyyy-MM-dd")
                })
        with open(EVENTS_FILE, "w") as f:
            json.dump(data, f, indent=4)

    def load_events(self):
        events = {}
        if os.path.exists(EVENTS_FILE):
            with open(EVENTS_FILE, "r") as f:
                data = json.load(f)
            for date_key, ev_list in data.items():
                events[date_key] = []
                for ev in ev_list:
                    ev["date"] = QDate.fromString(ev["date"], "yyyy-MM-dd")
                    events[date_key].append(ev)
        return events


    # Theme
    def apply_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("white"))
        palette.setColor(QPalette.ColorRole.WindowText, QColor("black"))
        palette.setColor(QPalette.ColorRole.Button, QColor("orange"))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor("white"))
        self.setPalette(palette)


    # Save the events when the app closes
    def closeEvent(self, event):
        self.save_events()
        event.accept()


# Main for the app to run also
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TravelPlanner()
    window.show()
    sys.exit(app.exec())
