from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton,
    QHBoxLayout, QDialog, QFormLayout, QLineEdit, QDateEdit, QMessageBox, QApplication
)
from PyQt5.QtCore import Qt, QDate
from datetime import datetime
import os
import json
from scheda_paziente import SchedaPazienteWindow
from functools import partial
import shutil

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
        self.dati = self.carica_pazienti_dimessi()
        self.setWindowTitle("Pazienti Dimessi")
        self.setMinimumWidth(750)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(24)

        label = QLabel("Elenco Pazienti Dimessi")
        label.setStyleSheet("font-size: 19px; font-weight: bold; color: #023047; padding-bottom: 12px;")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        # Bottoni
        btn_layout = QHBoxLayout()
    
        self.elimina_btn = QPushButton("Elimina selezionato")
        self.elimina_btn.setStyleSheet("font-size:14px; background:#e53935; color:white; padding:3px 12px; border-radius:6px;")
        self.elimina_btn.clicked.connect(self.elimina_paziente)
        btn_layout.addWidget(self.elimina_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Nome", "Cognome", "Data di nascita", "Data di ricovero", ""
        ])
        self.table.setMinimumWidth(700)
        self.table.setStyleSheet("""
            QTableWidget {font-size: 13px; border: none;}
            QTableWidget::item {padding: 2px; border: none;}
            QTableWidget::item:selected {background: #B3E5FC; color: #212121;}
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

    
    def carica_pazienti_dimessi(self):
        file_dimessi = "pazienti_dimessi.json"
        if os.path.exists(file_dimessi):
            with open(file_dimessi, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except Exception:
                    return []
        return []

    def aggiorna_tabella(self):
        self.table.setRowCount(len(self.dati))
        for riga, paziente in enumerate(self.dati):
            nome = paziente.get("nome", "")
            cognome = paziente.get("cognome", "")
            nascita = paziente.get("data_nascita", "")
            ricovero = paziente.get("data_ricovero", "")

            for i, value in enumerate([nome, cognome, nascita, ricovero]):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.table.setItem(riga, i, item)

            btn = QPushButton("Scheda")
            btn.setFixedWidth(70)
            btn.setFixedHeight(24)
            btn.setStyleSheet("""
                font-size: 11px;
                background-color: #1976d2;
                color: white;
                border-radius: 4px;
                padding: 0px 0px;
                font-weight: normal;
            """)
            btn.setFocusPolicy(Qt.NoFocus)
            btn.clicked.connect(partial(self.apri_scheda, riga))
            cell_widget = QWidget()
            cell_layout = QHBoxLayout(cell_widget)
            cell_layout.setContentsMargins(0, 0, 8, 0)
            cell_layout.addWidget(btn)
            cell_layout.setAlignment(Qt.AlignRight)
            self.table.setCellWidget(riga, 4, cell_widget)

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
        import os, shutil, json, unicodedata, traceback
        from PyQt5.QtWidgets import QMessageBox

        def norm(s):
            """Normalizza stringhe per confronto: rimuove accenti, mette lower, underscore, rimuove caratteri strani."""
            if not s:
                return ""
            s = str(s)
            s = unicodedata.normalize("NFKD", s)
            s = s.encode("ascii", "ignore").decode("ascii")  # tolgo accenti
            s = s.lower().strip()
            s = s.replace(" ", "_")
            s = "".join(ch for ch in s if ch.isalnum() or ch == "_")
            return s

        r = self.table.currentRow()
        if r < 0 or r >= len(self.dati):
            QMessageBox.information(self, "Seleziona paziente", "Seleziona un paziente dalla tabella.")
            return

        paziente = self.dati[r]
        nome = paziente.get("nome", "").strip()
        cognome = paziente.get("cognome", "").strip()

        reply = QMessageBox.question(
            self,
            "Conferma eliminazione",
            f"Eliminare definitivamente il paziente selezionato ({nome} {cognome})?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        # 1. Elimina dal JSON in memoria
        del self.dati[r]

        # 2. Riscrivi il file pazienti_dimessi.json
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            json_path = os.path.join(base_dir, "pazienti_dimessi.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(self.dati, f, ensure_ascii=False, indent=2)
        except Exception as e:
            QMessageBox.warning(self, "Errore", f"Impossibile aggiornare pazienti_dimessi.json:\n{e}")
            return

        # 3. Aggiorna la tabella GUI
        self.aggiorna_tabella()

        # 4. Cerca ed elimina cartella fisica del paziente
        project_dir = os.path.dirname(os.path.abspath(__file__))
        base = os.path.join(project_dir, "pazienti")

        print("=== DEBUG elimina_paziente ===")
        print("Project dir:", project_dir)
        print("Cartella pazienti:", base)
        print("Contenuto:", os.listdir(base) if os.path.exists(base) else [])

        target = norm(f"{nome}_{cognome}")
        print("Target:", target)

        candidates = []
        if os.path.exists(base):
            for d in os.listdir(base):
                folder_norm = norm(d)
                print("Confronto:", target, "IN", folder_norm, "->", (target in folder_norm))
                if target in folder_norm:
                    p = os.path.join(base, d)
                    if os.path.isdir(p):
                        candidates.append(p)

        if not candidates:
            print("Nessuna cartella trovata per:", target)
            return

        trash_dir = os.path.join(project_dir, "pazienti_eliminati")
        os.makedirs(trash_dir, exist_ok=True)

        for p in candidates:
            try:
                shutil.rmtree(p)
                print("Eliminata cartella:", p)
            except Exception as e_del:
                print("Errore eliminando:", p, "->", e_del)
                try:
                    base_name = os.path.basename(p)
                    dest = os.path.join(trash_dir, base_name)
                    suffix = 1
                    dest_try = dest
                    while os.path.exists(dest_try):
                        dest_try = f"{dest}_{suffix}"
                        suffix += 1
                    shutil.move(p, dest_try)
                    print("Spostata in cestino:", dest_try)
                except Exception as e_move:
                    QMessageBox.warning(
                        self, "Errore eliminazione",
                        f"Impossibile eliminare o spostare {p}:\n{e_del}\n{e_move}"
                    )






    def apri_scheda(self, riga):
        paziente = self.dati[riga]
        nome = paziente.get("nome", "")
        cognome = paziente.get("cognome", "")
        nascita = paziente.get("data_nascita", "")
        eta = self.calcola_eta(nascita)
        cartella = os.path.join("dimessi", f"{nome}_{cognome}_{eta}a")
        dati_file = os.path.join(cartella, "dati.json")

        # default vuoti
        valutazioni_aperte = []
        valutazioni_completate = []
        report_indici = []
        report_completi = []
        grafici = []

        # carica dati se esiste il file
        if os.path.exists(dati_file):
            try:
                with open(dati_file, "r", encoding="utf-8") as f:
                    dati = json.load(f)
                    valutazioni_aperte = dati.get("valutazioni_aperte", [])
                    valutazioni_completate = dati.get("valutazioni_completate", [])
                    report_indici = dati.get("report_indici", [])
                    report_completi = dati.get("report_completi", [])
                    grafici = dati.get("grafici", [])
            except Exception:
                pass

        # crea la finestra con i dati veri!
        self.scheda = SchedaPazienteWindow(
            nome, cognome, eta,
            valutazioni_aperte=valutazioni_aperte,
            valutazioni_completate=valutazioni_completate,
            report_indici=report_indici,
            report_completi=report_completi,
            grafici=grafici,
            sola_lettura=True,
            percorso_base="dimessi"
        )
        self.scheda.show()

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