# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mine_train.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QGridLayout, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QTextEdit, QVBoxLayout, QWidget)
import neuro_mine.ui.resources_rc

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(609, 727)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        font = QFont()
        font.setFamilies([u".AppleSystemUIFont"])
        Form.setFont(font)
        self.pushButton = QPushButton(Form)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(460, 690, 141, 32))
        sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy)
        self.groupBox = QGroupBox(Form)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(10, 40, 541, 261))
        self.label_19 = QLabel(self.groupBox)
        self.label_19.setObjectName(u"label_19")
        self.label_19.setGeometry(QRect(566, 249, 16, 16))
        self.layoutWidget = QWidget(self.groupBox)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(10, 26, 524, 231))
        self.gridLayout_3 = QGridLayout(self.layoutWidget)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.textEdit = QTextEdit(self.layoutWidget)
        self.textEdit.setObjectName(u"textEdit")
        sizePolicy.setHeightForWidth(self.textEdit.sizePolicy().hasHeightForWidth())
        self.textEdit.setSizePolicy(sizePolicy)

        self.gridLayout_3.addWidget(self.textEdit, 0, 0, 1, 2)

        self.textEdit_2 = QTextEdit(self.layoutWidget)
        self.textEdit_2.setObjectName(u"textEdit_2")
        sizePolicy.setHeightForWidth(self.textEdit_2.sizePolicy().hasHeightForWidth())
        self.textEdit_2.setSizePolicy(sizePolicy)

        self.gridLayout_3.addWidget(self.textEdit_2, 0, 2, 1, 2)

        self.pushButton_2 = QPushButton(self.layoutWidget)
        self.pushButton_2.setObjectName(u"pushButton_2")
        sizePolicy.setHeightForWidth(self.pushButton_2.sizePolicy().hasHeightForWidth())
        self.pushButton_2.setSizePolicy(sizePolicy)

        self.gridLayout_3.addWidget(self.pushButton_2, 1, 0, 1, 1)

        self.label_20 = QLabel(self.layoutWidget)
        self.label_20.setObjectName(u"label_20")
        sizePolicy.setHeightForWidth(self.label_20.sizePolicy().hasHeightForWidth())
        self.label_20.setSizePolicy(sizePolicy)
        self.label_20.setPixmap(QPixmap(u":/question.png"))

        self.gridLayout_3.addWidget(self.label_20, 1, 1, 1, 1)

        self.pushButton_3 = QPushButton(self.layoutWidget)
        self.pushButton_3.setObjectName(u"pushButton_3")
        sizePolicy.setHeightForWidth(self.pushButton_3.sizePolicy().hasHeightForWidth())
        self.pushButton_3.setSizePolicy(sizePolicy)

        self.gridLayout_3.addWidget(self.pushButton_3, 1, 2, 1, 1)

        self.label_21 = QLabel(self.layoutWidget)
        self.label_21.setObjectName(u"label_21")
        sizePolicy.setHeightForWidth(self.label_21.sizePolicy().hasHeightForWidth())
        self.label_21.setSizePolicy(sizePolicy)
        self.label_21.setPixmap(QPixmap(u":/question.png"))

        self.gridLayout_3.addWidget(self.label_21, 1, 3, 1, 1)

        self.groupBox_2 = QGroupBox(Form)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setGeometry(QRect(10, 390, 291, 151))
        self.layoutWidget1 = QWidget(self.groupBox_2)
        self.layoutWidget1.setObjectName(u"layoutWidget1")
        self.layoutWidget1.setGeometry(QRect(1, 21, 281, 124))
        self.gridLayout_2 = QGridLayout(self.layoutWidget1)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.label_8 = QLabel(self.layoutWidget1)
        self.label_8.setObjectName(u"label_8")
        sizePolicy.setHeightForWidth(self.label_8.sizePolicy().hasHeightForWidth())
        self.label_8.setSizePolicy(sizePolicy)

        self.horizontalLayout_9.addWidget(self.label_8)

        self.lineEdit_2 = QLineEdit(self.layoutWidget1)
        self.lineEdit_2.setObjectName(u"lineEdit_2")
        sizePolicy.setHeightForWidth(self.lineEdit_2.sizePolicy().hasHeightForWidth())
        self.lineEdit_2.setSizePolicy(sizePolicy)
        self.lineEdit_2.setMinimumSize(QSize(50, 0))

        self.horizontalLayout_9.addWidget(self.lineEdit_2)

        self.label_3 = QLabel(self.layoutWidget1)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_9.addWidget(self.label_3)


        self.gridLayout_2.addLayout(self.horizontalLayout_9, 0, 0, 1, 1)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.label_15 = QLabel(self.layoutWidget1)
        self.label_15.setObjectName(u"label_15")
        sizePolicy.setHeightForWidth(self.label_15.sizePolicy().hasHeightForWidth())
        self.label_15.setSizePolicy(sizePolicy)

        self.horizontalLayout_8.addWidget(self.label_15)

        self.lineEdit_8 = QLineEdit(self.layoutWidget1)
        self.lineEdit_8.setObjectName(u"lineEdit_8")
        sizePolicy.setHeightForWidth(self.lineEdit_8.sizePolicy().hasHeightForWidth())
        self.lineEdit_8.setSizePolicy(sizePolicy)
        self.lineEdit_8.setMinimumSize(QSize(50, 0))

        self.horizontalLayout_8.addWidget(self.lineEdit_8)

        self.label_28 = QLabel(self.layoutWidget1)
        self.label_28.setObjectName(u"label_28")

        self.horizontalLayout_8.addWidget(self.label_28)


        self.gridLayout_2.addLayout(self.horizontalLayout_8, 1, 0, 1, 1)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.label_16 = QLabel(self.layoutWidget1)
        self.label_16.setObjectName(u"label_16")
        sizePolicy.setHeightForWidth(self.label_16.sizePolicy().hasHeightForWidth())
        self.label_16.setSizePolicy(sizePolicy)

        self.horizontalLayout_7.addWidget(self.label_16)

        self.lineEdit_9 = QLineEdit(self.layoutWidget1)
        self.lineEdit_9.setObjectName(u"lineEdit_9")
        sizePolicy.setHeightForWidth(self.lineEdit_9.sizePolicy().hasHeightForWidth())
        self.lineEdit_9.setSizePolicy(sizePolicy)
        self.lineEdit_9.setMinimumSize(QSize(50, 0))

        self.horizontalLayout_7.addWidget(self.lineEdit_9)

        self.label_27 = QLabel(self.layoutWidget1)
        self.label_27.setObjectName(u"label_27")

        self.horizontalLayout_7.addWidget(self.label_27)


        self.gridLayout_2.addLayout(self.horizontalLayout_7, 2, 0, 1, 1)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_17 = QLabel(self.layoutWidget1)
        self.label_17.setObjectName(u"label_17")
        sizePolicy.setHeightForWidth(self.label_17.sizePolicy().hasHeightForWidth())
        self.label_17.setSizePolicy(sizePolicy)

        self.horizontalLayout_6.addWidget(self.label_17)

        self.lineEdit_10 = QLineEdit(self.layoutWidget1)
        self.lineEdit_10.setObjectName(u"lineEdit_10")
        sizePolicy.setHeightForWidth(self.lineEdit_10.sizePolicy().hasHeightForWidth())
        self.lineEdit_10.setSizePolicy(sizePolicy)
        self.lineEdit_10.setMinimumSize(QSize(50, 0))

        self.horizontalLayout_6.addWidget(self.lineEdit_10)

        self.label_26 = QLabel(self.layoutWidget1)
        self.label_26.setObjectName(u"label_26")

        self.horizontalLayout_6.addWidget(self.label_26)


        self.gridLayout_2.addLayout(self.horizontalLayout_6, 3, 0, 1, 1)

        self.groupBox_3 = QGroupBox(Form)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.groupBox_3.setGeometry(QRect(320, 400, 281, 151))
        self.layoutWidget2 = QWidget(self.groupBox_3)
        self.layoutWidget2.setObjectName(u"layoutWidget2")
        self.layoutWidget2.setGeometry(QRect(0, 20, 273, 124))
        self.verticalLayout = QVBoxLayout(self.layoutWidget2)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_11 = QLabel(self.layoutWidget2)
        self.label_11.setObjectName(u"label_11")
        sizePolicy.setHeightForWidth(self.label_11.sizePolicy().hasHeightForWidth())
        self.label_11.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.label_11)

        self.lineEdit_5 = QLineEdit(self.layoutWidget2)
        self.lineEdit_5.setObjectName(u"lineEdit_5")
        sizePolicy.setHeightForWidth(self.lineEdit_5.sizePolicy().hasHeightForWidth())
        self.lineEdit_5.setSizePolicy(sizePolicy)
        self.lineEdit_5.setMinimumSize(QSize(50, 0))

        self.horizontalLayout.addWidget(self.lineEdit_5)

        self.label_23 = QLabel(self.layoutWidget2)
        self.label_23.setObjectName(u"label_23")

        self.horizontalLayout.addWidget(self.label_23)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_9 = QLabel(self.layoutWidget2)
        self.label_9.setObjectName(u"label_9")
        sizePolicy.setHeightForWidth(self.label_9.sizePolicy().hasHeightForWidth())
        self.label_9.setSizePolicy(sizePolicy)

        self.horizontalLayout_2.addWidget(self.label_9)

        self.lineEdit_3 = QLineEdit(self.layoutWidget2)
        self.lineEdit_3.setObjectName(u"lineEdit_3")
        sizePolicy.setHeightForWidth(self.lineEdit_3.sizePolicy().hasHeightForWidth())
        self.lineEdit_3.setSizePolicy(sizePolicy)
        self.lineEdit_3.setMinimumSize(QSize(50, 0))

        self.horizontalLayout_2.addWidget(self.lineEdit_3)

        self.label_4 = QLabel(self.layoutWidget2)
        self.label_4.setObjectName(u"label_4")

        self.horizontalLayout_2.addWidget(self.label_4)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_12 = QLabel(self.layoutWidget2)
        self.label_12.setObjectName(u"label_12")
        sizePolicy.setHeightForWidth(self.label_12.sizePolicy().hasHeightForWidth())
        self.label_12.setSizePolicy(sizePolicy)

        self.horizontalLayout_4.addWidget(self.label_12)

        self.lineEdit_6 = QLineEdit(self.layoutWidget2)
        self.lineEdit_6.setObjectName(u"lineEdit_6")
        sizePolicy.setHeightForWidth(self.lineEdit_6.sizePolicy().hasHeightForWidth())
        self.lineEdit_6.setSizePolicy(sizePolicy)
        self.lineEdit_6.setMinimumSize(QSize(50, 0))

        self.horizontalLayout_4.addWidget(self.lineEdit_6)

        self.label_24 = QLabel(self.layoutWidget2)
        self.label_24.setObjectName(u"label_24")

        self.horizontalLayout_4.addWidget(self.label_24)


        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_13 = QLabel(self.layoutWidget2)
        self.label_13.setObjectName(u"label_13")
        sizePolicy.setHeightForWidth(self.label_13.sizePolicy().hasHeightForWidth())
        self.label_13.setSizePolicy(sizePolicy)

        self.horizontalLayout_5.addWidget(self.label_13)

        self.lineEdit_7 = QLineEdit(self.layoutWidget2)
        self.lineEdit_7.setObjectName(u"lineEdit_7")
        sizePolicy.setHeightForWidth(self.lineEdit_7.sizePolicy().hasHeightForWidth())
        self.lineEdit_7.setSizePolicy(sizePolicy)
        self.lineEdit_7.setMinimumSize(QSize(50, 0))

        self.horizontalLayout_5.addWidget(self.lineEdit_7)

        self.label_25 = QLabel(self.layoutWidget2)
        self.label_25.setObjectName(u"label_25")

        self.horizontalLayout_5.addWidget(self.label_25)


        self.verticalLayout.addLayout(self.horizontalLayout_5)

        self.groupBox_4 = QGroupBox(Form)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.groupBox_4.setGeometry(QRect(20, 630, 131, 41))
        self.layoutWidget3 = QWidget(self.groupBox_4)
        self.layoutWidget3.setObjectName(u"layoutWidget3")
        self.layoutWidget3.setGeometry(QRect(0, 20, 129, 23))
        self.horizontalLayout_14 = QHBoxLayout(self.layoutWidget3)
        self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
        self.horizontalLayout_14.setContentsMargins(0, 0, 0, 0)
        self.label_7 = QLabel(self.layoutWidget3)
        self.label_7.setObjectName(u"label_7")
        sizePolicy.setHeightForWidth(self.label_7.sizePolicy().hasHeightForWidth())
        self.label_7.setSizePolicy(sizePolicy)

        self.horizontalLayout_14.addWidget(self.label_7)

        self.checkBox_5 = QCheckBox(self.layoutWidget3)
        self.checkBox_5.setObjectName(u"checkBox_5")
        sizePolicy.setHeightForWidth(self.checkBox_5.sizePolicy().hasHeightForWidth())
        self.checkBox_5.setSizePolicy(sizePolicy)

        self.horizontalLayout_14.addWidget(self.checkBox_5)

        self.groupBox_5 = QGroupBox(Form)
        self.groupBox_5.setObjectName(u"groupBox_5")
        self.groupBox_5.setGeometry(QRect(20, 680, 301, 41))
        self.layoutWidget4 = QWidget(self.groupBox_5)
        self.layoutWidget4.setObjectName(u"layoutWidget4")
        self.layoutWidget4.setGeometry(QRect(0, 20, 307, 23))
        self.horizontalLayout_10 = QHBoxLayout(self.layoutWidget4)
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.horizontalLayout_10.setContentsMargins(0, 0, 0, 0)
        self.label_14 = QLabel(self.layoutWidget4)
        self.label_14.setObjectName(u"label_14")
        sizePolicy.setHeightForWidth(self.label_14.sizePolicy().hasHeightForWidth())
        self.label_14.setSizePolicy(sizePolicy)

        self.horizontalLayout_10.addWidget(self.label_14)

        self.checkBox_3 = QCheckBox(self.layoutWidget4)
        self.checkBox_3.setObjectName(u"checkBox_3")
        sizePolicy.setHeightForWidth(self.checkBox_3.sizePolicy().hasHeightForWidth())
        self.checkBox_3.setSizePolicy(sizePolicy)

        self.horizontalLayout_10.addWidget(self.checkBox_3)

        self.layoutWidget5 = QWidget(Form)
        self.layoutWidget5.setObjectName(u"layoutWidget5")
        self.layoutWidget5.setGeometry(QRect(20, 550, 268, 32))
        self.horizontalLayout_16 = QHBoxLayout(self.layoutWidget5)
        self.horizontalLayout_16.setObjectName(u"horizontalLayout_16")
        self.horizontalLayout_16.setContentsMargins(0, 0, 0, 0)
        self.pushButton_5 = QPushButton(self.layoutWidget5)
        self.pushButton_5.setObjectName(u"pushButton_5")
        sizePolicy.setHeightForWidth(self.pushButton_5.sizePolicy().hasHeightForWidth())
        self.pushButton_5.setSizePolicy(sizePolicy)

        self.horizontalLayout_16.addWidget(self.pushButton_5)

        self.pushButton_6 = QPushButton(self.layoutWidget5)
        self.pushButton_6.setObjectName(u"pushButton_6")
        sizePolicy.setHeightForWidth(self.pushButton_6.sizePolicy().hasHeightForWidth())
        self.pushButton_6.setSizePolicy(sizePolicy)

        self.horizontalLayout_16.addWidget(self.pushButton_6)

        self.layoutWidget6 = QWidget(Form)
        self.layoutWidget6.setObjectName(u"layoutWidget6")
        self.layoutWidget6.setGeometry(QRect(10, 10, 571, 25))
        self.horizontalLayout_15 = QHBoxLayout(self.layoutWidget6)
        self.horizontalLayout_15.setObjectName(u"horizontalLayout_15")
        self.horizontalLayout_15.setContentsMargins(0, 0, 0, 0)
        self.label_2 = QLabel(self.layoutWidget6)
        self.label_2.setObjectName(u"label_2")
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)

        self.horizontalLayout_15.addWidget(self.label_2)

        self.lineEdit = QLineEdit(self.layoutWidget6)
        self.lineEdit.setObjectName(u"lineEdit")
        sizePolicy.setHeightForWidth(self.lineEdit.sizePolicy().hasHeightForWidth())
        self.lineEdit.setSizePolicy(sizePolicy)
        self.lineEdit.setMinimumSize(QSize(359, 0))

        self.horizontalLayout_15.addWidget(self.lineEdit)

        self.label = QLabel(self.layoutWidget6)
        self.label.setObjectName(u"label")
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setPixmap(QPixmap(u":/logo.png"))
        self.label.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_15.addWidget(self.label)

        self.layoutWidget7 = QWidget(Form)
        self.layoutWidget7.setObjectName(u"layoutWidget7")
        self.layoutWidget7.setGeometry(QRect(20, 590, 581, 33))
        self.horizontalLayout_11 = QHBoxLayout(self.layoutWidget7)
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.horizontalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.pushButton_4 = QPushButton(self.layoutWidget7)
        self.pushButton_4.setObjectName(u"pushButton_4")
        sizePolicy.setHeightForWidth(self.pushButton_4.sizePolicy().hasHeightForWidth())
        self.pushButton_4.setSizePolicy(sizePolicy)

        self.horizontalLayout_11.addWidget(self.pushButton_4)

        self.lineEdit_11 = QLineEdit(self.layoutWidget7)
        self.lineEdit_11.setObjectName(u"lineEdit_11")

        self.horizontalLayout_11.addWidget(self.lineEdit_11)

        self.groupBox_6 = QGroupBox(Form)
        self.groupBox_6.setObjectName(u"groupBox_6")
        self.groupBox_6.setGeometry(QRect(10, 310, 581, 80))
        self.layoutWidget8 = QWidget(self.groupBox_6)
        self.layoutWidget8.setObjectName(u"layoutWidget8")
        self.layoutWidget8.setGeometry(QRect(11, 22, 552, 54))
        self.gridLayout_4 = QGridLayout(self.layoutWidget8)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gridLayout_4.setContentsMargins(0, 0, 0, 0)
        self.label_29 = QLabel(self.layoutWidget8)
        self.label_29.setObjectName(u"label_29")
        sizePolicy.setHeightForWidth(self.label_29.sizePolicy().hasHeightForWidth())
        self.label_29.setSizePolicy(sizePolicy)

        self.gridLayout_4.addWidget(self.label_29, 0, 0, 1, 1)

        self.checkBox_6 = QCheckBox(self.layoutWidget8)
        self.checkBox_6.setObjectName(u"checkBox_6")
        sizePolicy.setHeightForWidth(self.checkBox_6.sizePolicy().hasHeightForWidth())
        self.checkBox_6.setSizePolicy(sizePolicy)

        self.gridLayout_4.addWidget(self.checkBox_6, 0, 1, 1, 1)

        self.label_18 = QLabel(self.layoutWidget8)
        self.label_18.setObjectName(u"label_18")

        self.gridLayout_4.addWidget(self.label_18, 0, 2, 1, 1)

        self.checkBox_4 = QCheckBox(self.layoutWidget8)
        self.checkBox_4.setObjectName(u"checkBox_4")

        self.gridLayout_4.addWidget(self.checkBox_4, 0, 3, 1, 3)

        self.label_30 = QLabel(self.layoutWidget8)
        self.label_30.setObjectName(u"label_30")
        sizePolicy.setHeightForWidth(self.label_30.sizePolicy().hasHeightForWidth())
        self.label_30.setSizePolicy(sizePolicy)

        self.gridLayout_4.addWidget(self.label_30, 1, 0, 1, 1)

        self.checkBox_7 = QCheckBox(self.layoutWidget8)
        self.checkBox_7.setObjectName(u"checkBox_7")
        sizePolicy.setHeightForWidth(self.checkBox_7.sizePolicy().hasHeightForWidth())
        self.checkBox_7.setSizePolicy(sizePolicy)

        self.gridLayout_4.addWidget(self.checkBox_7, 1, 1, 1, 1)

        self.label_10 = QLabel(self.layoutWidget8)
        self.label_10.setObjectName(u"label_10")

        self.gridLayout_4.addWidget(self.label_10, 1, 2, 1, 2)

        self.lineEdit_4 = QLineEdit(self.layoutWidget8)
        self.lineEdit_4.setObjectName(u"lineEdit_4")

        self.gridLayout_4.addWidget(self.lineEdit_4, 1, 4, 1, 1)

        self.label_22 = QLabel(self.layoutWidget8)
        self.label_22.setObjectName(u"label_22")

        self.gridLayout_4.addWidget(self.label_22, 1, 5, 1, 1)


        self.retranslateUi(Form)

        self.pushButton.setDefault(True)


        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Neuro MINE Train", None))
        self.pushButton.setText(QCoreApplication.translate("Form", u"Run Model", None))
        self.groupBox.setTitle(QCoreApplication.translate("Form", u"Data Input", None))
        self.label_19.setText("")
        self.pushButton_2.setText(QCoreApplication.translate("Form", u"Browse Predictor File(s)...", None))
