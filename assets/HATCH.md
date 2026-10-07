# HATCH / 07

Banner de Antonio Navarro. Un cierre mecánico de dos hojas, con volante de cinco
brazos y dos cerrojos deslizantes, revela una composición tipográfica y un
monograma AN. Grafito, metal frío, blanco roto y amarillo ácido.

## Verlo

Abre `../preview.html` en Chrome, Edge o Firefox. No hace falta instalar paquetes
ni arrancar un servidor. La vista previa es autónoma y permite pausar, reiniciar,
arrastrar el tiempo, saltar entre fases y revisar anchos de 1200, 850 y 375 px.

Si Windows tiene activado movimiento reducido, la imagen permanece abierta.
En la vista previa, «Ver animación de todos modos» permite reproducirla por
elección expresa sin modificar Windows. El SVG del README respeta esa preferencia.

## Archivos

- `hatch-banner.svg`: fuente animada usada por el README.
- `hatch-banner-static.svg`: composición abierta sin animaciones activas.
- `../preview.html`: vista previa generada, con SVG incrustado.
- `../tools/preview.template.html`: plantilla de los controles.
- `../tools/build_preview.py`: regenera la vista previa y la versión estática.
- `../tools/render_checks.py`: comprobaciones XML y capturas locales con Chrome.

## Movimiento

Todas las pistas comparten un periodo de **20 segundos**:

| Tiempo | Acción |
| --- | --- |
| 0–1,2 s | Compuerta cerrada. La identidad abreviada ya se puede leer. |
| 1,2–3,2 s | Volante gira 144° sobre su eje, con aceleración y frenado. |
| 3,2–4 s | Dos cerrojos se retraen 44 px. |
| 4–6 s | Hoja izquierda viaja −730 px; derecha +650 px. |
| 6–16,6 s | Perfil abierto durante 10,6 s; órbita y señal ambiental suaves. |
| 16,6–18,8 s | Las puertas regresan a su asiento. |
| 18,8–19,2 s | Cerrojos vuelven a entrar en los alojamientos. |
| 19,2–20 s | El volante vuelve a su ángulo de reposo. |

El volante pertenece a la hoja izquierda. Nunca se divide ni queda suspendido en
el centro al abrir. La hoja derecha lleva los alojamientos de recepción. El marco
estacionario recorta ambas hojas. Las transformaciones base dejan las puertas
abiertas cuando se desactivan las animaciones, para conservar la información.

## Edición

El SVG contiene comentarios de cada grupo. `identity` y `identity-mark` son el
contenido interior; `left-leaf`, `right-leaf` y `handwheel`, el mecanismo. Los
keyframes están en el bloque `style`, con puntos expresados en porcentajes de 20 s.

Después de editar el SVG, desde la raíz del repositorio **Lunkynono**:

```powershell
python tools/build_preview.py
```

Para repetir las capturas (requiere Chrome ya instalado):

```powershell
python tools/render_checks.py
```

Los archivos de comprobación y el perfil de navegador aislado se guardan en
`.preview-qa/`, excluida de Git. El renderizador no usa el perfil personal de Chrome.

## Integración

1200 × 480, escala proporcional, SVG y CSS autocontenidos. El banner no contiene
JavaScript, fuentes remotas, imágenes externas ni `foreignObject`. El JavaScript
existe únicamente en la página local de revisión, para controlar el tiempo.

El README lo incluye con una etiqueta `img`. Se han renderizado las fases en ese
modo de imagen local, además de la previsualización; el resultado servido por
GitHub debe comprobarse tras publicar. No se ha hecho commit ni push.

Los pequeños rótulos forman parte del detalle visual y se vuelven ornamentales
en móvil; el nombre sigue siendo el elemento principal legible.

Referencia técnica: [SVG como imagen, MDN](https://developer.mozilla.org/en-US/docs/Web/SVG/Guides/SVG_as_an_image).
