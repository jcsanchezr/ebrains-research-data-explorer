# EBRAINS Research Data Explorer

A research software prototype for retrieving, normalizing, indexing,
and exposing scientific metadata from the EBRAINS research infrastructure.

## Motivation

Scientific research infrastructures contain large amounts of valuable
data, but discovery and reuse depend heavily on structured metadata,
interoperability, and accessible interfaces.

This project explores a reproducible workflow for:

1. retrieving metadata from EBRAINS,
2. normalizing heterogeneous scientific metadata,
3. storing it in a relational database,
4. exposing it through a documented REST API,
5. enabling search and filtering for research-data discovery.

## Planned architecture

```text
EBRAINS
   |
   | API / metadata
   v
Python ingestion
   |
   v
Normalization
   |
   v
PostgreSQL
   |
   v
FastAPI
   |
   v
Search / Web interface
