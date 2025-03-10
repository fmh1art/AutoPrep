DEMO_NL2SQLER = """A database table is shown as follows:
/*
row number | Year | Division | League | Regular Season | Playoffs | Open Cup | Avg. Attendance
---|---|---|---|---|---|---|---
1 | 2001 | 2 | USL A-League | 4th, Western | Quarterfinals | Did not qualify | 7,169
2 | 2002 | 2 | USL A-League | 2nd, Pacific | 1st Round | Did not qualify | 6,260
3 | 2003 | 2 | USL A-League | 3rd, Pacific | Did not qualify | Did not qualify | 5,871
4 | 2004 | 2 | USL A-League | 1st, Western | Quarterfinals | 4th Round | 5,628
5 | 2005 | 2 | USL First Division | 5th | Quarterfinals | 4th Round | 6,028
6 | 2006 | 2 | USL First Division | 11th | Did not qualify | 3rd Round | 5,575
7 | 2007 | 2 | USL First Division | 2nd | Semifinals | 2nd Round | 6,851
8 | 2008 | 2 | USL First Division | 11th | Did not qualify | 1st Round | 8,567
9 | 2009 | 2 | USL First Division | 1st | Semifinals | 3rd Round | 9,734
10 | 010 | 2 | USSF D-2 Pro League | 3rd, USL (3rd) | Quarterfinals | 3rd Round | 10,727
*/
Answer the following question with SQL based on the data above: "what was the last year where this team was a part of the usl a-league?"

Therefore, the semantically and syntactically correct SQL query that answers the question is:```SELECT `Year` FROM df WHERE `League` = "USL A-League" ORDER BY `Year` DESC LIMIT 1;```
----------------------------------------------------------------------
A database table is shown as follows:
/*
row number | Year | Competition | Venue | Position | Event | Notes
---|---|---|---|---|---|---
1 | 2001 | World Youth Championships | Debrecen, Hungary | 2nd | 400 m | 47.12
2 | 2001 | World Youth Championships | Debrecen, Hungary | 1st | Medley relay | 1:50.46
3 | 2001 | European Junior Championships | Grosseto, Italy | 1st | 4x400 m relay | 3:06.12
4 | 2003 | European Junior Championships | Tampere, Finland | 3rd | 400 m | 46.69
5 | 2003 | European Junior Championships | Tampere, Finland | 2nd | 4x400 m relay | 3:08.62
6 | 2005 | European U23 Championships | Erfurt, Germany | 11th (sf) | 400 m | 46.62
7 | 2005 | European U23 Championships | Erfurt, Germany | 1st | 4x400 m relay | 3:04.41
8 | 2005 | Universiade | Izmir, Turkey | 7th | 400 m | 46.89
9 | 2005 | Universiade | Izmir, Turkey | 1st | 4x400 m relay | 3:02.57
10 | 2006 | World Indoor Championships | Moscow, Russia | 2nd (h) | 4x400 m relay | 3:06.10
11 | 2006 | European Championships | Gothenburg, Sweden | 3rd | 4x400 m relay | 3:01.73
12 | 2007 | European Indoor Championships | Birmingham, United Kingdom | 3rd | 4x400 m relay | 3:08.14
13 | 2007 | Universiade | Bangkok, Thailand | 7th | 400 m | 46.85
14 | 2007 | Universiade | Bangkok, Thailand | 1st | 4x400 m relay | 3:02.05
15 | 2008 | World Indoor Championships | Valencia, Spain | 4th | 4x400 m relay | 3:08.76
16 | 2008 | Olympic Games | Beijing, China | 7th | 4x400 m relay | 3:00.32
17 | 2009 | Universiade | Belgrade, Serbia | 2nd | 4x400 m relay | 3:05.69
*/
Answer the following question with SQL based on the data above: "in what city did piotr's last 1st place finish occur?"

Therefore, the semantically and syntactically correct SQL query that answers the question is:```SELECT `Venue` FROM df WHERE `Position`="1st" ORDER BY `Year` DESC LIMIT 1;```
----------------------------------------------------------------------
A database table is shown as follows:
/*
row number | Team | County | Wins | Years_won
---|---|---|---|---
1 | Greystones | Wicklow | 1 | 2011
2 | Ballymore Eustace | Kildare | 1 | 2010
3 | Maynooth | Kildare | 1 | 2009
4 | Ballyroan Abbey | Laois | 1 | 2008
5 |   | Dublin | 1 | 2007
6 | Confey | Kildare | 1 | 2006
7 | Crettyard | Laois | 1 | 2005
8 | Wolfe Tones | Meath | 1 | 2004
9 | Dundalk Gaels | Louth | 1 | 2003
*/
Answer the following question with SQL based on the data above: "which team won previous to crettyard?"

Therefore, the semantically and syntactically correct SQL query that answers the question is:```SELECT `Team` FROM df WHERE `Years_won` < (SELECT `Years_won` FROM df WHERE `Team`="Crettyard") ORDER BY `Years_won` DESC LIMIT 1;```
----------------------------------------------------------------------
A database table is shown as follows:
/*
row number | Rank | City | Passengers | Ranking | Airline
---|---|---|---|---|---
1 | 1 | United States, Los Angeles | 14,749 |  | Alaska Airlines
2 | 2 | United States, Houston | 5,465 |  | United Express
3 | 3 | Canada, Calgary | 3,761 |  | Air Transat, WestJet
4 | 4 | Canada, Saskatoon | 2,282 | 4 | 
5 | 5 | Canada, Vancouver | 2,103 |  | Air Transat
6 | 6 | United States, Phoenix | 1,829 | 1 | US Airways
7 | 7 | Canada, Toronto | 1,202 | 1 | Air Transat, CanJet
8 | 8 | Canada, Edmonton | 110 |  | 
9 | 9 | United States, Oakland | 107 |  | 
*/
Answer the following question with SQL based on the data above: "how many more passengers flew to los angeles than to saskatoon from manzanillo airport in 2013?" 

Therefore, the semantically and syntactically correct SQL query that answers the question is:```SELECT (SELECT `Passengers` WHERE `City` = "United States, Los Angeles") - (SELECT `Passengers` WHERE `City` = "Canada, Saskatoon");```
"""

QUERY_NL2SQLER = """Please complete the prompt below,
A database table is shown as follows:
/*
{cot_tbl}
*/
Answer the following question with SQL based on the data above: "{question}"

Therefore, the semantically and syntactically correct SQL query that answers the question is:"""