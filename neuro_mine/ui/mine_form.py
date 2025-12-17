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
from PySide6.QtWidgets import (QApplication, QCheckBox, QGridLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QTextEdit, QWidget)
import neuro_mine.ui.resources_rc

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(634, 632)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        self.label = QLabel(Form)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(570, 20, 35, 21))
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setPixmap(QPixmap(u":/logo.png"))
        self.label.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.pushButton = QPushButton(Form)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(530, 590, 94, 32))
        sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy)
        self.pushButton_6 = QPushButton(Form)
        self.pushButton_6.setObjectName(u"pushButton_6")
        self.pushButton_6.setGeometry(QRect(440, 560, 184, 32))
        sizePolicy.setHeightForWidth(self.pushButton_6.sizePolicy().hasHeightForWidth())
        self.pushButton_6.setSizePolicy(sizePolicy)
        self.layoutWidget = QWidget(Form)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(10, 20, 450, 23))
        self.horizontalLayout = QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.label_2 = QLabel(self.layoutWidget)
        self.label_2.setObjectName(u"label_2")
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.label_2)

        self.lineEdit = QLineEdit(self.layoutWidget)
        self.lineEdit.setObjectName(u"lineEdit")
        sizePolicy.setHeightForWidth(self.lineEdit.sizePolicy().hasHeightForWidth())
        self.lineEdit.setSizePolicy(sizePolicy)
        self.lineEdit.setMinimumSize(QSize(359, 0))

        self.horizontalLayout.addWidget(self.lineEdit)

        self.layoutWidget1 = QWidget(Form)
        self.layoutWidget1.setObjectName(u"layoutWidget1")
        self.layoutWidget1.setGeometry(QRect(10, 50, 311, 231))
        self.gridLayout = QGridLayout(self.layoutWidget1)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.label_20 = QLabel(self.layoutWidget1)
        self.label_20.setObjectName(u"label_20")
        sizePolicy.setHeightForWidth(self.label_20.sizePolicy().hasHeightForWidth())
        self.label_20.setSizePolicy(sizePolicy)
        self.label_20.setPixmap(QPixmap(u":/question.png"))

        self.gridLayout.addWidget(self.label_20, 1, 1, 1, 1)

        self.pushButton_2 = QPushButton(self.layoutWidget1)
        self.pushButton_2.setObjectName(u"pushButton_2")
        sizePolicy.setHeightForWidth(self.pushButton_2.sizePolicy().hasHeightForWidth())
        self.pushButton_2.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.pushButton_2, 1, 0, 1, 1)

        self.textEdit = QTextEdit(self.layoutWidget1)
        self.textEdit.setObjectName(u"textEdit")
        sizePolicy.setHeightForWidth(self.textEdit.sizePolicy().hasHeightForWidth())
        self.textEdit.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.textEdit, 0, 0, 1, 2)

        self.layoutWidget2 = QWidget(Form)
        self.layoutWidget2.setObjectName(u"layoutWidget2")
        self.layoutWidget2.setGeometry(QRect(330, 50, 291, 231))
        self.gridLayout_2 = QGridLayout(self.layoutWidget2)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.textEdit_2 = QTextEdit(self.layoutWidget2)
        self.textEdit_2.setObjectName(u"textEdit_2")
        sizePolicy.setHeightForWidth(self.textEdit_2.sizePolicy().hasHeightForWidth())
        self.textEdit_2.setSizePolicy(sizePolicy)

        self.gridLayout_2.addWidget(self.textEdit_2, 0, 0, 1, 2)

        self.pushButton_3 = QPushButton(self.layoutWidget2)
        self.pushButton_3.setObjectName(u"pushButton_3")
        sizePolicy.setHeightForWidth(self.pushButton_3.sizePolicy().hasHeightForWidth())
        self.pushButton_3.setSizePolicy(sizePolicy)

        self.gridLayout_2.addWidget(self.pushButton_3, 1, 0, 1, 1)

        self.label_21 = QLabel(self.layoutWidget2)
        self.label_21.setObjectName(u"label_21")
        sizePolicy.setHeightForWidth(self.label_21.sizePolicy().hasHeightForWidth())
        self.label_21.setSizePolicy(sizePolicy)
        self.label_21.setPixmap(QPixmap(u":/question.png"))

        self.gridLayout_2.addWidget(self.label_21, 1, 1, 1, 1)

        self.layoutWidget3 = QWidget(Form)
        self.layoutWidget3.setObjectName(u"layoutWidget3")
        self.layoutWidget3.setGeometry(QRect(10, 290, 476, 58))
        self.gridLayout_3 = QGridLayout(self.layoutWidget3)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_5 = QLabel(self.layoutWidget3)
        self.label_5.setObjectName(u"label_5")
        sizePolicy.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy)

        self.horizontalLayout_2.addWidget(self.label_5)

        self.checkBox = QCheckBox(self.layoutWidget3)
        self.checkBox.setObjectName(u"checkBox")
        sizePolicy.setHeightForWidth(self.checkBox.sizePolicy().hasHeightForWidth())
        self.checkBox.setSizePolicy(sizePolicy)

        self.horizontalLayout_2.addWidget(self.checkBox)


        self.gridLayout_3.addLayout(self.horizontalLayout_2, 0, 0, 1, 1)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_6 = QLabel(self.layoutWidget3)
        self.label_6.setObjectName(u"label_6")
        sizePolicy.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy)

        self.horizontalLayout_3.addWidget(self.label_6)

        self.checkBox_2 = QCheckBox(self.layoutWidget3)
        self.checkBox_2.setObjectName(u"checkBox_2")
        sizePolicy.setHeightForWidth(self.checkBox_2.sizePolicy().hasHeightForWidth())
        self.checkBox_2.setSizePolicy(sizePolicy)

        self.horizontalLayout_3.addWidget(self.checkBox_2)


        self.gridLayout_3.addLayout(self.horizontalLayout_3, 0, 1, 1, 1)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_18 = QLabel(self.layoutWidget3)
        self.label_18.setObjectName(u"label_18")
        sizePolicy.setHeightForWidth(self.label_18.sizePolicy().hasHeightForWidth())
        self.label_18.setSizePolicy(sizePolicy)

        self.horizontalLayout_6.addWidget(self.label_18)

        self.checkBox_4 = QCheckBox(self.layoutWidget3)
        self.checkBox_4.setObjectName(u"checkBox_4")
        sizePolicy.setHeightForWidth(self.checkBox_4.sizePolicy().hasHeightForWidth())
        self.checkBox_4.setSizePolicy(sizePolicy)

        self.horizontalLayout_6.addWidget(self.checkBox_4)


        self.gridLayout_3.addLayout(self.horizontalLayout_6, 0, 2, 1, 1)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_7 = QLabel(self.layoutWidget3)
        self.label_7.setObjectName(u"label_7")
        sizePolicy.setHeightForWidth(self.label_7.sizePolicy().hasHeightForWidth())
        self.label_7.setSizePolicy(sizePolicy)

        self.horizontalLayout_4.addWidget(self.label_7)

        self.checkBox_5 = QCheckBox(self.layoutWidget3)
        self.checkBox_5.setObjectName(u"checkBox_5")
        sizePolicy.setHeightForWidth(self.checkBox_5.sizePolicy().hasHeightForWidth())
        self.checkBox_5.setSizePolicy(sizePolicy)

        self.horizontalLayout_4.addWidget(self.checkBox_5)


        self.gridLayout_3.addLayout(self.horizontalLayout_4, 1, 0, 1, 1)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_14 = QLabel(self.layoutWidget3)
        self.label_14.setObjectName(u"label_14")
        sizePolicy.setHeightForWidth(self.label_14.sizePolicy().hasHeightForWidth())
        self.label_14.setSizePolicy(sizePolicy)

        self.horizontalLayout_5.addWidget(self.label_14)

        self.checkBox_3 = QCheckBox(self.layoutWidget3)
        self.checkBox_3.setObjectName(u"checkBox_3")
        sizePolicy.setHeightForWidth(self.checkBox_3.sizePolicy().hasHeightForWidth())
        self.checkBox_3.setSizePolicy(sizePolicy)

        self.horizontalLayout_5.addWidget(self.checkBox_3)


        self.gridLayout_3.addLayout(self.horizontalLayout_5, 1, 1, 1, 2)

        self.layoutWidget4 = QWidget(Form)
        self.layoutWidget4.setObjectName(u"layoutWidget4")
        self.layoutWidget4.setGeometry(QRect(10, 520, 611, 33))
        self.horizontalLayout_8 = QHBoxLayout(self.layoutWidget4)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.pushButton_4 = QPushButton(self.layoutWidget4)
        self.pushButton_4.setObjectName(u"pushButton_4")
        sizePolicy.setHeightForWidth(self.pushButton_4.sizePolicy().hasHeightForWidth())
        self.pushButton_4.setSizePolicy(sizePolicy)

        self.horizontalLayout_8.addWidget(self.pushButton_4)

        self.lineEdit_11 = QLineEdit(self.layoutWidget4)
        self.lineEdit_11.setObjectName(u"lineEdit_11")
        sizePolicy.setHeightForWidth(self.lineEdit_11.sizePolicy().hasHeightForWidth())
        self.lineEdit_11.setSizePolicy(sizePolicy)
        self.lineEdit_11.setMinimumSize(QSize(359, 0))

        self.horizontalLayout_8.addWidget(self.lineEdit_11)

        self.layoutWidget5 = QWidget(Form)
        self.layoutWidget5.setObjectName(u"layoutWidget5")
        self.layoutWidget5.setGeometry(QRect(10, 350, 611, 166))
        self.gridLayout_6 = QGridLayout(self.layoutWidget5)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.gridLayout_6.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_4 = QGridLayout()
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.label_8 = QLabel(self.layoutWidget5)
        self.label_8.setObjectName(u"label_8")
        sizePolicy.setHeightForWidth(self.label_8.sizePolicy().hasHeightForWidth())
        self.label_8.setSizePolicy(sizePolicy)

        self.horizontalLayout_7.addWidget(self.label_8)

        self.lineEdit_2 = QLineEdit(self.layoutWidget5)
        self.lineEdit_2.setObjectName(u"lineEdit_2")
        sizePolicy.setHeightForWidth(self.lineEdit_2.sizePolicy().hasHeightForWidth())
        self.lineEdit_2.setSizePolicy(sizePolicy)
        self.lineEdit_2.setMinimumSize(QSize(50, 0))

        self.horizontalLayout_7.addWidget(self.lineEdit_2)

        self.label_3 = QLabel(self.layoutWidget5)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_7.addWidget(self.label_3)


        self.gridLayout_4.addLayout(self.horizontalLayout_7, 0, 0, 1, 1)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.label_9 = QLabel(self.layoutWidget5)
        self.label_9.setObjectName(u"label_9")
        sizePolicy.setHeightForWidth(self.label_9.sizePolicy().hasHeightForWidth())
        self.label_9.setSizePolicy(sizePolicy)

        self.horizontalLayout_9.addWidget(self.label_9)

        self.lineEdit_3 = QLineEdit(self.layoutWidget5)
        self.lineEdit_3.setObjectName(u"lineEdit_3")
        sizePolicy.setHeightForWidth(self.lineEdit_3.sizePolicy().hasHeightForWidth())
        self.lineEdit_3.setSizePolicy(sizePolicy)
        self.lineEdit_3.setMinimumSize(QSize(50, 0))

        self.horizontalLayout_9.addWidget(self.lineEdit_3)

        self.label_4 = QLabel(self.layoutWidget5)
        self.label_4.setObjectName(u"label_4")

        self.horizontalLayout_9.addWidget(self.label_4)


        self.gridLayout_4.addLayout(self.horizontalLayout_9, 1, 0, 1, 1)

        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.label_10 = QLabel(self.layoutWidget5)
        self.label_10.setObjectName(u"label_10")
        sizePolicy.setHeightForWidth(self.label_10.sizePolicy().hasHeightForWidth())
        self.label_10.setSizePolicy(sizePolicy)

        self.horizontalLayout_10.addWidget(self.label_10)

        self.lineEdit_4 = QLineEdit(self.layoutWidget5)
        self.lineEdit_4.setObjectName(u"lineEdit_4")
        sizePolicy.setHeightForWidth(self.lineEdit_4.sizePolicy().hasHeightForWidth())
        self.lineEdit_4.setSizePolicy(sizePolicy)
        self.lineEdit_4.setMinimumSize(QSize(50, 0))

        self.horizontalLayout_10.addWidget(self.lineEdit_4)

        self.label_22 = QLabel(self.layoutWidget5)
        self.label_22.setObjectName(u"label_22")

        self.horizontalLayout_10.addWidget(self.label_22)


        self.gridLayout_4.addLayout(self.horizontalLayout_10, 2, 0, 1, 1)

        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.label_12 = QLabel(self.layoutWidget5)
        self.label_12.setObjectName(u"label_12")
        sizePolicy.setHeightForWidth(self.label_12.sizePolicy().hasHeightForWidth())
        self.label_12.setSizePolicy(sizePolicy)

        self.horizontalLayout_11.addWidget(self.label_12)

        self.lineEdit_6 = QLineEdit(self.layoutWidget5)
        self.lineEdit_6.setObjectName(u"lineEdit_6")
        sizePolicy.setHeightForWidth(self.lineEdit_6.sizePolicy().hasHeightForWidth())
        self.lineEdit_6.setSizePolicy(sizePolicy)
        self.lineEdit_6.setMinimumSize(QSize(50, 0))

        self.horizontalLayout_11.addWidget(self.lineEdit_6)

        self.label_24 = QLabel(self.layoutWidget5)
        self.label_24.setObjectName(u"label_24")

        self.horizontalLayout_11.addWidget(self.label_24)


        self.gridLayout_4.addLayout(self.horizontalLayout_11, 3, 0, 1, 1)

        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.label_13 = QLabel(self.layoutWidget5)
        self.label_13.setObjectName(u"label_13")
        sizePolicy.setHeightForWidth(self.label_13.sizePolicy().hasHeightForWidth())
        self.label_13.setSizePolicy(sizePolicy)

        self.horizontalLayout_12.addWidget(self.label_13)

        self.lineEdit_7 = QLineEdit(self.layoutWidget5)
        self.lineEdit_7.setObjectName(u"lineEdit_7")
        sizePolicy.setHeightForWidth(self.lineEdit_7.sizePolicy().hasHeightForWidth())
        self.lineEdit_7.setSizePolicy(sizePolicy)
        self.lineEdit_7.setMinimumSize(QSize(50, 0))

        self.horizontalLayout_12.addWidget(self.lineEdit_7)

        self.label_25 = QLabel(self.layoutWidget5)
        self.label_25.setObjectName(u"label_25")

        self.horizontalLayout_12.addWidget(self.label_25)


        self.gridLayout_4.addLayout(self.horizontalLayout_12, 4, 0, 1, 1)


        self.gridLayout_6.addLayout(self.gridLayout_4, 0, 0, 2, 1)

        self.gridLayout_5 = QGridLayout()
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.horizontalLayout_13 = QHBoxLayout()
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.label_11 = QLabel(self.layoutWidget5)
        self.label_11.setObjectName(u"label_11")
        sizePolicy.setHeightForWidth(self.label_11.sizePolicy().hasHeightForWidth())
        self.label_11.setSizePolicy(sizePolicy)

        self.horizontalLayout_13.addWidget(self.label_11)

        self.lineEdit_5 = QLineEdit(self.layoutWidget5)
        self.lineEdit_5.setObjectName(u"lineEdit_5")
        sizePolicy.setHeightForWidth(self.lineEdit_5.sizePolicy().hasHeightForWidth())
        self.lineEdit_5.setSizePolicy(sizePolicy)
        self.lineEdit_5.setMinimumSize(QSize(50, 0))

        self.horizontalLayout_13.addWidget(self.lineEdit_5)

        self.label_23 = QLabel(self.layoutWidget5)
        self.label_23.setObjectName(u"label_23")

        self.horizontalLayout_13.addWidget(self.label_23)


        self.gridLayout_5.addLayout(self.horizontalLayout_13, 0, 0, 1, 1)

        self.horizontalLayout_14 = QHBoxLayout()
        self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
        self.label_15 = QLabel(self.layoutWidget5)
        self.label_15.setObjectName(u"label_15")
        sizePolicy.setHeightForWidth(self.label_15.sizePolicy().hasHeightForWidth())
        self.label_15.setSizePolicy(sizePolicy)

        self.horizontalLayout_14.addWidget(self.label_15)

        self.lineEdit_8 = QLineEdit(self.layoutWidget5)
        self.lineEdit_8.setObjectName(u"lineEdit_8")
        sizePolicy.setHeightForWidth(self.lineEdit_8.sizePolicy().hasHeightForWidth())
        self.lineEdit_8.setSizePolicy(sizePolicy)
        self.lineEdit_8.setMinimumSize(QSize(50, 0))

        self.horizontalLayout_14.addWidget(self.lineEdit_8)

        self.label_28 = QLabel(self.layoutWidget5)
        self.label_28.setObjectName(u"label_28")

        self.horizontalLayout_14.addWidget(self.label_28)


        self.gridLayout_5.addLayout(self.horizontalLayout_14, 1, 0, 1, 1)

        self.horizontalLayout_15 = QHBoxLayout()
        self.horizontalLayout_15.setObjectName(u"horizontalLayout_15")
        self.label_16 = QLabel(self.layoutWidget5)
        self.label_16.setObjectName(u"label_16")
        sizePolicy.setHeightForWidth(self.label_16.sizePolicy().hasHeightForWidth())
        self.label_16.setSizePolicy(sizePolicy)

        self.horizontalLayout_15.addWidget(self.label_16)

        self.lineEdit_9 = QLineEdit(self.layoutWidget5)
        self.lineEdit_9.setObjectName(u"lineEdit_9")
        sizePolicy.setHeightForWidth(self.lineEdit_9.sizePolicy().hasHeightForWidth())
        self.lineEdit_9.setSizePolicy(sizePolicy)
        self.lineEdit_9.setMinimumSize(QSize(50, 0))

        self.horizontalLayout_15.addWidget(self.lineEdit_9)

        self.label_27 = QLabel(self.layoutWidget5)
        self.label_27.setObjectName(u"label_27")

        self.horizontalLayout_15.addWidget(self.label_27)


        self.gridLayout_5.addLayout(self.horizontalLayout_15, 2, 0, 1, 1)

        self.horizontalLayout_16 = QHBoxLayout()
        self.horizontalLayout_16.setObjectName(u"horizontalLayout_16")
        self.label_17 = QLabel(self.layoutWidget5)
        self.label_17.setObjectName(u"label_17")
        sizePolicy.setHeightForWidth(self.label_17.sizePolicy().hasHeightForWidth())
        self.label_17.setSizePolicy(sizePolicy)

        self.horizontalLayout_16.addWidget(self.label_17)

        self.lineEdit_10 = QLineEdit(self.layoutWidget5)
        self.lineEdit_10.setObjectName(u"lineEdit_10")
        sizePolicy.setHeightForWidth(self.lineEdit_10.sizePolicy().hasHeightForWidth())
        self.lineEdit_10.setSizePolicy(sizePolicy)
        self.lineEdit_10.setMinimumSize(QSize(50, 0))

        self.horizontalLayout_16.addWidget(self.lineEdit_10)

        self.label_26 = QLabel(self.layoutWidget5)
        self.label_26.setObjectName(u"label_26")

        self.horizontalLayout_16.addWidget(self.label_26)


        self.gridLayout_5.addLayout(self.horizontalLayout_16, 3, 0, 1, 1)


        self.gridLayout_6.addLayout(self.gridLayout_5, 0, 1, 1, 1)

        self.pushButton_5 = QPushButton(self.layoutWidget5)
        self.pushButton_5.setObjectName(u"pushButton_5")
        sizePolicy.setHeightForWidth(self.pushButton_5.sizePolicy().hasHeightForWidth())
        self.pushButton_5.setSizePolicy(sizePolicy)

        self.gridLayout_6.addWidget(self.pushButton_5, 1, 1, 1, 1)


        self.retranslateUi(Form)

        self.pushButton.setDefault(True)


        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Neuro MINE", None))
        self.label.setText("")
        self.pushButton.setText(QCoreApplication.translate("Form", u"Run Model", None))
        self.pushButton_6.setText(QCoreApplication.translate("Form", u"Save Parameters to JSON", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"Model Name:", None))
