DEMO_END2ENDER = """Please deduce whether the statement is true or false based on the table.

/*
row number | opponent | result | hurricanes points | opponents
---|---|---|---|---
1 | colorado | win | 24 | 3
2 | louisiana state | loss | 8 | 10
3 | florida state | loss | 20 | 23
4 | georgia | win | 7 | 6
*/
Statement: the hurricane win less than 10 point against louisiana and georgia
The answer is: true.

/*
row number | league | year
---|---|---
1 | usl a-league | 2001
2 | usl a-league | 2002
3 | usl first division | 2005
*/
Statement: usl a-league and usl first division both exist in 2005
The answer is: false."""

QUERY_END2ENDER = """Here is the table to deduce true or false.'
/*
{table}
*/
Statement: {question}
The answer is:"""