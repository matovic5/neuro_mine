# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mine_predict.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QGridLayout, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QTextEdit,
    QWidget)
import neuro_mine.ui.resources_rc

class Ui_Widget(object):
    def setupUi(self, Widget):
        if not Widget.objectName():
            Widget.setObjectName(u"Widget")
        Widget.resize(489, 356)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Widget.sizePolicy().hasHeightForWidth())
        Widget.setSizePolicy(sizePolicy)
        self.gridLayout = QGridLayout(Widget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_2 = QLabel(Widget)
        self.label_2.setObjectName(u"label_2")
        font = QFont()
        font.setBold(True)
        self.label_2.setFont(font)

        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)

        self.label = QLabel(Widget)
        self.label.setObjectName(u"label")
        self.label.setPixmap(QPixmap(u":/logo.png"))

        self.gridLayout.addWidget(self.label, 0, 4, 1, 1)

        self.label_3 = QLabel(Widget)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)

        self.lineEdit = QLineEdit(Widget)
        self.lineEdit.setObjectName(u"lineEdit")

        self.gridLayout.addWidget(self.lineEdit, 1, 1, 1, 3)

        self.pushButton = QPushButton(Widget)
        self.pushButton.setObjectName(u"pushButton")

        self.gridLayout.addWidget(self.pushButton, 1, 4, 1, 1)

        self.label_4 = QLabel(Widget)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 2, 0, 1, 1)

        self.lineEdit_2 = QLineEdit(Widget)
        self.lineEdit_2.setObjectName(u"lineEdit_2")

        self.gridLayout.addWidget(self.lineEdit_2, 2, 1, 1, 3)

        self.pushButton_2 = QPushButton(Widget)
        self.pushButton_2.setObjectName(u"pushButton_2")

        self.gridLayout.addWidget(self.pushButton_2, 2, 4, 1, 1)

        self.label_6 = QLabel(Widget)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout.addWidget(self.label_6, 3, 0, 1, 1)

        self.pushButton_4 = QPushButton(Widget)
        self.pushButton_4.setObjectName(u"pushButton_4")

        self.gridLayout.addWidget(self.pushButton_4, 3, 4, 1, 1)

        self.label_5 = QLabel(Widget)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout.addWidget(self.label_5, 4, 0, 1, 1)

        self.lineEdit_3 = QLineEdit(Widget)
        self.lineEdit_3.setObjectName(u"lineEdit_3")

        self.gridLayout.addWidget(self.lineEdit_3, 4, 1, 1, 3)

        self.pushButton_3 = QPushButton(Widget)
        self.pushButton_3.setObjectName(u"pushButton_3")

        self.gridLayout.addWidget(self.pushButton_3, 4, 4, 1, 1)

        self.label_7 = QLabel(Widget)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setFont(font)

        self.gridLayout.addWidget(self.label_7, 5, 0, 1, 2)

        self.label_8 = QLabel(Widget)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout.addWidget(self.label_8, 6, 0, 1, 1)

        self.lineEdit_5 = QLineEdit(Widget)
        self.lineEdit_5.setObjectName(u"lineEdit_5")

        self.gridLayout.addWidget(self.lineEdit_5, 6, 1, 1, 3)

        self.label_9 = QLabel(Widget)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout.addWidget(self.label_9, 7, 0, 1, 2)

        self.lineEdit_6 = QLineEdit(Widget)
        self.lineEdit_6.setObjectName(u"lineEdit_6")

        self.gridLayout.addWidget(self.lineEdit_6, 7, 2, 1, 1)

        self.label_10 = QLabel(Widget)
        self.label_10.setObjectName(u"label_10")

        self.gridLayout.addWidget(self.label_10, 7, 3, 1, 1)

        self.pushButton_5 = QPushButton(Widget)
        self.pushButton_5.setObjectName(u"pushButton_5")

        self.gridLayout.addWidget(self.pushButton_5, 8, 3, 1, 2)

        self.textEdit = QTextEdit(Widget)
        self.textEdit.setObjectName(u"textEdit")

        self.gridLayout.addWidget(self.textEdit, 3, 1, 1, 3)


        self.retranslateUi(Widget)

        self.pushButton_5.setDefault(True)


        QMetaObject.connectSlotsByName(Widget)
    # setupUi

    def retranslateUi(self, Widget):
        Widget.setWindowTitle(QCoreApplication.translate("Widget", u"Neuro MINE Predict", None))
        self.label_2.setText(QCoreApplication.translate("Widget", u"Load Files", None))
        self.label.setText("")
        self.label_3.setText(QCoreApplication.translate("Widget", u"Weights File Path:", None))
        self.pushButton.setText(QCoreApplication.translate("Widget", u"Browse...", None))
        self.label_4.setText(QCoreApplication.translate("Widget", u"Analysis File Path:", None))
        self.pushButton_2.setText(QCoreApplication.translate("Widget", u"Browse...", None))
        self.label_6.setText(QCoreApplication.translate("Widget", u"Predictor File Path(s):", None))
        self.pushButton_4.setText(QCoreApplication.translate("Widget", u"Browse...", None))
        self.label_5.setText(QCoreApplication.translate("Widget", u"Configuration File Path:", None))
        self.pushButton_3.setText(QCoreApplication.translate("Widget", u"Browse...", None))
        self.label_7.setText(QCoreApplication.translate("Widget", u"Prediction Parameters", None))
        self.label_8.setText(QCoreApplication.translate("Widget", u"Prediction Name:", None))
        self.label_9.setText(QCoreApplication.translate("Widget", u"Test Threshold Cutoff:", None))
        self.label_10.setText(QCoreApplication.translate("Widget", u"[-1,1]", None))
        self.pushButton_5.setText(QCoreApplication.translate("Widget", u"Predict Responses", None))
    # retranslateUi

