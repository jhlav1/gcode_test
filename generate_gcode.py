"""
G-code Generator för 3D-utskrift
Genererar komplett G-code för en rektangulär kub som kan visualiseras i Cura slicer
"""

import math


def calculate_extrusion_amount(distance, layer_height, line_width, filament_diameter):
    """
    Beräknar extrusion amount (E-värde) baserat på avstånd och extruder-inställningar.
    
    Formel: E = (distance * layer_height * line_width) / (π * (filament_diameter/2)²)
    """
    filament_area = math.pi * (filament_diameter / 2) ** 2
    volume_extruded = distance * layer_height * line_width
    e_value = volume_extruded / filament_area
    return e_value


def generate_gcode_box(
    length=50.0,
    width=50.0,
    height=50.0,
    layer_height=0.2,
    nozzle_diameter=0.4,
    line_width=0.4,
    filament_diameter=2.85,  # Ultimaker använder 2.85mm filament
    bed_size_x=215.0,
    bed_size_y=215.0,
    extruder_temp=210,
    bed_temp=60,
    print_speed=1500,  # mm/min (25 mm/s)
    travel_speed=3000,  # mm/min (50 mm/s)
    infill_percentage=20,  # Infill procent (0-100)
    perimeter_count=2,  # Antal perimeter/väggar
    retract_length=4.5,  # Retraction längd i mm (viktigt för att undvika stringing)
    retract_speed=25,  # Retraction hastighet i mm/s
    first_layer_speed=None,  # Hastighet för första lagret (None = samma som print_speed)
    skirt_lines=3,  # Antal skirt-linjer (0 = ingen skirt)
    skirt_distance=5.0,  # Avstånd från objekt till skirt i mm
    output_file="generated_box.gcode"
):
    """
    Genererar komplett G-code för en rektangulär kub.
    
    Parametrar:
    -----------
    length : float
        Kubens längd i mm (X-riktning)
    width : float
        Kubens bredd i mm (Y-riktning)
    height : float
        Kubens höjd i mm (Z-riktning)
    layer_height : float
        Höjd per lager i mm (standard: 0.2)
    nozzle_diameter : float
        Nozzle diameter i mm (standard: 0.4)
    line_width : float
        Linjebredd i mm (ofta samma som nozzle)
    filament_diameter : float
        Filament diameter i mm (2.85 för Ultimaker, 1.75 för många andra)
    bed_size_x : float
        Sängens storlek i X-riktning
    bed_size_y : float
        Sängens storlek i Y-riktning
    extruder_temp : int
        Extruder temperatur i °C
    bed_temp : int
        Sängtemperatur i °C
    print_speed : int
        Utskriftshastighet i mm/min
    travel_speed : int
        Resehastighet (utan extrusion) i mm/min
    infill_percentage : int
        Infill procent (0-100)
    perimeter_count : int
        Antal perimeter/väggar (rekommenderas 2-3)
    retract_length : float
        Retraction längd i mm (viktigt för att undvika stringing)
    retract_speed : float
        Retraction hastighet i mm/s
    first_layer_speed : int or None
        Hastighet för första lagret (None = samma som print_speed)
    skirt_lines : int
        Antal skirt-linjer runt objektet (0 = ingen skirt)
    skirt_distance : float
        Avstånd från objekt till skirt i mm
    output_file : str
        Filnamn för output G-code fil
    """
    
    # Beräkna antal lager
    num_layers = int(height / layer_height)
    
    # Beräkna centrering
    center_x = bed_size_x / 2
    center_y = bed_size_y / 2
    
    # Startposition (vänster nedre hörn)
    start_x = center_x - length / 2
    start_y = center_y - width / 2
    end_x = center_x + length / 2
    end_y = center_y + width / 2
    
    # Kontrollera att kub passar på sängen
    if start_x < 0 or start_y < 0 or end_x > bed_size_x or end_y > bed_size_y:
        raise ValueError(f"Kuben passar inte på sängen! Kuben: {length}x{width}mm, Säng: {bed_size_x}x{bed_size_y}mm")
    
    # Initiera G-code
    gcode_lines = []
    
    # Header kommentarer
    gcode_lines.append(f"; G-code genererad för rektangulär kub")
    gcode_lines.append(f"; Dimensioner: {length}x{width}x{height} mm")
    gcode_lines.append(f"; Centrerad på säng: ({bed_size_x}x{bed_size_y} mm)")
    gcode_lines.append(f"; Layer height: {layer_height} mm")
    gcode_lines.append(f"; Nozzle: {nozzle_diameter} mm")
    gcode_lines.append(f"; Antal lager: {num_layers}")
    gcode_lines.append("")
    
    # Initialisering
    gcode_lines.append("; Initialisering")
    gcode_lines.append("G21 ; Sätt enheter till millimeter")
    gcode_lines.append("G90 ; Absolut positionering")
    gcode_lines.append("M82 ; Extruder i absolut läge")
    gcode_lines.append("")
    
    # Home alla axlar
    gcode_lines.append("; Home alla axlar")
    gcode_lines.append("G28 ; Home X, Y, Z")
    gcode_lines.append("")
    
    # Förbered skrivare
    gcode_lines.append("; Förbered skrivare")
    gcode_lines.append(f"M104 S{extruder_temp} ; Sätt extruder temperatur")
    gcode_lines.append(f"M140 S{bed_temp} ; Sätt sängtemperatur")
    gcode_lines.append(f"M109 S{extruder_temp} ; Vänta på extruder temperatur")
    gcode_lines.append(f"M190 S{bed_temp} ; Vänta på sängtemperatur")
    gcode_lines.append("")
    
    # Förbered extruder
    gcode_lines.append("; Förbered extruder")
    gcode_lines.append("G92 E0 ; Nollställ extruder")
    gcode_lines.append(f"G1 F{print_speed} ; Sätt feedrate")
    gcode_lines.append("")
    
    # Sätt första lagrets hastighet
    if first_layer_speed is None:
        first_layer_speed = print_speed
    
    # Retraction inställningar
    retract_speed_mm_min = retract_speed * 60  # Konvertera till mm/min
    
    # Variabel för att hålla koll på E-värde
    current_e = 0.0
    
    # Gå till startposition
    first_layer_z = layer_height
    gcode_lines.append(f"; Gå till startposition")
    gcode_lines.append(f"G1 X{start_x:.3f} Y{start_y:.3f} Z{first_layer_z:.3f} F{travel_speed}")
    gcode_lines.append("")
    
    # Aktivera fläkt
    gcode_lines.append("; Aktivera fläkt")
    gcode_lines.append("M106 S255 ; Sätt fläkt på max")
    gcode_lines.append("")
    
    # SKIRT (om önskat)
    if skirt_lines > 0:
        gcode_lines.append("; Skirt (purge/prime)")
        skirt_start_x = start_x - skirt_distance - (skirt_lines * line_width)
        skirt_start_y = start_y - skirt_distance - (skirt_lines * line_width)
        skirt_end_x = end_x + skirt_distance + (skirt_lines * line_width)
        skirt_end_y = end_y + skirt_distance + (skirt_lines * line_width)
        
        for skirt_num in range(skirt_lines):
            offset = skirt_num * line_width
            sk_x1 = skirt_start_x + offset
            sk_y1 = skirt_start_y + offset
            sk_x2 = skirt_end_x - offset
            sk_y2 = skirt_end_y - offset
            
            gcode_lines.append(f"; Skirt linje {skirt_num + 1}")
            gcode_lines.append(f"G1 X{sk_x1:.3f} Y{sk_y1:.3f} Z{first_layer_z:.3f} F{travel_speed}")
            # Rita skirt perimeter
            perimeter_length = (sk_x2 - sk_x1) * 2 + (sk_y2 - sk_y1) * 2
            e_increment = calculate_extrusion_amount(
                perimeter_length,
                layer_height,
                line_width,
                filament_diameter
            )
            current_e += e_increment
            gcode_lines.append(f"G1 X{sk_x2:.3f} Y{sk_y1:.3f} E{current_e:.4f} F{first_layer_speed}")
            current_e += e_increment
            gcode_lines.append(f"G1 X{sk_x2:.3f} Y{sk_y2:.3f} E{current_e:.4f} F{first_layer_speed}")
            current_e += e_increment
            gcode_lines.append(f"G1 X{sk_x1:.3f} Y{sk_y2:.3f} E{current_e:.4f} F{first_layer_speed}")
            current_e += e_increment
            gcode_lines.append(f"G1 X{sk_x1:.3f} Y{sk_y1:.3f} E{current_e:.4f} F{first_layer_speed}")
        
        # Retract efter skirt
        gcode_lines.append(f"G1 E{current_e - retract_length:.4f} F{retract_speed_mm_min:.0f} ; Retract")
        gcode_lines.append("")
    
    # ============================================
    # GENERERA ALLA LAGER
    # ============================================
    gcode_lines.append("; ============================================")
    gcode_lines.append("; SKRIV UT KUBEN")
    gcode_lines.append("; ============================================")
    gcode_lines.append("")
    
    for layer_num in range(num_layers):
        current_z = (layer_num + 1) * layer_height
        
        gcode_lines.append(f"; Lager {layer_num + 1} / {num_layers} (Z = {current_z:.3f} mm)")
        
        # Gå till lagerhöjd (första gången är vi redan där)
        if layer_num > 0:
            # Retract innan Z-förflyttning
            gcode_lines.append(f"G1 E{current_e - retract_length:.4f} F{retract_speed_mm_min:.0f} ; Retract")
            gcode_lines.append(f"G1 Z{current_z:.3f} F{travel_speed} ; Gå till lagerhöjd")
            # Prime efter Z-förflyttning
            current_e += retract_length
            gcode_lines.append(f"G1 E{current_e:.4f} F{retract_speed_mm_min:.0f} ; Prime")
        
        # PERIMETER (väggar)
        # Rita perimeter_count antal väggar, varje vägg är lite mindre än den föregående
        for perimeter in range(perimeter_count):
            offset = perimeter * line_width
            
            # Beräkna koordinater för denna perimeter
            perim_start_x = start_x + offset
            perim_start_y = start_y + offset
            perim_end_x = end_x - offset
            perim_end_y = end_y - offset
            
            perim_length = (perim_end_x - perim_start_x) * 2 + (perim_end_y - perim_start_y) * 2
            
            # Gå till startposition (travel move med retraction om nödvändigt)
            if perimeter == 0 and layer_num == 0:
                # Första lagret, första perimeter - vi är redan på rätt plats
                gcode_lines.append(f"G1 X{perim_start_x:.3f} Y{perim_start_y:.3f} F{travel_speed}")
            else:
                # Retract innan travel move
                gcode_lines.append(f"G1 E{current_e - retract_length:.4f} F{retract_speed_mm_min:.0f} ; Retract")
                gcode_lines.append(f"G1 X{perim_start_x:.3f} Y{perim_start_y:.3f} F{travel_speed}")
                # Prime efter travel move
                current_e += retract_length
                gcode_lines.append(f"G1 E{current_e:.4f} F{retract_speed_mm_min:.0f} ; Prime")
            
            # Använd första lagrets hastighet för första lagret
            current_print_speed = first_layer_speed if layer_num == 0 else print_speed
            
            # Rita perimeter (rektangel)
            # Linje 1: X+ (höger)
            e_increment = calculate_extrusion_amount(
                perim_end_x - perim_start_x,
                layer_height,
                line_width,
                filament_diameter
            )
            current_e += e_increment
            gcode_lines.append(f"G1 X{perim_end_x:.3f} Y{perim_start_y:.3f} E{current_e:.4f} F{current_print_speed}")
            
            # Linje 2: Y+ (framåt)
            e_increment = calculate_extrusion_amount(
                perim_end_y - perim_start_y,
                layer_height,
                line_width,
                filament_diameter
            )
            current_e += e_increment
            gcode_lines.append(f"G1 X{perim_end_x:.3f} Y{perim_end_y:.3f} E{current_e:.4f} F{current_print_speed}")
            
            # Linje 3: X- (vänster)
            e_increment = calculate_extrusion_amount(
                perim_end_x - perim_start_x,
                layer_height,
                line_width,
                filament_diameter
            )
            current_e += e_increment
            gcode_lines.append(f"G1 X{perim_start_x:.3f} Y{perim_end_y:.3f} E{current_e:.4f} F{current_print_speed}")
            
            # Linje 4: Y- (tillbaka)
            e_increment = calculate_extrusion_amount(
                perim_end_y - perim_start_y,
                layer_height,
                line_width,
                filament_diameter
            )
            current_e += e_increment
            gcode_lines.append(f"G1 X{perim_start_x:.3f} Y{perim_start_y:.3f} E{current_e:.4f} F{current_print_speed}")
        
        # INFILL (endast för lager som inte är sista lagret, och om infill > 0)
        if layer_num < num_layers - 1 and infill_percentage > 0:
            # Beräkna infill-område (innanför perimeter)
            infill_start_x = start_x + (perimeter_count * line_width)
            infill_start_y = start_y + (perimeter_count * line_width)
            infill_end_x = end_x - (perimeter_count * line_width)
            infill_end_y = end_y - (perimeter_count * line_width)
            
            # Kontrollera att infill-området är stort nog
            if infill_end_x > infill_start_x and infill_end_y > infill_start_y:
                infill_width = infill_end_x - infill_start_x
                infill_depth = infill_end_y - infill_start_y
                
                # Beräkna infill linjeavstånd baserat på infill_percentage
                # För grid infill: större procent = tätare linjer
                # Solid infill (100%) = linjeavstånd = line_width
                # 20% infill = linjeavstånd = line_width * 5
                if infill_percentage >= 100:
                    infill_spacing = line_width  # Solid infill
                else:
                    infill_spacing = line_width * (100.0 / infill_percentage)
                
                # Generera infill linjer i X-riktning (alternerar riktning per lager)
                num_infill_lines = max(1, int(infill_depth / infill_spacing))
                
                for i in range(num_infill_lines):
                    y_pos = infill_start_y + i * infill_spacing
                    
                    # Begränsa till infill-området
                    if y_pos > infill_end_y:
                        break
                    
                    # Alternera riktning för varje linje (för bättre adhesion)
                    if (layer_num + i) % 2 == 0:
                        # Gå till start (vänster) - travel move med retraction
                        gcode_lines.append(f"G1 E{current_e - retract_length:.4f} F{retract_speed_mm_min:.0f} ; Retract")
                        gcode_lines.append(f"G1 X{infill_start_x:.3f} Y{y_pos:.3f} F{travel_speed}")
                        # Prime och rita linje höger - med extrusion
                        current_e += retract_length
                        gcode_lines.append(f"G1 E{current_e:.4f} F{retract_speed_mm_min:.0f} ; Prime")
                        e_increment = calculate_extrusion_amount(
                            infill_width,
                            layer_height,
                            line_width,
                            filament_diameter
                        )
                        current_e += e_increment
                        gcode_lines.append(f"G1 X{infill_end_x:.3f} Y{y_pos:.3f} E{current_e:.4f} F{print_speed}")
                    else:
                        # Gå till start (höger) - travel move med retraction
                        gcode_lines.append(f"G1 E{current_e - retract_length:.4f} F{retract_speed_mm_min:.0f} ; Retract")
                        gcode_lines.append(f"G1 X{infill_end_x:.3f} Y{y_pos:.3f} F{travel_speed}")
                        # Prime och rita linje vänster - med extrusion
                        current_e += retract_length
                        gcode_lines.append(f"G1 E{current_e:.4f} F{retract_speed_mm_min:.0f} ; Prime")
                        e_increment = calculate_extrusion_amount(
                            infill_width,
                            layer_height,
                            line_width,
                            filament_diameter
                        )
                        current_e += e_increment
                        gcode_lines.append(f"G1 X{infill_start_x:.3f} Y{y_pos:.3f} E{current_e:.4f} F{print_speed}")
        
        gcode_lines.append("")  # Tom rad mellan lager
    
    # ============================================
    # SLUT
    # ============================================
    gcode_lines.append("; Slutposition")
    gcode_lines.append(f"G1 Z{height + 5:.3f} F{travel_speed} ; Lyft nozzle")
    gcode_lines.append(f"G1 X{center_x:.3f} Y{center_y:.3f} F{travel_speed} ; Gå till centrum")
    gcode_lines.append("")
    
    # Stäng av
    gcode_lines.append("; Stäng av")
    gcode_lines.append("M104 S0 ; Stäng av extruder värme")
    gcode_lines.append("M140 S0 ; Stäng av säng värme")
    gcode_lines.append("M106 S0 ; Stäng av fläkt")
    gcode_lines.append("")
    
    # Slut
    gcode_lines.append("; Slut")
    gcode_lines.append("M30 ; Program slut")
    
    # Skriv till fil
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(gcode_lines))
    
    print(f"G-code genererad: {output_file}")
    print(f"Dimensioner: {length}x{width}x{height} mm")
    print(f"Antal lager: {num_layers}")
    print(f"Total E-värde: {current_e:.2f} mm")
    
    return output_file


# Exempel på användning
if __name__ == "__main__":
    # Exempel 1: 50x50x50 mm kub
    generate_gcode_box(
        length=50.0,
        width=50.0,
        height=50.0,
        output_file="kub_50mm_auto.gcode"
    )
    
    # Exempel 2: Rektangulär kub
    # generate_gcode_box(
    #     length=60.0,
    #     width=40.0,
    #     height=30.0,
    #     output_file="rektangel_60x40x30.gcode"
    # )
