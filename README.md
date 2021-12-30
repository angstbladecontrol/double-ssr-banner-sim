# double-ssr-banner-sim
simulating 2 strats for fgo gacha
ODDS ARE OUTDATED. Might not be applicable anymore but i haven't kept up with all the changes.

Explanation:
I want to get copies of 2 different servants by rolling on their banners
Each banner is like a lottery and each roll is like buying a lottery ticket. I only have a limited number of rolls.
I want to determine my strategy for how I should roll on these banner
I can roll on 3 banners but they are only available for a limited time. If i skip a banner, I cannot go back.
The first banner gives me a chance at getting copies of the first servant
The second banner gives me a chance at getting copies of the second servant
the last banner gives me a chance at getting copies of both servants but at reduced rate for each

first copy is the most important.
addtional copies are valuable but beyond 2 copies has diminishing value for me
I do not have an explicit utility for each outcome so I want to tabulate the probability of any result
then I can make an intuitive decision on what strategy to go for

RollSimulation object has the simulation parameters and the results stored as properties
results are calculated lazily
2 strategies, soloForNP1 and duoOnly

soloForNP1:
roll on first banner until i get 1 copy of 1st serv. roll 2nd until i get 1 copy of 2nd serv. rest goes into duo
intuition is that this lets me target rolls for the one i dont have

duoOnly:
all in on duo banner
odds for both are lower individually but higher when added together.
