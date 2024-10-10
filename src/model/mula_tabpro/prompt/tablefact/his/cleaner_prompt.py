PROMPT_CLEANER = {
    # demo for determining if the column should be extracted
    'relate_col_demo': """Please extract related columns based on the key words of the statement.

For example,

/*
Columns: "Rank", "Nation", "Gold", "Silver", "Bronze", "Total"

"Rank": 1 | 2 | 3,
"Nation": "South Korea" | "Chinese Taipei" | "Spain",
"Gold": 11 | 2 | 2,
"Silver": 1 | 2 | 0,
"Bronze": 2 | 5 | 4,
"Total": 14 | 9 | 6
*/
Statement: south korea has the most medals?
Keywords of the statement: <which country>, <most medals>
Related Columns: "Nation", "Total"
Explanation: The column "Nation" is related to <which country>. The column "Total" is related to <most medals>.

/*
Columns: "date", "division", "league", "regular season", "playoffs", "open cup", "avg. attendance"

"date": "2001-01-02" | "2002-08-06" | "2005-03-24",
"division": "usl a-league" | "usl first division",
"league": "usl a-league" | "usl first division",
"regular season": "4th | western" | "2nd | pacific" | "5th",
"playoffs": "quarterfinals" | "1st round" | "quarterfinals",
"open cup": "did not qualify" | "did not qualify" | "4th round",
"avg. attendance": 7169 | 6260 | 6028
*/
Statement: which year is the last year where this team was a part of the usl a-league?
Keywords of the statement: <which year>, <last year>, <where>, <this team was a part of the usl a-league>
Related Columns: "date", "league"
Explanation: The column "date" is related to <which year>, <last year>, <where>. The column "league" is related to <this team was a part of the usl a-league>.

/*
Columns: "No.", "Date", "Tournament", "Surface", "Score"

"No.": 1 | 2 | 3,
"Date": "23 August 2004" | "6 June 2005" | "20 June 2005",
"Tournament": "La Paz | Bolivia" | "Santa Tecla | El Salvador" | "Santa Tecla | El Salvador",
"Surface": "Clay" | "Clay" | "Clay",
"Score": "6-3 | 4-6 | 0-6" | "7-6(7-5) | 6-4" | "6-3 | 6-2"
*/
Statement: 'where was the last tournament won by andrew koch benvenuto held?'
Keywords of the statement: <where>, <last>, <tournament>, <won by andrew koch benvenuto>
Related Columns: "Date", "Tournament", "Surface", "Score"
Explanation: The column "Date" is related to <last>. The column "Tournament" is related to <tournament>. The column "Surface" is related to <where>. The column "Score" is related to <won by andrew koch benvenuto>.

/*
Columns: "DATE", "OPPONENT1", "SCORE1", "OPPONENT2", "SCORE2"

"DATE": "October 19" | "July 13" | "September 23 Governor's Cup",
"OPPONENT1": "STA.LUCIA" | "TANDUAY" | "BRGY.GINEBRA",
"SCORE1": "101-94" | "104-98" | "108-93",
"OPPONENT2": "KWENDE" | "BRGY.GINEBRA" | "BRGY.GINEBRA",
"SCORE2": "111-98" | "111-98" | "111-98"
*/
Statement: which game with TANDUAY has the greatest score difference?
Keywords of the statement: <which game>, <TANDUAY>, <greatest score difference>
Related Columns: "DATE", "OPPONENT1", "SCORE1", "OPPONENT2", "SCORE2"
Explanation: The column "DATE" is related to <which game>. The column "OPPONENT1" and ""OPPONENT2" is related to <TANDUAY>. The column "SCORE1" and "SCORE2" is related to <greatest score difference>.""",

    # query for determining if the column should be extracted
    'relate_col_query': """Please complete the prompt below,
/*
{cot_tbl}
*/
Statement: {question}
Return ```column_in_list``` with NO other texts.
Related Columns:""",

    'deduplication_demo': """Please determine whether should we remove the following records from the table.

For example,

The original table have similar pairs as below:
/*
pair number | name | telephone
---|---|---
1 | John | 18695579288
2 | John | +86 18695579288
*/

/*
pair number | name | telephone
---|---|---
1 | Tom | 16842724878
2 | Tom | +86 16842724878
*/
The Statement for original table: how many people are there in the table?
Answer: ```yes```
Explanation: The statement is asking for the number of people in the table. The similar records should be removed to avoid duplication. Thus, the answer is yes.

The original table have similar pairs as below:
/*
pair number | athlete | result | year
---|---|---|---
1 | John | win | 2001
2 | John | win | 2002
*/

/*
pair number | athlete | result | year
---|---|---|---
1 | Tom | lose | 2004
2 | Tom | lose | 2005
*/
The Statement for original table: how many athletes have lost the game?
Answer: ```no```
Explanation: The statement is asking for the number of athletes who have lost the game. The records describe the different years of the same athlete. Thus, the answer is no.""",

    'deduplication_query': """Here are some similar records in the table:

{cot_pairs}

Given the Statement: {question}
Whether should we remove these records? Answer ```yes_or_no``` based on the table with NO other texts.
Answer:""",
}