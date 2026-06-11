# Football Runner
Piłkarska gra zręcznościowa 3D, polegająca na biegu zawodnikiem po boisku, przy jednoczesnym unikaniu przeszkód. Głównym celem gry jest dotarcie do bramki i oddanie na nią celnego strzału. 

### Technologie:
- język: Python 3.14.0
- biblioteki: Ursina

### Instalacja:
1. Pobierz projekt na swój komputer 
2. Zainstaluj wymagane biblioteki:
```bash
  pip install -r requirements.txt
```
3. Uruchom grę:
```bash
  python main.py
```

### Sterowanie:
- **ruch:**
  - strzałka w lewo/prawo - ruch w lewo/prawo 
  - strzałka w dół - przewrót
  - strzałka w górę - skok
- **siła strzału:**
  - kolor szary - strzał za słaby 
  - kolor zielony - strzał po ziemi 
  - kolor pomarańczowy - strzał górą
  - kolor czerwony - strzał za mocny
- **kierunek strzału:**
  - strzałka lewo/prawo - strzał w lewo/prawo
  - strzałka w górę - strzał w środek