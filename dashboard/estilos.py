import pandas as pd

# (límite superior, color RGBA, etiqueta)
ESCALA_MAGNITUD = [
    (4.0, [253, 230, 138, 220], "Menor a 4"),
    (5.0, [251, 191, 36, 220], "4 a 5"),
    (6.0, [251, 146, 60, 230], "5 a 6"),
    (7.0, [244, 63, 94, 240], "6 a 7"),
    (float("inf"), [190, 18, 60, 255], "7 o más"),
]

COLOR_SIN_DATO = [150, 150, 150, 180]

COLOR_TIERRA = "#A78BFA"
COLOR_MAR = "#60A5FA"


def color_magnitud(magnitud):
    if pd.isna(magnitud):
        return COLOR_SIN_DATO
    for limite, color, _ in ESCALA_MAGNITUD:
        if magnitud < limite:
            return color
    return ESCALA_MAGNITUD[-1][1]


def leyenda_html():
    items = []
    for _, color, etiqueta in ESCALA_MAGNITUD:
        r, g, b, _ = color
        items.append(f'<span style="color: rgb({r},{g},{b}); font-size: 1.2em;">●</span> {etiqueta}')
    return "&nbsp;&nbsp;&nbsp;".join(items)

def estilo_magnitud(magnitud):
    r, g, b, _ = color_magnitud(magnitud)
    return f"background-color: rgba({r}, {g}, {b}, 0.35); font-weight: 600;"