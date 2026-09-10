from typing import Any, Literal, Type, cast

from sqlalchemy import Table, inspect
from sqlalchemy.orm import Mapper
from sqlmodel import SQLModel


class SelectQueryBuilder:
    def __init__(
        self,
        model_cls: Type[SQLModel],
        selected_columns: Literal["*"] | list[str] | None = None,
        where_clauses: dict[str, Any] | None = None,
        offset: int | None = None,
        limit: int | None = None,
        order_by: str | None = None,
        order_dir: str = "DESC",
        allow_expressions: bool = False,
    ):
        mapper = cast(Mapper, inspect(model_cls))
        table: Table = mapper.local_table

        self._model_cls = model_cls
        self._schema = table.schema
        self._table_name = table.name
        self._fqtn = f"{self._schema + '.' if self._schema else ''}{self._table_name}"

        self._model_columns = {c.name for c in table.columns}
        self._where_clauses = where_clauses or {}
        self._offset = offset
        self._limit = limit
        self._order_by = order_by
        self._order_dir = order_dir.upper()

        if selected_columns is None:
            self._selected_columns: str | list[str] = list(self._model_columns)
        elif selected_columns == "*":
            self._selected_columns = "*"
        else:
            if not allow_expressions:
                for col in selected_columns:
                    if col not in self._model_columns:
                        raise ValueError(
                            f"Selected column '{col}' does not exist in "
                            f"model {model_cls.__name__}"
                        )
            self._selected_columns = list(selected_columns)

        for col in self._where_clauses.keys():
            if col not in self._model_columns:
                raise ValueError(
                    f"WHERE column '{col}' does not exist in model {model_cls.__name__}"
                )

        if self._order_by and self._order_by not in self._model_columns:
            raise ValueError(
                f"ORDER BY column '{self._order_by}"
                f"does not exist in model' {model_cls.__name__}"
            )

    def sql_query(self) -> tuple[str, list[Any]]:
        if isinstance(self._selected_columns, str):
            cols_clause = self._selected_columns
        else:
            cols_clause = ", ".join(self._selected_columns)

        query = f"SELECT {cols_clause} FROM {self._fqtn}"
        params: list[Any] = []

        if self._where_clauses:
            where_parts = []
            for idx, (col, val) in enumerate(self._where_clauses.items(), start=1):
                where_parts.append(f"{col} = ${idx}")
                params.append(val)
            query += f" WHERE {' AND '.join(where_parts)}"

        if self._order_by:
            dir_str = "ASC" if self._order_dir == "ASC" else "DESC"
            query += f" ORDER BY {self._order_by} {dir_str}"

        param_idx = len(params) + 1
        if self._limit is not None:
            query += f" LIMIT ${param_idx}"
            params.append(self._limit)
            param_idx += 1

        if self._offset is not None:
            query += f" OFFSET ${param_idx}"
            params.append(self._offset)

        return query, params


class InsertQueryBuilder:
    def __init__(
        self, model_cls: Type[SQLModel], explicit_columns: list[str] | None = None
    ):
        self._model_cls = model_cls
        table = model_cls.__table__  # pyrefly: ignore [missing-attribute]
        self._table_name = table.name

        if explicit_columns:
            self._columns = explicit_columns
        else:
            self._columns = [col.name for col in table.columns]

    def sql_query(self) -> tuple[str, list[str]]:
        sql_columns = ", ".join(self._columns)
        sql_values = ", ".join(f"${i + 1}" for i in range(len(self._columns)))
        return (
            f"INSERT INTO {self._table_name} ({sql_columns}) VALUES ({sql_values})",
            self._columns,
        )


class UpdateQueryBuilder:
    def __init__(
        self,
        model_cls: Type[SQLModel],
        updated_fields: list[str],
        where_fields: list[str],
        manage_version: bool = True,
    ):
        self._model_cls = model_cls
        table = model_cls.__table__  # pyrefly: ignore [missing-attribute]
        self._table_name = table.name
        self._updated_fields = updated_fields
        self._where_fields = where_fields
        self._manage_version = manage_version
        self._column_names = {col.name for col in table.columns}

        for f in updated_fields + where_fields:
            if f not in self._column_names:
                raise ValueError(
                    f"Field '{f}' does not exist in model '{model_cls.__name__}'"
                )

    def sql_query(self) -> tuple[str, list[str], list[str]]:
        assignments = [
            f"{field} = ${i + 1}" for i, field in enumerate(self._updated_fields)
        ]

        if self._manage_version and "version" in self._column_names:
            assignments.append("version = version + 1")

        set_clause = ", ".join(assignments)

        base_index = len(self._updated_fields) + 1
        where_parts = [
            f"{field} = ${base_index + i}" for i, field in enumerate(self._where_fields)
        ]
        where_clause = " AND ".join(where_parts)

        sql = f"UPDATE {self._table_name} SET {set_clause} WHERE {where_clause}"
        return sql, self._updated_fields, self._where_fields


class DeleteQueryBuilder:
    def __init__(self, model_cls: Type[SQLModel], where_clauses: dict[str, Any]):
        table = model_cls.__table__  # pyrefly: ignore [missing-attribute]
        self._table_name = table.name
        self._column_names = {col.name for col in table.columns}
        self._where_clauses = where_clauses or {}

        for col in self._where_clauses.keys():
            if col not in self._column_names:
                raise ValueError(
                    f"WHERE column '{col}' does not exist in model {model_cls.__name__}"
                )

    def sql_query(self) -> tuple[str, list[Any]]:
        if not self._where_clauses:
            raise ValueError("DELETE query requires at least one WHERE clause")

        conditions = []
        params: list[Any] = []
        for idx, (col, val) in enumerate(self._where_clauses.items(), start=1):
            conditions.append(f"{col} = ${idx}")
            params.append(val)

        sql = f"DELETE FROM {self._table_name} WHERE {' AND '.join(conditions)}"
        return sql, params
