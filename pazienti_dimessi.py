from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton,
    QHBoxLayout, QDialog, QFormLayout, QLineEdit, QDateEdit, QMessageBox, QApplication
)
from PyQt5.QtCore import Qt, QDate
from datetime import datetime
# from scheda_paziente import SchedaPazienteWindow # decommenta se hai la classe

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
        self.data_nascita_edit.setDate(QDate(1980, 1, 1))  # default facile da modificare

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

class PazientiDimessiWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pazienti Attivi")
        self.setMinimumWidth(750)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(24)

        label = QLabel("Elenco Pazienti Attivi")
        label.setStyleSheet("font-size: 19px; font-weight: bold; color: #023047; padding-bottom: 12px;")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        # Bottoni
        btn_layout = QHBoxLayout()
        self.nuovo_btn = QPushButton("Nuovo paziente")
        self.nuovo_btn.setStyleSheet("font-size:14px; background:#43a047; color:white; padding:3px 12px; border-radius:6px;")
        self.nuovo_btn.clicked.connect(self.nuovo_paziente)
        self.elimina_btn = QPushButton("Elimina selezionato")
        self.elimina_btn.setStyleSheet("font-size:14px; background:#e53935; color:white; padding:3px 12px; border-radius:6px;")
        self.elimina_btn.clicked.connect(self.elimina_paziente)
        btn_layout.addWidget(self.nuovo_btn)
        btn_layout.addWidget(self.elimina_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.dati = [
            ("Mario", "Rossi", "01/03/1975", "21/08/2025"),
            ("Giulia", "Verdi", "12/07/1983", "19/08/2025"),
            ("Franco", "Bianchi", "25/11/1990", "17/08/2025")
        ]

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Nome", "Cognome", "Data di nascita", "Data di ricovero", ""
        ])
        self.table.setMinimumWidth(700)
        self.table.setStyleSheet("""
            QTableWidget {font-size: 13px; border: none;}
            QTableWidget::item {padding: 2px; border: none;}
            QHeaderView::section {background-color: #e0e0e0; font-size: 14px; font-weight: bold; border: none; padding-right: 20px; padding-left: 10px;}
        """)
        self.table.setAlternatingRowColors(False)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.setShowGrid(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setFocusPolicy(Qt.StrongFocus)

        self.aggiorna_tabella()

        # Larghezza fissa delle colonne
        header = self.table.horizontalHeader()
        for i, w in enumerate([120, 120, 170, 170, 60]):
            header.setSectionResizeMode(i, self.table.horizontalHeader().Fixed)
            self.table.setColumnWidth(i, w)

        layout.addWidget(self.table)

    def aggiorna_tabella(self):
        self.table.setRowCount(len(self.dati))
        for riga, (nome, cognome, nascita, ricovero) in enumerate(self.dati):
            for i, value in enumerate([nome, cognome, nascita, ricovero]):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.table.setItem(riga, i, item)

            # Il pulsante "Scheda" NON interferisce con la selezione della riga.
            btn = QPushButton("Scheda")
            btn.setFixedWidth(50)
            btn.setFixedHeight(22)
            btn.setStyleSheet("""
                font-size: 11px;
                background-color: #1976d2;
                color: white;
                border-radius: 4px;
                padding: 0px 0px;
                font-weight: normal;
            """)
            # Per evitare bug di selezione, non selezioniamo la riga dal pulsante!
            btn.clicked.connect(lambda checked, r=riga: self.apri_scheda(r))
            self.table.setCellWidget(riga, 4, btn)

    def nuovo_paziente(self):
        dlg = NuovoPazienteDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            dati = dlg.get_dati()
            if all(dati[:2]):
                self.dati.append(dati)
                self.aggiorna_tabella()
            else:
                QMessageBox.warning(self, "Errore", "Compila nome e cognome!")

    def elimina_paziente(self):
        r = self.table.currentRow()
        if r >= 0 and r < len(self.dati):
            reply = QMessageBox.question(self, "Conferma eliminazione",
                f"Eliminare definitivamente il paziente selezionato ({self.dati[r][0]} {self.dati[r][1]})?",
                QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                del self.dati[r]
                self.aggiorna_tabella()
        else:
            QMessageBox.information(self, "Seleziona paziente", "Seleziona un paziente dalla tabella.")

    def apri_scheda(self, riga):
        nome, cognome, nascita, ricovero = self.dati[riga]
        eta = self.calcola_eta(nascita)
        valutazioni_aperte = ["21/08/2025", "19/08/2025"]
        report_indici = ["20/08/2025", "18/08/2025"]
        report_completi = ["15/08/2025", "12/08/2025"]
        grafici = ["21/08/2025", "19/08/2025"]
        # self.scheda = SchedaPazienteWindow(nome, cognome, eta, valutazioni_aperte, report_indici, report_completi, grafici)
        # self.scheda.show()
        QMessageBox.information(self, "Scheda", f"Scheda di {nome} {cognome} (età: {eta})")

    def calcola_eta(self, data_nascita):
        nascita = datetime.strptime(data_nascita, "%d/%m/%Y")
        oggi = datetime.today()
        eta = oggi.year - nascita.year - ((oggi.month, oggi.day) < (nascita.month, nascita.day))
        return eta

# Per testare la finestra da sola
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    win = PazientiDimessiWindow()
    win.show()
    sys.exit(app.exec_())