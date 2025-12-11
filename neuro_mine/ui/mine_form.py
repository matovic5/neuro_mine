# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mine_form.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QFormLayout, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QTextEdit,
    QWidget)
import neuro_mine.ui.resources_rc

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(665, 829)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        self.formLayout = QFormLayout(Form)
        self.formLayout.setObjectName(u"formLayout")
        self.label = QLabel(Form)
        self.label.setObjectName(u"label")
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setPixmap(QPixmap(u":/logo.png"))
        self.label.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.label)

        self.label_2 = QLabel(Form)
        self.label_2.setObjectName(u"label_2")
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_2)

        self.lineEdit = QLineEdit(Form)
        self.lineEdit.setObjectName(u"lineEdit")
        sizePolicy.setHeightForWidth(self.lineEdit.sizePolicy().hasHeightForWidth())
        self.lineEdit.setSizePolicy(sizePolicy)
        self.lineEdit.setMinimumSize(QSize(359, 0))

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.lineEdit)

        self.label_3 = QLabel(Form)
        self.label_3.setObjectName(u"label_3")
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_3)

        self.textEdit = QTextEdit(Form)
        self.textEdit.setObjectName(u"textEdit")
        sizePolicy.setHeightForWidth(self.textEdit.sizePolicy().hasHeightForWidth())
        self.textEdit.setSizePolicy(sizePolicy)

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.textEdit)

        self.label_20 = QLabel(Form)
        self.label_20.setObjectName(u"label_20")
        sizePolicy.setHeightForWidth(self.label_20.sizePolicy().hasHeightForWidth())
        self.label_20.setSizePolicy(sizePolicy)
        self.label_20.setPixmap(QPixmap(u":/question.png"))

        self.formLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_20)

        self.pushButton_2 = QPushButton(Form)
        self.pushButton_2.setObjectName(u"pushButton_2")
        sizePolicy.setHeightForWidth(self.pushButton_2.sizePolicy().hasHeightForWidth())
        self.pushButton_2.setSizePolicy(sizePolicy)

        self.formLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.pushButton_2)

        self.label_4 = QLabel(Form)
        self.label_4.setObjectName(u"label_4")
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)

        self.formLayout.setWidget(4, QFormLayout.ItemRole.LabelRole, self.label_4)

        self.textEdit_2 = QTextEdit(Form)
        self.textEdit_2.setObjectName(u"textEdit_2")
        sizePolicy.setHeightForWidth(self.textEdit_2.sizePolicy().hasHeightForWidth())
        self.textEdit_2.setSizePolicy(sizePolicy)

        self.formLayout.setWidget(4, QFormLayout.ItemRole.FieldRole, self.textEdit_2)

        self.label_21 = QLabel(Form)
        self.label_21.setObjectName(u"label_21")
        sizePolicy.setHeightForWidth(self.label_21.sizePolicy().hasHeightForWidth())
        self.label_21.setSizePolicy(sizePolicy)
        self.label_21.setPixmap(QPixmap(u":/question.png"))

        self.formLayout.setWidget(5, QFormLayout.ItemRole.LabelRole, self.label_21)

        self.pushButton_3 = QPushButton(Form)
        self.pushButton_3.setObjectName(u"pushButton_3")
        sizePolicy.setHeightForWidth(self.pushButton_3.sizePolicy().hasHeightForWidth())
        self.pushButton_3.setSizePolicy(sizePolicy)

        self.formLayout.setWidget(5, QFormLayout.ItemRole.FieldRole, self.pushButton_3)

        self.label_5 = QLabel(Form)
        self.label_5.setObjectName(u"label_5")
        sizePolicy.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy)

        self.formLayout.setWidget(7, QFormLayout.ItemRole.LabelRole, self.label_5)

        self.checkBox = QCheckBox(Form)
        self.checkBox.setObjectName(u"checkBox")
        sizePolicy.setHeightForWidth(self.checkBox.sizePolicy().hasHeightForWidth())
        self.checkBox.setSizePolicy(sizePolicy)

        self.formLayout.setWidget(7, QFormLayout.ItemRole.FieldRole, self.checkBox)

        self.label_6 = QLabel(Form)
        self.label_6.setObjectName(u"label_6")
        sizePolicy.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy)

        self.formLayout.setWidget(8, QFormLayout.ItemRole.LabelRole, self.label_6)

        self.checkBox_2 = QCheckBox(Form)
        self.checkBox_2.setObjectName(u"checkBox_2")
        sizePolicy.setHeightForWidth(self.checkBox_2.sizePolicy().hasHeightForWidth())
        self.checkBox_2.setSizePolicy(sizePolicy)

        self.formLayout.setWidget(8, QFormLayout.ItemRole.FieldRole, self.checkBox_2)

        self.label_7 = QLabel(Form)
        self.label_7.setObjectName(u"label_7")
        sizePolicy.setHeightForWidth(self.label_7.sizePolicy().hasHeightForWidth())
        self.label_7.setSizePolicy(sizePolicy)

        self.formLayout.setWidget(9, QFormLayout.ItemRole.LabelRole, self.label_7)

        self.checkBox_5 = QCheckBox(Form)
        self.checkBox_5.setObjectName(u"checkBox_5")
        sizePolicy.setHeightForWidth(self.checkBox_5.sizePolicy().hasHeightForWidth())
        self.checkBox_5.setSizePolicy(sizePolicy)

        self.formLayout.setWidget(9, QFormLayout.ItemRole.FieldRole, self.checkBox_5)

        self.label_8 = QLabel(Form)
        self.label_8.setObjectName(u"label_8")
        sizePolicy.setHeightForWidth(self.label_8.sizePolicy().hasHeightForWidth())
        self.label_8.setSizePolicy(sizePolicy)

        self.formLayout.setWidget(10, QFormLayout.ItemRole.LabelRole, self.label_8)

        self.lineEdit_2 = QLineEdit(Form)
        self.lineEdit_2.setObjectName(u"lineEdit_2")
        sizePolicy.setHeightForWidth(self.lineEdit_2.sizePolicy().hasHeightForWidth())
        self.lineEdit_2.setSizePolicy(sizePolicy)
        self.lineEdit_2.setMinimumSize(QSize(359, 0))

        self.formLayout.setWidget(10, QFormLayout.ItemRole.FieldRole, self.lineEdit_2)

        self.label_9 = QLabel(Form)
        self.label_9.setObjectName(u"label_9")
        sizePolicy.setHeightForWidth(self.label_9.sizePolicy().hasHeightForWidth())
        self.label_9.setSizePolicy(sizePolicy)

        self.formLayout.setWidget(11, QFormLayout.ItemRole.LabelRole, self.label_9)

        self.lineEdit_3 = QLineEdit(Form)
        self.lineEdit_3.setObjectName(u"lineEdit_3")
        sizePolicy.setHeightForWidth(self.lineEdit_3.sizePolicy().hasHeightForWidth())
        self.lineEdit_3.setSizePolicy(sizePolicy)
        self.lineEdit_3.setMinimumSize(QSize(359, 0))

        self.formLayout.setWidget(11, QFormLayout.ItemRole.FieldRole, self.lineEdit_3)

        self.label_10 = QLabel(Form)
        self.label_10.setObjectName(u"label_10")
        sizePolicy.setHeightForWidth(self.label_10.sizePolicy().hasHeightForWidth())
        self.label_10.setSizePolicy(sizePolicy)

        self.formLayout.setWidget(12, QFormLayout.ItemRole.LabelRole, self.label_10)

        self.lineEdit_4 = QLineEdit(Form)
        self.lineEdit_4.setObjectName(u"lineEdit_4")
        sizePolicy.setHeightForWidth(self.lineEdit_4.sizePolicy().hasHeightForWidth())
        self.lineEdit_4.setSizePolicy(sizePolicy)
        self.lineEdit_4.setMinimumSize(QSize(359, 0))

        self.formLayout.setWidget(12, QFormLayout.ItemRole.FieldRole, self.lineEdit_4)

        self.label_11 = QLabel(Form)
        self.label_11.setObjectName(u"label_11")
        sizePolicy.setHeightForWidth(self.label_11.sizePolicy().hasHeightForWidth())
        self.label_11.setSizePolicy(sizePolicy)

        self.formLayout.setWidget(13, QFormLayout.ItemRole.LabelRole, self.label_11)

        self.lineEdit_5 = QLineEdit(Form)
        self.lineEdit_5.setObjectName(u"lineEdit_5")
        sizePolicy.setHeightForWidth(self.lineEdit_5.sizePolicy().hasHeightForWidth())
        self.lineEdit_5.setSizePolicy(sizePolicy)
        self.lineEdit_5.setMinimumSize(QSize(359, 0))

        self.formLayout.setWidget(13, QFormLayout.ItemRole.FieldRole, self.lineEdit_5)

        self.label_12 = QLabel(Form)
        self.label_12.setObjectName(u"label_12")
        sizePolicy.setHeightForWidth(self.label_12.sizePolicy().hasHeightForWidth())
        self.label_12.setSizePolicy(sizePolicy)

        self.formLayout.setWidget(14, QFormLayout.ItemRole.LabelRole, self.label_12)

        self.lineEdit_6 = QLineEdit(Form)
        self.lineEdit_6.setObjectName(u"lineEdit_6")
        sizePolicy.setHeightForWidth(self.lineEdit_6.sizePolicy().hasHeightForWidth())
        self.lineEdit_6.setSizePolicy(sizePolicy)
        self.lineEdit_6.setMinimumSize(QSize(359, 0))

        self.formLayout.setWidget(14, QFormLayout.ItemRole.FieldRole, self.lineEdit_6)

        self.label_13 = QLabel(Form)
        self.label_13.setObjectName(u"label_13")
        sizePolicy.setHeightForWidth(self.label_13.sizePolicy().hasHeightForWidth())
        self.label_13.setSizePolicy(sizePolicy)

        self.formLayout.setWidget(15, QFormLayout.ItemRole.LabelRole, self.label_13)

        self.lineEdit_7 = QLineEdit(Form)
        self.lineEdit_7.setObjectName(u"lineEdit_7")
        sizePolicy.setHeightForWidth(self.lineEdit_7.sizePolicy().hasHeightForWidth())
        self.lineEdit_7.setSizePolicy(sizePolicy)
        self.lineEdit_7.setMinimumSize(QSize(359, 0))

        self.formLayout.setWidget(15, QFormLayout.ItemRole.FieldRole, self.lineEdit_7)

        self.label_14 = QLabel(Form)
        self.label_14.setObjectName(u"label_14")
        sizePolicy.setHeightForWidth(self.label_14.sizePolicy().hasHeightForWidth())
        self.label_14.setSizePolicy(sizePolicy)

        self.formLayout.setWidget(16, QFormLayout.ItemRole.LabelRole, self.label_14)

        self.checkBox_3 = QCheckBox(Form)
        self.checkBox_3.setObjectName(u"checkBox_3")
        sizePolicy.setHeightForWidth(self.checkBox_3.sizePolicy().hasHeightForWidth())
        self.checkBox_3.setSizePolicy(sizePolicy)

        self.formLayout.setWidget(16, QFormLayout.ItemRole.FieldRole, self.checkBox_3)

        self.label_15 = QLabel(Form)
        self.label_15.setObjectName(u"label_15")
        sizePolicy.setHeightForWidth(self.label_15.sizePolicy().hasHeightForWidth())
        self.label_15.setSizePolicy(sizePolicy)

        self.formLayout.setWidget(17, QFormLayout.ItemRole.LabelRole, self.label_15)

        self.lineEdit_8 = QLineEdit(Form)
        self.lineEdit_8.setObjectName(u"lineEdit_8")
        sizePolicy.setHeightForWidth(self.lineEdit_8.sizePolicy().hasHeightForWidth())
        self.lineEdit_8.setSizePolicy(sizePolicy)
        self.lineEdit_8.setMinimumSize(QSize(359, 0))

        self.formLayout.setWidget(17, QFormLayout.ItemRole.FieldRole, self.lineEdit_8)

        self.label_16 = QLabel(Form)
        self.label_16.setObjectName(u"label_16")
        sizePolicy.setHeightForWidth(self.label_16.sizePolicy().hasHeightForWidth())
        self.label_16.setSizePolicy(sizePolicy)

        self.formLayout.setWidget(18, QFormLayout.ItemRole.LabelRole, self.label_16)

        self.lineEdit_9 = QLineEdit(Form)
        self.lineEdit_9.setObjectName(u"lineEdit_9")
        sizePolicy.setHeightForWidth(self.lineEdit_9.sizePolicy().hasHeightForWidth())
        self.lineEdit_9.setSizePolicy(sizePolicy)
        self.lineEdit_9.setMinimumSize(QSize(359, 0))

        self.formLayout.setWidget(18, QFormLayout.ItemRole.FieldRole, self.lineEdit_9)

        self.label_17 = QLabel(Form)
        self.label_17.setObjectName(u"label_17")
        sizePolicy.setHeightForWidth(self.label_17.sizePolicy().hasHeightForWidth())
        self.label_17.setSizePolicy(sizePolicy)

        self.formLayout.setWidget(19, QFormLayout.ItemRole.LabelRole, self.label_17)

        self.lineEdit_10 = QLineEdit(Form)
        self.lineEdit_10.setObjectName(u"lineEdit_10")
        sizePolicy.setHeightForWidth(self.lineEdit_10.sizePolicy().hasHeightForWidth())
        self.lineEdit_10.setSizePolicy(sizePolicy)
        self.lineEdit_10.setMinimumSize(QSize(359, 0))

        self.formLayout.setWidget(19, QFormLayout.ItemRole.FieldRole, self.lineEdit_10)

        self.label_18 = QLabel(Form)
        self.label_18.setObjectName(u"label_18")
        sizePolicy.setHeightForWidth(self.label_18.sizePolicy().hasHeightForWidth())
        self.label_18.setSizePolicy(sizePolicy)

        self.formLayout.setWidget(20, QFormLayout.ItemRole.LabelRole, self.label_18)

        self.checkBox_4 = QCheckBox(Form)
        self.checkBox_4.setObjectName(u"checkBox_4")
        sizePolicy.setHeightForWidth(self.checkBox_4.sizePolicy().hasHeightForWidth())
        self.checkBox_4.setSizePolicy(sizePolicy)

        self.formLayout.setWidget(20, QFormLayout.ItemRole.FieldRole, self.checkBox_4)

        self.label_19 = QLabel(Form)
        self.label_19.setObjectName(u"label_19")
        sizePolicy.setHeightForWidth(self.label_19.sizePolicy().hasHeightForWidth())
        self.label_19.setSizePolicy(sizePolicy)

        self.formLayout.setWidget(21, QFormLayout.ItemRole.LabelRole, self.label_19)

        self.lineEdit_11 = QLineEdit(Form)
        self.lineEdit_11.setObjectName(u"lineEdit_11")
        sizePolicy.setHeightForWidth(self.lineEdit_11.sizePolicy().hasHeightForWidth())
        self.lineEdit_11.setSizePolicy(sizePolicy)
        self.lineEdit_11.setMinimumSize(QSize(359, 0))

        self.formLayout.setWidget(21, QFormLayout.ItemRole.FieldRole, self.lineEdit_11)

        self.pushButton_4 = QPushButton(Form)
        self.pushButton_4.setObjectName(u"pushButton_4")
        sizePolicy.setHeightForWidth(self.pushButton_4.sizePolicy().hasHeightForWidth())
        self.pushButton_4.setSizePolicy(sizePolicy)

        self.formLayout.setWidget(22, QFormLayout.ItemRole.FieldRole, self.pushButton_4)

        self.pushButton_5 = QPushButton(Form)
        self.pushButton_5.setObjectName(u"pushButton_5")
        sizePolicy.setHeightForWidth(self.pushButton_5.sizePolicy().hasHeightForWidth())
        self.pushButton_5.setSizePolicy(sizePolicy)

        self.formLayout.setWidget(23, QFormLayout.ItemRole.LabelRole, self.pushButton_5)

        self.pushButton = QPushButton(Form)
        self.pushButton.setObjectName(u"pushButton")
        sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy)

        self.formLayout.setWidget(23, QFormLayout.ItemRole.FieldRole, self.pushButton)

        self.pushButton_6 = QPushButton(Form)
        self.pushButton_6.setObjectName(u"pushButton_6")
        sizePolicy.setHeightForWidth(self.pushButton_6.sizePolicy().hasHeightForWidth())
        self.pushButton_6.setSizePolicy(sizePolicy)

        self.formLayout.setWidget(22, QFormLayout.ItemRole.LabelRole, self.pushButton_6)


        self.retranslateUi(Form)

        self.pushButton.setDefault(True)


        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Neuro MINE", None))
        self.label.setText("")
        self.label_2.setText(QCoreApplication.translate("Form", u"Model Name:", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"Predictor File Path(s) or Directory:", None))
