DEMO_TABLE_READER = """Please generate the table summarization based on the table and the question.

For example,

/*
row number | Rank | Nation | Gold | Silver | Bronze | Total
---|---|---|---|---|---|---
1 | 1 | South Korea | 11 | 1 | 2 | 14
2 | 2 | Chinese Taipei | 2 | 2 | 5 | 9
3 | 3 | Spain | 2 | 0 | 4 | 6
*/
Question: which county has the most medals?
Table Summarization: ```The table describes the medal numbers of nations in a sporting event.```

/*
row number | Year | Competition | Venue | Position | Notes
---|---|---|---|---|---
1 | 1999 | World Youth Championships | Bydgoszcz, Poland | 13th (q) | 4.60 m
2 | 2001 | European Junior Championships | Grosseto, Italy | 7th | 5.15 m
3 | 2002 | World Junior Championships | Kingston, Jamaica | 8th | 5.30 m
4 | 2003 | European U23 Championships | Bydgoszcz, Poland | 13th (q) | 5.20 m
*/
Question:what is the difference between przemyslaw's highest and lowest vault during his competition record?
Table Summarization: ```The table is about Przemyslaw's competition records in different championships.```"""

QUERY_TABLE_READER = """Please complete the prompt below,
/*
{cot_tbl}
*/
Question: {question}
Output ```your_summary_here``` without NO EXTRA text. Only summarize information related to the question.
Table Summarization:"""