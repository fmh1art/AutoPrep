DEMO_BINDER = """Generate SQL given the statement and table to verify the statement correctly.
If statement-relevant column(s) contents are not suitable for SQL comparisons or calculations, map it to a new column with clean content by a new grammar MAP("").

CREATE TABLE w(
	row_id int,
	res text,
	record text,
	opponent text,
	method text,
	event text,
	round text)
/*
Title: jason chambers
3 example rows:
SELECT * FROM w LIMIT 3;
row_id	res	record	opponent	method	event	round
0	win	18 - 5 - 2	dan new	submission (rear naked choke)	tfc - power fights	1
1	win	17 - 5 - 2	rene gonzalez	decision (split)	mainstream mma - cold war	n / a
2	loss	16 - 5 - 2	tristan yunker	submission ( armbar )	tfc 7 - total fight challenge 7	1
*/
Q: in mac - midwest absolute challenge , the player be defeat by dan spychalski in 1 round
NeuralSQL: ```SELECT (SELECT opponent, round FROM w WHERE event = "mac - midwest absolute challenge")=("dan spychalski", 1)```


CREATE TABLE w(
	row_id int,
	home team text,
	home team score text,
	away team text,
	away team score text,
	venue text,
	crowd int,
	date text)
/*
Title: 1943 vfl season
3 example rows:
SELECT * FROM w LIMIT 3;
row_id	home team	home team score	away team	away team score	venue	crowd	date
0	footscray	10.11 (71)	south melbourne	6.14 (50)	western oval	7500	1943-06-26 00:00:00
1	collingwood	10.21 (81)	melbourne	13.9 (87)	victoria park	5000	1943-06-26 00:00:00
2	carlton	15.16 (106)	fitzroy	9.13 (67)	princes park	12000	1943-06-26 00:00:00
*/
Q: western oval be the venue when the home team footscray score 10.11 (71)
NeuralSQL: ```SELECT (SELECT venue FROM w WHERE `home team`="footscray" AND `home team score`="10.11 (71)") = "western oval"```


CREATE TABLE w(
	row_id int,
	pick int,
	player text,
	country of origin text,
	pba team text,
	college text)
/*
Title: 2005 pba draft
3 example rows:
SELECT * FROM w LIMIT 3;
row_id	pick	player	country of origin	pba team	college
0	1	jay washington	united states	air21 express	eckerd
1	2	alex cabagnot	united states	sta lucia realtors	hawaii - hilo
2	3	dennis miranda	philippines	coca - cola tigers	feu
*/
Q: leo najorda be from philippine
NeuralSQL: ```SELECT (SELECT `country of origin` FROM w WHERE player = "leo najorda")="philippines"```


CREATE TABLE w(
	row_id int,
	event text,
	long course / short course text,
	year set int,
	time text,
	meet text)
/*
Title: none
3 example rows:
SELECT * FROM w LIMIT 3;
row_id	event	long course / short course	year set	time	meet
0	100 m freestyle	long course	2007	54.08	2007 fina world aquatic championships
1	200 m individual medley	long course	2011	2:11.23	2011 canadian world championship trials
2	4 x 100 m medley relay	long course	2010	3:38.14	2010 pan pacific championships
*/
Q: in 2009 the record be set in 7:51:80
NeuralSQL: ```SELECT (SELECT  time FROM w WHERE `year set` = 2009)="7:51.8"```


CREATE TABLE w(
	row_id int,
	round text,
	clubs remaining int,
	clubs involved int,
	winners from previous round real,
	new entries this round real,
	leagues entering at this round text)
/*
Title: turkish cup
3 example rows:
SELECT * FROM w LIMIT 3;
row_id	round	clubs remaining	clubs involved	winners from previous round	new entries this round	leagues entering at this round
0	first round	156	86	nan	86.0	tff third league & turkish regional amateur league
1	second round	113	108	43.0	65.0	süper lig & tff first league & tff second league
2	third round	59	54	54.0	nan	none
*/
Q: during the 3rd round of the turkish cup , there be no new entry during that stage
NeuralSQL: ```SELECT (SELECT `new entries this round` FROM w WHERE round = 'third round') IS NULL```


CREATE TABLE w(
	row_id int,
	round text,
	clubs remaining int,
	clubs involved int,
	winners from previous round real,
	new entries this round real,
	leagues entering at this round text)
/*
Title: turkish cup
3 example rows:
SELECT * FROM w LIMIT 3;
row_id	round	clubs remaining	clubs involved	winners from previous round	new entries this round	leagues entering at this round
0	first round	156	86	nan	86.0	tff third league & turkish regional amateur league
1	second round	113	108	43.0	65.0	süper lig & tff first league & tff second league
2	third round	59	54	54.0	nan	none
*/
Q: the lowest number of new entry conclude a round in the turkish cup be 5
NeuralSQL: ```SELECT (SELECT MIN(`new entries this round`) FROM w) = 5```


CREATE TABLE w(
	row_id int,
	letters text,
	organization text,
	nickname text,
	founding time text,
	founding university text,
	type text)
/*
Title: cultural interest fraternities and sororities
3 example rows:
SELECT * FROM w LIMIT 3;
row_id	letters	organization	nickname	founding time	founding university	type
0	αεπ	alpha epsilon pi 1	aepi	1913-11-07 00:00:00	new york university	fraternity
1	αεφ	alpha epsilon phi 2	aephi	1909-10-24 00:00:00	barnard college	sorority
2	σαεπ	sigma alpha epsilon pi 3	sigma	1998-10-01 00:00:00	university of california , davis	sorority
*/
Q: 4 of the cultural interest fraternity and sorority be fraternity while 3 be a sorority
NeuralSQL: ```SELECT (SELECT (SELECT COUNT(*) FROM w WHERE type = 'fraternity') = 4) AND (SELECT (SELECT COUNT(*) FROM w WHERE type = 'sorority') = 3)```


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
0	5 km	t19:29	andi drake	1990-05-27 00:00:00	søfteland , norway
1	5 miles	32:38 +	ian mccombie	1985-03-23 00:00:00	york , united kingdom
2	10 km	40:17	chris maddocks	1989-04-30 00:00:00	burrator , united kingdom
*/
Q: there be 8 different event that take place within the united kingdom
NeuralSQL: ```SELECT (SELECT COUNT(place) FROM w WHERE MAP("is it in united kingdom?"; place) = 'yes') = 8```


CREATE TABLE w(
	row_id int,
	tournament text,
	wins int,
	top - 10 int,
	top - 25 int,
	events int,
	cuts made int)
/*
Title: jeev milkha singh
3 example rows:
SELECT * FROM w LIMIT 3;
row_id	tournament	wins	top - 10	top - 25	events	cuts made
0	masters tournament	0	0	1	3	2
1	us open	0	0	0	4	3
2	the open championship	0	0	0	2	1
*/
Q: the number of cut made in the pga championship tournament be smaller than the number of event
NeuralSQL: ```SELECT (SELECT `cuts made` FROM w WHERE tournament = 'pga championship') < (SELECT events FROM w WHERE tournament = 'pga championship')```


CREATE TABLE w(
	row_id int,
	date text,
	visiting team text,
	final score text,
	host team text,
	stadium text)
/*
Title: espn sunday night football results (1987 - 2005)
3 example rows:
SELECT * FROM w LIMIT 3;
row_id	date	visiting team	final score	host team	stadium
0	september 11	indianapolis colts	24 - 7	baltimore ravens	m&t bank stadium
1	september 18	kansas city chiefs	23 - 17	oakland raiders	mcafee coliseum
2	september 25	new york giants	23 - 45	san diego chargers	qualcomm stadium
*/
Q: the hosting team be the new york giant on new year even and the st louis ram on new year 's day
NeuralSQL: ```SELECT (SELECT (SELECT `host team` FROM w WHERE MAP("is it new year even?"; date) = 'yes') = 'new york giant') AND (SELECT (SELECT `host team` FROM w WHERE MAP("is it new year's day?"; date) = 'yes') = 'st louis ram')```


CREATE TABLE w(
	row_id int,
	place text,
	player text,
	country text,
	score text,
	to par int)
/*
Title: 2008 women 's british open
3 example rows:
SELECT * FROM w LIMIT 3;
row_id	place	player	country	score	to par
0	t1	yuri fudoh	japan	66 + 68 = 134	10
1	t1	jiyai shin	south korea	66 + 68 = 134	10
2	3	juli inkster	united states	65 + 70 = 135	9
*/
Q: kristie kerr , tie for 4th place , finish the round 1 stroke under lorena ochoa of mexico
NeuralSQL: ```SELECT (SELECT (SELECT MAP("what is the derived score?"; score) FROM w WHERE player = 'cristie kerr') < (SELECT MAP("what is the derived score?"; score) FROM w WHERE player = 'lorena ochoa' AND country = 'mexico')) AND (SELECT (SELECT place FROM w WHERE player = 'cristie kerr') = "t4")```


CREATE TABLE w(
	row_id int,
	call sign text,
	frequency text,
	city of license text,
	facility id int,
	erp / power w int,
	height m ( ft ) real,
	class text)
/*
Title: connecticut public radio
3 example rows:
SELECT * FROM w LIMIT 3;
row_id	call sign	frequency	city of license	facility id	erp / power w	height m ( ft )	class
0	waic	91.9 fm	springfield , ma	1749	230	nan	b1
1	wedw - fm	88.5 fm	stamford , ct	13619	2000	nan	a
2	wnpr	90.5 fm ( hd ) connecticut public radio	meriden , ct	13627	18500	nan	b
*/
Q: there be 3 station with a call sign number in the 90s
NeuralSQL: ```SELECT (SELECT COUNT(*) FROM w WHERE MAP("is it in 90s?"; frequency) = 'yes' GROUP BY `call sign`) = 3```


CREATE TABLE w(
	row_id int,
	place text,
	player text,
	country text,
	score text,
	to par text,
	money text)
/*
Title: 1987 masters tournament
3 example rows:
SELECT * FROM w LIMIT 3;
row_id	place	player	country	score	to par	money
0	t1	larry mize	united states	70 + 72 + 72 + 71 = 285	-3	playoff
1	t1	bernhard langer	spain	73 + 71 + 70 + 71 = 285	-3	playoff
2	t1	greg norman	australia	73 + 74 + 66 + 72 = 285	-3	playoff
*/
Q: bernhard m. langer have more point than roger maltbie during the 1987 master tournament
NeuralSQL: ```SELECT (SELECT MAP("what is the total score?"; score) FROM w WHERE player = 'bernhard langer') > (SELECT MAP("what is the total score?"; score) FROM w WHERE player = 'roger maltbie')```


CREATE TABLE w(
	row_id int,
	rank int,
	name text,
	nation text,
	points real,
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
NeuralSQL: ```SELECT (SELECT (SELECT COUNT(*) FROM w) = 7) AND (SELECT (SELECT COUNT(*) FROM w WHERE nation = 'france') = 2)```"""

QUERY_BINDER = """{create_table_text}
/*
Title: {title}
example rows:
SELECT * FROM w;
{table}
*/
Q: {question}
Output ```your_NeuralSQL_here``` with no other texts.
NeuralSQL:"""