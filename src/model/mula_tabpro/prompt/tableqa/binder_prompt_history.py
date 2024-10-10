DEMO_BINDER = """Generate SQL given the question and table to answer the question correctly.
If question-relevant column(s) contents are not suitable for SQL comparisons or calculations, map it to a new column with clean content by a new grammar MAP("").

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
	career\nsr text,
	career\nwin-loss text)
/*
Title: Fabrice Santoro
3 example rows:
SELECT * FROM w LIMIT 3;
row_id	name	2001	2002	2003	2004	2005	2006	2007	2008	2009	2010	career\nsr	career\nwin-loss
0	australian open	2r	1r	3r	2r	1r	qf	3r	2r	3r	1r	0 / 18	22-18
1	french open	4r	2r	2r	3r	1r	1r	1r	2r	1r	a	0 / 20	17-20
2	wimbledon	3r	2r	2r	2r	2r	2r	2r	1r	2r	a	0 / 14	11-14
*/
Q: did he win more at the australian open or indian wells?
NeuralSQL: ```SELECT name FROM w WHERE name IN ('australian open', 'indian wells') ORDER BY MAP("how many wins?"; `career\nwin-loss`) DESC LIMIT 1```


CREATE TABLE w(
	row_id int,
	week int,
	date text,
	opponent text,
	time text,
	game site text,
	tv text,
	result/score text,
	record text)
/*
Title: 2007 New Orleans Saints season
3 example rows:
SELECT * FROM w LIMIT 3;
row_id	week	date	opponent	time	game site	tv	result/score	record
0	1	2007-9-6	indianapolis colts	t20:30 edt	away	nbc	loss	0-1
1	2	2007-9-16	tampa bay buccaneers	t13:0 edt	home	fox	win	1-1
2	3	2007-9-24	tennessee titans	t20:30 edt	away	espn	loss	1-2
*/
Q: what number of games were lost at home?
NeuralSQL: ```SELECT COUNT(*) FROM w WHERE `result/score` = 'loss' AND `game site` = 'home'```


CREATE TABLE w(
	row_id int,
	rank int,
	mountain peak text,
	mountain range text,
	elevation text,
	prominence text,
	isolation text,
	location text)
/*
Title: Highest mountain peaks of California
3 example rows:
SELECT * FROM w LIMIT 3;
row_id	rank	mountain peak	mountain range	elevation	prominence	isolation	location
0	1	mount whitney	sierra nevada	14505 ft; 4421 m	10080 ft; 3072 m	1646 mi; 2649 km	36°34′43″n 118°17′31″w﻿ / ﻿36.5786°n 118.292°w
1	2	mount williamson	sierra nevada	14379 ft; 4383 m	1677 ft; 511 m	5.4 mi; 8.7 km	36°39′21″n 118°18′40″w﻿ / ﻿36.6559°n 118.3111°w
2	3	white mountain peak	white mountains	14252 ft; 4344 m	7196 ft; 2193 m	67 mi; 109 km	37°38′3″n 118°15′21″w﻿ / ﻿37.6341°n 118.2557°w
*/
Q: which mountain peak has a prominence more than 10,000 ft?
NeuralSQL: ```SELECT `mountain peak` FROM w WHERE MAP("prominence in ft?"; prominence) > 10000```


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
NeuralSQL: ```SELECT CASE WHEN (SELECT `2010` FROM w WHERE filledcolumnname = 'hydro power') < (SELECT `2012` FROM w WHERE filledcolumnname = 'hydro power') THEN 'increase' ELSE 'decrease' END```


CREATE TABLE w(
	row_id int,
	party text,
	diet representation\nrepresentatives int,
	diet representation\ncouncillors int,
	party leader(s) text,
	comments text)
/*
Title: List of political parties in Japan
3 example rows:
SELECT * FROM w LIMIT 3;
row_id	party	diet representation\nrepresentatives	diet representation\ncouncillors	party leader(s)	comments
0	your party (yp); minna no tō みんなの党; ("everybody's party")	18	18	yoshimi watanabe reps.	conservative liberalism, neoliberalism, economic liberalism, libertarianism, anti-nuclear
1	japanese communist party (jcp); nihon kyōsan-tō 日本共産党	8	11	kazuo shii reps.	the japanese communist party is japan's oldest party. it was formed in 1922 as an underground organization in the empire of japan, but was legalized after world war ii during the occupation. it used to be a communist party, but the party has past_ref shifted to a socialist party.
2	people's life party (plp); seikatsu no tō 生活の党	7	2	ichirō ozawa reps.	life party was founded by ichirō ozawa and 14 other diet members who were in the 2022-7-4 party of japan after a leadership dispute between ozawa and yukiko kada.
*/
Q: what party is listed previous to the new renaissance party?
NeuralSQL: ```SELECT MAP("what is party name?"; party) FROM w WHERE row_id = (SELECT row_id FRO0M w WHERE MAP("what is party name?"; party) = 'new renaissance party') - 1```


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
NeuralSQL: ```SELECT `artist` FROM w ORDER by `draw` desc LIMIT 1```


CREATE TABLE w(
	row_id int,
	week int,
	date text,
	opponent text,
	time text,
	game site text,
	tv text,
	result/score text,
	record text)
/*
Title: 2007 New Orleans Saints season
3 example rows:
SELECT * FROM w LIMIT 3;
row_id	week	date	opponent	time	game site	tv	result/score	record
0	1	2007-9-6	indianapolis colts	t20:30 edt	rca dome	nbc	l 41 - 10	0-1
1	2	2007-9-16	tampa bay buccaneers	t13:0 edt	raymond james stadium	fox	l 31 - 14	0-2
2	3	2007-9-24	tennessee titans	t20:30 edt	louisiana superdome	espn	l 31 - 14	0-3
*/
Q: what number of games were lost at home?
NeuralSQL: ```SELECT COUNT(*) FROM w WHERE MAP("is it a loss?"; `result/score`) = 'yes' AND MAP("is it the home court of New Orleans Saints?"; `game site`) = 'yes'```


CREATE TABLE w(
	row_id int,
	language text,
	number int,
	percentage (%) text,
	males int,
	females int)
/*
Title: Płock Governorate
3 example rows:
SELECT * FROM w LIMIT 3;
row_id	language	number	percentage (%)	males	females
0	polish	447685	80.86	216794	230891
1	yiddish	51215	9.25	24538	26677
2	german	35931	6.49	17409	18522
*/
Q: how many male and female german speakers are there?
NeuralSQL: ```SELECT `males` + `females` FROM w WHERE `language` = 'german'```


CREATE TABLE w(
	row_id int,
	member text,
	party text,
	term text)
/*
Title: Electoral district of Lachlan
3 example rows:
SELECT * FROM w LIMIT 3;
row_id	member	party	term
0	john ryan	none	1859-1864
1	james martin	none	1864-1869
2	james watson	none	1869-1880
*/
Q: of the members of the third incarnation of the lachlan, who served the longest?
NeuralSQL: ```SELECT member FROM w ORDER BY MAP("how long does it last?"; term) DESC LIMIT 1```"""

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