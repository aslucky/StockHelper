# coding:utf8

import sys

from PyQt4 import QtGui, QtCore, uic


class PickupWindow(QtGui.QWidget):
    def __init__(self):
        super(PickupWindow, self).__init__()
        self.ui = uic.loadUi('../resource/pickup.ui', self)
        self.setWindowTitle("Stock Helper")
        self.setWindowIcon(QtGui.QIcon('../resource/app.png'))

        self.comboBox_maCondition.addItem(u'金叉')
        self.comboBox_maCondition.addItem(u'死叉')
        self.comboBox_maCondition.addItem(u'多头排列')

        self.comboBox_period.addItem(u'日线')
        self.comboBox_period.addItem(u'周线')

        list_data = ['MA', "MACD"]
        self.listWidget_condition.addItems(list_data)
        self.listWidget_condition.currentItemChanged.connect(self.on_item_changed)

    def on_item_changed(self, current, previous):
        if current.text() == "MA":
            self.stackedWidget.setCurrentIndex(0)
        elif current.text() == "MACD":
            self.stackedWidget.setCurrentIndex(1)

    def on_addPickupCond(self):
        str = u'';
        if self.listWidget_condition.currentItem().text() == "MA":
            str += self.lineEdit_ma1.text() + u'日均线与' + self.lineEdit_ma2.text() + u'日均线' + self.comboBox_maCondition.currentText()

        self.listWidget_pickupConds.addItem(str)

    def on_pickup(self):
        pass

    def on_deletePickupCond(self):
        item = self.listWidget_pickupConds.takeItem(self.listWidget_pickupConds.currentRow())
        item = None

    def on_specificDate(self):
        pass


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    gui = PickupWindow()
    gui.show()
    sys.exit(app.exec_())
