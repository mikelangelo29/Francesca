from PyQt5.QtWidgets import QApplication, QListWidget, QListWidgetItem
import sys

app = QApplication(sys.argv)
w = QListWidget()
for nome in ["report1", "report2", "report3"]:
    item = QListWidgetItem(f"💾 {nome}")
    item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
    item.setCheckState(Qt.Unchecked)
    w.addItem(item)
w.show()
sys.exit(app.exec_())