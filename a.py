emission_probs={"H":{"A":-2.322 , "C":-1.737, "G":-1.737 , "T":-2.322}, "L":{"A":-1.737 , "C":-2.322, "G":-2.322 , "T":-1.737} }
transition_probs={ "H" : {"H":-1,"L":-1}, "L" : {"H":-1.322,"L":-0.737} }
states=["H","L"]

input_str="GGCACTGAA"
start_probs={"H":-1, "L":-1}

vit_res={}
v_init_H=start_probs["H"]+emission_probs["H"][input_str[0]]
v_init_L=start_probs["L"]+emission_probs["L"][input_str[0]]
vit_res[0]={"H":v_init_H, "L":v_init_L}


for i in range(1, len(input_str)):
  temp_dict={}
  for j in range(len(states)):
    temp_dict[states[j]]=0
  vit_res[i]=temp_dict


for i in range(1,len(input_str)):
  for j in range(len(states)):
    term1=emission_probs[states[j]][input_str[i]]
    lis=[]
    for k in range(len(states)):
      lis.append(vit_res[i-1][states[k]]+transition_probs[states[k]][states[j]])
    maximum=max(lis)
    final_res=round(term1+maximum,6)

    vit_res[i][states[j]]=final_res

#print(vit_res)

h_lis=[]
l_lis=[]

for key in list(vit_res.keys()):
  val=vit_res[key]
  for v in list(val.keys()):
    if(v=='H'):
      h_lis.append(val[v])
    else:
      l_lis.append(val[v])


print("States",end="\t\t")
for key in list(vit_res.keys()):
  char=input_str[key]
  print(char,end="\t\t")

print("\n")
print("H",end="\t\t")
for h in h_lis:
  print(h,end="\t\t")

print("\n\n")
print("L",end="\t\t")
for l in l_lis:
  print(l,end="\t\t")


max_path=[]
print("\n\nPATH SEQUENCE")
for i in range(len(h_lis)):
  if(h_lis[i]>l_lis[i]):
    max_path.append('H')
  else:
    max_path.append('L')

print(max_path)

H = {'A': 0.2, 'C': 0.3, 'G': 0.3, 'T': 0.2}
L = {'A': 0.3, 'C': 0.2, 'G': 0.2, 'T': 0.3}

trProb = {     ('S', 'H'): 0.5, 
               ('S', 'L'): 0.5, 
               ('H', 'H'): 0.5, 
               ('L', 'L'): 0.6, 
               ('L', 'H'): 0.4, 
               ('H', 'L'): 0.5
         }

seq = 'GGCA'
P = []

for i in seq:
    if len(P) == 0:
        p = [trProb[('S', 'H')] * H[i] , trProb[('S', 'L')] * L[i]]
    else:
        p = []
        p.append(P[-1][0] * trProb[('H', 'H')] * H[i] + P[-1][1] * trProb[('L', 'H')] * H[i])
        p.append(P[-1][1] * trProb[('L', 'L')] * L[i] + P[-1][0] * trProb[('H', 'L')] * L[i])

    P.append(p)

print("Table: ", P)
print("Probability: ", P[-1][0] + P[-1][1])

import math 

transition={'pu':{'s':{'pu': 1}, 'a':{'pu': 0.5, 'pf':0.5}},
            'pf':{'s':{'rf':0.5, 'pu':0.5}, 'a':{'pf': 1}},
            'ru':{'s':{'ru':0.5, 'pu':0.5}, 'a':{'pu':0.5, 'pf':0.5}},
            'rf':{'s':{'rf':0.5, 'ru':0.5}, 'a':{'pf': 1}},
            }

rewards={'pu':0, 'pf':0, 'ru':10, 'rf':10}
newrewards={}
df=0.9

for j in range(5):
    for i in transition.keys():
        m = -math.inf 
        for actions in transition[i].keys():
            s = 0
            for state in transition[i][actions].keys():
                s += rewards[state]* transition[i][actions][state]
            m = max(m,s)
        newrewards[i] = rewards[i] + df*m
    flag = 0
    print(rewards, newrewards)
    for i in rewards.keys():
        if abs(rewards[i] - newrewards[i]) > 0.5:
            flag = 1
    
    if flag == 0:
        break
    
    rewards = newrewards.copy()
    newrewards = {}
