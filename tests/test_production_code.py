import production_code

conn, cursor = production_code.open_db("jobs_db.sqlite")

# def test_first_job_listing_in_file():
#     job_file = open(os.path.dirname(__file__) + '/../jobs.txt', 'r')
#     name_found_in_line = False
#     for line in job_file:
#         if 'F. Hoffmann-La Roche AG' in line:
#             name_found_in_line = True
#     assert name_found_in_line


def test_length_of_result():
    result = production_code.get_api_data()
    assert len(result) > 100


def test_length_of_result_from_stack_overflow():
    result = production_code.data_from_stack_overflow()
    assert len(result) == 1000


def test_known_result_in_db():
    production_code.insert_data_into_db(cursor, production_code.get_api_data())
    result = cursor.execute('SELECT company FROM api_jobs WHERE company = "DevsData"')
    assert result.fetchone()[0] == "DevsData"


# Test that data from stack overflow is in the database.
def test_data_from_stack_overflow():
    production_code.insert_data_into_db(cursor, production_code.data_from_stack_overflow())
    result = cursor.execute('SELECT company FROM api_jobs WHERE company = "X-Team"')
    assert result.fetchone()[0] == "X-Team"


def test_data_from_stack_overflow_is_entered_correctly():
    result = cursor.execute('SELECT * FROM api_jobs WHERE job_id = "361426"')
    for row in result:
        assert row[0] == '361426'
        assert row[4] == 'Fri, 07 Feb 2020 19:02:34 Z'


# Extra Test, tests that ALL the data from github in the db is correct after each pull from the API.
def test_all_data_in_db():
    production_code.drop_table_on_new_api_call(cursor)
    production_code.create_table(cursor)
    production_code.insert_data_into_db(cursor, production_code.get_api_data())
    production_code.insert_data_into_db(cursor, production_code.data_from_stack_overflow())
    result = cursor.execute('SELECT * FROM api_jobs')
    jobs = production_code.get_api_data()
    for (job, row) in zip(jobs, result):
        assert job['id'] == row[0]
        assert job['company'] == row[1]
        assert job['company_logo'] == row[2]
        assert job['company_url'] == row[3]
        assert job['created_at'] == row[4]
        assert job['description'] == row[5]
        assert job['how_to_apply'] == row[6]
        assert job['location'] == row[7]
        assert job['title'] == row[8]
        assert job['type'] == row[9]
        assert job['url'] == row[10]


def test_if_db_table_exists():
    result = cursor.execute('''SELECT name FROM sqlite_master WHERE type='table' AND name='api_jobs';''')
    assert result.fetchone()[0] == 'api_jobs'


def test_good_data_input():
    job_list = [{
        "company": "test",
        "company_logo": "test",
        "company_url": "test",
        "created_at": "test",
        "description": "test",
        "how_to_apply": "test",
        "id": "test",
        "location": "test",
        "title": "test",
        "type": "test",
        "url": "test"
    }]
    result = production_code.insert_data_into_db(cursor, job_list)
    assert result is None


# Missing a key. TESTS FOR BOTH API CALLS
def test_bad_data_input():
    job_list = [{
        "company_logo": 'test',
        "company_url": "test",
        "created_at": "test",
        "description": "test",
        "how_to_apply": "test",
        "id": "test",
        "location": "test",
        "title": "test",
        "type": "test",
        "url": "test"
    }]
    result = production_code.insert_data_into_db(cursor, job_list)
    assert result == "failed"


# Missing company name which is not allowed. TESTS FOR BOTH API CALLS
def test_bad_data_input_two():
    job_list = [{
        "company": None,
        "company_logo": 'test',
        "company_url": "test",
        "created_at": "test",
        "description": "test",
        "how_to_apply": "test",
        "id": "test",
        "location": "test",
        "title": "test",
        "type": "test",
        "url": "test"
    }]
    result = production_code.insert_data_into_db(cursor, job_list)
    assert result == "failed"


def test_data_for_tech_filter():
    production_code.create_table_cache_for_job_locations(cursor)
    all_jobs = production_code.grab_all_jobs_for_lat_long(cursor)
    production_code.geo_lat_and_long_for_location(cursor, all_jobs)
    all_jobs = production_code.fetch_all_jobs_with_lat_long(cursor, production_code.fetch_all_jobs(cursor))
    filtered_jobs = production_code.filter_jobs_by_desc("ruby", all_jobs)

    assert len(filtered_jobs) > 0


def test_data_for_company_filter():
    production_code.create_table_cache_for_job_locations(cursor)
    all_jobs = production_code.grab_all_jobs_for_lat_long(cursor)
    production_code.geo_lat_and_long_for_location(cursor, all_jobs)
    all_jobs = production_code.fetch_all_jobs_with_lat_long(cursor, production_code.fetch_all_jobs(cursor))
    filtered_jobs = production_code.filter_jobs_by_desc("siemens", all_jobs)

    assert len(filtered_jobs) > 0


def test_data_for_type_filter():
    production_code.create_table_cache_for_job_locations(cursor)
    all_jobs = production_code.grab_all_jobs_for_lat_long(cursor)
    production_code.geo_lat_and_long_for_location(cursor, all_jobs)
    all_jobs = production_code.fetch_all_jobs_with_lat_long(cursor, production_code.fetch_all_jobs(cursor))
    filtered_jobs = production_code.filter_jobs_by_desc("full time", all_jobs)

    assert len(filtered_jobs) > 0


def test_data_for_date_filter():
    production_code.create_table_cache_for_job_locations(cursor)
    all_jobs = production_code.grab_all_jobs_for_lat_long(cursor)
    production_code.geo_lat_and_long_for_location(cursor, all_jobs)
    all_jobs = production_code.fetch_all_jobs_with_lat_long(cursor, production_code.fetch_all_jobs(cursor))
    filtered_jobs = production_code.filter_jobs_by_desc("4", all_jobs)
    assert len(filtered_jobs) > 0


def test_data_for_more_details():
    production_code.create_table_cache_for_job_locations(cursor)
    all_jobs = production_code.grab_all_jobs_for_lat_long(cursor)
    production_code.geo_lat_and_long_for_location(cursor, all_jobs)
    all_jobs = production_code.fetch_all_jobs_with_lat_long(cursor, production_code.fetch_all_jobs(cursor))
    graph_data = {'points': [{'curveNumber': 0, 'pointNumber': 548, 'pointIndex': 548, 'lon': '-95.9383758',
                              'lat': '41.2587459',
                              'text': 'CSG Actuarial, Front-End/UI Engineer at CSG Actuarial (Omaha, NE)'}]}
    detailed_data = production_code.get_graph_point_detail_data(graph_data, all_jobs)
    assert detailed_data['company'] == 'CSG Actuarial'
