# Generated by Django 4.1.7 on 2023-04-06 09:04

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('Asymbol', '0009_alter_slope_value'),
    ]

    operations = [
        migrations.RunSQL(
            '''
                CREATE OR REPLACE FUNCTION to_seconds(t text)
                    RETURNS integer AS
                $BODY$ 
                    DECLARE
                        hs INTEGER;
                        ms INTEGER;
                        s INTEGER;
                    BEGIN
                        SELECT (EXTRACT( HOUR FROM  t::time) * 60*60) INTO hs; 
                        SELECT (EXTRACT (MINUTES FROM t::time) * 60) INTO ms;
                        SELECT (EXTRACT (SECONDS from t::time)) INTO s;
                        SELECT (hs + ms + s) INTO s;
                        RETURN s;
                    END;
                $BODY$
                    LANGUAGE 'plpgsql';
            '''
        )
    ]
