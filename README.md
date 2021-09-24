# Self-Consistent CFB Ranker
I was looking at a couple of computer CFB rankings, and the following occurred to me:
 - I can use a computer.
 - I know about football.
 - My opinions are better than other people's opinions.
 
So of course I had to do my own ranking system. Here are my principles:
 - Games are won or lost. Point differentials are meaningless. Really, your team is better because your 8th-string QB rushed for a couple garbage time TDs?
 - Wins and losses both matter. Equally.
 - The order in which games are played doesn't matter. No late-season bias. No inertia.
 - Beating a good team is better than beating a bad team, and similarly losing to a good team isn't as bad as losing to a bad team.
 - No judgement should be involved. No adjustable paramenters. In other words, there's no seed from a preseason poll, nor should there be sorting by P5/G5 etc. The rankings themselves have to determine what is a good win.
 - The final rankings should return themselves if run through the algorithm again.
 
 The guts of the ranking are as follows: an exponential function takes the "strength" of the opponent and uses win/loss outcome to set the sign. I set all the strengths at 1 to begin with, then it iterates until self-consistency of strengths. Multiple games are counted separately, rather than cancelling. 
 One caveat about the "no inputs" thing: only FBS teams are tracked, and all non-FBS teams have strength set to (minimum FBS strength - 1.0).

Data is downloaded from Sports Reference (i.e. https://www.sports-reference.com/cfb/years/2021-schedule.html click on "Share & Export" then "Get table as CSV (for Excel)").
