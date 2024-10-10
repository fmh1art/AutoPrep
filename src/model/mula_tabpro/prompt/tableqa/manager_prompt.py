DEMO_MANAGER = """You are a agent to generate data preparation for table question tasks. Given a table along with its title and a question, please generate data preparation requirements from three aspects: (1) related_columns, (2) column_augmentation, (3) column_normalization.

Title: Fabrice Santoro
/*
row_id	name	2001	2002	2003	2004	2005	2006	2007	2008	2009	2010	career\nsr	career\nwin-loss
0	australian open	2r	1r	3r	2r	1r	qf	3r	2r	3r	1r	0 / 18	22-18
1	french open	4r	2r	2r	3r	1r	1r	1r	2r	1r	a	0 / 20	17-20
2	wimbledon	3r	2r	2r	2r	2r	2r	2r	1r	2r	a	0 / 14	11-14
*/
Q: did he win more at the australian open or indian wells?
Requirements: ```{{(1) related columns: name, career\nwin-loss; (2) generate a column about the wins from the column career\nwin-loss; (3) None;}}```


Title: Portugal in the Eurovision Song Contest 1979
/*
row_id	draw	artist	song	points	place
0	1	gonzaga coutinho	"tema para um homem só"	102	5th
1	2	pedro osório s.a.r.l.	"uma canção comercial"	123	3rd
2	3	concha	"qualquer dia, quem diria"	78	6th
*/
Q: who was the last draw?
Requirements: ```{{(1) related columns: draw, artist; (2) None; (3) please normalize the column draw to int format;}}```


Title: 2007 New Orleans Saints season
/*
row_id	week	date	opponent	time	game site	tv	result/score	record
0	1	2007-9-6	indianapolis colts	t20:30 edt	rca dome	nbc	l 41 - 10	0-1
1	2	2007-9-16	tampa bay buccaneers	t13:0 edt	raymond james stadium	fox	l 31 - 14	0-2
2	3	2007-9-24	tennessee titans	t20:30 edt	louisiana superdome	espn	l 31 - 14	0-3
*/
Q: what number of games were lost at home?
Requirements: ```{{(1) related columns: game site, result/score; (2) generate a column about the loss from the column result/score; generate a column describing whether it is the home court of New Orleans Saints; (3) please normalize the column result/score to int format;}}```


Title: 2007-08 NHL season
/*
date	team_a	team_b	place
2007-10-4	1	2	home
2008-1-1	1	3	home
2013-5-1	1	4	home
*/
Q: which game have the largest score difference?
Requirements: ```{{(1) related columns: team_a, team_b; (2) generate a column about the score difference from the columns team_a, team_b; (3) please normalize the columns team_a to int format; please normalize the columns team_b to int format;}}```


Title: Płock Governorate
/*
row_id	language	number	percentage (%)	males	females
0	polish	447685	80.86	216,794	230,891
1	yiddish	51215	9.25	24,538	26,677
2	german	35931	6.49	17,409	18,522
*/
Q: how many male and female german speakers are there?
Requirements: ```{{(1) related columns: males, females; (2) None. (3) please normalize the column males to int format; please normalize the column females to int format;


Title: Electoral district of Lachlan
/*
row_id	member	party	term
0	john ryan	none	1859-1864
1	james martin	none	1864-1869
2	james watson	none	1869-1880
*/
Q: of the members of the third incarnation of the lachlan, who served the longest?
Requirements: ```{{(1) related columns: term; (2) generate a column about the duration from the column term; (3) None;}}```"""

QUERY_MANAGER = """Please complete the prompt following the format above.
Title: {title}
/*
{table}
*/
Q: {question}
Output ```generated_requirements``` with no other texts.
Requirements:"""


SELF_CORREC_INS_MANAGER = """{context}
Q: {question}
Last Error: {last_error}
Requirements: {a}"""