#if QT_CONFIG(tooltip)
        self.label_20.setToolTip("")
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(whatsthis)
        self.label_20.setWhatsThis(QCoreApplication.translate("Form", u"Predictor file(s) should be .csv format but with any type of delimiter; Time must be in the first column and all columns must have headers", None))
#endif // QT_CONFIG(whatsthis)
        self.label_20.setText("")
        self.pushButton_2.setText(QCoreApplication.translate("Form", u"Browse Predictor File(s)...", None))
        self.pushButton_3.setText(QCoreApplication.translate("Form", u"Browse Response File(s)...", None))
#if QT_CONFIG(tooltip)
        self.label_21.setToolTip("")
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(whatsthis)
        self.label_21.setWhatsThis(QCoreApplication.translate("Form", u"Response file(s) should be .csv format but with any type of delimiter; time must be in the first column", None))
#endif // QT_CONFIG(whatsthis)
        self.label_21.setText("")
        self.label_5.setText(QCoreApplication.translate("Form", u"Episodic Data:", None))
        self.checkBox.setText(QCoreApplication.translate("Form", u"Yes", None))
        self.label_6.setText(QCoreApplication.translate("Form", u"Uee Time as a Predictor:", None))
        self.checkBox_2.setText(QCoreApplication.translate("Form", u"Yes", None))
        self.label_18.setText(QCoreApplication.translate("Form", u"Verbose:", None))
        self.checkBox_4.setText(QCoreApplication.translate("Form", u"Yes", None))
        self.label_7.setText(QCoreApplication.translate("Form", u"Run Shuffle:", None))
        self.checkBox_5.setText(QCoreApplication.translate("Form", u"Yes", None))
        self.label_14.setText(QCoreApplication.translate("Form", u"Store Linear Receptive Fields (Jacobians):", None))
        self.checkBox_3.setText(QCoreApplication.translate("Form", u"Yes", None))
        self.pushButton_4.setText(QCoreApplication.translate("Form", u"Populate Parameters from JSON...", None))
        self.label_8.setText(QCoreApplication.translate("Form", u"Test Score Threshold:", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"[0,1]", None))
        self.label_9.setText(QCoreApplication.translate("Form", u"Taylor Expansion Significance Threshold:", None))
        self.label_4.setText(QCoreApplication.translate("Form", u"[0,1]", None))
        self.label_10.setText(QCoreApplication.translate("Form", u"Taylor Expansion Look Ahead:", None))
        self.label_22.setText(QCoreApplication.translate("Form", u"(0,4)", None))
        self.label_12.setText(QCoreApplication.translate("Form", u"Linear Fit Variance Fraction:", None))
        self.label_24.setText(QCoreApplication.translate("Form", u"[0,1]", None))
        self.label_13.setText(QCoreApplication.translate("Form", u"Square Fit Variance Fraction:", None))
        self.label_25.setText(QCoreApplication.translate("Form", u"[0,1]", None))
        self.label_11.setText(QCoreApplication.translate("Form", u"Taylor Cutoff:", None))
        self.label_23.setText(QCoreApplication.translate("Form", u"[0,1]", None))
        self.label_15.setText(QCoreApplication.translate("Form", u"Model History (seconds):", None))
        self.label_28.setText(QCoreApplication.translate("Form", u"\u22651", None))
        self.label_16.setText(QCoreApplication.translate("Form", u"Number of Epochs:", None))
        self.label_27.setText(QCoreApplication.translate("Form", u"[1,100]", None))
        self.label_17.setText(QCoreApplication.translate("Form", u"Train Data Fraction:", None))
        self.label_26.setText(QCoreApplication.translate("Form", u"[0,1]", None))
        self.pushButton_5.setText(QCoreApplication.translate("Form", u"Restore Preset Parameters", None))
    # retranslateUi

