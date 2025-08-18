# Proyecto NFL - Python & Prolog

Este proyecto procesa datos de jugadas de la NFL (2009–2018) y genera hechos en **Prolog** para luego realizar consultas específicas sobre partidos, anotaciones y equipos ganadores.

## Archivos principales

- **temporada.py**  
  Script en Python que lee el dataset original (`NFL Play by Play 2009-2018 (v5).csv`) y genera un archivo de hechos en Prolog (`temporada_<año>.pl`).

- **consultas.pl**  
  Archivo que define las consultas en Prolog para responder preguntas sobre partidos, equipos y jugadas.

- **NFL Play by Play 2009-2018 (v5).csv**  
  Dataset con jugadas históricas de la NFL (descargado previamente, no incluido).
  Se puede descargar en https://www.kaggle.com/datasets/maxhorowitz/nflplaybyplay2009to2016?select=NFL+Play+by+Play+2009-2018+%28v5%29.csv

---


## Uso del proyecto
1. Generar hechos en Prolog

   - **Ejecutar en consola:**
       - python temporada.py

   - **El programa pedirá el año de la temporada (ejemplo 2013), y generará un archivo:**
       - temporada_2013.pl

   - **Este contendrá hechos como:**
       - partido('2013-09-05', 'BAL', 'DEN', 27, 49).
       - anotacion(1, 'DEN', 'pase', '2013-09-05', 'BAL', 'DEN').

2. Consultas en Prolog

   - **Cargar los hechos y consultas en SWI-Prolog:**
       - ?- [temporada_2013].
       - ?- [consultas].

## Consultas disponibles
1. **Todos los equipos (local o visitante) que ganaron**

  ?- setof(Eq, ganador(Eq), Equipos).

2. **Todos los equipos que ganaron por más de X puntos**

  ?- setof(Eq, ganador_margen(Eq, 10), Equipos).

3. **Partidos donde hubo una anotación de cierto tipo**

  *Ejemplo: todos los partidos con field goal.*

  ?- setof((Fecha,V,L), partido_anotacion_tipo(Fecha,V,L,'gol_de_campo'), Partidos).

  Para cualquier touchdown (pase o corrida):

  ?- setof((Fecha,V,L), partido_con_touchdown(Fecha,V,L), Partidos).

4. **Partidos donde hubo más de 1 field goal por cada equipo**

  ?- setof((Fecha,V,L), partido_mas_de_un_field_goal(Fecha,V,L), Partidos).

5. **Partidos en que hubo safety**

  ?- setof((Fecha,V,L), partido_con_safety(Fecha,V,L), Partidos).

6. **Ganador (local o visitante) de un partido en una fecha específica**

  *Ejemplo:*

  ?- ganador_por_fecha('2013-09-05', Eq).

## Notas
El archivo CSV original es muy grande (GBs), por lo que el script procesa la información en chunks.

Los hechos generados incluyen tanto partidos como anotaciones (tipo, cuarto, equipo, etc.).

Se pueden generar múltiples temporadas repitiendo la ejecución de temporada.py.

## Autores

Mariana Lara Vargas






