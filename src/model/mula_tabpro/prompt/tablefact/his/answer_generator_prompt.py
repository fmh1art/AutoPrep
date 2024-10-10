DEMO_ANSWER_GENERATOR = """Please answer the Statement based on the TABLE.

If the answer is a string or a number, just output it.
If the answer is a list, output all elements separated with '|'.

For example,

/*
row number | opponent | result | hurricanes points | opponents
---|---|---|---|---
1 | colorado | win | 24 | 3
2 | louisiana state | loss | 8 | 10
3 | florida state | loss | 20 | 23
4 | georgia | win | 7 | 6
*/
Statement: the hurricane win less than 10 point against louisiana and georgia
Answer: ```true```
Explanation: The game with florida lost by 3 points, and the game with georgia won by 1 point, both less than 10 points.

/*
row number | league | year
---|---|---
1 | usl a-league | 2001
2 | usl a-league | 2002
3 | usl first division | 2005
*/
Statement: usl a-league and usl first division both exist in 2005
Answer: ```false```
Explanation: The usl a-league exists in 2001 and 2002, while the usl first division exists in 2005.

/*
row number | player | from | rebs
1 | kurt rambis | 1989 | 783
2 | michael redd | 2011 | 77
3 | terrence rencher | 1995 | 62
4 | joe reaves | 1973 | 8
*/
Statement: terrence rancher have the most amount of rebound in 1995
Answer: ```false```
Explanation: kur rambis has the most amount of rebound in 1989.

/*
row number | Country | Athelete_count
---|---|---
1 | USA | 3
2 | ARG | 2
3 | IND | 1
*/
Statement: america has the most athletes
Answer: ```true```
Explanation: America has 3 athletes, while Argentina has 2 athletes and India has 1 athlete.

/*
row number | league | year
---|---|---
1 | usl a-league | 2004
2 | usl a-league | 2002
3 | usl a-league | 2005
*/
Statement: 2005 is the last year where this team was a part of the usl a-league
Answer: ```true```"""

QUERY_ANSWER_GENERATOR = """Please complete the prompt below,
/*
{cot_tbl}
*/
Statement: {question}
Please answer true or false about the statement based on the table. Output ```true_or_false``` without NO EXTRA text.
Answer:"""