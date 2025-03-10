DEMO_NL2SQLER = """Generate SQL given the question and table to answer the question correctly.

CREATE TABLE w(
	row_id int,
	name text,
	2001 text,
	2002 text,
	2003 text,
	2004 text,
	2005 text,
	2006 text,
	2007 text,
	2008 text,
	2009 text,
	2010 text,
	career_sr text,
	wins int)
/*
Title: Fabrice Santoro
3 example rows:
SELECT * FROM w LIMIT 3;
row_id	name	2001	2002	2003	2004	2005	2006	2007	2008	2009	2010	career_sr	wins
0	australian open	2r	1r	3r	2r	1r	qf	3r	2r	3r	1r	0 / 18	22
1	french open	4r	2r	2r	3r	1r	1r	1r	2r	1r	a	0 / 20	17
2	wimbledon	3r	2r	2r	2r	2r	2r	2r	1r	2r	a	0 / 14	11
*/
Q: did he win more at the australian open or indian wells?
SQL: SELECT name FROM w WHERE name IN ('australian open', 'indian wells') ORDER BY wins DESC LIMIT 1


CREATE TABLE w(
	row_id int,
	week int,
	date text,
	opponent text,
	time text,
	game_site text,
	tv text,
	result text,
	record text)
/*
Title: 2007 New Orleans Saints season
3 example rows:
SELECT * FROM w LIMIT 3;
row_id	week	date	opponent	time	game_site	tv	result	record
0	1	2007-9-6	indianapolis colts	t20:30 edt	rca dome	nbc	l	0-1
1	2	2007-9-16	tampa bay buccaneers	t13:0 edt	raymond james stadium	fox	l	0-2
2	3	2007-9-24	tennessee titans	t20:30 edt	louisiana superdome	espn	l	0-3
*/
Q: what number of games were lost at home?
SQL: SELECT COUNT(*) FROM w WHERE result = 'l' AND `game_site` = 'louisiana superdome'


CREATE TABLE w(
	row_id int,
	week int,
	date text,
	opponent text,
	time text,
	game_site text,
	tv text,
	result_score text,
	record text)
/*
Title: 2007 New Orleans Saints season
3 example rows:
SELECT * FROM w LIMIT 3;
row_id	week	date	opponent	time	game_site	tv	result_score	record
0	1	2007-9-6	indianapolis colts	t20:30 edt	away	nbc	loss	0-1
1	2	2007-9-16	tampa bay buccaneers	t13:0 edt	home	fox	win	1-1
2	3	2007-9-24	tennessee titans	t20:30 edt	away	espn	loss	1-2
*/
Q: what number of games were lost at home?
SQL: SELECT COUNT(*) FROM w WHERE `result_score` = 'loss' AND `game_site` = 'home'


CREATE TABLE w(
	row_id int,
	filledcolumnname text,
	2005 int,
	2006 int,
	2007 int,
	2008 int,
	2009 int,
	2010 int,
	2011 int,
	2012 int)
/*
Title: Electricity in Sri Lanka
3 example rows:
SELECT * FROM w LIMIT 3;
row_id	filledcolumnname	2005	2006	2007	2008	2009	2010	2011	2012
0	hydro power	1293	1316	1326	1357	1379	1382	1401	1584
1	thermal	1155	1155	1155	1285	1290	1390	1690	1638
2	other renewables	3	3	3	3	15	45	50	90
*/
Q: did the hydro power increase or decrease from 2010 to 2012?
SQL: SELECT CASE WHEN (SELECT `2010` FROM w WHERE filledcolumnname = 'hydro power') < (SELECT `2012` FROM w WHERE filledcolumnname = 'hydro power') THEN 'increase' ELSE 'decrease' END


CREATE TABLE w(
	row_id int,
	draw int,
	artist text,
	song text,
	points int,
	place text)
/*
Title: Portugal in the Eurovision Song Contest 1979
3 example rows:
SELECT * FROM w LIMIT 3;
row_id	draw	artist	song	points	place
0	1	gonzaga coutinho	"tema para um homem só"	102	5th
1	2	pedro osório s.a.r.l.	"uma canção comercial"	123	3rd
2	3	concha	"qualquer dia, quem diria"	78	6th
*/
Q: who was the last draw?
SQL: SELECT `artist` FROM w ORDER by `draw` desc LIMIT 1


CREATE TABLE w(
	row_id int,
	year int,
	order text,
	quantity int,
	ger_nos text)
/*
Title: GER Class N31
3 example rows:
SELECT * FROM w LIMIT 3;
row_id	year	order	quantity	ger_nos
0	1893	n31	1	999
1	1893	h33	10	979
2	1894	l33	10	989
*/
Q: which had more ger numbers, 1898 or 1893?
SQL: SELECT `year` FROM w WHERE `year` IN ( '1898' , '1893' ) GROUP by `year` ORDER by SUM (`ger_nos`) desc LIMIT 1


CREATE TABLE w(
	row_id int,
	tramway text,
	country text,
	city text,
	height_of_pylons text,
	span_width_leaning_straight_line text,
	span_width_horizontal_measurement text,
	height_of_cable_over_ground text,
	year_of_inauguration text,
	notes text)
/*
Title: List of spans
3 example rows:
SELECT * FROM w LIMIT 3;
row_id	tramway	country	city	height_of_pylons	span_width_leaning_straight_line	span_width_horizontal_measurement	height_of_cable_over_ground	year_of_inauguration	notes
0	peak 2 peak gondola	canada	whistler	65m	3024 m	3019 m	436 m	2008	3s aerial tramway constructed by doppelmayr
1	hut of regensburg material transport aerial railway	austria	falbeson	?	?	?	430 m	?	none
2	vanoise express	france	vanoise	none	1850 m	1800 m	380 m	2003	none
*/
Q: was the sandia peak tramway innagurate before or after the 3s aerial tramway?
SQL: SELECT ( SELECT `year_of_inauguration` FROM w WHERE `tramway` = 'sandia peak tramway' ) < ( SELECT `year_of_inauguration` FROM w WHERE `tramway` = '3s aerial tramway' )


CREATE TABLE w(
	id int,
	year int,
	location text,
	gold text,
	silver text,
	bronze text)
/*
Title: World Artistic Gymnastics Championships - Women's floor
3 example rows:
SELECT * FROM w LIMIT 3;
id	year	location	gold	silver	bronze
0	1950	basel	helena rakoczy	tereza kočiš	stefania reindlova
1	1954	rome	tamara manina	eva bosáková	maria gorokovskaya
2	1958	moscow	eva bosáková	larisa latynina	keiko tanaka
*/
Q: where were the championships held before the 1962 prague championships?
SQL: SELECT `location` FROM w WHERE `year` < 1962 ORDER by `year` desc LIMIT 1


CREATE TABLE w(
	id int,
	wrestler text,
	times text,
	date text,
	location text,
	notes text)
/*
Title: WSL World Heavyweight Championship
3 example rows:
SELECT * FROM w LIMIT 3;
id	wrestler	times	date	location	notes
0	jonnie stewart	1	1996-6-6	rochester, minnesota	defeated larry gligorovich to win the awa superstars of wrestling world heavyweight championship.
1	king kong bundy	1	1999-3-31	oshkosh, wisconsin	later stripped of the title by owner dale gagne.
2	the patriot; (danny dominion)	1	2000-7-29	pine bluff, arkansas	defeated dale gagne in an impromptu match to win the title.
*/
Q: when did steve corino win his first wsl title?
SQL: SELECT `date` FROM w WHERE `wrestler` = 'steve corino' ORDER by `date` LIMIT 1


CREATE TABLE w(
	row_id int,
	language text,
	number int,
	percentage text,
	males int,
	females int)
/*
Title: Płock Governorate
3 example rows:
SELECT * FROM w LIMIT 3;
row_id	language	number	percentage	males	females
0	polish	447685	80.86	216794	230891
1	yiddish	51215	9.25	24538	26677
2	german	35931	6.49	17409	18522
*/
Q: how many male and female german speakers are there?
SQL: SELECT `males` + `females` FROM w WHERE `language` = 'german'


CREATE TABLE w(
	row_id int,
	no int,
	temple text,
	honzon_main_image text,
	city_town_village text,
	prefecture text)
/*
Title: Shikoku Pilgrimage
3 example rows:
SELECT * FROM w LIMIT 3;
row_id	no	temple	honzon_main_image	city_town_village	prefecture
0	1	ryōzen-ji (霊山寺)	shaka nyorai	naruto	tokushima prefecture
1	2	gokuraku-ji (極楽寺)	amida nyorai	naruto	tokushima prefecture
2	3	konsen-ji (金泉寺)	shaka nyorai	itano	tokushima prefecture
*/
Q: what is the difference in the number of temples between imabari and matsuyama?
SQL: SELECT abs ( ( SELECT COUNT ( `temple` ) FROM w WHERE `city_town_village` = 'imabari' ) - ( SELECT COUNT ( `temple` ) FROM w WHERE `city_town_village` = 'matsuyama' ) )


CREATE TABLE w(
	row_id int,
	rank real,
	name text,
	nationality text,
	time text)
/*
Title: Athletics at the 2001 Goodwill Games - Results
3 example rows:
SELECT * FROM w LIMIT 3;
row_id	rank	name	nationality	time
0	nan	brahim boulami	morocco	2022-07-17 08:17:43
1	nan	reuben kosgei	kenya	2022-07-17 08:18:37
2	nan	stephen cherono	kenya	2022-07-17 08:19:58
*/
Q: what counties had the least participants for the race?
SQL: SELECT `nationality` FROM w GROUP by `nationality` having COUNT ( `name` ) = ( SELECT COUNT ( `name` ) FROM w GROUP by `nationality` ORDER by COUNT ( `name` ) asc LIMIT 1 )

CREATE TABLE w(
	row_id int,
	administrative_area text,
	area_km2 real,
	area_sq_mi int,
	population int,
	administrative_centre text)
/*
Title: Saint Helena, Ascension and Tristan da Cunha
3 example rows:
SELECT * FROM w LIMIT 3;
row_id	administrative_area	area_km2	area_sq_mi	population	administrative_centre
0	saint helena	122.0	47	5809	jamestown
1	ascension island	91.0	35	1532	georgetown
2	tristan da cunha	184.0	71	388	edinburgh of the 7 seas
*/
Q: is the are of saint helena more than that of nightingale island?
SQL: SELECT ( SELECT `area_km2` FROM w WHERE `administrative_area` = 'saint helena' ) > ( SELECT `area_km2` FROM w WHERE `administrative_area` = 'nightingale island' )


CREATE TABLE w(
	row_id int,
	number int,
	title text,
	tpb_isbn text,
	tpb_release_date text,
	tpb_page_number int,
	collected_material text)
/*
Title: The Boys (comics)
3 example rows:
SELECT * FROM w LIMIT 3;
row_id	number	title	tpb_isbn	tpb_release_date	tpb_page_number	collected_material
0	1	the name of the game	isbn 91-33-30546-3	2007-06-01 00:00:00	152	the boys #1-6
1	2	get some	isbn 1-933305-68-1	2008-03-01 00:00:00	192	the boys #7-14
2	3	good for the soul	isbn 1-933305-92-4	2008-10-01 00:00:00	192	the boys #15-22
*/
Q: what title appears before "the self-preservation society"?
SQL: SELECT `title` FROM w WHERE row_id = ( SELECT row_id FROM w WHERE `title` = 'the self-preservation society' ) - 1"""

QUERY_NL2SQLER = """{create_table_text}
/*
Title: {title}
example rows:
SELECT * FROM w;
{table}
*/
Q: {question}
SQL:"""

SELF_CORREC_INS_NL2SQLER = """{context}
Q: {question}
Last Error: {last_error}
SQL: {a}"""