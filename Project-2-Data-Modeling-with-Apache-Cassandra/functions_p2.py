# Fuctions for project 02

def create_table(table_name, dic_columns, partiton_key, cluster_key, session):
    """
    Make the Query and create the table using the query created on the Keyspace of Apache Cassandra.

    Args:
    table_name: string. Name of the table to be created
    dic_columns: dictionary. Dictionary with all columns name and values to be inserted in the query.
    partiton_key: list. List with all the partition keys of the table that will be created. 
    cluster_key: list. List with all the cluster keys of the table that will be created. 
    session: cursor of apache cassandra database.

    Returns:
    None
    """
    query = 'CREATE TABLE IF NOT EXISTS {} ('.format(table_name)

    for key, value in dic_columns.items():
        query += '{} {}, '.format(key, value[0])

    if len(partiton_key) >= 2 and len(cluster_key) >= 2:
        pk = ", ".join(partiton_key)
        ck = ", ".join(cluster_key)
        primary_key_query = 'PRIMARY KEY(({}), {}))'.format(pk, ck)

    elif len(partiton_key) == 1 and len(cluster_key) >= 2:
        ck = ", ".join(cluster_key)
        primary_key_query = 'PRIMARY KEY(({}), {}))'.format(partiton_key[0], ck)

    elif len(partiton_key) >= 2 and len(cluster_key) == 1:
        pk = ", ".join(partiton_key)
        primary_key_query = 'PRIMARY KEY(({}), {}))'.format(pk, cluster_key[0])

    else:
        primary_key_query = 'PRIMARY KEY(({}), {}))'.format(partiton_key[0], cluster_key[0])

    query += primary_key_query 

    try:
        # Creating the table for query 01
        session.execute(query)
        print('Table {} created with success.'.format(table_name))
    except Exception as e:
        # Printing EXCEPTION in case of error
        print(e)


def insert_table(file, table_name, dic_columns, session):
    """
    Make the Query and Insert values in the table created on the Keyspace of Apache Cassandra.

    Args:
    file: string. Path of the csv file to be processed.
    table_name: string. Name of the table to be created
    dic_columns: dictionary. Dictionary with all columns name and values to be inserted in the query. 
    session: cursor of apache cassandra database.

    Returns:
    None
    """
    import csv

    with open(file, encoding = 'utf8') as f:
        csvreader = csv.reader(f)
        next(csvreader) # skip header

        # Loop to pass in each line of the csv file
        for line in csvreader:
            query = 'INSERT INTO {} ('.format(table_name)

            t = []
            v = []
            w = []

            for key, values in dic_columns.items():
                t.append(key)
                v.append('%s')

                if values[0] == 'int':
                    w.append(int(line[values[1]]))
                elif values[0] == 'decimal':
                    w.append(float(line[values[1]]))
                else:
                    w.append(line[values[1]])


            x = ", ".join(t)
            y = ", ".join(v)
            z = tuple(w)

            query += x

            query += ") VALUES (" + y + ")"
            # Assigning the right values for each column.
            try:
                # Inserting values on table artist_library
                session.execute(query, z)

            except Exception as e:
                # Printing EXCEPTION in case of error
                print(e)

    print('Values inserted on table {}.'.format(table_name))