#if QT_CONFIG(tooltip)
        self.label_20.setToolTip("")
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(whatsthis)
        self.label_20.setWhatsThis(QCoreApplication.translate("Form", u"Predictor file(s) should be .csv format but with any type of delimiter; Time must be in the first column and all columns must have headers", None))
#endif // QT_CONFIG(whatsthis)
        self.label_20.setText("")
        self.pushButton_3.setText(QCoreApplication.translate("Form", u"Browse Response File(s)...", None))
#if QT_CONFIG(tooltip)
        self.label_21.setToolTip("")
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(whatsthis)
        self.label_21.setWhatsThis(QCoreApplication.translate("Form", u"Response file(s) should be .csv format but with any type of delimiter; time must be in the first column", None))
#endif // QT_CONFIG(whatsthis)
        self.label_21.setText("")
        self.groupBox_2.setTitle(QCoreApplication.translate("Form", u"Fitting Parameters:", None))
        self.label_8.setText(QCoreApplication.translate("Form", u"Test Score Threshold:", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"[0,1]", None))
        self.label_15.setText(QCoreApplication.translate("Form", u"Model History (sec):", None))
        self.label_28.setText(QCoreApplication.translate("Form", u">0", None))
        self.label_16.setText(QCoreApplication.translate("Form", u"Number of Epochs:", None))
        self.label_27.setText(QCoreApplication.translate("Form", u"{1,...,500}", None))
        self.label_17.setText(QCoreApplication.translate("Form", u"Train Data Fraction:", None))
        self.label_26.setText(QCoreApplication.translate("Form", u"[0,1]", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("Form", u"Taylor Expansion Parameters:", None))
        self.label_11.setText(QCoreApplication.translate("Form", u"Taylor Cutoff:", None))
        self.label_23.setText(QCoreApplication.translate("Form", u"[0,1]", None))
        self.label_9.setText(QCoreApplication.translate("Form", u"Significance Threshold:", None))
        self.label_4.setText(QCoreApplication.translate("Form", u"[0,1]", None))
        self.label_12.setText(QCoreApplication.translate("Form", u"Linear Fit Variance Fraction:", None))
        self.label_24.setText(QCoreApplication.translate("Form", u"[0,1]", None))
        self.label_13.setText(QCoreApplication.translate("Form", u"Square Fit Variance Fraction:", None))
        self.label_25.setText(QCoreApplication.translate("Form", u"[0,1]", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("Form", u"Run Diagnostics", None))
        self.label_7.setText(QCoreApplication.translate("Form", u"Run Shuffle:", None))
        self.checkBox_5.setText(QCoreApplication.translate("Form", u"Yes", None))
        self.groupBox_5.setTitle(QCoreApplication.translate("Form", u"Additional Outputs", None))
        self.label_14.setText(QCoreApplication.translate("Form", u"Store Linear Receptive Fields (Jacobians):", None))
        self.checkBox_3.setText(QCoreApplication.translate("Form", u"Yes", None))
        self.pushButton_5.setText(QCoreApplication.translate("Form", u"Restore Presets", None))
        self.pushButton_6.setText(QCoreApplication.translate("Form", u"Save Parameters", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"Model Name:", None))
        self.label.setText("")
        self.pushButton_4.setText(QCoreApplication.translate("Form", u"Populate Parameters from JSON...", None))
        self.groupBox_6.setTitle(QCoreApplication.translate("Form", u"Processing Parameters", None))
        self.label_29.setText(QCoreApplication.translate("Form", u"Use Time as a Predictor:", None))
        self.checkBox_6.setText(QCoreApplication.translate("Form", u"Yes", None))
        self.label_18.setText(QCoreApplication.translate("Form", u"Downsample Data:", None))
        self.checkBox_4.setText(QCoreApplication.translate("Form", u"Yes", None))
        self.label_30.setText(QCoreApplication.translate("Form", u"Data is Episodic:", None))
        self.checkBox_7.setText(QCoreApplication.translate("Form", u"Yes", None))
        self.label_10.setText(QCoreApplication.translate("Form", u"Downsampling Factor:", None))
        self.label_22.setText(QCoreApplication.translate("Form", u"{1,...,2^15}", None))
    # retranslateUi

