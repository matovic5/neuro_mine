import datetime
import importlib.resources
import json
from PySide6.QtWidgets import QApplication, QWidget, QLineEdit, QMessageBox, QFileDialog
from neuro_mine.ui.mine_predict import Ui_Widget
import neuro_mine.ui.ui_utilities as uu
import subprocess
import sys

class Predict_App(QWidget, Ui_Widget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.pushButton.clicked.connect(lambda: uu.browse_file(self, self.lineEdit, "Weights File", "*.hdf5", self.last_dir))
        self.pushButton_2.clicked.connect(lambda: uu.browse_file(self, self.lineEdit_2, "Analysis File", "*.hdf5", self.last_dir))
        self.pushButton_3.clicked.connect(lambda: self.handle_json_browse(self.lineEdit_3))
        self.pushButton_4.clicked.connect(lambda: uu.browse_multiple_files(self, self.textEdit, "Predictor File(s)", "*.csv", self.last_dir))
        self.pushButton_5.clicked.connect(self.on_run_clicked)

        self.lineEdit_6.setText("-1") # Test Score Threshold

        self.valid_fields = {}
        for le, minv, maxv in [
            (self.lineEdit_6, -1, 1)
        ]:
            le.editingFinished.connect(
                lambda le=le, minv=minv, maxv=maxv:
                uu.validate_range(le, minv, maxv, self.valid_fields, self)
            )

        self.last_dir = ""

        self.lineEdit.textChanged.connect(self.update_button_states) # weights file
        self.lineEdit_2.textChanged.connect(self.update_button_states) # analysis file
        self.lineEdit_3.textChanged.connect(self.update_button_states) # configuration file path
        self.textEdit.textChanged.connect(self.update_button_states) # predictor filepath(s)
        self.lineEdit_5.textChanged.connect(self.update_button_states) # name
        self.lineEdit_6.textChanged.connect(self.update_button_states) # test threshold cutoff

        self.update_button_states()

    def handle_json_browse(self, target_lineedit):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select JSON File", "", "JSON Files (*.json)",
        options = QFileDialog.DontUseNativeDialog
        )
        if file_path:
            target_lineedit.setText(file_path)
            self.load_json_and_populate(file_path)

    def load_json_and_populate(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if "run" in data:
                data = data["run"]
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not read JSON:\n{e}")
            return

        now = datetime.datetime.now().strftime("%b%d%Y_%I%M%p")
        self.lineEdit_5.setText(str(data.get("model_name", "prediction_model"))+"_predicition_"+now)

    def update_button_states(self):
        all_valid = all(self.valid_fields.values())

        line_edits_filled = all(bool(le.text().strip()) for le in [
            self.lineEdit,
            self.lineEdit_2,
            self.lineEdit_3,
            self.lineEdit_5,
            self.lineEdit_6
        ])

        text_filled = bool(self.textEdit.toPlainText().strip())

        self.pushButton_5.setEnabled(all_valid and line_edits_filled and text_filled)

    def on_run_clicked(self):

        predictors = self.textEdit.toPlainText().strip().split()
        config = self.lineEdit_3.text()
        weights = self.lineEdit.text()
        analysis = self.lineEdit_2.text()
        th_test = self.lineEdit_6.text()

        with importlib.resources.path("neuro_mine.scripts", "response_prediction.py") as script_path:
            args = [sys.executable, str(script_path)]

            if predictors:
                args.append("--predictors")
                args.extend(predictors)
            if config:
                args.extend(["--config", config])
            if weights:
                args.extend(["--weights", weights])
            if analysis:
                args.extend(["--analysis", analysis])
            if th_test:
                args.extend(["--th_test", th_test])

            subprocess.run(args)

        QApplication.quit()

def run_ui():
    app = QApplication(sys.argv)
    window = Predict_App()
    window.show()
    app.exec()

if __name__ == "__main__":
    run_ui()