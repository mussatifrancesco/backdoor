# 🛡️ Multi-Platform C2 & Reverse Shell Framework

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://microsoft.com/windows)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Un framework avanzato di **Command & Control (C2)** progettato per la gestione remota di sistemi Windows. Il progetto include un server multi-client, un client persistente con integrazione PowerShell e vettori di attacco fisici tramite **BadUSB**.

---

## 🚀 Caratteristiche Principali

* **Multi-Client Handling:** Gestione di più connessioni simultanee tramite threading e ID univoci.
* **PowerShell Deep Integration:** Mantiene la posizione della directory (`cd` persistente) tra i comandi.
* **Persistenza Automatica:** Script per l'auto-copia nella cartella `Startup` di Windows.
* **Evasione Defender:** Comandi inclusi per impostare esclusioni nel percorso di esecuzione (richiede privilegi admin).
* **Vettori BadUSB:** Script pronti per **Arduino (ATmega32U4)** e **RPi Pico** con layout tastiera IT.
* **Configurazione YAML:** Gestione centralizzata di host, porta e limiti di connessione.

---

## 📂 Struttura della Repository

| Cartella / File | Descrizione |
| :--- | :--- |
| `server.py` | Core del Server C2 con interfaccia a riga di comando. |
| `client.py` | Payload da eseguire sul target (Reverse Shell). |
| `requirements.txt`| Elenco delle dipendenze Python necessarie. |
| `badusb/` | Contiene gli sketch per Arduino e Duckyscript per Pico. |
| `conf/` | Contiene `configuration.yaml` per le impostazioni del server. |
| `log/` | Registro cronologico delle attività e delle connessioni. |

---

## 🛠️ Installazione e Requisiti

### 1. Installazione Dipendenze
Il framework richiede alcune librerie esterne. Installa tutto con il comando:
```bash
pip install -r requirements.txt