# G-code Generator för 3D-utskrift

Python-funktion för att generera komplett G-code för rektangulära kuber som kan visualiseras och användas i Cura slicer.

## Funktioner

- ✅ Genererar komplett G-code med alla lager
- ✅ Perimeter (väggar) med konfigurerbart antal lager
- ✅ Infill med konfigurerbar densitet
- ✅ Retraction för att undvika stringing
- ✅ Skirt för purge/prime
- ✅ Centrerad på sängen
- ✅ Första lagret med justerbar hastighet
- ✅ Kompatibel med Ultimaker 3D-skrivare

## Användning

### Grundläggande användning

```python
from generate_gcode import generate_gcode_box

# Generera en 50x50x50 mm kub
generate_gcode_box(
    length=50.0,
    width=50.0,
    height=50.0,
    output_file="kub_50mm.gcode"
)
```

### Avancerad användning med alla parametrar

```python
generate_gcode_box(
    # Dimensioner
    length=60.0,        # Längd i mm (X-riktning)
    width=40.0,         # Bredd i mm (Y-riktning)
    height=30.0,        # Höjd i mm (Z-riktning)
    
    # Utskriftsinställningar
    layer_height=0.2,           # Höjd per lager i mm
    nozzle_diameter=0.4,         # Nozzle diameter i mm
    line_width=0.4,             # Linjebredd i mm
    filament_diameter=2.85,      # Filament diameter (2.85 för Ultimaker, 1.75 för många andra)
    
    # Sänginställningar
    bed_size_x=215.0,           # Sängens storlek i X-riktning
    bed_size_y=215.0,           # Sängens storlek i Y-riktning
    
    # Temperatur
    extruder_temp=210,          # Extruder temperatur i °C
    bed_temp=60,                # Sängtemperatur i °C
    
    # Hastighet
    print_speed=1500,           # Utskriftshastighet i mm/min (25 mm/s)
    travel_speed=3000,          # Resehastighet i mm/min (50 mm/s)
    first_layer_speed=1000,     # Hastighet för första lagret (None = samma som print_speed)
    
    # Infill och perimeter
    infill_percentage=20,       # Infill procent (0-100)
    perimeter_count=2,          # Antal perimeter/väggar (rekommenderas 2-3)
    
    # Retraction (viktigt för att undvika stringing)
    retract_length=4.5,         # Retraction längd i mm
    retract_speed=25,           # Retraction hastighet i mm/s
    
    # Skirt
    skirt_lines=3,              # Antal skirt-linjer (0 = ingen skirt)
    skirt_distance=5.0,         # Avstånd från objekt till skirt i mm
    
    # Output
    output_file="min_kub.gcode"
)
```

## Parametrar

### Obligatoriska parametrar
Inga - alla har standardvärden.

### Viktiga parametrar att justera

1. **Dimensioner**: `length`, `width`, `height` - kubens storlek
2. **Retraction**: `retract_length`, `retract_speed` - viktigt för att undvika stringing
3. **Infill**: `infill_percentage` - 0-100%, högre = tätare infill
4. **Perimeter**: `perimeter_count` - antal väggar (2-3 är vanligt)
5. **Filament**: `filament_diameter` - 2.85mm för Ultimaker, 1.75mm för många andra

### Ytterligare parametrar

- `layer_height`: Höjd per lager (0.1-0.3mm är vanligt)
- `nozzle_diameter`: Nozzle storlek (0.4mm är vanligast)
- `line_width`: Ofta samma som nozzle diameter
- `bed_size_x/y`: Sängens storlek för centrering
- `extruder_temp/bed_temp`: Temperaturinställningar (beroende på material)
- `print_speed/travel_speed`: Hastighetsinställningar
- `first_layer_speed`: Långsammare första lager för bättre adhesion
- `skirt_lines/skirt_distance`: Skirt för purge/prime

## Exempel

### Exempel 1: Enkel kub
```python
generate_gcode_box(
    length=50.0,
    width=50.0,
    height=50.0
)
```

### Exempel 2: Rektangulär låda
```python
generate_gcode_box(
    length=80.0,
    width=60.0,
    height=40.0,
    infill_percentage=15,
    perimeter_count=3,
    output_file="lada_80x60x40.gcode"
)
```

### Exempel 3: Tunn platta
```python
generate_gcode_box(
    length=100.0,
    width=100.0,
    height=2.0,
    layer_height=0.1,
    infill_percentage=50,
    output_file="platta_100x100x2.gcode"
)
```

## Visualisering i Cura

1. Öppna Cura slicer
2. File → Open File(s)
3. Välj den genererade `.gcode` filen
4. Cura kommer att visualisera G-coden och visa alla lager

## Viktiga noteringar

- **Retraction** är viktigt för att undvika stringing mellan delar
- **Första lagret** bör ofta printas långsammare för bättre adhesion
- **Infill procent** påverkar styrka och materialanvändning
- **Perimeter count** påverkar väggtjocklek och styrka
- Justera temperaturer efter material (PLA, ABS, PETG, etc.)

## Tekniska detaljer

- G-code genereras enligt Marlin/RepRap standard
- Extrusion beräknas baserat på volym: `E = (distance × layer_height × line_width) / (π × (filament_diameter/2)²)`
- Alla lager genereras komplett (inte bara exempel)
- Retraction används vid alla travel moves
- Infill alternerar riktning per lager för bättre styrka

## Felsökning

**Problem: Stringing**
- Öka `retract_length` (t.ex. 5-6mm)
- Öka `retract_speed` (t.ex. 30-40 mm/s)

**Problem: Dålig adhesion första lagret**
- Minska `first_layer_speed` (t.ex. 800-1000 mm/min)
- Öka `bed_temp` (t.ex. 65-70°C för PLA)

**Problem: Kub passar inte på sängen**
- Kontrollera `bed_size_x` och `bed_size_y`
- Minska kubens dimensioner

## Licens

Fritt att använda och modifiera.
