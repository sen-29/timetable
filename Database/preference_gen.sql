DO 
$do$
BEGIN
    FOR i IN 2..46 LOOP
        FOR j in 1..25 LOOP 
            INSERT INTO perferences VALUES (i,j);
        END LOOP;
    END LOOP;
END; 
$do$