## CS258 Final Project RSA Reinforcement 

# About
CS258 final project using reinforcement learning to better utilize link utilization, using PPO, DQN, and a baseline with no learning. This project uses the OpenAI based implementations of PPO and DQN to interact with a custom network enviornment built in Gymnasium. 

# Structure Breakdown
* A4: contains a full implmentation of A4 but with the use of nsfnet.gml instead of 4 edge graph.
* Reinforcement Learning: contains the reinforcement learning implementation using PPOConfig, baseline, and DQN
* LaTex: contains the source file and pdf of the final report
* Data: contains the data from scenario 1 and 2, as well as utilization of the links
  
# Branch Breakdown
A4 branch is the implementation of Martin and ejamdar is the branch of Eshaq. The final report mainly uses results obtained from the A4 Martin branch and is merged into main. The ejamdar branch is a different implementation but will not use the results from it. However, if you wanted to observe the ejamdar solution, the branch has the source code as well as the reinfocement learning results and the average utilization results.
