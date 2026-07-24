from django.db import migrations

# Same root cause as 0011: 0001_initial has been hand-edited over time to
# add models after it was already marked as applied against the production
# database, so those CreateModel operations were never actually run there.
# BubbleEvent is confirmed missing on Railway's Postgres; the rest are
# checked defensively so future model additions to 0001_initial don't cause
# the same silent drift.
MODELS = [
    "Room",
    "StudyYear",
    "Subject",
    "Cohort",
    "Event",
    "GymEvent",
    "Instructor",
    "ClassEvent",
    "MealTime",
    "BubbleEvent",
    "Contact",
    "TVBooking",
    "Reminder",
]


def create_missing_tables(apps, schema_editor):
    connection = schema_editor.connection
    existing_tables = set(connection.introspection.table_names())

    for model_name in MODELS:
        model = apps.get_model("camphub", model_name)
        table = model._meta.db_table
        if table not in existing_tables:
            schema_editor.create_model(model)


class Migration(migrations.Migration):

    dependencies = [
        ("camphub", "0011_fix_legacy_fk_column_names"),
    ]

    operations = [
        migrations.RunPython(create_missing_tables, reverse_code=migrations.RunPython.noop),
    ]
