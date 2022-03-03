# basketball
Analytics tools for evaluating NBA player propositions. Player propositions are forms of wagers that many sportsbooks offer. They are often simple questions; for instance, is Stephen Curry going to have have over or under 24.5 points in tonight's game? I don't intend to place bets myself, but it's a great subject for analyzing. Given a collection of player propositions, my goal is to find the combination of picks that is most likely to result in a positive payout.

Written in Python, this project features web scraping, object-oriented programming, database manipulation, and statistical analysis.

Limitations:

- Proposition scraping
My initial goal was to scrape not only player game logs, but also player propositions from sportsbook websites. Then, I could automatically have a database of every player proposition offered on a given day and sort them by the probability they hit. Unfortunately, I believe that scraping such a website is against the terms of service agreements, and I don't want to ruffle any feathers. As a substitute, I can hard-code in various hypothetical player propositions to test my analysis pipeline.

- Player lookup
On basketballreference.com, a fantastic website containing game logs for NBA players, each NBA player is assigned a unique ID. This ID follows a simple formula. For example, Kevin Durant's player ID is d/duranke01, and Devin Booker's is b/bookede01. The 01 at the end of the ID's indicates they are the first player with that naming template. This is true in the vast majority of cases, but not all. For that reason, I have a dictionary of these ID's until I figure out a way to validate the ID is correct.


Future improvements:

-Generalize player lookup by checking if a generated player ID leads to the correct webpage.

