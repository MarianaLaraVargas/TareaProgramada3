% ================================
% Consultas Prolog - Tarea
% ================================

% Hechos esperados:
% partido(Fecha, Visitante, Local, PtsV, PtsL).
% anotacion(Cuarto, Equipo, Tipo, Fecha, Visitante, Local).

% 1) Todos los equipos (visitante o local) que ganaron
ganador(Eq) :-
    partido(_, V, L, PV, PL),
    ( PV > PL -> Eq = V
    ; PL > PV -> Eq = L
    ).

% 2) Equipos que ganaron por más de X puntos
ganador_margen(Eq, X) :-
    partido(_, V, L, PV, PL),
    ( PV > PL -> Eq = V, Dif is PV-PL
    ; PL > PV -> Eq = L, Dif is PL-PV
    ),
    Dif > X.

% 3) Partidos con anotaciones de un Tipo dado
partido_anotacion_tipo(Fecha, V, L, Tipo) :-
    anotacion(_, _, Tipo, Fecha, V, L).

% "Cualquier touchdown" (pase, corrida o touchdown_otro)
es_td(T) :- member(T, ['pase','corrida','touchdown_otro']).
partido_con_touchdown(Fecha, V, L) :-
    anotacion(_, _, T, Fecha, V, L),
    es_td(T).

% 4) Partidos donde hubo >1 field goal para cada equipo
partido_mas_de_un_field_goal(Fecha, V, L) :-
    findall(E, anotacion(_, E, 'gol_de_campo', Fecha, V, L), Eqs),
    include(=(V), Eqs, FGVs), length(FGVs, CV),
    include(=(L), Eqs, FGLs), length(FGLs, CL),
    CV > 1, CL > 1,
    partido(Fecha, V, L, _, _).

% 5) Partidos en que hubo safety
partido_con_safety(Fecha, V, L) :-
    anotacion(_, _, 'safety', Fecha, V, L).

% 6) Dada una fecha, visitante o local que ganó ese partido
ganador_por_fecha(Fecha, Eq) :-
    partido(Fecha, V, L, PV, PL),
    ( PV > PL -> Eq = V
    ; PL > PV -> Eq = L
    ).
