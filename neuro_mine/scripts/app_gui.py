import datetime
import importlib.resources
import json
from PySide6.QtCore import QProcess
from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QApplication, QWidget, QFileDialog, QLineEdit, QCheckBox, QMessageBox
from neuro_mine.ui.ui_form import Ui_Widget
import os
from process_csv import default_options
import subprocess
import sys

class MyApp(QWidget, Ui_Widget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        now = datetime.datetime.now().strftime("%B_%d_%Y_%I_%M%p")
        self.lineEdit.setText(now) # Model Name
        self.checkBox.setChecked(default_options["use_time"]) # Use Time as Predictor
        self.checkBox_2.setChecked(default_options["run_shuffle"]) # Shuffle Data
        self.lineEdit_3.setText(str(default_options["th_test"])) # Test Score Threshold
        self.lineEdit_5.setText(str(default_options["taylor_sig"])) # Taylor Expansion Significance Threshold
        self.lineEdit_11.setText(str(default_options["taylor_look"]))  # Taylor Cutoff
        self.lineEdit_6.setText(str(default_options["taylor_cut"])) # Taylor Cutoff
        self.lineEdit_7.setText(str(default_options["th_lax"]))  # Linear Fit Variance explained cutoff
        self.lineEdit_8.setText(str(default_options["th_sqr"])) # Square Fit Variance explained cutoff
        self.checkBox_4.setChecked(default_options["jacobian"]) # Store Linear Receptive Fields (Jacobians)
        self.lineEdit_9.setText(str(default_options["history"])) # Model History [s]
        self.lineEdit_12.setText(str(default_options["n_epochs"])) # Number of Epochs
        self.lineEdit_13.setText(str(default_options["miner_train_fraction"])) # Fraction of Data to use to Train
        self.checkBox_3.setChecked(default_options["miner_verbose"]) # Verbose Fitting Updates

        # connect signals
        self.pushButton.clicked.connect(self.on_run_clicked)
        self.pushButton_2.clicked.connect(lambda: self.browse_file(self.lineEdit_4, "Predictor", "*.csv"))
        self.pushButton_3.clicked.connect(lambda: self.browse_file(self.lineEdit_2, "Response", "*.csv"))
        self.pushButton_4.clicked.connect(lambda: self.handle_json_browse(self.lineEdit_10))
        self.pushButton_5.clicked.connect(self.clear_form)
        self.pushButton_6.clicked.connect(self.save_to_json)

        # connect field validation
        self.valid_fields = {}
        for le, minv, maxv in [
            (self.lineEdit_3, 0, 1),
            (self.lineEdit_5, 0, 1),
            (self.lineEdit_11, 0.00000001, 3.999999999),
            (self.lineEdit_6, 0, 1),
            (self.lineEdit_7, 0, 1),
            (self.lineEdit_8, 0, 1),
            (self.lineEdit_9, 1, None),
            (self.lineEdit_12, 0, 100),
            (self.lineEdit_13, 0, 1)
        ]:
            le.editingFinished.connect(lambda le=le, minv=minv, maxv=maxv: self.validate_range(le, minv, maxv))

        self.last_dir = ""

        self.lineEdit_4.textChanged.connect(self.update_button_states)
        self.lineEdit_2.textChanged.connect(self.update_button_states)

        self.update_button_states()

    def browse_file(self, target_lineedit, file_type, file_filter):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            f"Select {file_type}",
            self.last_dir or "",
            file_filter,
            options=QFileDialog.DontUseNativeDialog
        )
        if file_path:
            target_lineedit.setText(file_path)

    def clear_form(self):
        for line_edit in self.findChildren(QLineEdit):
            line_edit.clear()
        for checkbox in self.findChildren(QCheckBox):
            checkbox.setChecked(False)

    def save_to_json(self):
        data = {
            "config": {
                "use_time":self.checkBox.isChecked(),
                "run_shuffle":self.checkBox_2.isChecked(),
                "th_test":self.lineEdit_3.text().strip(),
                "taylor_sig":self.lineEdit_5.text().strip(),
                "taylor_cut":self.lineEdit_6.text().strip(),
                "th_lax":self.lineEdit_7.text().strip(),
                "th_sqr":self.lineEdit_8.text().strip(),
                "history":self.lineEdit_9.text().strip(),
                "taylor_look":self.lineEdit_11.text().strip(),
                "jacobian":self.checkBox_4.isChecked(),
                "n_epochs":self.lineEdit_12.text().strip(),
                "miner_verbose":self.checkBox_3.isChecked(),
                "miner_train_fraction":self.lineEdit_13.text().strip()
                }
        }

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Configuration",
            self.last_dir or "",
            "JSON Files (*.json);;All Files (*)",
            options=QFileDialog.DontUseNativeDialog
        )

        if file_path:
            if not file_path.lower().endswith(".json"):
                file_path += ".json"

            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file:\n{e}")

            self.last_dir = os.path.dirname(file_path)

    def handle_json_browse(self, target_lineedit):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select JSON File", "", "JSON Files (*.json)")
        if file_path:
            target_lineedit.setText(file_path)
            self.load_json_and_populate(file_path)

    def load_json_and_populate(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if "config" in data:
                data = data["config"]
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not read JSON:\n{e}")
            return

        self.checkBox.setChecked(data.get("use_time", default_options["use_time"]))
        self.checkBox_2.setChecked(data.get("run_shuffle", default_options["run_shuffle"]))
        self.lineEdit_3.setText(str(data.get("th_test", default_options["th_test"])))
        self.lineEdit_5.setText(str(data.get("taylor_sig", default_options["taylor_sig"])))
        self.lineEdit_6.setText(str(data.get("taylor_cut", default_options["taylor_cut"])))
        self.lineEdit_7.setText(str(data.get("th_lax", default_options["th_lax"])))
        self.lineEdit_8.setText(str(data.get("th_sqr", default_options["th_sqr"])))
        self.lineEdit_9.setText(str(data.get("history", default_options["history"])))
        self.lineEdit_11.setText(str(data.get("taylor_look", default_options["taylor_look"])))
        self.checkBox_4.setChecked(data.get("jacobian", default_options["jacobian"]))
        self.lineEdit_12.setText(str(data.get("n_epochs", default_options["n_epochs"])))
        self.checkBox_3.setChecked(data.get("miner_verbose", default_options["miner_verbose"]))
        self.lineEdit_13.setText(str(data.get("miner_train_fraction", default_options["miner_train_fraction"])))

    def validate_range(self, line_edit, min_val, max_val):
        text = line_edit.text().strip()

        try:
            value = float(text)
            if min_val <= value <= max_val:
                line_edit.setPalette(self.style().standardPalette())
                self.valid_fields[line_edit.objectName()] = True
            else:
                palette = line_edit.palette()
                palette.setColor(QPalette.Base, QColor("crimson"))
                line_edit.setPalette(palette)
                self.valid_fields[line_edit.objectName()] = False
        except ValueError:
            palette = line_edit.palette()
            palette.setColor(QPalette.Base, QColor("crimson"))
            line_edit.setPalette(palette)
            self.valid_fields[line_edit.objectName()] = False

        self.update_button_states()

    def update_button_states(self):
        # Check all range validations
        all_valid = all(self.valid_fields.values())

        # Check that the required fields have *non-empty trimmed* text
        line4_filled = bool(self.lineEdit_4.text().strip())
        line2_filled = bool(self.lineEdit_2.text().strip())
        required_fields_filled = line4_filled and line2_filled

        # ✅ Run button depends on both being valid *and* filled
        self.pushButton.setEnabled(all_valid and required_fields_filled)

        # ✅ pushButton_6 only cares about range validity
        self.pushButton_6.setEnabled(all_valid)

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
        taylor_look = self.lineEdit_11.text()
        jacobian = self.checkBox_4.isChecked()
        config = self.lineEdit_10.text()
        n_epochs = self.lineEdit_12.text()
        miner_verbose = self.checkBox_3.isChecked()
        miner_train_fraction = self.lineEdit_13.text()

        with importlib.resources.path("neuro_mine.scripts", "process_csv.py") as script_path:
            args = [sys.executable, str(script_path)]

            if model_name:
                args.extend(["--model_name", model_name])
            if predictors:
                args.extend(["--predictors", predictors])
            if responses:
                args.extend(["--responses", responses])
            if use_time:
                args.extend(["--use_time"])
            if run_shuffle:
                args.extend(["--run_shuffle"])
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
                args.extend(["--jacobian"])
            if config:
                args.extend(["--config", config])
            if config:
                args.extend(["--n_epochs", n_epochs])
            if config:
                args.extend(["--miner_verbose", miner_verbose])
            if config:
                args.extend(["--miner_train_fraction", miner_train_fraction])

            subprocess.run(args)

        QApplication.quit()

def run_ui():
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    app.exec()

if __name__ == "__main__":
    run_ui()
