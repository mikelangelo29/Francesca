import json
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton,
    QHBoxLayout, QDialog, QFormLayout, QLineEdit, QDateEdit, QMessageBox, QApplication, QHeaderView, QWidget, QHBoxLayout
)
from PyQt5.QtCore import Qt, QDate
from functools import partial
from datetime import datetime
from scheda_paziente import SchedaPazienteWindow
import shutil

DATA_FILE = "pazienti.json"

class NuovoPazienteDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nuovo paziente")
        layout = QFormLayout(self)

        self.nome_edit = QLineEdit()
        self.cognome_edit = QLineEdit()
        self.data_nascita_edit = QDateEdit()
        self.data_nascita_edit.setCalendarPopup(True)
        self.data_nascita_edit.setDisplayFormat("dd/MM/yyyy")
        self.data_nascita_edit.setMinimumDate(QDate(1920, 1, 1))
        self.data_nascita_edit.setMaximumDate(QDate.currentDate())
        self.data_nascita_edit.setDate(QDate(1980, 1, 1))

        self.data_ricovero_edit = QDateEdit()
        self.data_ricovero_edit.setCalendarPopup(True)
        self.data_ricovero_edit.setDisplayFormat("dd/MM/yyyy")
        oggi = QDate.currentDate()
        self.data_ricovero_edit.setMinimumDate(oggi.addYears(-1))
        self.data_ricovero_edit.setMaximumDate(oggi.addYears(5))
        self.data_ricovero_edit.setDate(oggi)

        layout.addRow("Nome:", self.nome_edit)
        layout.addRow("Cognome:", self.cognome_edit)
        layout.addRow("Data di nascita:", self.data_nascita_edit)
        layout.addRow("Data di ricovero:", self.data_ricovero_edit)

        btn_layout = QHBoxLayout()
        salva_btn = QPushButton("Salva")
        salva_btn.clicked.connect(self.accept)
        annulla_btn = QPushButton("Annulla")
        annulla_btn.clicked.connect(self.reject)
        btn_layout.addWidget(salva_btn)
        btn_layout.addWidget(annulla_btn)
        layout.addRow(btn_layout)

    def get_dati(self):
        return (
            self.nome_edit.text().strip(),
            self.cognome_edit.text().strip(),
            self.data_nascita_edit.date().toString("dd/MM/yyyy"),
            self.data_ricovero_edit.date().toString("dd/MM/yyyy")
        )

class PazientiAttiviWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pazienti Attivi")
        self.setMinimumWidth(750)
        self.setMinimumHeight(320)

        self.dati = self.carica_pazienti()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 14, 20, 14)
        layout.setSpacing(16)

        label = QLabel("Elenco Pazienti Attivi")
        label.setStyleSheet("font-size: 19px; font-weight: bold; color: #023047; padding-bottom: 9px;")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        btn_layout = QHBoxLayout()
        self.nuovo_btn = QPushButton("Nuovo paziente")
        self.nuovo_btn.setStyleSheet("font-size:13px; background:#43a047; color:white; padding:2px 11px; border-radius:6px;")
        self.nuovo_btn.clicked.connect(self.nuovo_paziente)
        self.elimina_btn = QPushButton("Elimina selezionato")
        self.elimina_btn.setStyleSheet("font-size:13px; background:#e53935; color:white; padding:2px 11px; border-radius:6px;")
        self.elimina_btn.clicked.connect(self.elimina_paziente)
        self.dimetti_btn = QPushButton("Dimetti paziente")
        self.dimetti_btn.setStyleSheet("font-size:13px; background:#ffa726; color:white; padding:2px 11px; border-radius:6px;")
        self.dimetti_btn.clicked.connect(self.dimetti_paziente)
        btn_layout.addWidget(self.dimetti_btn)
        btn_layout.addWidget(self.nuovo_btn)
        btn_layout.addWidget(self.elimina_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Nome", "Cognome", "Data di nascita", "Data di ricovero", ""
        ])
        self.table.setMinimumWidth(700)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setStyleSheet("""
            QTableWidget {font-size: 13px; border: none;}
            QTableWidget::item {padding: 6px 8px; border: none;}
            QTableWidget::item:selected {background: #B3E5FC; color: #212121;}
            QHeaderView::section {background-color: #e0e0e0; font-size: 14px; font-weight: bold; border: none;}
            QScrollBar:vertical {
                width: 18px;
                background: #b0b0b0;
                margin: 0px;
                border-radius: 7px;
            }
            QScrollBar::handle:vertical {
                background: #616161;
                min-height: 24px;
                border-radius: 7px;
            }
            QScrollBar:horizontal {
                height: 18px;
                background: #b0b0b0;
                margin: 0px;
                border-radius: 7px;
            }
            QScrollBar::handle:horizontal {
                background: #616161;
                min-width: 24px;
                border-radius: 7px;
            }
        """)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setFocusPolicy(Qt.StrongFocus)

        header = self.table.horizontalHeader()
        for i in range(4):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.horizontalHeaderItem(0).setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.table.horizontalHeaderItem(1).setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.table.horizontalHeaderItem(2).setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.table.horizontalHeaderItem(3).setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.table.horizontalHeaderItem(4).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)

        self.aggiorna_tabella()
        layout.addWidget(self.table)

        self.adjustSize()

    def carica_pazienti(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def salva_pazienti(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.dati, f, ensure_ascii=False, indent=2)

    def aggiorna_tabella(self):
        self.table.setRowCount(len(self.dati))
        for riga, paziente in enumerate(self.dati):
            if isinstance(paziente, dict):
                nome = paziente.get("nome", "")
                cognome = paziente.get("cognome", "")
                nascita = paziente.get("data_nascita", "")
                ricovero = paziente.get("data_ricovero", "")
            else:
                nome, cognome, nascita, ricovero = paziente
            for i, value in enumerate([nome, cognome, nascita, ricovero]):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                item.setFont(self.table.font())
                self.table.setItem(riga, i, item)

            btn = QPushButton("Scheda")
            btn.setFixedWidth(90)
            btn.setFixedHeight(25)
            btn.setStyleSheet("""
            QPushButton {
                font-size: 11px;
                background-color: #1976d2;
                color: white;
                border-radius: 4px;
            }
            QPushButton:pressed {
                background-color: #115293;
                padding-top: 2px;
                padding-bottom: 0px;
}                 
            """)
            btn.setFocusPolicy(Qt.NoFocus)
            btn.clicked.connect(partial(self.apri_scheda, riga))

            cell_widget = QWidget()
            cell_layout = QHBoxLayout(cell_widget)
            cell_layout.setContentsMargins(0, 0, 8, 0)  # margine destro moderato
            cell_layout.addWidget(btn)
            cell_layout.setAlignment(Qt.AlignRight)
            self.table.setCellWidget(riga, 4, cell_widget)

        self.table.resizeRowsToContents()

    def nuovo_paziente(self):
        dlg = NuovoPazienteDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            dati = dlg.get_dati()
            if all(dati[:2]):
                nuovo = {
                    "nome": dati[0],
                    "cognome": dati[1],
                    "data_nascita": dati[2],
                    "data_ricovero": dati[3]
                }
                self.dati.append(nuovo)
                self.salva_pazienti()
                self.aggiorna_tabella()
            else:
                QMessageBox.warning(self, "Errore", "Compila nome e cognome!")

    def elimina_paziente(self):
        import os, shutil
        from PyQt5.QtWidgets import QMessageBox

        r = self.table.currentRow()
        if r < 0 or r >= len(self.dati):
            QMessageBox.information(
                self, "Seleziona paziente", "Seleziona un paziente dalla tabella."
            )
            return

        paziente = self.dati[r]
        nome = paziente["nome"] if isinstance(paziente, dict) else paziente[0]
        cognome = paziente["cognome"] if isinstance(paziente, dict) else paziente[1]

        reply = QMessageBox.question(
            self,
            "Conferma eliminazione",
            f"Eliminare definitivamente il paziente selezionato ({nome} {cognome})?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        # 🔹 elimina dal JSON e aggiorna GUI (identico alla vecchia versione)
        del self.dati[r]
        self.salva_pazienti()
        self.aggiorna_tabella()

        # 🔹 cerca ed elimina le cartelle dopo il salvataggio
        base = "pazienti"
        prefix = f"{nome}_{cognome}_"
        if os.path.exists(base):
            for d in os.listdir(base):
                if d.startswith(prefix):
                    p = os.path.join(base, d)
                    if os.path.isdir(p):
                        try:
                            shutil.rmtree(p)
                        except Exception as e:
                            QMessageBox.warning(
                                self, "Errore eliminazione", f"Impossibile eliminare {p}:\n{e}"
                            )

    import os
    import shutil

    def dimetti_paziente(self):
        riga = self.table.currentRow()
        if riga < 0:
            QMessageBox.warning(self, "Selezione", "Seleziona un paziente da dimettere.")
            return

        paziente = self.dati.pop(riga)
        self.salva_pazienti()

        # aggiungi a dimessi.json
        dimessi = []
        if os.path.exists("dimessi.json"):
            with open("dimessi.json", "r", encoding="utf-8") as f:
                dimessi = json.load(f)
        dimessi.append(paziente)
        with open("dimessi.json", "w", encoding="utf-8") as f:
            json.dump(dimessi, f, indent=2, ensure_ascii=False)

        # sposta cartella
        eta = self.calcola_eta(paziente["data_nascita"])
        src = os.path.join("pazienti", f"{paziente['nome']}_{paziente['cognome']}_{eta}a")
        dst = os.path.join("dimessi", f"{paziente['nome']}_{paziente['cognome']}_{eta}a")
        try:
            if os.path.exists(src):
                shutil.move(src, dst)
            else:
                print(f"Attenzione: la cartella {src} non esiste.")
        except Exception as e:
            print(f"Errore durante lo spostamento della cartella: {e}")

        self.aggiorna_tabella()


    def apri_scheda(self, riga):
        self.table.clearSelection()
        paziente = self.dati[riga]
        if isinstance(paziente, dict):
            nome = paziente.get("nome", "")
            cognome = paziente.get("cognome", "")
            nascita = paziente.get("data_nascita", "")
            ricovero = paziente.get("data_ricovero", "")
        else:
            nome, cognome, nascita, ricovero = paziente
        eta = self.calcola_eta(nascita)
        valutazioni_aperte = []
        valutazioni_completate = []
        report_indici = []
        report_completi = []
        grafici = []
        self.scheda = SchedaPazienteWindow(
            nome, cognome, eta, valutazioni_aperte, valutazioni_completate, report_indici, report_completi, grafici
        )
        self.scheda.show()

    def calcola_eta(self, data_nascita):
        try:
            nascita = datetime.strptime(data_nascita, "%d/%m/%Y")
            oggi = datetime.today()
            eta = oggi.year - nascita.year - ((oggi.month, oggi.day) < (nascita.month, nascita.day))
            return eta
        except Exception:
            return "?"

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    win = PazientiAttiviWindow()
    win.showMaximized()  # la finestra si apre direttamente a schermo intero
    sys.exit(app.exec_())