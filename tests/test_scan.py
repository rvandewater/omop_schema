"""Reading OMOP tables into their schema with `omop_schema.scan.scan_table`."""

import datetime as dt
import gzip
from pathlib import Path

import polars as pl
import polars.selectors as cs
import pytest

from omop_schema.convert import convert_to_schema_polars
from omop_schema.scan import SHARDS_PER_CONCAT, scan_table
from omop_schema.utils import load_table_polars
from omop_schema.versions import get_schema_loader

SCHEMA = get_schema_loader("5.4")
NOTE_CSV = (
    "note_id,person_id,note_date,note_datetime,note_text,xtn_note_last_edit_datetime\n"
    "1,10,2020-01-01,2020-01-01 08:00:00,a,2020-01-03 09:00:00\n"
    "2,11,2020-01-02 00:00:00,2020-01-02 08:00:00,b,\n"
)
NOTE_TYPES = {
    "note_id": pl.Int64,
    "person_id": pl.Int64,
    "note_date": pl.Date,
    "note_datetime": pl.Datetime("us"),
    "note_text": pl.String,
}


def _notes() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "note_id": [1, 2],
            "person_id": [10, 11],
            "note_date": ["2020-01-01", "2020-01-02 00:00:00"],
            "note_datetime": ["2020-01-01 08:00:00", "2020-01-02 08:00:00"],
            "note_text": ["a", "b"],
            "xtn_note_last_edit_datetime": ["2020-01-03 09:00:00", None],
        }
    )


def _assert_note_types(table: pl.LazyFrame) -> pl.DataFrame:
    df = table.collect()
    assert {c: df.schema[c] for c in NOTE_TYPES} == NOTE_TYPES
    assert df.sort("note_id")["note_date"].to_list() == [dt.date(2020, 1, 1), dt.date(2020, 1, 2)]
    return df


# --- files ----------------------------------------------------------------------------------------


@pytest.mark.parametrize("suffix", [".csv", ".csv.gz"])
def test_csv_file_is_read_in_the_schema_with_extra_columns_kept(tmp_path: Path, suffix):
    fp = tmp_path / f"note{suffix}"
    data = NOTE_CSV.encode()
    fp.write_bytes(gzip.compress(data) if suffix.endswith(".gz") else data)

    df = _assert_note_types(scan_table(fp, SCHEMA))

    assert df["xtn_note_last_edit_datetime"].to_list() == ["2020-01-03 09:00:00", None]


def test_uppercase_csv_headers_get_their_schema_types(tmp_path: Path):
    # SQL Server exports write uppercase headers; they used to skip the schema and stay text.
    header, rows = NOTE_CSV.split("\n", 1)
    (tmp_path / "note.csv").write_text("﻿" + header.upper() + "\n" + rows)

    df = _assert_note_types(scan_table(tmp_path / "note.csv", SCHEMA))

    assert df.columns == [c.lower() for c in header.split(",")]


def test_column_case_is_kept_on_request_and_types_still_apply(tmp_path: Path):
    (tmp_path / "death.csv").write_text("PERSON_ID,DEATH_DATE\n1,2005-05-07\n")

    df = scan_table(tmp_path / "death.csv", SCHEMA, lowercase_columns=False).collect()

    assert df.schema == {"PERSON_ID": pl.Int64, "DEATH_DATE": pl.Date}


def test_parquet_file_is_cast_to_the_schema(tmp_path: Path):
    notes = _notes().with_columns(
        pl.col("note_id").cast(pl.Int32),
        pl.col("note_datetime").str.to_datetime(time_unit="ms"),
    )
    notes.rename({"person_id": "PERSON_ID"}).write_parquet(tmp_path / "note.parquet")

    df = _assert_note_types(scan_table(tmp_path / "note.parquet", SCHEMA))

    assert "xtn_note_last_edit_datetime" in df.columns


@pytest.mark.parametrize("strict", [True, False])
def test_a_date_with_a_time_of_day_fails_unless_not_strict(tmp_path: Path, strict):
    (tmp_path / "death.csv").write_text("person_id,death_date\n1,2005-05-07 13:45:00\n")
    table = scan_table(tmp_path / "death.csv", SCHEMA, strict=strict)

    if strict:
        with pytest.raises(pl.exceptions.PolarsError):
            table.collect()
    else:
        assert table.collect()["death_date"].to_list() == [None]