#if QT_CONFIG(tooltip)
        self.label_20.setToolTip("")
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(whatsthis)
        self.label_20.setWhatsThis(QCoreApplication.translate("Form", u"Predictor file(s) should be .csv format but with any type of delimiter; Time must be in the first column and all columns must have headers", None))
#endif // QT_CONFIG(whatsthis)
        self.label_20.setText("")
        self.pushButton_2.setText(QCoreApplication.translate("Form", u"Browse...", None))
        self.label_4.setText(QCoreApplication.translate("Form", u"Predictor File Path(s) or Directory:", None))
#if QT_CONFIG(tooltip)
        self.label_21.setToolTip("")
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(whatsthis)
        self.label_21.setWhatsThis(QCoreApplication.translate("Form", u"Response file(s) should be .csv format but with any type of delimiter; time must be in the first column", None))
#endif // QT_CONFIG(whatsthis)
        self.label_21.setText("")
        self.pushButton_3.setText(QCoreApplication.translate("Form", u"Browse...", None))
        self.label_5.setText(QCoreApplication.translate("Form", u"Episodic Data:", None))
        self.checkBox.setText(QCoreApplication.translate("Form", u"Yes", None))
        self.label_6.setText(QCoreApplication.translate("Form", u"Uee Time as a Predictor:", None))
        self.checkBox_2.setText(QCoreApplication.translate("Form", u"Yes", None))
        self.label_7.setText(QCoreApplication.translate("Form", u"Run Shuffle:", None))
        self.checkBox_5.setText(QCoreApplication.translate("Form", u"Yes", None))
        self.label_8.setText(QCoreApplication.translate("Form", u"Test Score Threshold [0,1]:", None))
        self.label_9.setText(QCoreApplication.translate("Form", u"Taylor Expansion Significance Threshold [0,1]:", None))
        self.label_10.setText(QCoreApplication.translate("Form", u"Taylor Expansion Look Ahead (0,4):", None))
        self.label_11.setText(QCoreApplication.translate("Form", u"Taylor Cutoff [0,1]:", None))
        self.label_12.setText(QCoreApplication.translate("Form", u"Linear Fit Variance Fraction [0,1]:", None))
        self.label_13.setText(QCoreApplication.translate("Form", u"Square Fit Variance Fraction [0,1]:", None))
        self.label_14.setText(QCoreApplication.translate("Form", u"Store Linear Receptive Fields (Jacobians):", None))
        self.checkBox_3.setText(QCoreApplication.translate("Form", u"Yes", None))
        self.label_15.setText(QCoreApplication.translate("Form", u"Model History (seconds) \u22651:", None))
        self.label_16.setText(QCoreApplication.translate("Form", u"Number of Epochs [0,100]:", None))
        self.label_17.setText(QCoreApplication.translate("Form", u"Train Data Fraction [0,1]:", None))
        self.label_18.setText(QCoreApplication.translate("Form", u"Verbose:", None))
        self.checkBox_4.setText(QCoreApplication.translate("Form", u"Yes", None))
        self.label_19.setText(QCoreApplication.translate("Form", u"Populate with Parameters from JSON:", None))
        self.pushButton_4.setText(QCoreApplication.translate("Form", u"Browse JSON...", None))
        self.pushButton_5.setText(QCoreApplication.translate("Form", u"Restore Preset Parameters", None))
        self.pushButton.setText(QCoreApplication.translate("Form", u"Run Model", None))
        self.pushButton_6.setText(QCoreApplication.translate("Form", u"Save Parameters to JSON", None))
    # retranslateUi

