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
	date text,
	team_a int,
	team_b int,
	place text)
/*
Title: 2007–08 NHL season
3 example rows:
SELECT * FROM w LIMIT 3;
date	team_a	team_b	place
2007-10-4	1	2	home
2008-1-1	1	3	home
2013-5-1	1	4	home
*/
Q: which game have the largest score difference?
NeuralSQL: ```SELECT `date` FROM w ORDER BY MAP("what is the score difference?"; `team_a`, `team_b`) DESC LIMIT 1```


CREATE TABLE w(
	row_id int,
	language text,
	number int,
	percentage (%) text,
	males text,
	females text)
/*
Title: Płock Governorate
3 example rows:
SELECT * FROM w LIMIT 3;
row_id	language	number	percentage (%)	males	females
0	polish	447685	80.86	216,794	230,891
1	yiddish	51215	9.25	24,538	26,677
2	german	35931	6.49	17,409	18,522
*/
Q: how many male and female german speakers are there?
NeuralSQL: ```SELECT SUM(CAST(`males` AS INT) + CAST(`females` AS INT)) FROM w WHERE `language` = 'german'```


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
NeuralSQL: ```SELECT member FROM w ORDER BY MAP("how long does it last?"; `term`) DESC LIMIT 1```"""

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


SELF_CORREC_INS_BINDER = """{context}
Q: {question}
Last Error: {last_error}
NeuralSQL: {a}"""