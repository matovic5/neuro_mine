import datetime
import importlib.resources
from PySide6.QtCore import QProcess
from PySide6.QtWidgets import QApplication, QWidget, QFileDialog, QLineEdit, QCheckBox
from neuro_mine.ui.ui_form import Ui_Widget
import subprocess
import sys

class MyApp(QWidget, Ui_Widget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        now = datetime.datetime.now().strftime("%B_%d_%Y_%I_%M%p")
        self.lineEdit.setText(now) # Model Name
        self.lineEdit_3.setText("0.2236068") # Test Score Threshold
        self.lineEdit_5.setText("0.05") # Taylor Expansion Significance Threshold
        self.lineEdit_6.setText("0.1") # Fit Variance Fraction
        self.lineEdit_7.setText("0.8")  # Linear Fit Variance Fraction
        self.lineEdit_8.setText("0.5") # Square Fit Variance Fraction
        self.lineEdit_9.setText("10.0") # Model History

        # connect signals
        self.pushButton.clicked.connect(self.on_run_clicked)
        self.pushButton_2.clicked.connect(lambda: self.browse_file(self.lineEdit_4, "Predictor", "*.csv"))
        self.pushButton_3.clicked.connect(lambda: self.browse_file(self.lineEdit_2, "Response", "*.csv"))
        self.pushButton_4.clicked.connect(lambda: self.browse_file(self.lineEdit_10, "Configuration File", ".json"))
        self.pushButton_5.clicked.connect(self.clear_form)

        self.last_dir = ""

    def browse_file(self, target_lineedit, file_type, file_filter):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            f"Select {file_type}",
            self.last_dir or "",
            file_filter
        )
        if file_path:
            target_lineedit.setText(file_path)

    def clear_form(self):
        for line_edit in self.findChildren(QLineEdit):
            line_edit.clear()
        for checkbox in self.findChildren(QCheckBox):
            checkbox.setChecked(False)

    def on_run_clicked(self):

        model_name = self.lineEdit.text()
        predictors = self.lineEdit_4.text()
        responses = self.lineEdit_2.text()
        use_time = self.checkBox.isChecked()
        run_shuffle = self.checkBox_2.isChecked()
        th_test = self.lineEdit_3.text()
        taylor_sig = self.lineEdit_5.text()
        taylor_cut = self.lineEdit_6.text()
        th_lax = self.lineEdit_7.text()
        th_sqr = self.lineEdit_8.text()
        history = self.lineEdit_9.text()
        taylor_look = self.checkBox_3.isChecked()
        jacobian = self.checkBox_4.isChecked()
        config = self.lineEdit_10.text()

        with importlib.resources.path("neuro_mine.scripts", "process_csv.py") as script_path:
            args = [sys.executable, str(script_path)]

            if model_name:
                args.extend(["--model_name", model_name])
            if predictors:
                args.extend(["--predictors", predictors])
            if responses:
                args.extend(["--responses", responses])
            if use_time:
                args.extend(["--use_time", use_time])
            if run_shuffle:
                args.extend(["--run_shuffle", run_shuffle])
            if th_test:
                args.extend(["--th_test", th_test])
            if taylor_sig:
                args.extend(["--taylor_sig", taylor_sig])
            if taylor_cut:
                args.extend(["--taylor_cut", taylor_cut])
            if th_lax:
                args.extend(["--th_lax", th_lax])
            if th_sqr:
                args.extend(["--th_sqr", th_sqr])
            if history:
                args.extend(["--history", history])
            if taylor_look:
                args.extend(["--taylor_look", taylor_look])
            if jacobian:
                args.extend(["--jacobian", jacobian])
            if config:
                args.extend(["--config", config])

            subprocess.run(args)

        QApplication.quit()

def run_ui():
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    app.exec()

if __name__ == "__main__":
    run_ui()
