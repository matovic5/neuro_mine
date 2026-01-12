import datetime
import importlib.resources
import json
from PySide6.QtGui import QPalette, QColor, QIntValidator, QDoubleValidator
from PySide6.QtWidgets import QApplication, QWidget, QFileDialog, QLineEdit, QCheckBox, QMessageBox
from neuro_mine.ui.mine_form import Ui_Form
import neuro_mine.ui.ui_utilities as uu
import numpy as np
import os
from neuro_mine.scripts.neuromine_fit import default_options
import subprocess
import sys

class Mine_App(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.lineEdit.setFocus()
        self.default_options = default_options

        now = datetime.datetime.now().strftime("%b%d%Y_%I%M%p")
        validator = QDoubleValidator(0.0, 1.0, 2 ,self)
        validator.setNotation(QDoubleValidator.Notation.StandardNotation)

        self.lineEdit.setText(now) # Model Name
        self.checkBox_2.setChecked(default_options["use_time"]) # Use Time as Predictor
        self.checkBox_5.setChecked(default_options["run_shuffle"]) # Shuffle Data
        self.lineEdit_2.setValidator(validator) # validate that test score threshold is only 2 decimal places
        self.lineEdit_2.setText(f"{float(default_options['th_test']):.2f}") # Test Score Threshold
        self.lineEdit_3.setText(str(default_options["taylor_sig"])) # Taylor Expansion Significance Threshold
        self.lineEdit_4.setText(str(default_options["taylor_look"]))  # Taylor Look Ahead
        self.lineEdit_5.setText(str(default_options["taylor_cut"])) # Taylor Cutoff
        self.lineEdit_6.setText(str(default_options["th_lax"]))  # Linear Fit Variance explained cutoff
        self.lineEdit_7.setText(str(default_options["th_sqr"])) # Square Fit Variance explained cutoff
        self.checkBox_3.setChecked(default_options["jacobian"]) # Store Linear Receptive Fields (Jacobians)
        self.lineEdit_8.setText(str(default_options["history"])) # Model History [s]
        self.lineEdit_9.setValidator(QIntValidator(1, 100, self)) # limit epochs to integers
        self.lineEdit_9.setText(str(default_options["n_epochs"])) # Number of Epochs
        self.lineEdit_10.setText(str(default_options["miner_train_fraction"])) # Number of Epochs # Fraction of Data to use to Train
        self.checkBox_4.setChecked(True) # Verbose Fitting Updates

        # connect signals
        self.pushButton.clicked.connect(self.on_run_clicked)
        self.pushButton_2.clicked.connect(lambda: uu.browse_multiple_files(self, self.textEdit, "Predictor File(s)", "*.csv", self.last_dir))
        self.pushButton_3.clicked.connect(lambda: uu.browse_multiple_files(self, self.textEdit_2, "Response File(s)", "*.csv", self.last_dir))
        self.pushButton_4.clicked.connect(lambda: self.handle_json_browse(self.lineEdit_11))
        self.pushButton_5.clicked.connect(self.restore_defaults)
        self.pushButton_6.clicked.connect(self.save_to_json)

        # connect field validation
        self.valid_fields = {}
        for le, minv, maxv in [
            (self.lineEdit_2, 0, 1),
            (self.lineEdit_3, 0, 1),
            (self.lineEdit_4, 0.00000001, 3.999999999),
            (self.lineEdit_5, 0, 1),
            (self.lineEdit_6, 0, 1),
            (self.lineEdit_7, 0, 1),
            (self.lineEdit_8, 1.0, np.inf),
            (self.lineEdit_9, 1, 100),
            (self.lineEdit_10, 0, 1)
        ]:
            le.editingFinished.connect(
                lambda le=le, minv=minv, maxv=maxv:
                uu.validate_range(le, minv, maxv, self.valid_fields, self)
            )

        self.last_dir = ""

        self.textEdit.textChanged.connect(self.update_button_states)
        self.textEdit_2.textChanged.connect(self.update_button_states)

        self.update_button_states()

    def populate_presets(self):
        for attr, value in default_options["line_edits"].items():
            widget = getattr(self, attr, None)
            if isinstance(widget, QLineEdit):
                widget.setText(value)

        for attr, value in default_options["check_boxes"].items():
            widget = getattr(self, attr, None)
            if isinstance(widget, QCheckBox):
                widget.setChecked(value)

    def save_to_json(self):
        data = {
            "config": {
                "episodic":self.checkBox.isChecked(),
                "use_time":self.checkBox_2.isChecked(),
                "run_shuffle":self.checkBox_5.isChecked(),
                "th_test":self.lineEdit_2.text().strip(),
                "taylor_sig":self.lineEdit_3.text().strip(),
                "taylor_cut":self.lineEdit_5.text().strip(),
                "th_lax":self.lineEdit_6.text().strip(),
                "th_sqr":self.lineEdit_7.text().strip(),
                "history":self.lineEdit_8.text().strip(),
                "taylor_look":self.lineEdit_4.text().strip(),
                "jacobian":self.checkBox_3.isChecked(),
                "n_epochs":self.lineEdit_9.text().strip(),
                "miner_verbose":self.checkBox_4.isChecked(),
                "miner_train_fraction":self.lineEdit_10.text().strip()
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
        file_path, _ = QFileDialog.getOpenFileName(self, "Select JSON File", "", "JSON Files (*.json)",
        options=QFileDialog.DontUseNativeDialog)
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

        self.checkBox.setChecked(data.get("episodic", default_options["episodic"]))
        self.checkBox_2.setChecked(data.get("use_time", default_options["use_time"]))
        self.checkBox_5.setChecked(data.get("run_shuffle", default_options["run_shuffle"]))
        self.lineEdit_2.setText(str(data.get("th_test", default_options["th_test"])))
        self.lineEdit_3.setText(str(data.get("taylor_sig", default_options["taylor_sig"])))
        self.lineEdit_5.setText(str(data.get("taylor_cut", default_options["taylor_cut"])))
        self.lineEdit_6.setText(str(data.get("th_lax", default_options["th_lax"])))
        self.lineEdit_7.setText(str(data.get("th_sqr", default_options["th_sqr"])))
        self.lineEdit_8.setText(str(data.get("history", default_options["history"])))
        self.lineEdit_4.setText(str(data.get("taylor_look", default_options["taylor_look"])))
        self.checkBox_3.setChecked(data.get("jacobian", default_options["jacobian"]))
        self.lineEdit_9.setText(str(data.get("n_epochs", default_options["n_epochs"])))
        self.checkBox_4.setChecked(data.get("miner_verbose", default_options["miner_verbose"]))
        self.lineEdit_10.setText(str(data.get("miner_train_fraction", default_options["miner_train_fraction"])))

    def update_button_states(self):
        all_valid = all(self.valid_fields.values())

        line4_filled = bool(self.textEdit.toPlainText().strip())
        line2_filled = bool(self.textEdit_2.toPlainText().strip())
        required_fields_filled = line4_filled and line2_filled

        self.pushButton.setEnabled(all_valid and required_fields_filled)

        self.pushButton_6.setEnabled(all_valid)

    def restore_defaults(self):
        """Restore UI elements to their default preset values."""
        global default_options

        self.checkBox.setChecked(default_options["episodic"])
        self.checkBox_2.setChecked(default_options["use_time"])
        self.checkBox_5.setChecked(default_options["run_shuffle"])
        self.lineEdit_2.setText(str(default_options["th_test"]))
        self.lineEdit_3.setText(str(default_options["taylor_sig"]))
        self.lineEdit_4.setText(str(default_options["taylor_look"]))
        self.lineEdit_5.setText(str(default_options["taylor_cut"]))
        self.lineEdit_6.setText(str(default_options["th_lax"]))
        self.lineEdit_7.setText(str(default_options["th_sqr"]))
        self.checkBox_3.setChecked(default_options["jacobian"])
        self.lineEdit_8.setText(str(default_options["history"]))
        self.lineEdit_9.setText(str(default_options["n_epochs"]))
        self.lineEdit_10.setText(str(default_options["miner_train_fraction"]))
        self.checkBox_4.setChecked(True)

        self.reset_validation_state()

    def reset_validation_state(self):
        """Resets line edit colors and re-enables buttons after restoring defaults."""
        for widget in [self.lineEdit_2, self.lineEdit_3, self.lineEdit_4,
                       self.lineEdit_5, self.lineEdit_6, self.lineEdit_7,
                       self.lineEdit_8, self.lineEdit_9, self.lineEdit_10]:
            widget.setPalette(self.style().standardPalette())

        for le, minv, maxv in [
            (self.lineEdit_2, 0, 1),
            (self.lineEdit_3, 0, 1),
            (self.lineEdit_4, 0.00000001, 3.999999999),
            (self.lineEdit_5, 0, 1),
            (self.lineEdit_6, 0, 1),
            (self.lineEdit_7, 0, 1),
            (self.lineEdit_8, 1.0, np.inf),
            (self.lineEdit_9, 0, 100),
            (self.lineEdit_10, 0, 1)
        ]:
            le.editingFinished.connect(lambda le=le, minv=minv, maxv=maxv: uu.validate_range(le, minv, maxv))

    def on_run_clicked(self):

        model_name = self.lineEdit.text()
        predictors = self.textEdit.toPlainText().strip().split()
        responses = self.textEdit_2.toPlainText().strip().split()
        episodic = self.checkBox.isChecked()
        use_time = self.checkBox_2.isChecked()
        run_shuffle = self.checkBox_5.isChecked()
        th_test = self.lineEdit_2.text()
        taylor_sig = self.lineEdit_3.text()
        taylor_cut = self.lineEdit_5.text()
        th_lax = self.lineEdit_6.text()
        th_sqr = self.lineEdit_7.text()
        history = self.lineEdit_8.text()
        taylor_look = self.lineEdit_4.text()
        jacobian = self.checkBox_3.isChecked()
        config = self.lineEdit_11.text()
        n_epochs = self.lineEdit_9.text()
        miner_verbose = self.checkBox_4.isChecked()
        miner_train_fraction = self.lineEdit_10.text()

        with importlib.resources.path("neuro_mine.scripts", "neuromine_fit.py") as script_path:
            args = [sys.executable, str(script_path)]

            if model_name:
                args.extend(["--model_name", model_name])
            if predictors:
                args.append("--predictors")
                args.extend(predictors)
            if responses:
                args.append("--responses")
                args.extend(responses)
            if use_time:
                args.extend(["--use_time"])
            if run_shuffle:
                args.extend(["--run_shuffle"])
            if episodic:
                args.extend(["--episodic"])
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
            if n_epochs:
                args.extend(["--n_epochs", n_epochs])
            if miner_verbose:
                args.extend(["--miner_verbose"])
            if miner_train_fraction:
                args.extend(["--miner_train_fraction", miner_train_fraction])

            subprocess.run(args)

        QApplication.quit()

def run_ui():
    app = QApplication(sys.argv)
    window = Mine_App()
    window.show()
    app.exec()

if __name__ == "__main__":
    run_ui()
