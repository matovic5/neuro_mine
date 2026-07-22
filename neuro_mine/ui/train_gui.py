import importlib.resources
import json
from PySide6.QtGui import QPalette, QColor, QIntValidator, QDoubleValidator
from PySide6.QtWidgets import QApplication, QWidget, QFileDialog, QLineEdit, QCheckBox, QMessageBox
from PySide6.QtCore import QProcess
from neuro_mine.ui.mine_train import Ui_Form
import neuro_mine.ui.ui_utilities as uu
import numpy as np
import os
from neuro_mine.lib.options import default_options
import sys

os.system('color')

class Mine_App(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.lineEdit.setFocus()
        self.default_options = default_options

        # process for running command line program
        self.p = None

        validator = QDoubleValidator(0.0, 1.0, 2, self)
        validator.setNotation(QDoubleValidator.Notation.StandardNotation)

        self.checkBox.setChecked(default_options["ignore_memory_warning"]) # Force Run even if there is a memory warning
        self.checkBox_6.setChecked(default_options["use_time"]) # Use Time as Predictor
        self.checkBox_5.setChecked(default_options["run_shuffle"]) # Shuffle Data
        self.checkBox_8.setChecked(default_options["train_progress"]) # Training curve
        self.checkBox_3.setChecked(default_options["jacobian"]) # Store Linear Receptive Fields (Jacobians)
        self.checkBox_4.toggled.connect(
            lambda checked: uu.handle_checkbox_4(checked, self.lineEdit_4)
        )
        uu.handle_checkbox_4(self.checkBox_4.isChecked(), self.lineEdit_4)
        self.lineEdit_4.setEnabled(self.checkBox_4.isChecked())
        self.lineEdit_2.setValidator(validator) # validate that test score threshold is only 2 decimal places
        self.lineEdit_2.setText(f"{float(default_options['th_test']):.2f}") # Test Score Threshold
        self.lineEdit_2.textChanged.connect(lambda: uu.validate_range(
            self.lineEdit_2, 0, 1, self.valid_fields, self
        ))
        self.lineEdit_3.setText(str(default_options["taylor_sig"])) # Taylor Expansion Significance Threshold
        self.lineEdit_4.setValidator(QIntValidator(1,2147483647,self))
        self.lineEdit_4.setText(str(default_options["downsampling"]))
        self.lineEdit_4.textChanged.connect(lambda: uu.validate_range(
            self.lineEdit_4, 1, 2147483647, self.valid_fields, self
        ))
        self.lineEdit_5.setText(str(default_options["taylor_cut"])) # Taylor Cutoff
        self.lineEdit_6.setText(str(default_options["th_lax"]))  # Linear Fit Variance explained cutoff
        self.lineEdit_7.setText(str(default_options["th_sqr"])) # Square Fit Variance explained cutoff
        self.lineEdit_8.setText(str(default_options["history"])) # Model History [s]
        self.lineEdit_9.setValidator(QIntValidator(1, 500, self)) # limit epochs to integers
        self.lineEdit_9.setText(str(default_options["n_epochs"])) # Number of Epochs
        self.lineEdit_9.textChanged.connect(lambda: uu.validate_range(
            self.lineEdit_9, 0, 500, self.valid_fields, self
        ))
        self.lineEdit_10.setText(str(default_options["miner_train_fraction"])) # Number of Epochs # Fraction of Data to use to Train

        # connect signals
        self.pushButton.clicked.connect(self.on_run_clicked)
        self.pushButton_2.clicked.connect(lambda: uu.browse_multiple_files(self, self.textEdit, "Predictor File(s)", "Data Files (*.csv *.tsv);;All Files (*)", self.last_dir))
        self.pushButton_3.clicked.connect(lambda: uu.browse_multiple_files(self, self.textEdit_2, "Response File(s)", "Data Files (*.csv *.tsv);;All Files (*)", self.last_dir))
        self.pushButton_4.clicked.connect(lambda: self.handle_json_browse(self.lineEdit_11))
        self.pushButton_5.clicked.connect(self.restore_defaults)
        self.pushButton_6.clicked.connect(self.save_to_json)
        self.pushButton_7.clicked.connect(lambda:uu.browse_for_directory(self, self.lineEdit,"Select Output Directory"))

        # connect field validation
        self.valid_fields = {}
        for le, minv, maxv in [
            (self.lineEdit_2, 0, 1),
            (self.lineEdit_3, 0, 1),
            (self.lineEdit_4, 1, 2147483647),
            (self.lineEdit_5, 0, 1),
            (self.lineEdit_6, 0, 1),
            (self.lineEdit_7, 0, 1),
            (self.lineEdit_8, 0.00000001, np.inf),
            (self.lineEdit_9, 1, 500),
            (self.lineEdit_10, 0, 1)
        ]:
            le.editingFinished.connect(
                lambda le=le, minv=minv, maxv=maxv:
                uu.validate_range(le, minv, maxv, self.valid_fields, self)
            )
        self.lineEdit.editingFinished.connect(
            lambda: uu.validate_populated(
                self.lineEdit, self.valid_fields, self
            )
        )

        self.last_dir = ""

        self.textEdit.textChanged.connect(self.update_button_states)
        self.textEdit_2.textChanged.connect(self.update_button_states)

        self.update_button_states()

    def closeEvent(self, event):
        if self.p is not None:
            self.p.close()
        event.accept()

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
            "use_time": self.checkBox_6.isChecked(),
            "run_shuffle": self.checkBox_5.isChecked(),
            "th_test": float(self.lineEdit_2.text().strip()),
            "taylor_sig": float(self.lineEdit_3.text().strip()),
            "taylor_cut": float(self.lineEdit_5.text().strip()),
            "th_lax": float(self.lineEdit_6.text().strip()),
            "th_sqr": float(self.lineEdit_7.text().strip()),
            "history": float(self.lineEdit_8.text().strip()),
            "jacobian": self.checkBox_3.isChecked(),
            "n_epochs": int(self.lineEdit_9.text().strip()),
            "miner_train_fraction": float(self.lineEdit_10.text().strip()),
            "downsampling": int(self.lineEdit_4.text().strip()),
            "ignore_memory_warning": self.checkBox.isChecked(),
            "train_progress": self.checkBox_8.isChecked(),
          },
          "run": {
            "outdir": self.lineEdit.text().strip(),
            "predictor_file": self.textEdit.toPlainText().strip(),
            "response_file": self.textEdit_2.toPlainText().strip(),
            "is_episodic": self.checkBox_7.isChecked(),
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

        self.checkBox_7.setChecked(data.get("episodic", default_options["episodic"]))
        self.checkBox_6.setChecked(data.get("use_time", default_options["use_time"]))
        self.checkBox_5.setChecked(data.get("run_shuffle", default_options["run_shuffle"]))
        self.checkBox_8.setChecked(data.get("train_progress", default_options["train_progress"]))
        self.lineEdit_2.setText(str(data.get("th_test", default_options["th_test"])))
        self.lineEdit_3.setText(str(data.get("taylor_sig", default_options["taylor_sig"])))
        self.lineEdit_5.setText(str(data.get("taylor_cut", default_options["taylor_cut"])))
        self.lineEdit_6.setText(str(data.get("th_lax", default_options["th_lax"])))
        self.lineEdit_7.setText(str(data.get("th_sqr", default_options["th_sqr"])))
        self.lineEdit_8.setText(str(data.get("history", default_options["history"])))
        self.checkBox_3.setChecked(data.get("jacobian", default_options["jacobian"]))
        self.lineEdit_9.setText(str(data.get("n_epochs", default_options["n_epochs"])))
        self.lineEdit_10.setText(str(data.get("miner_train_fraction", default_options["miner_train_fraction"])))
        downsampling = data.get("downsampling", default_options["downsampling"])
        self.lineEdit_4.setText(str(downsampling))
        self.checkBox_4.setChecked(downsampling > 1)
        self.checkBox.setChecked(data.get("ignore_memory_warning", default_options["ignore_memory_warning"]))

    def update_button_states(self):
        all_valid = all(self.valid_fields.values())

        line4_filled = bool(self.textEdit.toPlainText().strip())
        line2_filled = bool(self.textEdit_2.toPlainText().strip())
        required_fields_filled = line4_filled and line2_filled

        self.pushButton.setEnabled(all_valid and required_fields_filled and (self.p is None))

        self.pushButton_6.setEnabled(all_valid)

    def restore_defaults(self):
        """Restore UI elements to their default preset values."""
        global default_options

        self.checkBox_4.setChecked(False)
        self.checkBox_7.setChecked(default_options["episodic"])
        self.checkBox_8.setChecked(default_options["train_progress"])
        self.checkBox.setChecked(default_options["ignore_memory_warning"])
        self.checkBox_6.setChecked(default_options["use_time"])
        self.checkBox_5.setChecked(default_options["run_shuffle"])
        self.lineEdit_2.setText(f"{float(default_options['th_test']):.2f}")
        self.lineEdit_3.setText(str(default_options["taylor_sig"]))
        self.lineEdit_4.setText(str(default_options["downsampling"]))
        self.lineEdit_5.setText(str(default_options["taylor_cut"]))
        self.lineEdit_6.setText(str(default_options["th_lax"]))
        self.lineEdit_7.setText(str(default_options["th_sqr"]))
        self.checkBox_3.setChecked(default_options["jacobian"])
        self.lineEdit_8.setText(str(default_options["history"]))
        self.lineEdit_9.setText(str(default_options["n_epochs"]))
        self.lineEdit_10.setText(str(default_options["miner_train_fraction"]))

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
            (self.lineEdit_4, 1, 2147483647),
            (self.lineEdit_5, 0, 1),
            (self.lineEdit_6, 0, 1),
            (self.lineEdit_7, 0, 1),
            (self.lineEdit_8, 1.0, np.inf),
            (self.lineEdit_9, 0, 100),
            (self.lineEdit_10, 0, 1)
        ]:
            le.editingFinished.connect(lambda le=le, minv=minv, maxv=maxv: uu.validate_range(le, minv, maxv, self.valid_fields, self))

    def on_run_clicked(self):

        outdir = self.lineEdit.text()
        predictors = self.textEdit.toPlainText().strip().split()
        responses = self.textEdit_2.toPlainText().strip().split()
        episodic = self.checkBox_7.isChecked()
        train_progress = self.checkBox_8.isChecked()
        ignore_mem = self.checkBox.isChecked()
        use_time = self.checkBox_6.isChecked()
        run_shuffle = self.checkBox_5.isChecked()
        th_test = self.lineEdit_2.text()
        taylor_sig = self.lineEdit_3.text()
        taylor_cut = self.lineEdit_5.text()
        th_lax = self.lineEdit_6.text()
        th_sqr = self.lineEdit_7.text()
        history = self.lineEdit_8.text()
        jacobian = self.checkBox_3.isChecked()
        n_epochs = self.lineEdit_9.text()
        miner_train_fraction = self.lineEdit_10.text()
        downsampling = self.lineEdit_4.text()

        with importlib.resources.path("neuro_mine.scripts", "neuromine_train.py") as script_path:
            args = [str(script_path)]

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
            if jacobian:
                args.extend(["--jacobian"])
            if n_epochs:
                args.extend(["--n_epochs", n_epochs])
            if miner_train_fraction:
                args.extend(["--miner_train_fraction", miner_train_fraction])
            if downsampling:
                args.extend(["--downsampling", downsampling])
            if outdir:
                args.extend(["--outdir", outdir])
            if train_progress:
                args.extend(["--train_progress"])
            if ignore_mem:
                args.extend(["--ignore_mem"])

            self.pushButton.setEnabled(False)
            print("#### RUN STARTED ####")
            self.p = QProcess()
            self.p.finished.connect(self.process_finished)
            self.p.readyReadStandardOutput.connect(self.handle_command_line_update)
            self.p.readyReadStandardError.connect(self.handle_command_line_error)
            self.p.start(sys.executable, args)

    def process_finished(self):
        print("#### RUN ENDED ####")
        self.p = None
        self.update_button_states()

    def handle_command_line_update(self):
        data = self.p.readAllStandardOutput()
        self.message(bytes(data).decode("utf-8"))

    def handle_command_line_error(self):
        data = self.p.readAllStandardError()
        self.message(bytes(data).decode("utf-8"), True)

    @staticmethod
    def message(s, error=False):
        # aggressively filter out warnings that are sent to standard error because tensorflow does not know
        # how to initialize abseil
        if "WARNING:" in s or "XLA" in s:
            return
        if error:
            print('\033[91m' + s + '\033[0m')
        else:
            print(s)

def run_ui():
    app = QApplication(sys.argv)
    window = Mine_App()
    window.show()
    app.exec()

if __name__ == "__main__":
    run_ui()