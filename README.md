# Break Timer

Szünet-emlékeztető időzítő Windows-ra.

## Telepítés

```bash
pip install -r requirements.txt
```

## Indítás

```bash
python main.py
```

## Módok

- **Figyelmeztető**: Bezárható popup jelenik meg
- **Kényszerű szünet**: Fullscreen overlay, bevitel blokkolva, elhalasztható

## Beállítások

Tray ikon → Beállítások:
- Munkaidő, szünet hossza, elhalasztás ideje/darabszám, mód, hangjelzés

A beállítások `~/.break_timer.json`-ban tárolódnak.
