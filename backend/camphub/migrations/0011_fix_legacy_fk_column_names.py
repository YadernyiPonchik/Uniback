from django.db import migrations

# (table, old_column, new_column, references_table)
#
# These FK fields declare db_column='<field_name>' explicitly, but on
# databases created before that db_column was added, Django's default
# '<field_name>_id' column name is still what's physically on disk.
# On a fresh database (created straight from the current migrations)
# the column is already correctly named, so every step here is a no-op.
FK_COLUMNS = [
    ("camphub_cohort", "study_year_id_id", "study_year_id", "camphub_studyyear"),
    ("camphub_cohort", "room_id_id", "room_id", "camphub_room"),
    ("camphub_classevent", "subject_id_id", "subject_id", "camphub_subject"),
    ("camphub_classevent", "instructor_id_id", "instructor_id", "camphub_instructor"),
    ("camphub_classevent", "cohort_id_id", "cohort_id", "camphub_cohort"),
    ("camphub_classevent", "event_id_id", "event_id", "camphub_event"),
    ("camphub_classevent", "room_id_id", "room_id", "camphub_room"),
    ("camphub_gymevent", "event_id_id", "event_id", "camphub_event"),
    ("camphub_mealtime", "event_id_id", "event_id", "camphub_event"),
    ("camphub_bubbleevent", "event_id_id", "event_id", "camphub_event"),
    ("camphub_tvbooking", "user_id_id", "user_id", "accounts_useraccount"),
    ("camphub_tvbooking", "event_id_id", "event_id", "camphub_event"),
    ("camphub_reminder", "user_id_id", "user_id", "accounts_useraccount"),
    ("camphub_reminder", "event_id_id", "event_id", "camphub_event"),
]


def fix_column_names(apps, schema_editor):
    connection = schema_editor.connection
    existing_tables = set(connection.introspection.table_names())

    with connection.cursor() as cursor:
        for table, old_col, new_col, _ in FK_COLUMNS:
            if table not in existing_tables:
                continue

            columns = {
                col.name
                for col in connection.introspection.get_table_description(cursor, table)
            }

            if new_col in columns:
                continue  # already correctly named

            if old_col in columns:
                schema_editor.execute(
                    schema_editor.sql_rename_column
                    % {
                        "table": schema_editor.quote_name(table),
                        "old_column": schema_editor.quote_name(old_col),
                        "new_column": schema_editor.quote_name(new_col),
                        "type": "",
                    }
                )
            else:
                # Column missing under either name -- add it fresh.
                schema_editor.execute(
                    "ALTER TABLE %s ADD COLUMN %s bigint NULL"
                    % (schema_editor.quote_name(table), schema_editor.quote_name(new_col))
                )


class Migration(migrations.Migration):

    dependencies = [
        ("camphub", "0010_remove_reminder_day_remove_reminder_reminder_type_and_more"),
    ]

    operations = [
        migrations.RunPython(fix_column_names, reverse_code=migrations.RunPython.noop),
    ]
