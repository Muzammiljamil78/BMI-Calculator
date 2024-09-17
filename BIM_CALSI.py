import sys
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

class BMICalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('BMI Calculator')
        self.setGeometry(100, 100, 400, 300)
        
        self.init_db()
        self.init_ui()

    def init_db(self):
        self.conn = sqlite3.connect('bmi_data.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS bmi_records (
                id INTEGER PRIMARY KEY,
                name TEXT,
                weight REAL,
                height REAL,
                bmi REAL
            )
        ''')
        self.conn.commit()

    def init_ui(self):
        self.name_input = QLineEdit(self)
        self.weight_input = QLineEdit(self)
        self.height_input = QLineEdit(self)
        self.bmi_display = QLabel(self)
        self.result_label = QLabel(self)

        self.calculate_button = QPushButton('Calculate BMI', self)
        self.calculate_button.clicked.connect(self.calculate_bmi)

        self.save_button = QPushButton('Save Record', self)
        self.save_button.clicked.connect(self.save_record)

        self.show_data_button = QPushButton('Show Historical Data', self)
        self.show_data_button.clicked.connect(self.show_historical_data)

        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.fig)
        self.update_plot()

        layout = QVBoxLayout()
        form_layout = QFormLayout()
        form_layout.addRow('Name:', self.name_input)
        form_layout.addRow('Weight (kg):', self.weight_input)
        form_layout.addRow('Height (cm):', self.height_input)
        form_layout.addWidget(self.calculate_button)
        form_layout.addWidget(self.save_button)
        form_layout.addWidget(self.show_data_button)
        form_layout.addRow('BMI:', self.bmi_display)
        form_layout.addRow('Result:', self.result_label)

        layout.addLayout(form_layout)
        layout.addWidget(self.canvas)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def calculate_bmi(self):
        try:
            weight = float(self.weight_input.text())
            height_cm = float(self.height_input.text())
            height_m = height_cm / 100
            bmi = weight / (height_m ** 2)
            self.bmi_display.setText(f'{bmi:.2f}')
            result = self.get_bmi_category(bmi)
            self.result_label.setText(result)
        except ValueError:
            self.bmi_display.setText('Invalid input')

    def get_bmi_category(self, bmi):
        if bmi < 18.5:
            return 'Underweight'
        elif 18.5 <= bmi < 24.9:
            return 'Normal weight'
        elif 25 <= bmi < 29.9:
            return 'Overweight'
        else:
            return 'Obesity'

    def save_record(self):
        name = self.name_input.text()
        weight = float(self.weight_input.text())
        height = float(self.height_input.text())
        bmi = float(self.bmi_display.text())

        self.cursor.execute('''
            INSERT INTO bmi_records (name, weight, height, bmi)
            VALUES (?, ?, ?, ?)
        ''', (name, weight, height, bmi))
        self.conn.commit()
        self.update_plot()
        self.clear_inputs()

    def clear_inputs(self):
        self.name_input.clear()
        self.weight_input.clear()
        self.height_input.clear()
        self.bmi_display.clear()
        self.result_label.clear()

    def show_historical_data(self):
        self.cursor.execute('SELECT * FROM bmi_records')
        records = self.cursor.fetchall()

        self.table_widget = QTableWidget()
        self.table_widget.setRowCount(len(records))
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(['ID', 'Name', 'Weight', 'Height', 'BMI'])

        for row_idx, record in enumerate(records):
            for col_idx, item in enumerate(record):
                self.table_widget.setItem(row_idx, col_idx, QTableWidgetItem(str(item)))

        self.table_widget.show()

    def update_plot(self):
        self.cursor.execute('SELECT height, bmi FROM bmi_records')
        records = self.cursor.fetchall()
        if records:
            heights, bmis = zip(*records)
            self.ax.clear()
            self.ax.plot(heights, bmis, 'o-', label='BMI')
            self.ax.set_xlabel('Height (cm)')
            self.ax.set_ylabel('BMI')
            self.ax.set_title('BMI Trend')
            self.ax.legend()
            self.canvas.draw()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    bmi_calculator = BMICalculator()
    bmi_calculator.show()
    sys.exit(app.exec_())