# --- directories and lists of shards --------------------------------------------------------------


def test_parquet_shards_keep_extra_columns_and_tolerate_differing_columns(tmp_path: Path):
    # The last-edit column notes need for leakage-safe times is outside the schema and only in one shard.
    shards = tmp_path / "note"
    (shards / "nested").mkdir(parents=True)
    _notes()[:1].write_parquet(shards / "part_0.parquet")
    _notes()[1:].drop("xtn_note_last_edit_datetime").select(pl.all().reverse()).write_parquet(
        shards / "nested" / "part_1.parquet"
    )
    (shards / "README.txt").write_text("not data")

    df = _assert_note_types(scan_table(shards, SCHEMA))

    assert df.sort("note_id")["xtn_note_last_edit_datetime"].to_list() == ["2020-01-03 09:00:00", None]


def test_csv_shards_are_stacked(tmp_path: Path):
    header, *rows = NOTE_CSV.strip().split("\n")
    (tmp_path / "note").mkdir()
    for i, row in enumerate(rows):
        (tmp_path / "note" / f"{i}.csv.gz").write_bytes(gzip.compress(f"{header}\n{row}\n".encode()))

    assert _assert_note_types(scan_table(tmp_path / "note", SCHEMA)).height == 2


def test_more_shards_than_one_concat_takes_are_all_read(tmp_path: Path):
    n_shards = SHARDS_PER_CONCAT * 2 + 3
    (tmp_path / "death").mkdir()
    for i in range(n_shards):
        pl.DataFrame({"person_id": [i]}).write_parquet(tmp_path / "death" / f"{i:04d}.parquet")

    df = scan_table(tmp_path / "death", SCHEMA).collect()

    assert sorted(df["person_id"].to_list()) == list(range(n_shards))


def test_list_of_shards_needs_a_table_name_for_an_omop_schema(tmp_path: Path):
    fps = []
    for i, part in enumerate((_notes()[:1], _notes()[1:])):
        fps.append(tmp_path / f"part_{i}.parquet")
        part.write_parquet(fps[-1])

    with pytest.raises(ValueError, match="table_name"):
        scan_table(fps, SCHEMA)
    assert _assert_note_types(scan_table(fps, SCHEMA, table_name="note")).height == 2


def test_csv_shards_take_precedence_over_parquet_shards(tmp_path: Path):
    (tmp_path / "death").mkdir()
    (tmp_path / "death" / "a.csv").write_text("person_id\n1\n")
    pl.DataFrame({"person_id": [2]}).write_parquet(tmp_path / "death" / "b.parquet")

    assert scan_table(tmp_path / "death", SCHEMA).collect()["person_id"].to_list() == [1]


@pytest.mark.parametrize("name", ["empty_dir", "death.txt", "missing.csv"])
def test_sources_without_csv_or_parquet_data_give_none(tmp_path: Path, name):
    if name == "empty_dir":
        (tmp_path / name).mkdir()
    elif name == "death.txt":
        (tmp_path / name).write_text("person_id\n1\n")

    assert scan_table(tmp_path / name, SCHEMA) is None


# --- options --------------------------------------------------------------------------------------


def test_selector_applies_to_lowercased_columns(tmp_path: Path):
    (tmp_path / "death.csv").write_text("PERSON_ID,DEATH_DATE,XTN_SOURCE\n1,2005-05-07,x\n")

    table = scan_table(tmp_path / "death.csv", SCHEMA, selector=~cs.matches("^xtn_"))

    assert table.collect_schema().names() == ["person_id", "death_date"]


def test_missing_schema_columns_are_added_on_request(tmp_path: Path):
    (tmp_path / "death.csv").write_text("person_id\n1\n")

    kept = scan_table(tmp_path / "death.csv", SCHEMA).collect_schema()
    added = scan_table(tmp_path / "death.csv", SCHEMA, add_missing_columns=True).collect_schema()

    assert kept.names() == ["person_id"]
    assert dict(added) == SCHEMA.get_polars_schema("death")


def test_without_a_schema_types_are_kept_as_read(tmp_path: Path):
    _notes().rename({"note_id": "NOTE_ID"}).write_parquet(tmp_path / "note.parquet")

    df = scan_table(tmp_path / "note.parquet").collect()

    assert df.schema["note_id"] == pl.Int64 and df.schema["note_date"] == pl.String


