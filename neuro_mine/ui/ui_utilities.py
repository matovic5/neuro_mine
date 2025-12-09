"""
Module with common UI functions for main app and predict app
"""

from PySide6.QtWidgets import QFileDialog, QLineEdit
from PySide6.QtGui import QPalette, QColor

def browse_file(parent, target_lineedit, file_type, file_filter, last_dir):
    file_path, _ = QFileDialog.getOpenFileName(
        parent,
        f"Select {file_type}",
        last_dir or "",
        file_filter,
        options=QFileDialog.DontUseNativeDialog
    )

    if file_path:
        target_lineedit.setText(file_path)
        return file_path

    return None

def validate_range(line_edit, min_val, max_val, valid_fields, parent):
    text = line_edit.text().strip()

    try:
        value = float(text)
        if min_val <= value <= max_val:
            line_edit.setPalette(parent.style().standardPalette())
            valid_fields[line_edit.objectName()] = True
        else:
            palette = line_edit.palette()
            palette.setColor(QPalette.Base, QColor("crimson"))
            line_edit.setPalette(palette)
            valid_fields[line_edit.objectName()] = False

    except ValueError:
        palette = line_edit.palette()
        palette.setColor(QPalette.Base, QColor("crimson"))
        line_edit.setPalette(palette)
        valid_fields[line_edit.objectName()] = False

    if hasattr(parent, "update_button_states"):
        parent.update_button_states()

if __name__ == "__main__":
    print("Module with common UI functions for main app and predict app")