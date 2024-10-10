from global_values import NAMES

IMPUTATER_PROMPT = {
	'head': """This agent is designed to deduce the missing value of the column(s) in the table. 

If some values can not be deduced, please keep the original value. If some values are ambiguous, please deduce a reasonable value to try not to affect the execution of the SQL query.""",

    f"demo_{NAMES['STAND_NUMERICAL']}": """Please deduce the unstandardized values in the column `rank` to numerical format.

/*
{
    1: {"rank": "nan", "rank_cleaned": "[?]"},
    2: {"rank": "nan", "rank_cleaned": "[?]"},
    3: {"rank": "nan", "rank_cleaned": "[?]"},
    4: {"rank": "4.0", "rank_cleaned": 4},
    5: {"rank": "5.0", "rank_cleaned": 5},
    6: {"rank": "6.0", "rank_cleaned": 6},
}
*/
Requirement: please standardize the column `rank` to numerical format abd fill the token [?] of row(1, 2, 3).
SQL: SELECT rank FROM table WHERE rank < 10
Output: ```{1: {'rank': 'nan', 'rank_cleaned': '[n.a.]'}, 2: {'rank': 'nan', 'rank_cleaned': 2}, 3: {'rank': 'nan', 'rank_cleaned': 3}}```

/*
{
	1: {'year_built': 1966, 'year_built_cleaned': 1966},
	2: {'year_built': 1984, 'year_built_cleaned': 1984},
	3: {'year_built': 1931, 'year_built_cleaned': 1931},
	4: {'year_built': 'Early 2012', 'year_built_cleaned': '[?]'},
	5: {'year_built': '194?', 'year_built_cleaned': '[?]'},
}
*/
Requirement: please standardize the column `year_built` to numerical format and fill the token [?] of row(4, 5).
SQL: SELECT year_built FROM table WHERE year_built > 1935
Output: ```{4: {'year_built': 'Early 2012', 'year_built_cleaned': 2012}, 5: {'year_built': '194?', 'year_built_cleaned': 1940}}```

/*
{
	1: {'position': '4th', 'position_cleaned': 4},
	2: {'position': '4th', 'position_cleaned': 4},
	3: {'position': '3rd', 'position_cleaned': 3},
	4: {'position': 'nan', 'position_cleaned': '[?]'},
	5: {'position': '8th', 'position_cleaned': 8},
	6: {'position': 'Champion', 'position_cleaned': '[?]'},
	7: {'position': '6th', 'position_cleaned': 6},
	8: {'position': 'Champion', 'position_cleaned': '[?]'},
}
*/
Requirement: please standardize the column `position` to numerical format and fill the token [?] of row(4, 6, 8).
SQL: SELECT `position` FROM table WHERE `position` < 3
Output: ```{4: {'position': 'nan', 'position_cleaned': '[n.a.]'}, 6: {'position': 'Champion', 'position_cleaned': 1}, 8: {'position': 'Champion', 'position_cleaned': 1}}```

/*
{
	1: {'time': '10.55', 'time_cleaned': 10.55},
	2: {'time': '11.00', 'time_cleaned': 11.0},
	3: {'time': '11.17', 'time_cleaned': 11.17},
	4: {'time': 'dns', 'time_cleaned': '[?]'},
	5: {'time': 'dp', 'time_cleaned': '[?]'},
}
*/
Requirement: please standardize the column `time` to numerical format and fill the token [?] of row(4, 5).
SQL: SELECT `name` FROM w WHERE `time` = (SELECT MIN(`time`) FROM w WHERE `heat` = 1)
Output: ```{4: {'time': 'dns', 'time_cleaned': '[n.a.]'}, 5: {'time': 'dp', 'time_cleaned': '[n.a.]'}}```

/*
{
	1: {'diameter': '18 mm', 'diameter_cleaned': 18},
	2: {'diameter': '21 mm', 'diameter_cleaned': 21},
	3: {'diameter': '24 mm', 'diameter_cleaned': 24},
    4: {'diameter': '32-33 mm', 'diameter_cleaned': '[?]'},
}
Requirement: please standardize the column `diameter` to numerical format and fill the token [?] of row(4).
SQL: SELECT `diameter` FROM w WHERE `diameter` > 20
Output: ```{4: {'diameter': '32-33 mm', 'diameter_cleaned': 32}}```""",

	f"demo_{NAMES['STAND_DATETIME']}": """Please deduce the unstandardized values in the column `date` to datetime format.

/*
{
	1: {'elected_date': 'March 22, 1954', 'elected_date_cleaned': '1954-03-22'},
	2: {'elected_date': 'March 31, 1958', 'elected_date_cleaned': 4},
	3: {'elected_date': 'March 28, 1958 entered', 'elected_date_cleaned': '[?]'},
	4: {'elected_date': 'March 5, 1891', 'elected_date_cleaned': '1891-03-05'},
	5: {'elected_date': '-', 'elected_date_cleaned': '[?]'},
}
*/
Requirement: please standardize the column `elected_date` to datetime format and fill the token [?] of row(3, 5).
SQL: SELECT COUNT(*) FROM w WHERE `elected_date` < '1950-01-01'
Output: ```{3: {'elected_date': 'March 28, 1958 entered', 'elected_date_cleaned': '1958-03-28'}, 5: {'elected_date': '-', 'elected_date_cleaned': '[n.a.]'}}```

/*
{
	1: {'date': 'September 3, 1995', 'date_cleaned': '1995-09-03'},
	2: {'date': 'September 10, 1995', 'date_cleaned': '1995-09-10'},
	3: {'date': 'October 8, 1995', 'date_cleaned': '1995-10-08'},
	4: {'date': 'bye', 'date_cleaned': '[?]'},
}
*/
Requirement: please standardize the column `date` to datetime format and fill the token [?] of row(4).
SQL: SELECT `date` FROM w WHERE `date` = (SELECT MIN(`date`) FROM w WHERE `name` = 'John')
Output: ```{4: {'date': 'bye', 'date_cleaned': '[n.a.]'}}```

/*
{
	1: {'season': '1997-98', 'season_cleaned': '[?]'},
	2: {'season': '1998-99', 'season_cleaned': '[?]'},
	3: {'season': '1999-00', 'season_cleaned': '[?]'},
	4: {'season': '2000-01', 'season_cleaned': '[?]'},
}
*/
Requirement: please standardize the column `season` to datetime format and fill the token [?] of row(1, 2, 3, 4).
SQL: SELECT `season` FROM w WHERE `season` LIKE '%2001%'
Output: ```{1: {'season': '1997-98', 'season_cleaned': '1997-1998'}, 2: {'season': '1998-99', 'season_cleaned': '1998-1999'}, 3: {'season': '1999-00', 'season_cleaned': '1999-2000'}, 4: {'season': '2000-01', 'season_cleaned': '2000-2001'}}```""",

	f"demo_{NAMES['GEN_NEW_COL']}": """Please deduce the values that does not generate correctly.

/*
{
	1: {'score': 'w 8-1', 'score_difference': 7},
	2: {'score': 'w 4-3 (10)', 'score_difference': 1},
	3: {'score': 'w 6:5', 'score_difference': '[?]'},
	4: {'score': 'l 2-5', 'score_difference': '3'},
	5: {'score': 'l4-8', 'score_difference': '[?]'},
}
*/
Requirement: please generate a new column `score_difference` based on the column `score` and fill the token [?] of row(3, 5).
SQL: SELECT COUNT(*) FROM w WHERE `score_difference` = 1
Output: ```{3: {'score': 'w 6:5', 'score_difference': 1}, 5: {'score': 'l4-8', 'score_difference': 4}}```

/*
{
	1: {'launched': '19 february 1946', 'fate': 'scrapped in 1972', 'service_duration': '26'},
    2: {'launched': '30 august 1946', 'fate': 'scrapped in 1974', 'service_duration': '26'},
    3: {'launched': '6 july 1944', 'fate': 'sold as oil hulk in 1960', 'service_duration': '[?]'},
    4: {'launched': '1943/10/27', 'fate': 'scrapped in 1960', 'service_duration': '[?]'},
    5: {'launched': '30 september 1943', 'fate': 'scrapped in 1966', 'service_duration': '17'},
}
*/
Requirement: please generate a new column `service_duration` based on the columns `launched` and `fate` and fill the token [?] of row(3, 4).
SQL: SELECT MAX(`service_duration`) FROM w WHERE `service_duration` < 20
Output: ```{3: {'launched': '6 july 1944', 'fate': 'sold as oil hulk in 1960', 'service_duration': 16}, 4: {'launched': '1943/10/27', 'fate': 'scrapped in 1960', 'service_duration': 17}}```

/*
{
	1: {'season': '2000-01', 'season_cleaned': '2000-2001'},
	2: {'season': '2005-06', 'season_cleaned': '2005-2006'},
	3: {'season': '2009-10', 'season_cleaned': '[?]'},
	4: {'season': '2010-11', 'season_cleaned': '[?]'},
	5: {'season': '2011-12', 'season_cleaned': '[?]'},
}
*/
Requirement: please generate a new column `season_cleaned` based on the column `season` and fill the token [?] of row(3, 4, 5).
SQL: SELECT MIN(`season`) FROM w WHERE `league_top_scorer` LIKE '%bent christensen%'
Output: ```{3: {'season': '2009-10', 'season_cleaned': '2009-2010'}, 4: {'season': '2010-11', 'season_cleaned': '2010-2011'}, 5: {'season': '2011-12', 'season_cleaned': '2011-2012'}}```""",

	# query for standardize
	f"query_standardize": """Please complete the following prompt.

/*
{table}
*/
Requirement: please standardize the column `{column}` to {coltype} format and fill the token [?] of row({rows}).
SQL: {sql}
Please output json format as above. If the value cannot be deduced, keep the original value.
Output:""",

	# query for generate new column
	f"query_generate": """Please complete the following prompt.
    
/*
{table}
*/
Requirement: please generate a new column `{new_col}` based on the {column_flag} `{column_str}` and fill the token [?] of row({rows}).
SQL: {sql}
Please output json format as above. If the value cannot be deduced, output [n.a.].
Output:""", #!

	# self-correc
    f"self_correc_ins": """/*
{context}
*/
Requirement: {question}
Last Error: {last_error}
Output: {a}"""

}