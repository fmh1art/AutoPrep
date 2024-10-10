DEMO_COT_END2ENDER = """Read the table below regarding "2008 Clásica de San Sebastián" to answer the following questions.

col: Rank | Cyclist | Team | Time | UCI ProTour Points
row1: 1 | Alejandro Valverde (ESP) | Caisse d'Epargne | 5h 29' 10 | 40
row2: 2 | Alexandr Kolobnev (RUS) | Team CSC Saxo Bank | s.t. | 30
row3: 3 | Davide Rebellin (ITA) | Gerolsteiner | s.t. | 25
row4: 4 | Paolo Bettini (ITA) | Quick Step | s.t. | 20
row5: 5 | Franco Pellizotti (ITA) | Liquigas | s.t. | 15
row6: 6 | Denis Menchov (RUS) | Rabobank | s.t. | 11
row7: 7 | Samuel Sánchez (ESP) | Euskaltel-Euskadi | s.t. | 7
row8: 8 | Stéphane Goubert (FRA) | Ag2r-La Mondiale | + 2 | 5
row9: 9 | Haimar Zubeldia (ESP) | Euskaltel-Euskadi | + 2 | 3
row10: 10 | David Moncoutié (FRA) | Cofidis | + 2 | 1

Question: which country had the most cyclists finish within the top 10?
Explanation: ITA occurs three times in the table, more than any others. Therefore, the answer is Italy.

Question: how many players got less than 10 points?
Explanation: Samuel Sánchez,  Stéphane Goubert, Haimar Zubeldia and David Moncoutié received less than 10 points.  Therefore, the answer is 4.

Question: how many points does the player from rank 3, rank 4 and rank 5 combine to have? 
Explanation: rank 3 has 25 points, rank 4 has 20 points, rank 5 has 15 points, they combine to have a total of 60 points. Therefore, the answer is 60.

Question: who spent the most time in the 2008 Clásica de San Sebastián?
Explanation: David Moncoutié spent the most time to finish the game and ranked the last. Therefore, the answer is David Moncoutié."""

QUERY_COT_END2ENDER = """Read the table below regarding "{title}" to answer the following questions.
/*
{table}
*/
Question: {question}
Answer the question based on the table with the format as above.
Explanation:"""