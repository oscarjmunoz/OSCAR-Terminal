# DECISION CORE

## Purpose

El objetivo de Decision Core es definir objetos basicos, reutilizables y deterministas
para representar reglas y resultados de decision sin introducir logica de trading,
motores ni dependencias de UI.

## DecisionStatus

DecisionStatus es un Enum estandar para expresar el estado de una evaluacion.

Valores:

- PASS
- FAIL
- WAIT
- WARNING
- READY

Beneficio:

- Estandariza estados entre motores presentes y futuros.
- Mantiene decisiones explicables y comparables.

## Rule

Rule representa la definicion de una regla reusable.

Campos:

- id
- code
- title
- description
- category
- weight
- critical

Propiedades de diseno:

- Modelo tipado.
- Inmutable cuando es posible para evitar cambios accidentales en tiempo de ejecucion.

## RuleResult

RuleResult representa el resultado de evaluar una Rule.

Campos:

- rule
- status
- score
- reason
- warning

Beneficio:

- Conecta una regla con un estado de salida consistente.
- Permite trazabilidad explicable por regla.

## Future Engine Usage

Estos objetos son la base para que motores futuros (Liquidity, Premium Discount,
Structure, Context, MSS, IEZ, Entry y Trade Management) reporten decisiones con
un contrato uniforme, desacoplado de UI y sin duplicar logica transversal.