def test_a_schema_mapping_works_without_a_table_name(tmp_path: Path):
    paths = [tmp_path / "a.parquet"]
    pl.DataFrame({"x": ["2005-05-07"]}).write_parquet(paths[0])

    assert scan_table(paths, {"x": pl.Date}).collect()["x"].to_list() == [dt.date(2005, 5, 7)]


def test_extension_columns_are_dropped_on_request(tmp_path: Path):
    _notes().write_parquet(tmp_path / "note.parquet")

    columns = scan_table(tmp_path / "note.parquet", SCHEMA, keep_extra_columns=False).collect_schema().names()

    assert "xtn_note_last_edit_datetime" not in columns
    assert set(columns) == set(_notes().columns) - {"xtn_note_last_edit_datetime"}


@pytest.mark.parametrize("strict", [True, False])
def test_relaxed_alignment_nulls_values_a_shard_cannot_fit(tmp_path: Path, strict):
    (tmp_path / "death").mkdir()
    pl.DataFrame({"person_id": [1]}).write_parquet(tmp_path / "death" / "a.parquet")
    pl.DataFrame({"person_id": ["2", "unknown"]}).write_parquet(tmp_path / "death" / "b.parquet")
    table = scan_table(tmp_path / "death", SCHEMA, strict=strict)

    if strict:
        with pytest.raises(pl.exceptions.PolarsError):
            table.collect()
    else:
        assert sorted(table.collect()["person_id"].to_list(), key=str) == [1, 2, None]


def test_compact_and_slashed_dates_are_read(tmp_path: Path):
    (tmp_path / "death.csv").write_text("person_id,death_date\n1,20050507\n2,2005/05/08\n")

    dates = scan_table(tmp_path / "death.csv", SCHEMA).collect()["death_date"].to_list()

    assert dates == [dt.date(2005, 5, 7), dt.date(2005, 5, 8)]


@pytest.mark.parametrize("value", ["2005/05/07", "2005.05.07", "07-05-2005", "07/05/2005", "07.05.2005"])
def test_year_first_and_day_first_dates_are_read_as_polars_infers_them(tmp_path: Path, value):
    (tmp_path / "death.csv").write_text(f"person_id,death_date\n1,{value}\n")

    assert scan_table(tmp_path / "death.csv", SCHEMA).collect()["death_date"].to_list() == [
        dt.date(2005, 5, 7)
    ]


def test_any_object_with_a_pyarrow_schema_can_be_the_schema(tmp_path: Path):
    class SiteSchema:  # e.g. a site's own schema, not derived from OMOPSchemaBase
        def get_pyarrow_schema(self, table_name):
            return SCHEMA.get_pyarrow_schema(table_name)

    (tmp_path / "death.csv").write_text("person_id,death_date\n1,2005-05-07\n")

    assert scan_table(tmp_path / "death.csv", SiteSchema()).collect().schema == {
        "person_id": pl.Int64,
        "death_date": pl.Date,
    }
    with pytest.raises(ValueError, match="table_name"):
        scan_table([tmp_path / "death.csv"], SiteSchema())


# --- callers --------------------------------------------------------------------------------------


def test_load_table_polars_reads_through_scan_table(tmp_path: Path):
    (tmp_path / "death.csv").write_text("PERSON_ID,DEATH_DATE\n1,2005-05-07 00:00:00\n")

    assert load_table_polars(tmp_path / "death.csv", SCHEMA).collect().schema == {
        "person_id": pl.Int64,
        "death_date": pl.Date,
    }
    assert load_table_polars(tmp_path / "death.csv", case_insensitive=False).collect().columns == [
        "PERSON_ID",
        "DEATH_DATE",
    ]


def test_convert_to_schema_polars_parses_text_dates(tmp_path: Path):
    # Polars 2 no longer casts text to dates, which made this raise for string-typed date columns.
    df = pl.DataFrame({"d": ["2005-05-07", "2005-05-08 00:00:00"], "t": ["2005-05-07 08:00:00", None]})

    out = convert_to_schema_polars(df, {"d": pl.Date, "t": pl.Datetime("us")})

    assert out.schema == {"d": pl.Date, "t": pl.Datetime("us")}
    assert out["d"].to_list() == [dt.date(2005, 5, 7), dt.date(2005, 5, 8)]
