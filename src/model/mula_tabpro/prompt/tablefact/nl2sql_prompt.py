DEMO_NL2SQLER = """Generate SQL given the statement and table to verify the statement correctly.

CREATE TABLE w(
	row_id int,
	round text,
	clubs_remaining int,
	clubs_involved int,
	winners_from_previous_round float,
	new_entries_this_round float,
	leagues_entering_at_this_round text)
/*
Title: turkish cup
3 example rows:
SELECT * FROM w LIMIT 3;
row_id	round	clubs_remaining	clubs_involved	winners_from_previous_round	new_entries_this_round	leagues_entering_at_this_round
0	first round	156	86	nan	86.0	tff third league
1	second round	113	108	43.0	65.0	süper ligs
2	third round	59	54	54.0	nan	none
*/
Q: süper lig be the league to win a round in the turkish cup with 110 clubs
SQL: SELECT (SELECT clubs FROM w WHERE `leagues_entering_at_this_round` = 'süper ligs') = 110

CREATE TABLE w(
	row_id int,
	round text,
	clubs_remaining int,
	clubs_involved int,
	winners_from_previous_round float,
	new_entries_this_round float,
	leagues_entering_at_this_round text)
/*
Title: turkish cup
3 example rows:
SELECT * FROM w LIMIT 3;
row_id	round	clubs_remaining	clubs_involved	winners_from_previous_round	new_entries_this_round	leagues_entering_at_this_round
0	first round	156	86	nan	86.0	tff third league & turkish regional amateur league
1	second round	113	108	43.0	65.0	süper lig & tff first league & tff second league
2	third round	59	54	54.0	nan	none
*/
Q: the lowest number of new entry conclude a round in the turkish cup be 5
SQL: SELECT (SELECT MIN(`new_entries_this_round`) FROM w) = 5

CREATE TABLE w(
	row_id int,
	letters text,
	organization text,
	nickname text,
	founding_time text,
	founding_university text,
	type text)
/*
Title: cultural interest fraternities and sororities
3 example rows:
SELECT * FROM w LIMIT 3;
row_id	letters	organization	nickname	founding_time	founding_university	type
0	αεπ	alpha epsilon pi 1	aepi	1913-11-07 00:00:00	new york university	fraternity
1	αεφ	alpha epsilon phi 2	aephi	1909-10-24 00:00:00	barnard college	sorority
2	σαεπ	sigma alpha epsilon pi 3	sigma	1998-10-01 00:00:00	university of california , davis	sorority
*/
Q: 4 of the cultural interest fraternity and sorority be fraternity while 3 be a sorority
SQL: SELECT (SELECT (SELECT COUNT(*) FROM w WHERE type = 'fraternity') = 4) AND (SELECT (SELECT COUNT(*) FROM w WHERE type = 'sorority') = 3)

CREATE TABLE w(
	row_id int,
	event text,
	data text,
	athlete text,
	date text,
	place text)
/*
Title: british records in athletics
3 example rows:
SELECT * FROM w LIMIT 3;
row_id	event	data	athlete	date	place
0	5 km	t19:29	andi drake	1990-05-27 00:00:00	norway
1	5 miles	32:38 +	ian mccombie	1985-03-23 00:00:00	united kingdom
2	10 km	40:17	chris maddocks	1989-04-30 00:00:00	united kingdom
*/
Q: there be 8 different event that take place within the united kingdom
SQL: SELECT (SELECT COUNT(place) FROM w WHERE place = 'united kingdom') = 8

CREATE TABLE w(
	row_id int,
	tournament text,
	wins int,
	top_10 int,
	top_25 int,
	events int,
	cuts_made int)
/*
Title: jeev milkha singh
3 example rows:
SELECT * FROM w LIMIT 3;
row_id	tournament	wins	top_10	top_25	events	cuts_made
0	masters tournament	0	0	1	3	2
1	us open	0	0	0	4	3
2	the open championship	0	0	0	2	1
*/
Q: the number of cut made in the pga championship tournament be smaller than the number of event
SQL: SELECT (SELECT `cuts_made` FROM w WHERE tournament = 'pga championship') < (SELECT events FROM w WHERE tournament = 'pga championship')

CREATE TABLE w(
	row_id int,
	place text,
	player text,
	country text,
	score int,
	to_par int)
/*
Title: 2008 women 's british open
3 example rows:
SELECT * FROM w LIMIT 3;
row_id	place	player	country	score	to_par
0	1	juli inkster	united states	65	7
1	t2	momoko ueda	japan	66	6
2	t2	laura diaz	united states	66	6
*/
Q: the 3 player from japan have the same score
SQL: SELECT (SELECT COUNT(DISTINCT score) FROM w WHERE country = 'japan' GROUP BY score) = 1

CREATE TABLE w(
	row_id int,
	place text,
	player text,
	country text,
	score text,
	to_par int)
/*
Title: 2008 women 's british open
3 example rows:
SELECT * FROM w LIMIT 3;
row_id	place	player	country	score	to_par
0	t1	yuri fudoh	japan	134	10
1	t1	jiyai shin	south korea	134	10
2	3	juli inkster	united states 135	9
*/
Q: kristie kerr , tie for 4th place , finish the round 1 stroke under lorena ochoa of mexico
SQL: SELECT (SELECT (SELECT score FROM w WHERE player = 'cristie kerr') < (SELECT score FROM w WHERE player = 'lorena ochoa' AND country = 'mexico')) AND (SELECT (SELECT place FROM w WHERE player = 'cristie kerr') = "t4")

CREATE TABLE w(
	row_id int,
	date text,
	opponent text,
	score text,
	loss text,
	time text,
	att int,
	record text)
/*
Title: 2003 chicago white sox season
3 example rows:
SELECT * FROM w LIMIT 3;
row_id	date	opponent	score	loss	time	att	record
0	august 1	mariners	12 - 1	garcía (9 - 11)	2:52	39337	58 - 51
1	august 2	mariners	0 - 10	wright (0 - 5)	2:22	45719	58 - 52
2	august 3	mariners	2 - 8	buehrle (9 - 11)	2:57	45632	58 - 53
*/
Q: the 2003 chicago white sox game play on 26th august be longer than the game play on 24th august
SQL: SELECT (SELECT time FROM w WHERE date = 'august 26') > (SELECT time FROM w WHERE date = 'august 24')

CREATE TABLE w(
	row_id int,
	place text,
	player text,
	country text,
	score text,
	to_par text,
	money text)
/*
Title: 1987 masters tournament
3 example rows:
SELECT * FROM w LIMIT 3;
row_id	place	player	country	score	to_par	money
0	t1	larry mize	united states	70 + 72 + 72 + 71 = 285	-3	playoff
1	t1	bernhard langer	spain	73 + 71 + 70 + 71 = 285	-3	playoff
2	t1	greg norman	australia	73 + 74 + 66 + 72 = 285	-3	playoff
*/
Q: bernhard m. langer have more point than roger maltbie during the 1987 master tournament
SQL: SELECT (SELECT score FROM w WHERE player = 'bernhard langer') > (SELECT score FROM w WHERE player = 'roger maltbie')

CREATE TABLE w(
	row_id int,
	rank int,
	name text,
	nation text,
	points float,
	places int)
/*
Title: 1976 world junior figure skating championships
3 example rows:
SELECT * FROM w LIMIT 3;
row_id	rank	name	nation	points	places
0	1	sherri baier / robin cowan	canada	128.39	9
1	2	lorene mitchell / donald mitchell	united states	124.94	16
2	3	elizabeth cain / peter cain	australia	116.67	33
*/
Q: 2 of the 7 top - ranked figure skate team be from france
SQL: SELECT (SELECT (SELECT COUNT(*) FROM w) = 7) AND (SELECT (SELECT COUNT(*) FROM w WHERE nation = 'france') = 2)"""

QUERY_NL2SQLER = """{create_table_text}
/*
Title: {title}
example rows:
SELECT * FROM w;
{table}
*/
Q: {question}
SQL: """

SELF_CORREC_INS_NL2SQLER = """{context}
Q: {question}
Last Error: {last_error}
SQL: {a}"""